import React, { useState, useEffect, useRef } from 'react';
import type { SceneManifest } from '../../types/database';
import { WebCodecsRenderer, type RenderProgressEvent, type RenderResult } from '../../services/webcodecsRenderer';
import { checkWebCodecsSupport, type WebCodecsSupportResult } from '../../services/webcodecs';
import { X, Play, Download, AlertTriangle, CheckCircle2, Film, FileText } from 'lucide-react';

interface RenderModalProps {
  manifest: SceneManifest;
  isOpen: boolean;
  onClose: () => void;
}

export const RenderModal: React.FC<RenderModalProps> = ({ manifest, isOpen, onClose }) => {
  const [support, setSupport] = useState<WebCodecsSupportResult | null>(null);
  const [isRendering, setIsRendering] = useState(false);
  const [progress, setProgress] = useState<RenderProgressEvent | null>(null);
  const [result, setResult] = useState<RenderResult | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const rendererRef = useRef<WebCodecsRenderer | null>(null);

  useEffect(() => {
    if (isOpen) {
      checkWebCodecsSupport().then((res) => {
        setSupport(res);
      });
    } else {
      // Cleanup preview url when closed
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
        setVideoUrl(null);
      }
      setResult(null);
      setProgress(null);
      setIsRendering(false);
      setError(null);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleStartRender = async () => {
    setError(null);
    setIsRendering(true);
    setProgress({
      percent: 0,
      currentFrame: 0,
      totalFrames: Math.round(manifest.total_duration_sec * (manifest.video_specs.fps || 30)),
      effectiveFps: 0,
      estimatedRemainingSec: 0,
      statusText: 'Đang khởi tạo mã hóa phần cứng WebCodecs...',
    });

    const renderer = new WebCodecsRenderer();
    rendererRef.current = renderer;

    try {
      const renderRes = await renderer.renderVideo(manifest, (p) => {
        setProgress(p);
      });

      setResult(renderRes);
      const url = URL.createObjectURL(renderRes.blob);
      setVideoUrl(url);
    } catch (err: any) {
      if (err?.message !== 'Video rendering was cancelled') {
        setError(err?.message || 'Có lỗi xảy ra trong quá trình kết xuất video');
      }
    } finally {
      setIsRendering(false);
      rendererRef.current = null;
    }
  };

  const handleCancel = () => {
    if (rendererRef.current) {
      rendererRef.current.cancel();
    }
    setIsRendering(false);
    setProgress(null);
  };

  const downloadFile = (blob: Blob, filename: string) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleDownloadSRT = () => {
    let srtContent = '';
    let counter = 1;
    let accumulatedMs = 0;

    const formatSRTTime = (ms: number) => {
      const totalSec = Math.floor(ms / 1000);
      const hours = Math.floor(totalSec / 3600);
      const mins = Math.floor((totalSec % 3600) / 60);
      const secs = totalSec % 60;
      const millis = Math.floor(ms % 1000);
      return `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')},${String(millis).padStart(3, '0')}`;
    };

    manifest.scenes.forEach((scene) => {
      const sceneStartMs = accumulatedMs;
      const sceneEndMs = sceneStartMs + Math.round(scene.duration_seconds * 1000);

      srtContent += `${counter}\n`;
      srtContent += `${formatSRTTime(sceneStartMs)} --> ${formatSRTTime(sceneEndMs)}\n`;
      srtContent += `${scene.narration_text.trim()}\n\n`;
      counter++;
      accumulatedMs = sceneEndMs;
    });

    const blob = new Blob([srtContent], { type: 'text/plain;charset=utf-8' });
    downloadFile(blob, `${manifest.title || 'video'}-subtitles.srt`);
  };

  const handleDownloadCredits = () => {
    let content = `=== BẢN QUYỀN VÀ NGUỒN TƯ LIỆU (${manifest.title || 'Video'}) ===\n`;
    content += `Video này sử dụng các tư liệu hình ảnh và âm thanh tuân thủ giấy phép Creative Commons và Miền công cộng:\n\n`;

    manifest.scenes.forEach((scene, sIdx) => {
      const asset = scene.assets?.[0];
      if (asset) {
        content += `Cảnh ${sIdx + 1}: ${asset.attribution_text || asset.source_url}\n`;
        if (asset.license_type) content += `  Giấy phép: ${asset.license_type}\n`;
        if (asset.source_url) content += `  Nguồn: ${asset.source_url}\n\n`;
      }
    });

    content += `Giọng đọc: Microsoft Edge Neural TTS (${manifest.voice_config?.voice || 'vi-VN-NamMinhNeural'})\n`;
    content += `Sản xuất tự động bởi YTBER Studio.\n`;

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    downloadFile(blob, `${manifest.title || 'video'}-credits.txt`);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-studio-surface border border-studio-border rounded-2xl max-w-xl w-full p-6 shadow-2xl relative flex flex-col gap-5">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-studio-border pb-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-studio-primary/20 flex items-center justify-center text-studio-primary">
              <Film className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Kết Xuất Video Trực Tiếp (In-Browser)</h3>
              <p className="text-xs text-gray-400">WebCodecs Hardware Acceleration • 1080×1920 • 30 FPS</p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isRendering}
            className="text-gray-400 hover:text-white transition p-1 disabled:opacity-40"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Browser compatibility check */}
        {support && !support.supported && (
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex gap-3 text-amber-200 text-xs">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 text-amber-400" />
            <div className="flex flex-col gap-1">
              <p className="font-semibold text-amber-300">Trình duyệt không hỗ trợ đầy đủ WebCodecs</p>
              <ul className="list-disc list-inside space-y-0.5">
                {support.issues.map((issue, idx) => (
                  <li key={idx}>{issue}</li>
                ))}
              </ul>
              <p className="text-gray-300 mt-1">
                Vui lòng sử dụng <strong>Google Chrome, Microsoft Edge hoặc Brave</strong> trên máy tính để kết xuất video trực tiếp mượt mà nhất.
              </p>
            </div>
          </div>
        )}

        {/* Initial state (Ready to render) */}
        {!isRendering && !result && (
          <div className="flex flex-col gap-4">
            <div className="bg-studio-card p-4 rounded-xl border border-studio-border text-sm space-y-2">
              <div className="flex justify-between text-gray-300">
                <span>Độ phân giải:</span>
                <span className="font-mono text-white">{manifest.video_specs.width} × {manifest.video_specs.height} ({manifest.aspect_ratio || '9:16'})</span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Tốc độ khung hình:</span>
                <span className="font-mono text-white">30 FPS (H.264 Main L4.2)</span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Tổng thời lượng:</span>
                <span className="font-mono text-white">~{Math.round(manifest.total_duration_sec)} giây ({manifest.scenes.length} cảnh)</span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Âm thanh:</span>
                <span className="font-mono text-white">Stereo 48kHz AAC (Dynamic Ducking -3.5dB)</span>
              </div>
            </div>

            <button
              onClick={handleStartRender}
              disabled={support ? !support.supported : true}
              className="w-full py-3.5 bg-gradient-to-r from-studio-primary to-indigo-600 hover:from-indigo-500 hover:to-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold rounded-xl shadow-lg flex items-center justify-center gap-2 transition hover:scale-[1.01]"
            >
              <Play className="w-5 h-5 fill-current" />
              Bắt Đầu Kết Xuất Video (Không Tốn Server)
            </button>
          </div>
        )}

        {/* Rendering progress state */}
        {isRendering && progress && (
          <div className="flex flex-col gap-4 py-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-300 font-medium">{progress.statusText}</span>
              <span className="font-mono font-bold text-studio-accent text-lg">{progress.percent}%</span>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-studio-card h-3 rounded-full overflow-hidden border border-studio-border">
              <div
                className="bg-gradient-to-r from-studio-primary via-indigo-400 to-studio-accent h-full transition-all duration-150 ease-out"
                style={{ width: `${progress.percent}%` }}
              />
            </div>

            {/* Render stats */}
            <div className="grid grid-cols-3 gap-2 text-center text-xs bg-studio-card/60 p-3 rounded-xl border border-studio-border">
              <div>
                <p className="text-gray-400">Khung hình</p>
                <p className="font-mono font-semibold text-white mt-0.5">{progress.currentFrame} / {progress.totalFrames}</p>
              </div>
              <div>
                <p className="text-gray-400">Tốc độ kết xuất</p>
                <p className="font-mono font-semibold text-studio-highlight mt-0.5">{progress.effectiveFps} FPS</p>
              </div>
              <div>
                <p className="text-gray-400">Thời gian còn lại</p>
                <p className="font-mono font-semibold text-white mt-0.5">~{progress.estimatedRemainingSec}s</p>
              </div>
            </div>

            <button
              onClick={handleCancel}
              className="py-2.5 px-4 bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/30 rounded-xl text-sm font-semibold transition"
            >
              Hủy Kết Xuất
            </button>
          </div>
        )}

        {/* Completed state */}
        {result && videoUrl && (
          <div className="flex flex-col gap-4 animate-fade-in">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center gap-3 text-emerald-300 text-sm">
              <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-emerald-400" />
              <div>
                <p className="font-semibold">Kết xuất hoàn tất thành công!</p>
                <p className="text-xs text-emerald-400/80">
                  Thời lượng: {result.durationSec.toFixed(1)}s • Tốc độ: {result.effectiveFps} FPS • Dung lượng: {(result.fileSizeBytes / (1024 * 1024)).toFixed(1)} MB
                </p>
              </div>
            </div>

            {/* Video preview preview */}
            <div className="max-h-60 overflow-hidden rounded-xl border border-studio-border flex justify-center bg-black">
              <video src={videoUrl} controls className="h-60 max-w-full object-contain" />
            </div>

            {/* Action buttons */}
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => downloadFile(result.blob, `${manifest.title || 'video'}.mp4`)}
                className="py-2.5 px-3 bg-studio-primary hover:bg-indigo-600 text-white text-xs font-bold rounded-xl shadow flex items-center justify-center gap-1.5 transition"
              >
                <Download className="w-3.5 h-3.5" />
                Tải MP4
              </button>

              <button
                onClick={handleDownloadSRT}
                className="py-2.5 px-3 bg-studio-card hover:bg-studio-border text-gray-200 border border-studio-border text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 transition"
              >
                <FileText className="w-3.5 h-3.5" />
                Phụ Đề (.SRT)
              </button>

              <button
                onClick={handleDownloadCredits}
                className="py-2.5 px-3 bg-studio-card hover:bg-studio-border text-gray-200 border border-studio-border text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 transition"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-studio-accent" />
                Nguồn (.TXT)
              </button>
            </div>

            <button
              onClick={() => {
                setResult(null);
                setVideoUrl(null);
              }}
              className="text-xs text-center text-gray-400 hover:text-white transition py-1"
            >
              Kết xuất lại phiên bản mới
            </button>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-300 text-xs">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};
