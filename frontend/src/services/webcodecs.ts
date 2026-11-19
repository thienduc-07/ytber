export interface WebCodecsSupportResult {
  supported: boolean;
  videoEncoder: boolean;
  audioEncoder: boolean;
  h264Level42: boolean;
  aacAudio: boolean;
  issues: string[];
}

export async function checkWebCodecsSupport(): Promise<WebCodecsSupportResult> {
  const result: WebCodecsSupportResult = {
    supported: false,
    videoEncoder: typeof window !== 'undefined' && typeof (window as any).VideoEncoder !== 'undefined',
    audioEncoder: typeof window !== 'undefined' && typeof (window as any).AudioEncoder !== 'undefined',
    h264Level42: false,
    aacAudio: false,
    issues: []
  };

  if (!result.videoEncoder) {
    result.issues.push('Trình duyệt không hỗ trợ WebCodecs VideoEncoder.');
  }

  if (!result.audioEncoder) {
    result.issues.push('Trình duyệt không hỗ trợ WebCodecs AudioEncoder (cần Safari 26+ hoặc Chrome 94+).');
  }

  // Check H.264 Level 4.2 support (1080x1920 @ 30 FPS)
  if (result.videoEncoder) {
    try {
      const vSupport = await (window as any).VideoEncoder.isConfigSupported({
        codec: 'avc1.4d002a', // H.264 Main Profile Level 4.2
        width: 1080,
        height: 1920,
        bitrate: 7_500_000,
        framerate: 30,
        hardwareAcceleration: 'prefer-hardware'
      });
      result.h264Level42 = !!vSupport.supported;
      if (!result.h264Level42) {
        result.issues.push('Phần cứng không hỗ trợ mã hóa video H.264 độ phân giải 1080x1920.');
      }
    } catch (e: any) {
      result.issues.push(`Lỗi kiểm tra VideoEncoder: ${e.message}`);
    }
  }

  // Check AAC Audio support (48kHz Stereo)
  if (result.audioEncoder) {
    try {
      const aSupport = await (window as any).AudioEncoder.isConfigSupported({
        codec: 'mp4a.40.2',
        sampleRate: 48000,
        numberOfChannels: 2,
        bitrate: 192000
      });
      result.aacAudio = !!aSupport.supported;
      if (!result.aacAudio) {
        result.issues.push('Không hỗ trợ mã hóa âm thanh AAC stereo 48kHz.');
      }
    } catch (e: any) {
      result.issues.push(`Lỗi kiểm tra AudioEncoder: ${e.message}`);
    }
  }

  result.supported = result.videoEncoder && result.audioEncoder && result.h264Level42 && result.aacAudio;
  return result;
}
