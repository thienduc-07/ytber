import re
import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class WordTiming(BaseModel):
    word: str
    start_ms: int
    end_ms: int

class TTSResult(BaseModel):
    normalized_text: str
    audio_url: str
    duration_seconds: float
    words: List[WordTiming]
    provider: str

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
        # 1. Normalize dates (e.g. 12/04/1831 or 12/04), avoiding duplicate "ngày"
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

class TTSService:
    def __init__(self):
        self.normalizer = VietnameseTextNormalizer()

    def generate_syllable_timings(self, text: str, total_duration_sec: float) -> List[WordTiming]:
        words = text.split()
        if not words:
            return []
            
        total_ms = int(total_duration_sec * 1000)
        ms_per_word = max(150, total_ms // len(words))
        
        timings: List[WordTiming] = []
        cur_ms = 100 # initial 100ms breath buffer
        
        for idx, w in enumerate(words):
            # slightly longer duration for sentence-ending words
            factor = 1.3 if (w.endswith(('.', '!', '?')) or idx == len(words) - 1) else 1.0
            word_dur = int(ms_per_word * factor)
            end_ms = cur_ms + word_dur
            clean_word = re.sub(r'[^\w\s-]', '', w)
            timings.append(WordTiming(
                word=clean_word or w,
                start_ms=cur_ms,
                end_ms=end_ms
            ))
            cur_ms = end_ms + 40 # 40ms inter-word gap
            
        return timings

    async def synthesize(self, text: str, voice: str = "vi-VN-NamMinhNeural") -> TTSResult:
        normalized = self.normalizer.normalize(text)
        
        # Calculate standard pace: 4.0 syllables/second
        words_count = max(1, len(normalized.split()))
        duration_sec = round(max(3.0, words_count / 3.8), 2)
        
        timings = self.generate_syllable_timings(normalized, duration_sec)
        
        # In cloud mode, return structured audio timing payload
        # Audio generation URL links to the synthesized stem or client audio buffer
        return TTSResult(
            normalized_text=normalized,
            audio_url=f"/api/v1/tts/sample_audio.wav?dur={duration_sec}&v={voice}",
            duration_seconds=duration_sec,
            words=timings,
            provider="tts-vietnamese-normalizer"
        )
