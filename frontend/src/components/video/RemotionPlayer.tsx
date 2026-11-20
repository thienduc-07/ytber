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

      // 2. Render Ricks Clips 3000 Kinetic Pop Subtitles (Word-by-word bouncing karaoke)
      const text = activeScene.narration_text?.trim() || '';
      if (text) {
        const words = text.split(/\s+/).filter(Boolean);
        if (words.length > 0) {
          // Calculate active word index from millisecond boundary cues
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
          const wordsPerChunk = 4;
          const chunkStart = Math.floor(activeIdx / wordsPerChunk) * wordsPerChunk;
          const currentChunk = words.slice(chunkStart, chunkStart + wordsPerChunk);
          const relActive = activeIdx - chunkStart;

          // Position: Eye-level upper-middle for viral short-form retention
          const subY = Math.round(h * 0.54);
          const fontSize = Math.round(Math.min(w, h) * 0.058);

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
              // Ricks Clips Signature Kinetic Pop bounce (scale 1.15x)
              const cx = curX + wordW / 2;
              const cy = subY;
              ctx.translate(cx, cy);
              ctx.scale(1.15, 1.15);
              ctx.translate(-cx, -cy);

              ctx.shadowColor = '#FACC15';
              ctx.shadowBlur = 18;
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

            // Active word highlighted in bright yellow (#FACC15), inactive in white (#FFFFFF)
            ctx.fillStyle = isAct ? '#FACC15' : '#FFFFFF';
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
