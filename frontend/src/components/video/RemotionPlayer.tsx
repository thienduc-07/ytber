import React, { useRef, useState, useEffect } from 'react';
import type { SceneManifest } from '../../types/database';
import { AnimationEngine } from '../../services/animationEngine';
import { 
  Play, Pause, RotateCcw, Volume2, VolumeX, ChevronLeft, ChevronRight, SkipBack, SkipForward,
  Maximize2, Minimize2, Keyboard
} from 'lucide-react';

interface RemotionPlayerProps {
  manifest: SceneManifest;
  currentTimeSec: number;
  onTimeUpdate?: (timeSec: number) => void;
}

export const RemotionPlayer: React.FC<RemotionPlayerProps> = ({
  manifest,
  currentTimeSec,
  onTimeUpdate
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [localTime, setLocalTime] = useState(currentTimeSec);

  const totalDuration = manifest.scenes.reduce((acc, s) => acc + s.duration_seconds, 0) || 60;

  // Keyboard Shortcuts: Space to Play/Pause, ` to Toggle Fullscreen, Esc to Exit Fullscreen
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (
        target &&
        (target.tagName === 'INPUT' ||
          target.tagName === 'TEXTAREA' ||
          target.tagName === 'SELECT' ||
          target.isContentEditable)
      ) {
        return;
      }

      if (e.code === 'Space') {
        e.preventDefault();
        setIsPlaying((prev) => !prev);
      } else if (e.key === '`' || e.code === 'Backquote') {
        e.preventDefault();
        setIsFullscreen((prev) => !prev);
      } else if (e.key === 'Escape' && isFullscreen) {
        e.preventDefault();
        setIsFullscreen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen]);

  // Sync local time with external timeline playhead changes
  useEffect(() => {
    if (!isPlaying) {
      setLocalTime(currentTimeSec);
    }
  }, [currentTimeSec, isPlaying]);

  // DaVinci Timecode Formatter: HH:MM:SS:FF at 30 FPS
  const formatTimecode = (sec: number) => {
    const totalFrames = Math.floor(sec * 30);
    const frames = totalFrames % 30;
    const totalSeconds = Math.floor(sec);
    const s = totalSeconds % 60;
    const m = Math.floor(totalSeconds / 60) % 60;
    const h = Math.floor(totalSeconds / 3600);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}:${frames.toString().padStart(2, '0')}`;
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = manifest.video_specs?.width || 1080;
    const h = manifest.video_specs?.height || 1920;
    canvas.width = w;
    canvas.height = h;

    // Find active scene and local normalized progress
    let accumulatedTime = 0;
    let activeScene = manifest.scenes[0];
    let localT = 0;

    for (const scene of manifest.scenes) {
      if (localTime >= accumulatedTime && localTime <= accumulatedTime + scene.duration_seconds) {
        activeScene = scene;
        localT = (localTime - accumulatedTime) / Math.max(0.1, scene.duration_seconds);
        break;
      }
      accumulatedTime += scene.duration_seconds;
    }

    if (activeScene) {
      // 1. Render Rich Temporal Animation
      const isSpeaking = isPlaying && !!activeScene.narration_text;
      AnimationEngine.renderScene(
        ctx,
        w,
        h,
        activeScene,
        localT,
        localTime,
        manifest.character_registry,
        isSpeaking
      );

      // 2. Render Modern Clean Kinetic Subtitles (Lower third, NO bounding boxes around words)
      const text = activeScene.narration_text?.trim() || '';
      if (text) {
        const words = text.split(/\s+/).filter(Boolean);
        if (words.length > 0) {
          const cues = activeScene.subtitles_json || [];
          const localMs = Math.round(localT * activeScene.duration_seconds * 1000);
          let activeIdx = -1;
          if (cues.length > 0) {
            activeIdx = cues.findIndex((c: any) => localMs >= (c.start_ms || 0) && localMs <= (c.end_ms || 0));
            if (activeIdx === -1) {
              for (let i = cues.length - 1; i >= 0; i--) {
                if (localMs >= (cues[i].start_ms || 0)) {
                  activeIdx = i;
                  break;
                }
              }
            }
          }
          if (activeIdx === -1) {
            activeIdx = Math.min(words.length - 1, Math.floor(localT * words.length));
          }

          // Chunk words into rapid 3-4 word phrases centered on screen
          const wordsPerChunk = 3;
          const chunkStart = Math.floor(activeIdx / wordsPerChunk) * wordsPerChunk;
          const currentChunk = words.slice(chunkStart, chunkStart + wordsPerChunk);
          const relActive = activeIdx - chunkStart;

          // Safe Lower-Third Zone Positioning
          const isLong = manifest.video_format === 'long-form';
          const subY = isLong ? Math.round(h * 0.86) : Math.round(h * 0.78);
          const fontSize = Math.round(Math.min(w, h) * (isLong ? 0.048 : 0.056));

          ctx.save();
          ctx.font = `900 ${fontSize}px "Montserrat", "Impact", "Arial Black", sans-serif`;
          ctx.textAlign = 'left';
          ctx.textBaseline = 'middle';

          const spaceW = ctx.measureText(' ').width;
          const widths = currentChunk.map(wd => ctx.measureText(wd.toUpperCase()).width);
          const totalW = widths.reduce((a, b) => a + b, 0) + (currentChunk.length - 1) * spaceW;

          let curX = (w - totalW) / 2;

          for (let idx = 0; idx < currentChunk.length; idx++) {
            const wd = currentChunk[idx].toUpperCase();
            const isAct = idx === relActive;
            const wordW = widths[idx];

            ctx.save();
            if (isAct) {
              // Word Highlight Pop: Scale 1.20x, Vibrant Orange Fill, Golden Glow
              const cx = curX + wordW / 2;
              const cy = subY;
              ctx.translate(cx, cy);
              ctx.scale(1.20, 1.20);
              ctx.translate(-cx, -cy);

              ctx.shadowColor = '#FF6B00';
              ctx.shadowBlur = 24;
            } else {
              ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
              ctx.shadowBlur = 12;
              ctx.shadowOffsetX = 0;
              ctx.shadowOffsetY = 4;
            }

            // Heavy Solid Black Outline Stroke
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = Math.round(fontSize * 0.22);
            ctx.lineJoin = 'round';
            ctx.miterLimit = 2;
            ctx.strokeText(wd, curX, subY);

            // Active word: vibrant orange #FF5722 / #FF9800, Inactive: pure white #FFFFFF (No boxes)
            ctx.fillStyle = isAct ? '#FF5722' : '#FFFFFF';
            ctx.fillText(wd, curX, subY);
            ctx.restore();

            curX += wordW + spaceW;
          }
          ctx.restore();
        }
      }
    }
  }, [localTime, manifest, isPlaying]);

  // Animation playback loop
  useEffect(() => {
    let animId: number;
    if (isPlaying) {
      let lastTimestamp = performance.now();
      const step = (now: number) => {
        const deltaSec = (now - lastTimestamp) / 1000;
        lastTimestamp = now;
        setLocalTime((prev) => {
          const next = prev + deltaSec;
          if (next >= totalDuration) {
            setIsPlaying(false);
            return 0;
          }
          if (onTimeUpdate) onTimeUpdate(next);
          return next;
        });
        animId = requestAnimationFrame(step);
      };
      animId = requestAnimationFrame(step);
    }
    return () => cancelAnimationFrame(animId);
  }, [isPlaying, totalDuration, onTimeUpdate]);

  const handleStepFrame = (forward: boolean) => {
    const frameDur = 1.0 / 30.0;
    const next = forward 
      ? Math.min(totalDuration, localTime + frameDur)
      : Math.max(0, localTime - frameDur);
    setLocalTime(next);
    if (onTimeUpdate) onTimeUpdate(next);
  };

  return (
    <div className={`flex flex-col items-center transition-all ${
      isFullscreen 
        ? 'fixed inset-0 z-50 bg-[#030712]/95 backdrop-blur-2xl p-6 justify-center' 
        : 'bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-2xl w-full'
    }`}>
      {/* DaVinci Resolve Top Timecode Bar & Shortcut Badge */}
      <div className={`w-full flex items-center justify-between pb-2 mb-2 border-b border-gray-800 text-xs ${
        isFullscreen ? 'max-w-[720px]' : ''
      }`}>
        <div className="flex items-center gap-2">
          <span className="font-bold text-gray-200">
            {isFullscreen ? '🖥️ Xem Trước Toàn Màn Hình' : 'Khung Hình Xem Trước'}
          </span>
          <span className="hidden sm:inline-flex items-center gap-1 text-[10px] bg-[#070b16] border border-studio-border/70 px-2 py-0.5 rounded-full text-gray-400 font-mono">
            <Keyboard className="w-3 h-3 text-studio-primary" />
            Space: Phát | `: Toàn màn hình
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-[#070b16] border border-studio-border px-2.5 py-1 rounded-lg">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-mono text-emerald-400 font-bold tracking-wider text-xs">
              {formatTimecode(localTime)}
            </span>
          </div>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 hover:text-white rounded-lg bg-studio-card/80 hover:bg-studio-card border border-studio-border text-gray-400 transition"
            title={isFullscreen ? 'Thu nhỏ lại (Nhấn ` hoặc Esc)' : 'Phóng to toàn màn hình (Nhấn `)'}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4 text-studio-primary" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Dynamic Aspect Ratio Canvas Preview */}
      <div className={`relative ${
        isFullscreen
          ? manifest.video_format === 'long-form' 
            ? 'w-[90vw] max-w-[1100px] aspect-[16/9]' 
            : 'h-[75vh] max-h-[820px] aspect-[9/16]'
          : manifest.video_format === 'long-form' 
            ? 'aspect-[16/9] max-w-[420px]' 
            : 'aspect-[9/16] max-w-[280px]'
      } w-full bg-black rounded-xl overflow-hidden shadow-2xl border border-studio-border`}>
        <canvas
          ref={canvasRef}
          width={manifest.video_specs?.width || 1080}
          height={manifest.video_specs?.height || 1920}
          className="w-full h-full object-contain"
        />
        {/* Play overlay button when paused */}
        {!isPlaying && (
          <button
            onClick={() => setIsPlaying(true)}
            className="absolute inset-0 m-auto w-14 h-14 bg-studio-primary/90 text-white rounded-full flex items-center justify-center hover:scale-110 transition shadow-lg"
          >
            <Play className="w-7 h-7 fill-current ml-1" />
          </button>
        )}
      </div>

      {/* DaVinci Resolve Professional Transport Controls */}
      <div className={`w-full ${isFullscreen ? 'max-w-[480px]' : 'max-w-[340px]'} mt-3 flex flex-col gap-2`}>
        {/* Continuous Scrubber Slider */}
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-gray-400 font-mono w-10 text-right">
            {localTime.toFixed(1)}s
          </span>
          <input
            type="range"
            min={0}
            max={totalDuration}
            step={0.05}
            value={localTime}
            onChange={(e) => {
              const val = parseFloat(e.target.value);
              setLocalTime(val);
              if (onTimeUpdate) onTimeUpdate(val);
            }}
            className="w-full accent-studio-primary cursor-pointer h-1.5 bg-studio-card rounded-lg"
          />
          <span className="text-[11px] text-gray-400 font-mono w-10">
            {totalDuration.toFixed(1)}s
          </span>
        </div>

        {/* Transport Buttons (DaVinci Standard: Jump Start, Frame Back, Play/Pause, Frame Forward, Jump End) */}
        <div className="flex items-center justify-center gap-2 text-gray-300">
          <button
            onClick={() => { setLocalTime(0); if (onTimeUpdate) onTimeUpdate(0); }}
            className="p-1.5 hover:text-white rounded-lg hover:bg-studio-card transition"
            title="Về đầu phim (Jump to Start)"
          >
            <SkipBack className="w-4 h-4" />
          </button>

          <button
            onClick={() => handleStepFrame(false)}
            className="p-1.5 hover:text-white rounded-lg hover:bg-studio-card transition"
            title="Lùi 1 khung hình (Step 1 Frame Back)"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2.5 bg-studio-primary hover:bg-indigo-600 text-white rounded-xl shadow transition"
            title={isPlaying ? 'Tạm dừng (Phím Space)' : 'Phát (Phím Space)'}
          >
            {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-0.5" />}
          </button>

          <button
            onClick={() => handleStepFrame(true)}
            className="p-1.5 hover:text-white rounded-lg hover:bg-studio-card transition"
            title="Tiến 1 khung hình (Step 1 Frame Forward)"
          >
            <ChevronRight className="w-4 h-4" />
          </button>

          <button
            onClick={() => { setLocalTime(totalDuration); if (onTimeUpdate) onTimeUpdate(totalDuration); }}
            className="p-1.5 hover:text-white rounded-lg hover:bg-studio-card transition"
            title="Đến cuối phim (Jump to End)"
          >
            <SkipForward className="w-4 h-4" />
          </button>

          <div className="w-[1px] h-4 bg-gray-700 mx-1" />

          <button
            onClick={() => { setLocalTime(0); setIsPlaying(false); if (onTimeUpdate) onTimeUpdate(0); }}
            className="p-1.5 hover:text-white rounded-lg hover:bg-studio-card transition"
            title="Đặt lại từ đầu"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsMuted(!isMuted)}
            className="p-1.5 hover:text-white rounded-lg hover:bg-studio-card transition"
            title={isMuted ? 'Bật âm' : 'Tắt âm'}
          >
            {isMuted ? <VolumeX className="w-4 h-4 text-red-400" /> : <Volume2 className="w-4 h-4" />}
          </button>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 hover:text-white rounded-lg hover:bg-studio-card transition ml-1"
            title={isFullscreen ? 'Thu nhỏ lại (Phím `)' : 'Toàn màn hình (Phím `)'}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4 text-studio-primary" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
};
