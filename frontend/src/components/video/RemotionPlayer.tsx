import React, { useRef, useState, useEffect } from 'react';
import type { SceneManifest } from '../../types/database';
import { AnimationEngine } from '../../services/animationEngine';
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
      // 1. Render Rich Temporal Animation (Parallax, Vector Characters, Maps, Infographics, Particles)
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

      // 2. Render Synchronized Subtitle Overlay
      const subY = Math.round(h * 0.78);
      const subH = Math.min(180, Math.round(h * 0.16));
      const cardW = Math.round(w * 0.88);
      const cardX = Math.round((w - cardW) / 2);

      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = 'rgba(10, 8, 16, 0.85)';
      ctx.roundRect(cardX, subY - subH / 2, cardW, subH, 24);
      ctx.fill();
      ctx.strokeStyle = '#2A2238';
      ctx.lineWidth = 3;
      ctx.stroke();

      ctx.fillStyle = '#FFDF00';
      ctx.font = 'bold 36px "Be Vietnam Pro", sans-serif';
      const displayText = activeScene.narration_text.length > 55
        ? activeScene.narration_text.slice(0, 55) + '...'
        : activeScene.narration_text;
      ctx.fillText(displayText, w / 2, subY);
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

  return (
    <div className="flex flex-col items-center bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-2xl w-full">
      {/* Dynamic Aspect Ratio Canvas Preview (9:16 Shorts vs 16:9 Long-Form) */}
      <div className={`relative ${manifest.video_format === 'long-form' ? 'aspect-[16/9] max-w-[420px]' : 'aspect-[9/16] max-w-[300px]'} w-full bg-black rounded-xl overflow-hidden shadow-inner border border-studio-border`}>
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
