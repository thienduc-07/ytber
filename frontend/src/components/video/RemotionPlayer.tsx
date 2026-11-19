import React, { useRef, useState, useEffect } from 'react';
import type { SceneManifest } from '../../types/database';
import { Play, Pause, RotateCcw, Volume2, VolumeX } from 'lucide-react';

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
  const [localTime, setLocalTime] = useState(currentTimeSec);

  const totalDuration = manifest.scenes.reduce((acc, s) => acc + s.duration_seconds, 0) || 60;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = 1080;
    const h = 1920;

    // Find active scene
    let accumulatedTime = 0;
    let activeScene = manifest.scenes[0];

    for (const scene of manifest.scenes) {
      if (localTime >= accumulatedTime && localTime <= accumulatedTime + scene.duration_seconds) {
        activeScene = scene;
        break;
      }
      accumulatedTime += scene.duration_seconds;
    }

    // Render Preview Frame
    const grad = ctx.createLinearGradient(0, 0, w, h);
    grad.addColorStop(0, '#1c1c2b');
    grad.addColorStop(1, '#0d0d12');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Visual modality indicator
    ctx.fillStyle = '#FFB36B';
    ctx.font = 'bold 48px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`CẢNH: ${activeScene?.scene_type?.toUpperCase() || 'NARRATIVE'}`, w / 2, 400);

    ctx.fillStyle = '#FFFFFF';
    ctx.font = '36px sans-serif';
    ctx.fillText(`Phương thức: ${activeScene?.visual_method?.toUpperCase() || 'PHOTO'}`, w / 2, 480);

    // Subtitle card preview
    if (activeScene) {
      ctx.fillStyle = 'rgba(0,0,0,0.8)';
      ctx.roundRect(80, 1350, w - 160, 160, 24);
      ctx.fill();

      ctx.fillStyle = '#FFDF00';
      ctx.font = 'bold 52px "Be Vietnam Pro", sans-serif';
      ctx.fillText(activeScene.narration_text.slice(0, 45) + '...', w / 2, 1440);
    }
  }, [localTime, manifest]);

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

  return (
    <div className="flex flex-col items-center bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-2xl">
      {/* 9:16 Portrait Canvas Preview */}
      <div className="relative aspect-[9/16] w-full max-w-[320px] bg-black rounded-xl overflow-hidden shadow-inner border border-studio-border">
        <canvas
          ref={canvasRef}
          width={1080}
          height={1920}
          className="w-full h-full object-contain"
        />
        {/* Play overlay button when paused */}
        {!isPlaying && (
          <button
            onClick={() => setIsPlaying(true)}
            className="absolute inset-0 m-auto w-16 h-16 bg-studio-primary/90 text-white rounded-full flex items-center justify-center hover:scale-110 transition shadow-lg"
          >
            <Play className="w-8 h-8 fill-current ml-1" />
          </button>
        )}
      </div>

      {/* Playback Controls */}
      <div className="w-full max-w-[320px] mt-4 flex flex-col gap-2">
        {/* Timeline Scrubber */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 font-mono">
            {localTime.toFixed(1)}s
          </span>
          <input
            type="range"
            min={0}
            max={totalDuration}
            step={0.1}
            value={localTime}
            onChange={(e) => {
              const val = parseFloat(e.target.value);
              setLocalTime(val);
              if (onTimeUpdate) onTimeUpdate(val);
            }}
            className="w-full accent-studio-primary cursor-pointer h-1.5 bg-studio-card rounded-lg"
          />
          <span className="text-xs text-gray-400 font-mono">
            {totalDuration.toFixed(1)}s
          </span>
        </div>

        {/* Buttons Row */}
        <div className="flex items-center justify-between text-gray-300 px-1">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 hover:text-white rounded-lg hover:bg-studio-card transition"
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </button>
          <button
            onClick={() => { setLocalTime(0); setIsPlaying(false); }}
            className="p-2 hover:text-white rounded-lg hover:bg-studio-card transition"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
          <button
            onClick={() => setIsMuted(!isMuted)}
            className="p-2 hover:text-white rounded-lg hover:bg-studio-card transition"
          >
            {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </div>
  );
};
