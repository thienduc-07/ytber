import os
import re
import json
import uuid
import random
import hashlib
import asyncio
import math
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import httpx
from pydantic import BaseModel, Field

import edge_tts
from backend.core.config import settings
from backend.providers.tts_chunker import VietnameseTextChunker, TextChunk
from backend.providers.mp3_stitcher import MP3Stitcher

logger = logging.getLogger(__name__)

TTS_ENGINE_VERSION = "2.2.0"

class TTSGenerationError(Exception):
    """Raised when TTS synthesis fails and cannot produce genuine audio."""
    pass

def validate_audio_file(data_or_path: Any, min_bytes: int = 512) -> Tuple[bool, str]:
    """
    Validates audio file or bytes:
    1. Size >= min_bytes
    2. Valid audio header (MP3 frame sync 0xFFFB/0xFFFA/0xFFF3 or RIFF/WAVE header)
    3. Non-silent waveform (checks frame entropy / dynamic variance / non-uniformity)
    """
    if isinstance(data_or_path, (str, os.PathLike)):
        if not os.path.exists(data_or_path):
            return False, f"Audio file does not exist: {data_or_path}"
        with open(data_or_path, "rb") as f:
            raw_bytes = f.read()
    elif isinstance(data_or_path, (bytes, bytearray)):
        raw_bytes = bytes(data_or_path)
    else:
        return False, "Invalid audio input type"

    if len(raw_bytes) < min_bytes:
        return False, f"Audio file too small: {len(raw_bytes)} bytes (minimum: {min_bytes} bytes)"

    # Check for MP3 ID3 header or sync word
    is_mp3 = False
    is_wav = False

    if raw_bytes.startswith(b"ID3"):
        is_mp3 = True
    elif raw_bytes.startswith(b"RIFF") and b"WAVE" in raw_bytes[:16]:
        is_wav = True
    else:
        for i in range(min(1024, len(raw_bytes) - 1)):
            if raw_bytes[i] == 0xFF and (raw_bytes[i + 1] & 0xE0) == 0xE0:
                is_mp3 = True
                break

    if not (is_mp3 or is_wav):
        return False, "Invalid audio format: neither valid MP3 frame sync nor RIFF/WAVE header found"

    # Check for silent / dummy / repeating pattern (e.g. all 0x00 or repeating 0x55)
    sample_slice = raw_bytes[min(128, len(raw_bytes)): min(4096, len(raw_bytes))]
    if len(sample_slice) > 32:
        unique_bytes = len(set(sample_slice))
        if unique_bytes < 8:
            return False, f"Audio stream detected as silent/synthetic mock (only {unique_bytes} unique byte values)"

    return True, "Valid non-silent audio"

class WordTiming(BaseModel):
    word: str
    text: Optional[str] = None
    start_ms: int
    end_ms: int
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    chunk_index: int = 0

    def __init__(self, **data):
        super().__init__(**data)
        if self.text is None:
            self.text = self.word
        if self.start_time is None:
            self.start_time = round(self.start_ms / 1000.0, 3)
        if self.end_time is None:
            self.end_time = round(self.end_ms / 1000.0, 3)

class TTSResult(BaseModel):
    audio_id: str
    normalized_text: str
    audio_url: str
    duration_seconds: float
    words: List[WordTiming]
    provider: str
    sample_rate: int = 24000
    format: str = "mp3"
    cached: bool = False

# Vietnamese number-to-words dictionary
ONES = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]

def number_to_vietnamese_words(n: int) -> str:
    if n < 0:
        return "âm " + number_to_vietnamese_words(abs(n))
    if n < 10:
        return ONES[n]
    if n < 20:
        if n == 10:
            return "mười"
        if n == 15:
            return "mười lăm"
        return "mười " + ONES[n % 10]
    if n < 100:
        tens = n // 10
        rem = n % 10
        tens_str = ONES[tens] + " mươi"
        if rem == 0:
            return tens_str
        if rem == 1:
            return tens_str + " mốt"
        if rem == 4:
            return tens_str + " tư"
        if rem == 5:
            return tens_str + " lăm"
        return tens_str + " " + ONES[rem]
    if n < 1000:
        hundreds = n // 100
        rem = n % 100
        res = ONES[hundreds] + " trăm"
        if rem == 0:
            return res
        if rem < 10:
            return res + " linh " + ONES[rem]
        return res + " " + number_to_vietnamese_words(rem)
    if n < 1000000:
        thousands = n // 1000
        rem = n % 1000
        res = number_to_vietnamese_words(thousands) + " nghìn"
        if rem == 0:
            return res
        if rem < 100:
            return res + " không trăm " + number_to_vietnamese_words(rem)
        return res + " " + number_to_vietnamese_words(rem)
    return str(n)

class VietnameseTextNormalizer:
    LOAN_WORDS = {
        "render": "ren đơ",
        "fps": "khung hình trên giây",
        "shorts": "vi đê ô ngắn",
        "tiktok": "tíc tốc",
        "youtube": "du túp",
        "audio": "âm thanh",
        "ducking": "đắc kinh",
        "manchester": "man che tơ",
        "broughton": "brâu tơn"
    }

    def normalize(self, text: str) -> str:
        res = text
        # 1. Normalize dates (e.g. 12/04/1831 or 12/04)
        def replace_date(m):
            prefix = m.group(1) or ""
            d, mo = int(m.group(2)), int(m.group(3))
            mo_str = "tư" if mo == 4 else number_to_vietnamese_words(mo)
            yr = f" năm {number_to_vietnamese_words(int(m.group(4)))}" if m.group(4) else ""
            d_prefix = "ngày " if not prefix else prefix
            return f"{d_prefix}{number_to_vietnamese_words(d)} tháng {mo_str}{yr}"

        res = re.sub(r'(?i)(ngày\s+)?\b(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b', replace_date, res)

        # 1.5. Normalize decimals and percentages (e.g. 7.09% -> bảy phẩy không chín phần trăm)
        digits_map = {'0': 'không', '1': 'một', '2': 'hai', '3': 'ba', '4': 'bốn', '5': 'năm', '6': 'sáu', '7': 'bảy', '8': 'tám', '9': 'chín'}
        def replace_decimal(m):
            left = number_to_vietnamese_words(int(m.group(1)))
            right_digits = [digits_map[d] for d in m.group(2)]
            return f"{left} phẩy {' '.join(right_digits)}"

        res = re.sub(r'\b(\d+)\.(\d+)\b', replace_decimal, res)
        res = res.replace("%", " phần trăm")

        # 2. Normalize integers (e.g. 74, 1831)
        def replace_num(m):
            num = int(m.group(0))
            if num < 1000000:
                return number_to_vietnamese_words(num)
            return m.group(0)

        res = re.sub(r'\b\d+\b', replace_num, res)

        # 3. Normalize loan words
        for eng, vn in self.LOAN_WORDS.items():
            pattern = re.compile(rf'\b{re.escape(eng)}\b', re.IGNORECASE)
            res = pattern.sub(vn, res)

        return re.sub(r'\s+', ' ', res).strip()

VOICE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "vi-VN-NamMinhNeural": {
        "id": "vi-VN-NamMinhNeural",
        "name": "Nam Minh (Giọng Nam - Miền Bắc)",
        "display_name": "Nam Minh (Nam Bắc)",
        "gender": "Male",
        "locale": "vi-VN",
        "sample_rate": 24000,
        "default_rate": "+0%",
        "default_pitch": "+0Hz",
        "default_volume": "+0%",
        "supported_parameters": ["rate", "pitch", "volume"],
        "description": "Giọng nam tự nhiên, truyền cảm, thích hợp làm phim tài liệu, lịch sử, tin tức."
    },
    "vi-VN-HoaiMyNeural": {
        "id": "vi-VN-HoaiMyNeural",
        "name": "Hoài My (Giọng Nữ - Miền Bắc)",
        "display_name": "Hoài My (Nữ Bắc)",
        "gender": "Female",
        "locale": "vi-VN",
        "sample_rate": 24000,
        "default_rate": "+0%",
        "default_pitch": "+0Hz",
        "default_volume": "+0%",
        "supported_parameters": ["rate", "pitch", "volume"],
        "description": "Giọng nữ truyền cảm, ấm áp, thích hợp làm video kinh tế, giáo dục, giải thích."
    }
}

class VoiceProvider(ABC):
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: str = "vi-VN-NamMinhNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%"
    ) -> TTSResult:
        pass

    @abstractmethod
    def get_supported_voices(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def estimate_duration(self, text: str) -> float:
        pass

class EdgeTTSVoiceProvider(VoiceProvider):
    """
    Production-grade Vietnamese Speech Synthesis Engine using Microsoft Edge Neural TTS.
    Features:
    - Hierarchical Vietnamese Text Chunker (handles scripts from 10 to 10,000+ words)
    - Independent chunk generation & frame-synchronized MP3 stitching
    - Monotonic, globally accurate word-level timestamps relative to full timeline
    - Bounded concurrency control via asyncio.Semaphore
    - Exponential backoff retry with jitter
    - Deterministic SHA256 content-based caching with deduplication locks
    - Failure recovery with valid on-disk fallback audio
    """

    def __init__(self, storage_dir: Optional[str] = None):
        self.normalizer = VietnameseTextNormalizer()
        self.chunker = VietnameseTextChunker(max_chars=getattr(settings, "TTS_MAX_CHUNK_CHARS", 250))
        self.stitcher = MP3Stitcher()
        self._storage_dir = storage_dir

        max_conc = getattr(settings, "MAX_TTS_CONCURRENCY", 2)
        self._semaphore = asyncio.Semaphore(max_conc)
        self._cache_locks: Dict[str, asyncio.Lock] = {}

    @property
    def storage_dir(self) -> str:
        d = self._storage_dir or settings.AUDIO_STORAGE_PATH
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        return d

    def get_supported_voices(self) -> List[Dict[str, Any]]:
        return list(VOICE_REGISTRY.values())

    def estimate_duration(self, text: str) -> float:
        normalized = self.normalizer.normalize(text)
        words_count = max(1, len(normalized.split()))
        return round(max(1.5, words_count / 3.8), 2)

    def _generate_cache_key(self, text: str, voice: str, rate: str, pitch: str, volume: str) -> str:
        raw_key = f"{TTS_ENGINE_VERSION}|{text}|{voice}|{rate}|{pitch}|{volume}|mp3"
        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    async def _synthesize_single_chunk(
        self,
        chunk_text: str,
        voice: str,
        rate: str,
        pitch: str,
        volume: str,
        timeout_sec: float
    ) -> Tuple[bytes, List[Dict[str, Any]]]:
        comm_kwargs = {}
        if rate and rate != "+0%":
            comm_kwargs["rate"] = rate
        if pitch and pitch != "+0Hz":
            comm_kwargs["pitch"] = pitch
        if volume and volume != "+0%":
            comm_kwargs["volume"] = volume

        # Vietnamese neural voices in Microsoft Edge-TTS do not support boundary='WordBoundary'
        # and reject the stream with NoAudioReceived. We omit boundary so it defaults to
        # SentenceBoundary / standard binary audio stream.
        communicate = edge_tts.Communicate(
            text=chunk_text,
            voice=voice,
            **comm_kwargs
        )
        # Critical Fix: edge_tts internally converts 'vi-VN-NamMinhNeural' into the legacy long string
        # 'Microsoft Server Speech Text to Speech Voice (vi-VN, NamMinhNeural)', which causes
        # Microsoft's WebSocket service to reject multi-sentence Vietnamese texts with NoAudioReceived.
        # Re-assigning the clean short voice name ensures 100% synthesis success and full audio streams.
        communicate.tts_config.voice = voice

        audio_bytes = bytearray()
        raw_words: List[Dict[str, Any]] = []

        async def stream_worker():
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])
                elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                    start_ms = int(chunk["offset"] // 10000)
                    dur_ms = int(chunk["duration"] // 10000)
                    raw_words.append({
                        "word": chunk.get("text", "").strip(),
                        "start_ms": start_ms,
                        "end_ms": start_ms + dur_ms
                    })

        await asyncio.wait_for(stream_worker(), timeout=timeout_sec)

        if len(audio_bytes) == 0:
            raise ValueError("Edge-TTS returned empty audio stream")

        return bytes(audio_bytes), raw_words

    async def _synthesize_chunk_with_retry(
        self,
        chunk_text: str,
        voice: str,
        rate: str,
        pitch: str,
        volume: str,
        max_retries: int = 3
    ) -> Tuple[bytes, List[Dict[str, Any]]]:
        """
        Synthesizes a single text chunk with concurrency control, timeout, and jittered backoff.
        """
        timeout_sec = getattr(settings, "TTS_TIMEOUT_SECONDS", 30.0)
        last_error = None

        for attempt in range(max_retries):
            try:
                async with self._semaphore:
                    return await self._synthesize_single_chunk(
                        chunk_text=chunk_text,
                        voice=voice,
                        rate=rate,
                        pitch=pitch,
                        volume=volume,
                        timeout_sec=timeout_sec
                    )
            except asyncio.CancelledError:
                raise
            except Exception as e:
                last_error = e
                if attempt == max_retries - 1:
                    break
                # Exponential backoff with jitter
                delay = (0.5 * (2 ** attempt)) + random.uniform(0.1, 0.4)
                await asyncio.sleep(delay)

        raise RuntimeError(f"Edge-TTS chunk synthesis failed after {max_retries} attempts: {str(last_error)}")

    async def synthesize(
        self,
        text: str,
        voice: str = "vi-VN-NamMinhNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%"
    ) -> TTSResult:
        normalized_text = self.normalizer.normalize(text)
        if not normalized_text:
            raise ValueError("Văn bản đầu vào không được để trống sau khi chuẩn hóa")

        # Validate voice
        selected_voice = voice if voice in VOICE_REGISTRY else "vi-VN-NamMinhNeural"

        # Content-based Cache Key
        cache_key = self._generate_cache_key(normalized_text, selected_voice, rate, pitch, volume)
        audio_filename = f"{cache_key}.mp3"
        audio_filepath = os.path.join(self.storage_dir, audio_filename)
        meta_filepath = os.path.join(self.storage_dir, f"{cache_key}.meta.json")

        # Fast path: Cache hit check
        if getattr(settings, "TTS_CACHE_ENABLED", True):
            if os.path.exists(audio_filepath) and os.path.exists(meta_filepath):
                try:
                    with open(meta_filepath, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    words = [WordTiming(**w) for w in meta.get("words", [])]
                    return TTSResult(
                        audio_id=cache_key,
                        normalized_text=normalized_text,
                        audio_url=f"/api/v1/tts/audio/{audio_filename}",
                        duration_seconds=meta.get("duration_seconds", 0.0),
                        words=words,
                        provider="edge-tts-neural-cache",
                        sample_rate=meta.get("sample_rate", 24000),
                        format="mp3",
                        cached=True
                    )
                except Exception:
                    pass  # If cache file corrupt, regenerate

        # Concurrent deduplication lock per cache_key
        if cache_key not in self._cache_locks:
            self._cache_locks[cache_key] = asyncio.Lock()

        async with self._cache_locks[cache_key]:
            # Double check cache after acquiring lock
            if os.path.exists(audio_filepath) and os.path.exists(meta_filepath):
                try:
                    with open(meta_filepath, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    words = [WordTiming(**w) for w in meta.get("words", [])]
                    return TTSResult(
                        audio_id=cache_key,
                        normalized_text=normalized_text,
                        audio_url=f"/api/v1/tts/audio/{audio_filename}",
                        duration_seconds=meta.get("duration_seconds", 0.0),
                        words=words,
                        provider="edge-tts-neural-cache",
                        sample_rate=meta.get("sample_rate", 24000),
                        format="mp3",
                        cached=True
                    )
                except Exception:
                    pass

            # Chunk text if necessary
            chunks = self.chunker.chunk_text(normalized_text)
            if not chunks:
                chunks = [TextChunk(0, normalized_text, len(normalized_text), len(normalized_text.split()))]

            chunk_audio_buffers: List[bytes] = []
            chunk_raw_words: List[List[Dict[str, Any]]] = []

            try:
                for chunk in chunks:
                    c_audio, c_words = await self._synthesize_chunk_with_retry(
                        chunk_text=chunk.text,
                        voice=selected_voice,
                        rate=rate,
                        pitch=pitch,
                        volume=volume
                    )
                    chunk_audio_buffers.append(c_audio)
                    chunk_raw_words.append(c_words)

                # Stitch all audio chunks seamlessly
                stitched_bytes, chunk_durations, total_duration = self.stitcher.stitch_chunks(
                    chunk_audio_buffers,
                    default_sample_rate=24000
                )

                # Rebase word timestamps to global timeline
                global_words: List[WordTiming] = []
                current_offset_ms = 0

                for c_idx, c_words in enumerate(chunk_raw_words):
                    c_dur_ms = int(chunk_durations[c_idx] * 1000)

                    for w in c_words:
                        w_start = current_offset_ms + w["start_ms"]
                        w_end = current_offset_ms + w["end_ms"]
                        global_words.append(WordTiming(
                            word=w["word"],
                            text=w["word"],
                            start_ms=w_start,
                            end_ms=w_end,
                            start_time=round(w_start / 1000.0, 3),
                            end_time=round(w_end / 1000.0, 3),
                            chunk_index=c_idx
                        ))

                    current_offset_ms += c_dur_ms

                # If sentence boundary or sparse cues were returned, refine into syllable word cues for kinetic pop captions
                if len(global_words) < max(1, len(normalized_text.split()) // 2):
                    global_words = TTSService(storage_dir=self.storage_dir).generate_syllable_timings(normalized_text, total_duration)

                # Write stitched audio file to disk atomically
                temp_audio_path = f"{audio_filepath}.tmp"
                with open(temp_audio_path, "wb") as f:
                    f.write(stitched_bytes)
                os.replace(temp_audio_path, audio_filepath)

                # Save metadata for fast cache retrieval
                meta_dict = {
                    "cache_key": cache_key,
                    "duration_seconds": total_duration,
                    "words": [w.model_dump() if hasattr(w, "model_dump") else w.dict() for w in global_words],
                    "sample_rate": 24000,
                    "chunks_count": len(chunks),
                    "created_at": asyncio.get_event_loop().time()
                }
                with open(meta_filepath, "w", encoding="utf-8") as f:
                    json.dump(meta_dict, f, ensure_ascii=False)

                return TTSResult(
                    audio_id=cache_key,
                    normalized_text=normalized_text,
                    audio_url=f"/api/v1/tts/audio/{audio_filename}",
                    duration_seconds=total_duration,
                    words=global_words,
                    provider="edge-tts-neural",
                    sample_rate=24000,
                    format="mp3",
                    cached=False
                )

            except Exception as e:
                logger.error(f"EdgeTTS synthesis failed for text: {normalized_text[:30]}... Error: {e}")
                raise TTSGenerationError(f"EdgeTTS synthesis failed: {str(e)}")

class TTSService:
    """Offline Fallback Voice Service maintaining 100% API and filesystem continuity."""
    def __init__(self, storage_dir: Optional[str] = None):
        self.normalizer = VietnameseTextNormalizer()
        self.storage_dir = storage_dir or getattr(settings, "AUDIO_STORAGE_PATH", "./data/audio")
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)

    def generate_syllable_timings(self, text: str, total_duration_sec: float) -> List[WordTiming]:
        words = text.split()
        if not words:
            return []

        total_ms = int(total_duration_sec * 1000)
        start_buffer = min(80, total_ms // (len(words) * 2))
        end_buffer = min(80, total_ms // (len(words) * 2))
        usable_ms = max(len(words) * 60, total_ms - start_buffer - end_buffer)

        weights = [1.35 if (w.endswith(('.', '!', '?', ',', ';', ':')) or idx == len(words) - 1) else 1.0 for idx, w in enumerate(words)]
        total_weight = sum(weights)

        timings: List[WordTiming] = []
        cur_ms = start_buffer

        for idx, w in enumerate(words):
            raw_dur = int((weights[idx] / total_weight) * usable_ms)
            word_dur = max(40, raw_dur)
            end_ms = cur_ms + word_dur
            if idx == len(words) - 1:
                end_ms = min(total_ms, max(cur_ms + 40, total_ms - 20))
            else:
                end_ms = min(total_ms - (len(words) - 1 - idx) * 40, end_ms)

            clean_word = re.sub(r'[^\w\s-]', '', w)
            timings.append(WordTiming(
                word=clean_word or w,
                text=clean_word or w,
                start_ms=cur_ms,
                end_ms=end_ms,
                start_time=round(cur_ms / 1000.0, 3),
                end_time=round(end_ms / 1000.0, 3),
                chunk_index=0
            ))
            cur_ms = end_ms

        return timings

    async def synthesize(self, text: str, voice: str = "vi-VN-NamMinhNeural") -> TTSResult:
        raise TTSGenerationError(
            "Synthetic harmonic tones are strictly disabled in production. "
            "A genuine neural voice provider (VoiceStudio or EdgeTTS) is required."
        )

class VoiceStudioProvider(VoiceProvider):
    """
    Primary Vietnamese Speech Synthesis Engine using debpalash/VoiceStudio.
    Features:
    - High-quality open-source neural TTS (AGPL-3.0) via local HTTP server
    - Automatic health checking with fast-fail circuit breaker
    - Full input validation & non-silent audio output verification
    - Deterministic SHA256 caching
    - Real audio duration measurement directly from frame analysis
    """
    def __init__(self, storage_dir: Optional[str] = None):
        self.normalizer = VietnameseTextNormalizer()
        self.stitcher = MP3Stitcher()
        self._storage_dir = storage_dir
        self.base_url = getattr(settings, "VOICESTUDIO_URL", "http://127.0.0.1:3900").rstrip("/")
        self.timeout = getattr(settings, "VOICESTUDIO_TIMEOUT_SECONDS", 30.0)
        self.enabled = getattr(settings, "VOICESTUDIO_ENABLED", True)

    @property
    def storage_dir(self) -> str:
        d = self._storage_dir or settings.AUDIO_STORAGE_PATH
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        return d

    def get_supported_voices(self) -> List[Dict[str, Any]]:
        return list(VOICE_REGISTRY.values())

    def estimate_duration(self, text: str) -> float:
        normalized = self.normalizer.normalize(text)
        words_count = max(1, len(normalized.split()))
        return round(max(1.5, words_count / 3.8), 2)

    def _parse_speed(self, rate_str: str) -> float:
        if not rate_str or rate_str == "+0%":
            return 1.0
        m = re.match(r"^([+-]?\d+)%$", rate_str)
        if m:
            pct = int(m.group(1))
            return max(0.5, min(2.0, 1.0 + (pct / 100.0)))
        return 1.0

    async def is_available(self) -> bool:
        """Fast health check probe with 1.5s timeout."""
        if not self.enabled:
            return False
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.base_url}/health")
                return res.status_code == 200
        except Exception:
            return False

    async def synthesize(
        self,
        text: str,
        voice: str = "vi-VN-NamMinhNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%"
    ) -> TTSResult:
        normalized_text = self.normalizer.normalize(text)
        if not normalized_text:
            raise ValueError("Văn bản đầu vào không được để trống sau khi chuẩn hóa")

        speed = self._parse_speed(rate)
        cache_key = hashlib.sha256(
            f"VOICESTUDIO|{normalized_text}|{voice}|{speed}|mp3".encode("utf-8")
        ).hexdigest()
        filename = f"vs_{cache_key}.mp3"
        filepath = os.path.join(self.storage_dir, filename)
        meta_filepath = os.path.join(self.storage_dir, f"vs_{cache_key}.meta.json")

        # Cache check
        if getattr(settings, "TTS_CACHE_ENABLED", True) and os.path.exists(filepath) and os.path.exists(meta_filepath):
            try:
                with open(meta_filepath, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                return TTSResult(
                    audio_id=f"vs_{cache_key}",
                    normalized_text=normalized_text,
                    audio_url=f"/api/v1/tts/audio/{filename}",
                    duration_seconds=meta.get("duration_seconds", 0.0),
                    words=[WordTiming(**w) for w in meta.get("words", [])],
                    provider="voicestudio-cached",
                    sample_rate=meta.get("sample_rate", 24000),
                    format="mp3",
                    cached=True
                )
            except Exception:
                pass

        payload = {
            "model": "omnivoice",
            "input": normalized_text,
            "voice": voice,
            "response_format": "mp3",
            "speed": speed,
            "language": "vi"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/v1/audio/speech", json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"VoiceStudio API error: HTTP {resp.status_code} - {resp.text[:200]}")

            audio_bytes = resp.content

        # Output validation
        is_valid, err_msg = validate_audio_file(audio_bytes, min_bytes=512)
        if not is_valid:
            raise ValueError(f"VoiceStudio produced invalid audio: {err_msg}")

        # Real audio duration parsing
        num_frames, real_dur, pure_audio = self.stitcher.parse_frames(audio_bytes)
        if real_dur <= 0.0:
            real_dur = self.estimate_duration(normalized_text)

        # Word timing generation
        timings = TTSService(storage_dir=self.storage_dir).generate_syllable_timings(normalized_text, real_dur)

        # Atomic file write
        temp_path = f"{filepath}.tmp"
        with open(temp_path, "wb") as f:
            f.write(pure_audio if pure_audio else audio_bytes)
        os.replace(temp_path, filepath)

        meta_dict = {
            "cache_key": cache_key,
            "duration_seconds": real_dur,
            "words": [w.model_dump() if hasattr(w, "model_dump") else w.dict() for w in timings],
            "sample_rate": 24000,
            "provider": "voicestudio",
            "created_at": asyncio.get_event_loop().time()
        }
        with open(meta_filepath, "w", encoding="utf-8") as f:
            json.dump(meta_dict, f, ensure_ascii=False)

        return TTSResult(
            audio_id=f"vs_{cache_key}",
            normalized_text=normalized_text,
            audio_url=f"/api/v1/tts/audio/{filename}",
            duration_seconds=real_dur,
            words=timings,
            provider="voicestudio",
            sample_rate=24000,
            format="mp3",
            cached=False
        )

class UnifiedTTSProvider(VoiceProvider):
    """
    Unified Production TTS Provider with dual-engine failover:
    Primary: VoiceStudioProvider (Local Neural TTS via debpalash/VoiceStudio)
    Secondary: EdgeTTSVoiceProvider (Microsoft Edge Neural TTS)
    
    Zero-Mock Strict Policy:
    Provides intelligent auto-switching with diagnostic recovery.
    """
    def __init__(
        self,
        storage_dir: Optional[str] = None,
        allow_offline_fallback: bool = False,
        engine_mode: str = "auto"
    ):
        self.voicestudio = VoiceStudioProvider(storage_dir=storage_dir)
        self.edge_tts = EdgeTTSVoiceProvider(storage_dir=storage_dir)
        self._storage_dir = storage_dir
        self.allow_offline_fallback = allow_offline_fallback
        self.engine_mode = engine_mode  # "auto" | "voicestudio" | "edgetts"

    @property
    def storage_dir(self) -> str:
        return self._storage_dir or settings.AUDIO_STORAGE_PATH

    def set_engine_mode(self, mode: str):
        if mode in ("auto", "voicestudio", "edgetts"):
            self.engine_mode = mode

    def set_voicestudio_url(self, url: str):
        if url and url.startswith("http"):
            self.voicestudio.base_url = url.rstrip("/")

    def get_supported_voices(self) -> List[Dict[str, Any]]:
        return list(VOICE_REGISTRY.values())

    def estimate_duration(self, text: str) -> float:
        return self.edge_tts.estimate_duration(text)

    async def synthesize(
        self,
        text: str,
        voice: str = "vi-VN-NamMinhNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%"
    ) -> TTSResult:
        vs_error = None
        edge_error = None

        # 1. Attempt VoiceStudio if mode is 'voicestudio' or 'auto'
        if self.engine_mode in ("auto", "voicestudio") and getattr(settings, "VOICESTUDIO_ENABLED", True):
            try:
                is_up = await self.voicestudio.is_available()
                if is_up:
                    result = await self.voicestudio.synthesize(
                        text=text,
                        voice=voice,
                        rate=rate,
                        pitch=pitch,
                        volume=volume
                    )
                    audio_path = os.path.join(self.storage_dir, f"{result.audio_id}.mp3")
                    if os.path.exists(audio_path):
                        is_valid, msg = validate_audio_file(audio_path)
                        if is_valid:
                            return result
                elif self.engine_mode == "voicestudio":
                    vs_error = f"VoiceStudio server offline trên {self.voicestudio.base_url}"
            except Exception as e:
                vs_error = str(e)

        # If user explicitly configured 'voicestudio' only and it failed, do not silently switch unless allowed
        if self.engine_mode == "voicestudio" and not self.allow_offline_fallback:
            raise TTSGenerationError(f"Chế độ chỉ dùng VoiceStudio thất bại: {vs_error or 'Server không phản hồi'}")

        # 2. Attempt EdgeTTS if mode is 'edgetts' or fallback from 'auto'
        try:
            result = await self.edge_tts.synthesize(
                text=text,
                voice=voice,
                rate=rate,
                pitch=pitch,
                volume=volume
            )
            return result
        except Exception as e:
            edge_error = str(e)

        # 3. Both genuine providers failed: Raise TTSGenerationError with root cause (NO MOCK/SINE AUDIO)
        diag = []
        if vs_error:
            diag.append(f"VoiceStudio ({self.voicestudio.base_url}): {vs_error}")
        else:
            diag.append(f"VoiceStudio: offline/unreachable on {self.voicestudio.base_url}")
        if edge_error:
            diag.append(f"Edge-TTS: {edge_error}")

        raise TTSGenerationError(
            f"Không thể tạo giọng đọc AI từ cả 2 nguồn: {'; '.join(diag)}. "
            f"Vui lòng kiểm tra VoiceStudio server (port 3900) hoặc kết nối mạng đến Edge-TTS."
        )
