import re
from typing import List

class TextChunk:
    def __init__(self, index: int, text: str, char_length: int, word_count: int):
        self.index = index
        self.text = text
        self.char_length = char_length
        self.word_count = word_count

    def to_dict(self):
        return {
            "index": self.index,
            "text": self.text,
            "char_length": self.char_length,
            "word_count": self.word_count
        }

class VietnameseTextChunker:
    """
    Production-grade text chunker for Vietnamese Text-to-Speech synthesis.
    Features:
    - Hierarchical splitting: Paragraphs -> Sentences -> Clauses -> Words
    - Never breaks words in the middle
    - Preserves Vietnamese Unicode diacritics, punctuation, numbers, and symbols
    - Configurable maximum chunk length (default: 250 characters)
    - Zero content loss: word set preservation
    - Rejects empty chunks
    """

    def __init__(self, max_chars: int = 250, min_chars: int = 20):
        self.max_chars = max(50, max_chars)
        self.min_chars = max(5, min_chars)

    def chunk_text(self, text: str) -> List[TextChunk]:
        clean_text = text.strip()
        if not clean_text:
            return []

        # 1. Break into paragraphs
        raw_paragraphs = [p.strip() for p in re.split(r'\n+', clean_text) if p.strip()]
        if not raw_paragraphs:
            return []

        all_sentences: List[str] = []
        for para in raw_paragraphs:
            # Split by primary sentence-ending punctuation while preserving the punctuation
            # Matches . ! ? ; or newline
            sentences = re.split(r'(?<=[.!?;\n])\s+', para)
            for s in sentences:
                s_clean = s.strip()
                if s_clean:
                    all_sentences.append(s_clean)

        # 2. Break any sentence that exceeds max_chars by secondary punctuation or word boundaries
        atomic_units: List[str] = []
        for s in all_sentences:
            if len(s) <= self.max_chars:
                atomic_units.append(s)
            else:
                # Sub-split by secondary punctuation: comma, colon, dash, quotes
                clauses = re.split(r'(?<=[,:\-–—\(\)])\s+', s)
                for cl in clauses:
                    cl_clean = cl.strip()
                    if not cl_clean:
                        continue
                    if len(cl_clean) <= self.max_chars:
                        atomic_units.append(cl_clean)
                    else:
                        # Split by words
                        words = cl_clean.split()
                        cur_segment = []
                        cur_len = 0
                        for w in words:
                            w_len = len(w) + (1 if cur_segment else 0)
                            if cur_len + w_len > self.max_chars and cur_segment:
                                atomic_units.append(" ".join(cur_segment))
                                cur_segment = [w]
                                cur_len = len(w)
                            else:
                                cur_segment.append(w)
                                cur_len += w_len
                        if cur_segment:
                            atomic_units.append(" ".join(cur_segment))

        # 3. Greedy packing of atomic units into chunks up to max_chars
        chunks: List[TextChunk] = []
        current_chunk_words: List[str] = []
        current_chunk_str = ""

        for unit in atomic_units:
            if not current_chunk_str:
                current_chunk_str = unit
            else:
                combined = current_chunk_str + " " + unit
                if len(combined) <= self.max_chars:
                    current_chunk_str = combined
                else:
                    chunks.append(TextChunk(
                        index=len(chunks),
                        text=current_chunk_str,
                        char_length=len(current_chunk_str),
                        word_count=len(current_chunk_str.split())
                    ))
                    current_chunk_str = unit

        if current_chunk_str:
            chunks.append(TextChunk(
                index=len(chunks),
                text=current_chunk_str,
                char_length=len(current_chunk_str),
                word_count=len(current_chunk_str.split())
            ))

        return chunks
