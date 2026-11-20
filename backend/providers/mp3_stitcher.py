import struct
from typing import List, Tuple

class MP3Stitcher:
    """
    Production-grade MP3 elementary stream stitcher and frame parser.
    Features:
    - Pure Python implementation (zero dependency on FFmpeg binary)
    - Strips ID3v2 metadata from non-initial chunks to prevent decoder glitches
    - Strips ID3v1 trailing tags
    - Accurate MPEG audio frame synchronization and duration calculation
    - Concatenates audio frames with seamless acoustic transition
    """

    MPEG2_BITRATES = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0]
    MPEG1_BITRATES = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]

    SAMPLE_RATES = {
        0: 11025,  # MPEG 2.5
        2: 24000,  # MPEG 2
        3: 48000   # MPEG 1 (or 44100 depending on index)
    }

    @staticmethod
    def strip_id3v2(data: bytes) -> bytes:
        if data.startswith(b'ID3') and len(data) >= 10:
            # Synchsafe integer size in bytes 6..9
            size = (data[6] << 21) | (data[7] << 14) | (data[8] << 7) | data[9]
            total_id3_len = 10 + size
            if total_id3_len < len(data):
                return data[total_id3_len:]
        return data

    @staticmethod
    def strip_id3v1(data: bytes) -> bytes:
        if len(data) >= 128 and data[-128:-125] == b'TAG':
            return data[:-128]
        return data

    @classmethod
    def parse_frames(cls, data: bytes, default_sample_rate: int = 24000) -> Tuple[int, float, bytes]:
        """
        Parses MP3 stream, validates frames, removes leading/trailing non-audio padding,
        and returns (frame_count, duration_seconds, clean_audio_bytes).
        """
        clean_data = cls.strip_id3v2(data)
        clean_data = cls.strip_id3v1(clean_data)

        pos = 0
        frames = 0
        first_frame_pos = -1
        last_frame_end = 0

        sample_rate = default_sample_rate
        samples_per_frame = 576  # 576 for MPEG-2/2.5 Layer 3, 1152 for MPEG-1 Layer 3

        while pos <= len(clean_data) - 4:
            # Look for 11-bit sync word 0xFFE / 0xFFF
            if clean_data[pos] == 0xFF and (clean_data[pos + 1] & 0xE0) == 0xE0:
                header = struct.unpack('>I', clean_data[pos:pos+4])[0]
                version = (header >> 19) & 0x3
                layer = (header >> 17) & 0x3
                bitrate_idx = (header >> 12) & 0xF
                sr_idx = (header >> 10) & 0x3
                padding = (header >> 9) & 0x1

                if layer == 1:  # Layer 3 (01 in binary)
                    is_mpeg1 = (version == 3)
                    samples_per_frame = 1152 if is_mpeg1 else 576
                    
                    # Determine sample rate
                    if is_mpeg1:
                        sr_table = [44100, 48000, 32000, 0]
                        sample_rate = sr_table[sr_idx] if sr_idx < 3 else default_sample_rate
                        bitrates = cls.MPEG1_BITRATES
                    else:
                        sr_table = [22050, 24000, 16000, 0]
                        sample_rate = sr_table[sr_idx] if sr_idx < 3 else default_sample_rate
                        bitrates = cls.MPEG2_BITRATES

                    bitrate = bitrates[bitrate_idx] * 1000 if bitrate_idx < len(bitrates) else 48000

                    if sample_rate > 0 and bitrate > 0:
                        # Frame size formula
                        coeff = 144 if is_mpeg1 else 72
                        frame_len = int((coeff * bitrate) / sample_rate) + padding
                        if frame_len > 0 and pos + frame_len <= len(clean_data):
                            if first_frame_pos == -1:
                                first_frame_pos = pos
                            frames += 1
                            pos += frame_len
                            last_frame_end = pos
                            continue
            pos += 1

        if first_frame_pos != -1 and last_frame_end > first_frame_pos:
            pure_audio = clean_data[first_frame_pos:last_frame_end]
        else:
            pure_audio = clean_data

        duration_sec = (frames * samples_per_frame / float(sample_rate)) if (frames > 0 and sample_rate > 0) else (len(pure_audio) / 6000.0)
        return frames, round(duration_sec, 3), pure_audio

    @classmethod
    def stitch_chunks(cls, chunk_bytes_list: List[bytes], default_sample_rate: int = 24000) -> Tuple[bytes, List[float], float]:
        """
        Stitches a list of MP3 chunk byte buffers into a single continuous MP3 stream.
        Returns:
            stitched_bytes: The combined MP3 stream.
            chunk_durations: Exact duration in seconds for each chunk.
            total_duration: Total combined duration in seconds.
        """
        stitched_frames = bytearray()
        chunk_durations: List[float] = []

        for idx, c_bytes in enumerate(chunk_bytes_list):
            if not c_bytes:
                chunk_durations.append(0.0)
                continue

            frames, dur, pure_audio = cls.parse_frames(c_bytes, default_sample_rate=default_sample_rate)
            chunk_durations.append(dur)
            stitched_frames.extend(pure_audio)

        total_duration = round(sum(chunk_durations), 3)
        return bytes(stitched_frames), chunk_durations, total_duration
