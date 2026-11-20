# PHASE 2 — VIETNAMESE TTS PERFORMANCE BENCHMARK REPORT
**Project:** YTBER — Unified AI Video Studio  
**Engine:** Microsoft Edge Neural TTS + Hierarchical Vietnamese Chunker + Pure-Python MP3 Frame Stitcher  
**Test Environment:** macOS Darwin (Apple M3, 8GB Unified Memory), Python 3.9.6  
**Date:** 2026-11-20  
**Status:** PASS (All 4 Tiers Verified & Validated)

---

## 1. Executive Summary

This benchmark rigorously evaluates the performance, throughput, stability, and audio validity of the upgraded **Production-Grade Vietnamese TTS Engine** across 4 script tiers:
- **Tier 1 (Short):** 100 words (~26 seconds audio) — YouTube Shorts / TikTok Reels
- **Tier 2 (Medium):** 500 words (~2.17 minutes audio) — Standard Explainer / News Recap
- **Tier 3 (Long):** 2,000 words (~8.68 minutes audio) — Documentary / Long Episode
- **Tier 4 (Extra Long):** 5,000 words (~21.70 minutes audio) — Audiobook / In-Depth Deep Dive

All tests were executed against the live Edge-TTS neural engine (`vi-VN-NamMinhNeural` voice) with bounded concurrency (`MAX_TTS_CONCURRENCY=2`), deterministic SHA-256 caching, frame-exact pure-Python MP3 stitching, and word-level karaoke boundary extraction.

---

## 2. Empirical Benchmark Matrix

| Metric | Tier 1: Short | Tier 2: Medium | Tier 3: Long | Tier 4: Extra Long |
| :--- | :---: | :---: | :---: | :---: |
| **Word Target** | 100 words | 500 words | 2,000 words | 5,000 words |
| **Actual Word Count** | 100 words | 500 words | 2,000 words | 5,000 words |
| **Character Count** | 439 chars | 2,219 chars | 8,882 chars | 22,223 chars |
| **Chunks Count (~250 chars/chunk)** | 3 chunks | 12 chunks | 46 chunks | 115 chunks |
| **Text Chunker Latency** | **0.067 ms** | **0.088 ms** | **0.303 ms** | **0.594 ms** |
| **Cold Synthesis Latency** | **18.54 s** | **40.28 s** | **38.55 s** | **87.05 s** |
| **Cached Retrieval Latency** | **1.21 ms** | **5.17 ms** | **9.09 ms** | **18.89 ms** |
| **Cache Speedup Factor** | **15,322x** | **7,791x** | **4,241x** | **4,608x** |
| **Audio Duration** | **26.09 s** | **130.39 s** (2m 10s) | **520.92 s** (8m 41s) | **1,302.22 s** (21m 42s) |
| **Real-Time Factor (RTF)** | **0.711** | **0.309** | **0.074** | **0.067** |
| **Throughput (Speech Gen Speed)** | 1.4x real-time | 3.2x real-time | 13.5x real-time | 15.0x real-time |
| **Words Detected & Timed** | 100 / 100 (100%) | 500 / 500 (100%) | 2,000 / 2,000 (100%) | 5,000 / 5,000 (100%) |
| **Timestamp Monotonicity** | **PASSED** (100%) | **PASSED** (100%) | **PASSED** (100%) | **PASSED** (100%) |
| **Audio File Size** | 152.86 KB | 764.02 KB | 3,052.27 KB (~2.98 MB) | 7,630.17 KB (~7.45 MB) |
| **Audio Format** | MP3 (MPEG-2 Layer III) | MP3 (MPEG-2 Layer III) | MP3 (MPEG-2 Layer III) | MP3 (MPEG-2 Layer III) |
| **Sample Rate** | 24,000 Hz | 24,000 Hz | 24,000 Hz | 24,000 Hz |
| **CoreAudio `afinfo` Validation** | **VALID (0 errors)** | **VALID (0 errors)** | **VALID (0 errors)** | **VALID (0 errors)** |

---

## 3. Analysis & Key Technical Insights

### 3.1 Real-Time Factor (RTF) Scaling
- **Short Tier (100 words):** Initial websocket handshake overhead dominates (~18s), yielding RTF of 0.711 (faster than real-time playback).
- **Medium Tier (500 words):** As chunk pipelining engages with bounded concurrency, RTF drops to 0.309.
- **Long & Extra Long Tiers (2,000 to 5,000 words):** Continuous pipelining achieves an exceptional **RTF of 0.067 - 0.074**. The system generates **21.7 minutes of full audio in only 87 seconds** (15x real-time speed).

### 3.2 Word-Level Karaoke Synchronization
- Across all 4 tiers, **100% of the words** were accurately captured with exact millisecond start and end boundaries.
- No words were dropped at chunk transitions.
- Timestamps are strictly monotonic ($start\_ms \le end\_ms$ and $word_{i}.start\_ms \le word_{i+1}.start\_ms$), ready for immediate WebCodecs subtitle animation.

### 3.3 Cache Efficiency & Latency Reduction
- Cold synthesis of 5,000 words requires 87 seconds.
- Re-requesting the identical or previously generated script returns in **18.89 milliseconds** from disk cache, representing a **4,600x speedup** and zero external network bandwidth consumption.

### 3.4 File Format & Audio Quality Verification
- Every generated output file was validated with macOS native `afinfo` (CoreAudio Architecture File Info).
- Verification confirmed:
  - 0 invalid frames or sync drops
  - Stripped non-initial ID3v2 metadata preventing audio pops/clicks
  - Consistent 24,000 Hz sampling rate and constant frame duration of 24 ms ($576 / 24,000$)
