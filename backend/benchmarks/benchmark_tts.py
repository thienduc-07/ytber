import os
import sys
import time
import json
import asyncio
import subprocess
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.providers.tts_chunker import VietnameseTextChunker
from backend.providers.tts_engine import EdgeTTSVoiceProvider, VietnameseTextNormalizer
from backend.providers.mp3_stitcher import MP3Stitcher

SAMPLE_CORPUS = [
    "Việt Nam trải qua hàng ngàn năm dựng nước và giữ nước với những trang sử hào hùng oanh liệt.",
    "Từ thời các vua Hùng khai sơn lập quốc cho đến thời đại Hồ Chí Minh rực rỡ gấm hoa vạn dặm.",
    "Thành phố Thăng Long xưa và Hà Nội ngày nay luôn là trái tim văn hiến của toàn thể dân tộc.",
    "Công nghệ trí tuệ nhân tạo và xử lý ngôn ngữ tự nhiên đang mở ra những cánh cửa phát triển vượt bậc.",
    "Âm thanh truyền tải cảm xúc chân thực, kết nối tâm hồn và lan tỏa tri thức đến muôn nơi xa xôi.",
    "Dòng sông Mê Kông cuồn cuộn chảy qua đồng bằng Nam Bộ bồi đắp phù sa cho vựa lúa trù phú bát ngát.",
    "Đỉnh Fansipan hùng vĩ sừng sững giữa trời mây Hoàng Liên Sơn như biểu tượng cho ý chí kiên cường.",
    "Các thế hệ con người Việt Nam luôn đoàn kết một lòng, vượt qua mọi phong ba bão táp để vươn tới tương lai."
]

def generate_text(word_target: int) -> str:
    words = []
    normalizer = VietnameseTextNormalizer()
    idx = 0
    while len(words) < word_target:
        sentence = SAMPLE_CORPUS[idx % len(SAMPLE_CORPUS)]
        words.extend(sentence.split())
        idx += 1
    raw = " ".join(words[:word_target])
    return normalizer.normalize(raw)

async def run_tier_benchmark(provider: EdgeTTSVoiceProvider, chunker: VietnameseTextChunker, word_target: int, tier_name: str) -> dict:
    text = generate_text(word_target)
    actual_words = len(text.split())
    actual_chars = len(text)

    # 1. Chunking analysis
    t0_chunk = time.perf_counter()
    chunks = chunker.chunk_text(text)
    t1_chunk = time.perf_counter()
    chunk_latency_ms = round((t1_chunk - t0_chunk) * 1000, 3)

    print(f"\n=======================================================")
    print(f"BENCHMARK TIER: {tier_name} (~{word_target} words)")
    print(f"=======================================================")
    print(f"Words: {actual_words:,} | Chars: {actual_chars:,} | Chunks: {len(chunks)} | Chunker latency: {chunk_latency_ms} ms")

    # 2. Cold Synthesis
    print(f"Running Cold Synthesis (Voice: vi-VN-NamMinhNeural)...")
    t0_cold = time.perf_counter()
    res_cold = await provider.synthesize(text, voice="vi-VN-NamMinhNeural")
    t1_cold = time.perf_counter()
    cold_duration_sec = round(t1_cold - t0_cold, 3)
    assert not res_cold.cached, "Cold run should not be cached"
    print(f"-> Cold synthesis completed in {cold_duration_sec:.2f} s (Audio duration: {res_cold.duration_seconds:.2f} s)")

    # 3. Cached Synthesis
    print(f"Running Cached Retrieval...")
    t0_cache = time.perf_counter()
    res_cache = await provider.synthesize(text, voice="vi-VN-NamMinhNeural")
    t1_cache = time.perf_counter()
    cache_duration_ms = round((t1_cache - t0_cache) * 1000, 3)
    assert res_cache.cached, "Second run must be a cache hit"
    print(f"-> Cache retrieval completed in {cache_duration_ms:.2f} ms")

    # 4. Audio File Inspection
    filename = f"{res_cold.audio_id}.mp3"
    filepath = os.path.join(provider.storage_dir, filename)
    file_size_bytes = os.path.getsize(filepath)
    file_size_kb = round(file_size_bytes / 1024, 2)

    # 5. CoreAudio afinfo verification
    afinfo_res = subprocess.run(["afinfo", filepath], capture_output=True, text=True)
    afinfo_valid = (afinfo_res.returncode == 0)

    # 6. Monotonicity check
    words_count = len(res_cold.words)
    monotonic = True
    prev = -1
    for w in res_cold.words:
        if w.start_ms < prev or w.end_ms < w.start_ms:
            monotonic = False
            break
        prev = w.start_ms

    # Calculate real-time factor (RTF = Cold Synthesis Duration / Audio Duration)
    rtf = round(cold_duration_sec / res_cold.duration_seconds, 3) if res_cold.duration_seconds > 0 else 0

    tier_metrics = {
        "tier": tier_name,
        "word_target": word_target,
        "actual_words": actual_words,
        "actual_chars": actual_chars,
        "chunks_count": len(chunks),
        "chunk_latency_ms": chunk_latency_ms,
        "cold_synthesis_seconds": cold_duration_sec,
        "cache_retrieval_ms": cache_duration_ms,
        "audio_duration_seconds": res_cold.duration_seconds,
        "rtf": rtf,
        "words_detected": words_count,
        "words_monotonic": monotonic,
        "file_size_kb": file_size_kb,
        "afinfo_valid": afinfo_valid,
        "sample_rate": res_cold.sample_rate
    }
    print(f"Metrics: RTF={rtf} | Size={file_size_kb} KB | afinfo valid={afinfo_valid}")
    return tier_metrics

async def main():
    print("Initializing Production TTS Benchmark Suite...")
    provider = EdgeTTSVoiceProvider()
    chunker = VietnameseTextChunker(max_chars=250)

    tiers = [
        (100, "Short (Shorts/Reels)"),
        (500, "Medium (Standard Explainer)"),
        (2000, "Long (Documentary / Episode)"),
        (5000, "Extra Long (Audiobook / Deep Dive)")
    ]

    all_metrics = []
    for word_target, name in tiers:
        metrics = await run_tier_benchmark(provider, chunker, word_target, name)
        all_metrics.append(metrics)

    output_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2, ensure_ascii=False)
    print(f"\nAll benchmark tiers finished successfully! Saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
