import React, { useState, useEffect, useRef } from 'react';
import type { SceneManifest } from '../../types/database';
import { apiClient } from '../../services/apiClient';
import { X, Download, CheckCircle2, Film, FileText, Sparkles, Loader2, AlertTriangle, StopCircle } from 'lucide-react';

interface RenderModalProps {
  manifest: SceneManifest;
  isOpen: boolean;
  onClose: () => void;
  autoStart?: boolean;
  initialJobId?: string | null;
}

const STORAGE_ACTIVE_JOB_KEY = 'ytber_active_render_job_id';

export const RenderModal: React.FC<RenderModalProps> = ({
  manifest,
  isOpen,
  onClose,
  autoStart = false,
  initialJobId = null
}) => {
  const [isRendering, setIsRendering] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const [jobStatus, setJobStatus] = useState<string>('idle');
  const [currentStage, setCurrentStage] = useState<string>('Sẵn sàng kết xuất video');
  const [progressPercent, setProgressPercent] = useState<number>(0);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [videoMetadata, setVideoMetadata] = useState<{ duration?: number; size?: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);

  const pollIntervalRef = useRef<any>(null);
  const consecutiveErrorsRef = useRef<number>(0);

  const cleanupPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  const startPolling = (targetJobId: string) => {
    cleanupPolling();
    setIsRendering(true);
    setIsCancelling(false);
    setJobId(targetJobId);
    consecutiveErrorsRef.current = 0;
    try {
      localStorage.setItem(STORAGE_ACTIVE_JOB_KEY, targetJobId);
    } catch {
      // localStorage may fail in private mode
    }

    pollIntervalRef.current = setInterval(async () => {
      try {
        const status = await apiClient.getRenderStatus(targetJobId);
        consecutiveErrorsRef.current = 0;

        setJobStatus(status.status);
        setProgressPercent(status.progress_percent || 0);
        setCurrentStage(status.stage_text || 'Đang xử lý...');

        if (status.status === 'completed') {
          cleanupPolling();
          try {
            localStorage.removeItem(STORAGE_ACTIVE_JOB_KEY);
          } catch {}
          setIsRendering(false);
          setIsCancelling(false);
          const downloadUri = await apiClient.getRenderDownloadUrl(targetJobId);
          setDownloadUrl(downloadUri);
          setVideoUrl(downloadUri);
          setVideoMetadata({
            duration: status.duration_seconds,
            size: status.file_size_bytes,
          });
        } else if (status.status === 'failed') {
          cleanupPolling();
          try {
            localStorage.removeItem(STORAGE_ACTIVE_JOB_KEY);
          } catch {}
          setIsRendering(false);
          setIsCancelling(false);
          setError(status.error_message || 'Quá trình kết xuất video thất bại');
        } else if (status.status === 'cancelled') {
          cleanupPolling();
          try {
            localStorage.removeItem(STORAGE_ACTIVE_JOB_KEY);
          } catch {}
          setIsRendering(false);
          setIsCancelling(false);
          setCurrentStage('Tiến trình kết xuất đã được hủy an toàn.');
        }
      } catch (err: any) {
        consecutiveErrorsRef.current += 1;
        console.warn(`Error polling render status (${consecutiveErrorsRef.current}/5):`, err);
        if (consecutiveErrorsRef.current >= 5) {
          cleanupPolling();
          setIsRendering(false);
          setIsCancelling(false);
          setError('Mất kết nối với máy chủ quản lý render sau nhiều lần thử lại. Vui lòng kiểm tra mạng hoặc trạng thái máy chủ.');
        }
      }
    }, 1200);
  };

  useEffect(() => {
    if (isOpen) {
      const persistedJobId = localStorage.getItem(STORAGE_ACTIVE_JOB_KEY);
      const effectiveJobId = initialJobId || persistedJobId;

      if (effectiveJobId && !videoUrl) {
        startPolling(effectiveJobId);
      } else if (autoStart && !isRendering && !videoUrl) {
        handleStartHyperFramesRender();
      }
    } else {
      cleanupPolling();
      setIsRendering(false);
      setIsCancelling(false);
      setProgressPercent(0);
      setError(null);
    }

    return () => {
      cleanupPolling();
    };
  }, [isOpen, autoStart, initialJobId]);

  const handleStartHyperFramesRender = async () => {
    setError(null);
    setIsRendering(true);
    setIsCancelling(false);
    setProgressPercent(2);
    setJobStatus('preparing');
    setCurrentStage('Đang khởi tạo kiến trúc đồ họa chuyển động HyperFrames...');

    try {
      const startRes = await apiClient.startRender(manifest);
      setJobId(startRes.job_id);
      setCurrentStage(startRes.stage_text || 'Đang kết xuất video...');
      startPolling(startRes.job_id);
    } catch (err: any) {
      setIsRendering(false);
      setError(err?.message || 'Không thể bắt đầu kết xuất video');
    }
  };

  const handleCancel = async () => {
    if (!jobId) {
      cleanupPolling();
      setIsRendering(false);
      setProgressPercent(0);
      setCurrentStage('Đã hủy kết xuất');
      return;
    }

    setIsCancelling(true);
    setCurrentStage('Đang gửi lệnh dừng khẩn cấp tới HyperFrames Worker...');

    try {
      await apiClient.cancelRender(jobId);
      setCurrentStage('Đang dừng các tiến trình render...');
    } catch (err: any) {
      console.warn('Lỗi khi gửi yêu cầu hủy render:', err);
      // Even if cancel API errors, clean up locally
      cleanupPolling();
      try {
        localStorage.removeItem(STORAGE_ACTIVE_JOB_KEY);
      } catch {}
      setIsRendering(false);
      setIsCancelling(false);
      setError(err?.message || 'Không thể gửi yêu cầu hủy render');
    }
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
    content += `Video được xây dựng bằng kiến trúc Code-First Motion Graphics (HyperFrames + GSAP):\n\n`;
    manifest.scenes.forEach((scene, sIdx) => {
      content += `Cảnh ${sIdx + 1}: ${scene.narration_text}\n`;
      content += `  Thời lượng: ${scene.duration_seconds}s\n`;
      content += `  Hiệu ứng: ${scene.visual_method || 'Đồ họa chuyển động vector'}\n\n`;
    });
    content += `Giọng đọc: Neural TTS (${manifest.voice_config?.voice || 'vi-VN-NamMinhNeural'})\n`;
    content += `Sản xuất tự động bởi YTBER Unified AI Video Studio.\n`;

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    downloadFile(blob, `${manifest.title || 'video'}-credits.txt`);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="bg-studio-surface border border-studio-border rounded-2xl max-w-xl w-full p-6 shadow-2xl relative flex flex-col gap-5">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-studio-border pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-studio-primary flex items-center justify-center text-white shadow-md">
              <Film className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                Kết Xuất Video MP4
                <span className="text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full font-mono uppercase tracking-wider">
                  Durable HyperFrames Queue
                </span>
              </h3>
              <p className="text-xs text-gray-400">
                {manifest.aspect_ratio === '16:9' ? '1920×1080 (16:9 Long-form)' : '1080×1920 (9:16 Shorts)'} • 30 FPS • H.264 & AAC 48kHz
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              if (isRendering && !isCancelling) {
                if (window.confirm('Tiến trình kết xuất đang chạy ngầm. Bạn có muốn đóng cửa sổ theo dõi? Tiến trình vẫn sẽ tiếp tục kết xuất trên máy chủ.')) {
                  onClose();
                }
              } else {
                onClose();
              }
            }}
            className="text-gray-400 hover:text-white transition p-1"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Initial state (Ready to render) */}
        {!isRendering && !videoUrl && (
          <div className="flex flex-col gap-4">
            <div className="bg-studio-card p-4 rounded-xl border border-studio-border text-xs space-y-2.5">
              <div className="flex justify-between text-gray-300">
                <span>Độ phân giải & Tỷ lệ:</span>
                <span className="font-mono text-white font-semibold">{manifest.video_specs.width} × {manifest.video_specs.height} ({manifest.aspect_ratio || '9:16'})</span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Khung hình & Chuẩn nén:</span>
                <span className="font-mono text-white font-semibold">30 FPS (H.264 High Profile avc1)</span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Tổng thời lượng & Cảnh:</span>
                <span className="font-mono text-white font-semibold">~{Math.round(manifest.total_duration_sec)} giây ({manifest.scenes.length} cảnh hoạt hình)</span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Âm thanh & Lồng tiếng:</span>
                <span className="font-mono text-emerald-300 font-semibold">Stereo 48kHz AAC (Thuyết minh + BGM + SFX)</span>
              </div>
            </div>

            <button
              onClick={handleStartHyperFramesRender}
              className="w-full py-3.5 bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-extrabold rounded-xl shadow-lg flex items-center justify-center gap-2 transition hover:scale-[1.01] border border-emerald-400/40 text-sm"
            >
              <Sparkles className="w-4 h-4 text-amber-300 animate-pulse" />
              Bắt Đầu Kết Xuất MP4 (Durable Worker Pipeline)
            </button>
          </div>
        )}

        {/* Rendering progress state */}
        {isRendering && (
          <div className="flex flex-col gap-4 py-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-300 font-medium flex items-center gap-2">
                <Loader2 className="w-3.5 h-3.5 text-studio-primary animate-spin" />
                {currentStage}
              </span>
              <span className="font-mono font-bold text-studio-accent text-base">{progressPercent}%</span>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-studio-card h-3 rounded-full overflow-hidden border border-studio-border">
              <div
                className={`h-full transition-all duration-300 ease-out ${
                  isCancelling
                    ? 'bg-amber-500 animate-pulse'
                    : 'bg-gradient-to-r from-emerald-500 via-studio-primary to-amber-400'
                }`}
                style={{ width: `${progressPercent}%` }}
              />
            </div>

            {/* Render stats */}
            <div className="grid grid-cols-3 gap-2 text-center text-xs bg-studio-card/60 p-3 rounded-xl border border-studio-border">
              <div>
                <p className="text-gray-400">Mã Render Job</p>
                <p className="font-mono font-semibold text-emerald-400 mt-0.5">{jobId ? jobId.slice(0, 8) : 'Pending'}</p>
              </div>
              <div>
                <p className="text-gray-400">Trạng thái Hàng đợi</p>
                <p className="font-mono font-semibold text-studio-highlight mt-0.5 uppercase tracking-wide">
                  {jobStatus}
                </p>
              </div>
              <div>
                <p className="text-gray-400">Định dạng & Âm thanh</p>
                <p className="font-mono font-semibold text-white mt-0.5">MP4 • 48kHz AAC</p>
              </div>
            </div>

            <button
              onClick={handleCancel}
              disabled={isCancelling}
              className="py-2.5 px-4 bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 rounded-xl text-xs font-semibold transition flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isCancelling ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-red-300" />
                  Đang hủy tiến trình trên máy chủ...
                </>
              ) : (
                <>
                  <StopCircle className="w-3.5 h-3.5 text-red-400" />
                  Hủy Tiến Trình Kết Xuất
                </>
              )}
            </button>
          </div>
        )}

        {/* Completed state */}
        {videoUrl && (
          <div className="flex flex-col gap-4 animate-fade-in">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center gap-3 text-emerald-300 text-xs">
              <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-emerald-400" />
              <div>
                <p className="font-bold text-sm">Kết xuất video thành công 100%!</p>
                <p className="text-gray-300 mt-0.5">
                  Thời lượng: {videoMetadata?.duration ? `${videoMetadata.duration.toFixed(1)}s` : `~${Math.round(manifest.total_duration_sec)}s`} • Dung lượng: {videoMetadata?.size ? `${(videoMetadata.size / (1024 * 1024)).toFixed(2)} MB` : 'Chuẩn'}
                </p>
              </div>
            </div>

            {/* Video preview */}
            <div className="max-h-72 overflow-hidden rounded-xl border border-studio-border flex justify-center bg-black shadow-inner">
              <video src={videoUrl} controls autoPlay className="h-72 max-w-full object-contain" />
            </div>

            {/* Action buttons */}
            <div className="grid grid-cols-3 gap-2">
              <a
                href={downloadUrl || videoUrl}
                download={`${manifest.title || 'video'}.mp4`}
                className="py-2.5 px-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold rounded-xl shadow flex items-center justify-center gap-1.5 transition text-center"
              >
                <Download className="w-3.5 h-3.5" />
                Tải MP4
              </a>

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
                setVideoUrl(null);
                setDownloadUrl(null);
                setJobStatus('idle');
              }}
              className="text-xs text-center text-gray-400 hover:text-white transition py-1"
            >
              Kết xuất lại phiên bản mới
            </button>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-300 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
};