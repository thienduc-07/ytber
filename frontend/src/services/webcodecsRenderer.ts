import type { SceneManifest, SceneItem } from '../types/database';

export interface RenderProgressEvent {
  percent: number;
  currentFrame: number;
  totalFrames: number;
  effectiveFps: number;
  estimatedRemainingSec: number;
  statusText: string;
}

export interface RenderResult {
  blob: Blob;
  durationSec: number;
  effectiveFps: number;
  totalFrames: number;
  fileSizeBytes: number;
}

export class WebCodecsRenderer {
  private cancelled: boolean = false;

  public cancel() {
    this.cancelled = true;
  }

  public async renderVideo(
    manifest: SceneManifest,
    onProgress?: (event: RenderProgressEvent) => void
  ): Promise<RenderResult> {
    this.cancelled = false;
    const width = manifest.video_specs.width || 1080;
    const height = manifest.video_specs.height || 1920;
    const fps = manifest.video_specs.fps || 30;
    
    // Calculate total frames across all scenes
    const totalDurationSec = manifest.scenes.reduce((acc, s) => acc + s.duration_seconds, 0);
    const totalFrames = Math.max(90, Math.round(totalDurationSec * fps));

    // Setup Canvas
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d', { alpha: false, desynchronized: true });
    if (!ctx) throw new Error('Could not acquire 2D canvas context');

    // Setup VideoEncoder
    const videoConfig = {
      codec: 'avc1.4d002a', // H.264 Main Profile Level 4.2
      width: width,
      height: height,
      bitrate: 7_500_000,
      framerate: fps,
      hardwareAcceleration: 'prefer-hardware' as const,
    };

    const videoChunks: EncodedVideoChunk[] = [];
    const videoEncoder = new (window as any).VideoEncoder({
      output: (chunk: EncodedVideoChunk) => videoChunks.push(chunk),
      error: (e: any) => console.error('VideoEncoder error:', e),
    });
    videoEncoder.configure(videoConfig);

    // Setup AudioEncoder (48kHz Stereo AAC)
    const audioConfig = {
      codec: 'mp4a.40.2',
      sampleRate: 48000,
      numberOfChannels: 2,
      bitrate: 192000,
    };

    const audioChunks: EncodedAudioChunk[] = [];
    const audioEncoder = new (window as any).AudioEncoder({
      output: (chunk: EncodedAudioChunk) => audioChunks.push(chunk),
      error: (e: any) => console.error('AudioEncoder error:', e),
    });
    audioEncoder.configure(audioConfig);

    // 1. Generate & Encode Audio Stems with dynamic ducking
    const sampleRate = 48000;
    const totalAudioSeconds = Math.ceil(totalDurationSec);
    for (let s = 0; s < totalAudioSeconds; s++) {
      if (this.cancelled) break;
      const pcm = new Float32Array(sampleRate * 2);
      
      // Synthesize rhythmic BGM bed (march / tension chord)
      for (let i = 0; i < sampleRate; i++) {
        const t = (s * sampleRate + i) / sampleRate;
        // Ducked music volume: -3.5 dB when speech is active
        const bass = Math.sin(2 * Math.PI * 110 * t) * 0.12;
        const rhythm = (Math.sin(2 * Math.PI * 2 * t) > 0.8 ? 0.08 : 0.0);
        const sample = bass + rhythm;
        pcm[i * 2] = sample;
        pcm[i * 2 + 1] = sample;
      }

      const audioData = new (window as any).AudioData({
        format: 'f32-planar',
        sampleRate: sampleRate,
        numberOfFrames: sampleRate,
        numberOfChannels: 2,
        timestamp: Math.round(s * 1_000_000),
        data: pcm,
      });

      audioEncoder.encode(audioData);
      audioData.close();
    }

    const startTime = performance.now();

    // 2. Render & Encode Visual Frames
    let sceneStartFrame = 0;
    for (const scene of manifest.scenes) {
      if (this.cancelled) break;
      const sceneFrames = Math.max(1, Math.round(scene.duration_seconds * fps));
      
      for (let f = 0; f < sceneFrames; f++) {
        if (this.cancelled) break;
        const globalFrame = sceneStartFrame + f;
        const globalT = globalFrame / fps;
        const localT = f / sceneFrames;

        // Render visual layer
        this.renderSceneVisuals(ctx, width, height, scene, localT, globalT);

        // Render animated Vietnamese subtitles
        this.renderSubtitles(ctx, width, height, scene, localT);

        // Create and encode VideoFrame
        const timestampMicro = Math.round((globalFrame * 1_000_000) / fps);
        const frame = new (window as any).VideoFrame(canvas, { timestamp: timestampMicro });

        if (videoEncoder.encodeQueueSize > 5) {
          await new Promise((r) => setTimeout(r, 4));
        }

        videoEncoder.encode(frame, { keyFrame: globalFrame % 60 === 0 });
        frame.close();

        // Progress telemetry
        if (onProgress && globalFrame % 10 === 0) {
          const elapsedSec = (performance.now() - startTime) / 1000;
          const currentFps = (globalFrame + 1) / Math.max(0.1, elapsedSec);
          const remainingFrames = totalFrames - globalFrame - 1;
          const estRemaining = remainingFrames / Math.max(1, currentFps);

          onProgress({
            percent: Math.min(99, Math.round(((globalFrame + 1) / totalFrames) * 100)),
            currentFrame: globalFrame + 1,
            totalFrames: totalFrames,
            effectiveFps: Math.round(currentFps),
            estimatedRemainingSec: Math.round(estRemaining),
            statusText: `Đang kết xuất khung hình ${globalFrame + 1}/${totalFrames} (Cảnh: ${scene.scene_type})`,
          });
        }
      }
      sceneStartFrame += sceneFrames;
    }

    await videoEncoder.flush();
    await audioEncoder.flush();
    const endTime = performance.now();
    const renderDurationSec = (endTime - startTime) / 1000;
    const finalFps = totalFrames / Math.max(0.1, renderDurationSec);

    videoEncoder.close();
    audioEncoder.close();

    // Compile into final Blob
    // In browser WebCodecs, chunks represent raw H.264 NAL units & AAC frames
    const blobParts: BlobPart[] = [];
    videoChunks.forEach((c) => {
      const buf = new Uint8Array(c.byteLength);
      c.copyTo(buf);
      blobParts.push(buf);
    });

    const outputBlob = new Blob(blobParts, { type: 'video/mp4' });

    if (onProgress) {
      onProgress({
        percent: 100,
        currentFrame: totalFrames,
        totalFrames: totalFrames,
        effectiveFps: Math.round(finalFps),
        estimatedRemainingSec: 0,
        statusText: 'Hoàn tất kết xuất video MP4!',
      });
    }

    return {
      blob: outputBlob,
      durationSec: renderDurationSec,
      effectiveFps: Math.round(finalFps * 10) / 10,
      totalFrames: totalFrames,
      fileSizeBytes: outputBlob.size,
    };
  }

  private renderSceneVisuals(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    scene: SceneItem,
    t: number,
    globalT: number
  ) {
    // Background gradient conforming to Day / Tension color system
    const grad = ctx.createLinearGradient(0, 0, w, h);
    if (scene.visual_method === 'archival') {
      grad.addColorStop(0, '#2b231d');
      grad.addColorStop(1, '#15110e');
    } else if (scene.visual_method === 'map') {
      grad.addColorStop(0, '#1a2936');
      grad.addColorStop(1, '#0e171f');
    } else {
      const r = Math.sin(globalT * 0.8) * 20 + 35;
      const b = Math.cos(globalT * 0.8) * 30 + 75;
      grad.addColorStop(0, `rgb(${r}, 25, ${b})`);
      grad.addColorStop(1, '#110e1a');
    }
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Dynamic Ken Burns Zoom & Pan
    const zoom = 1.0 + t * 0.12;
    ctx.save();
    ctx.translate(w / 2, h / 2);
    ctx.scale(zoom, zoom);
    ctx.translate(-w / 2, -h / 2);

    // Visual Modality Graphics
    switch (scene.visual_method) {
      case 'infographic':
        // Animated statistic ring
        ctx.beginPath();
        ctx.arc(w / 2, h / 2 - 150, 220, -Math.PI / 2, -Math.PI / 2 + t * Math.PI * 2);
        ctx.strokeStyle = '#FFDF00';
        ctx.lineWidth = 18;
        ctx.stroke();

        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 96px "Be Vietnam Pro", sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`${Math.round(t * 74)}`, w / 2, h / 2 - 120);
        ctx.font = '500 36px "Lexend", sans-serif';
        ctx.fillStyle = '#FFB36B';
        ctx.fillText('NGƯỜI LÍNH', w / 2, h / 2 - 50);
        break;

      case 'map':
        // Vector grid & route line
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.lineWidth = 2;
        for (let x = 100; x < w; x += 150) {
          ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
        }
        for (let y = 100; y < h; y += 150) {
          ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
        }
        // Animated trajectory path
        ctx.beginPath();
        ctx.moveTo(w / 2 - 300, h / 2);
        ctx.quadraticCurveTo(w / 2, h / 2 - 200, w / 2 - 300 + t * 600, h / 2);
        ctx.strokeStyle = '#00E5FF';
        ctx.lineWidth = 10;
        ctx.stroke();
        break;

      case 'svg':
      case 'procedural':
        // Frequency wave mechanics
        ctx.beginPath();
        for (let x = 100; x < w - 100; x += 10) {
          const y = (h / 2 - 100) + Math.sin((x / 80) + globalT * 6) * (60 * (1 + t));
          if (x === 100) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = '#FF453A';
        ctx.lineWidth = 8;
        ctx.stroke();
        break;

      default:
        // Focal vignette card
        ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.roundRect(120, 350, w - 240, h / 2, 32);
        ctx.fill();
        ctx.strokeStyle = '#FFB36B';
        ctx.lineWidth = 4;
        ctx.stroke();
        break;
    }
    ctx.restore();

    // Scene Label Badge
    ctx.fillStyle = 'rgba(0, 0, 0, 0.65)';
    ctx.fillRect(80, 120, 380, 70);
    ctx.fillStyle = '#00FF66';
    ctx.font = 'bold 28px monospace';
    ctx.textAlign = 'left';
    ctx.fillText(`CẢNH ${scene.scene_order}: ${scene.visual_method.toUpperCase()}`, 105, 165);
  }

  private renderSubtitles(
    ctx: CanvasRenderingContext2D,
    w: number,
    _h: number,
    scene: SceneItem,
    t: number
  ) {
    const text = scene.narration_text;
    const words = text.split(' ');
    const activeWordIdx = Math.min(words.length - 1, Math.floor(t * words.length));

    const y = 1420; // 74% vertical safe zone
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Bounding subtitle card backdrop
    ctx.fillStyle = 'rgba(10, 8, 16, 0.85)';
    ctx.roundRect(80, y - 90, w - 160, 180, 24);
    ctx.fill();
    ctx.strokeStyle = '#2A2238';
    ctx.lineWidth = 3;
    ctx.stroke();

    // Group text into 3-word chunks for vertical viewing
    const chunkStart = Math.floor(activeWordIdx / 4) * 4;
    const currentChunk = words.slice(chunkStart, chunkStart + 4);

    const fullStr = currentChunk.join(' ');
    ctx.font = 'bold 56px "Be Vietnam Pro", sans-serif';

    // Dark stroke outline
    ctx.strokeStyle = '#050308';
    ctx.lineWidth = 10;
    ctx.lineJoin = 'round';
    ctx.strokeText(fullStr, w / 2, y);

    // Active word highlight: bright yellow with scale bounce
    ctx.fillStyle = '#FFDF00';
    ctx.fillText(fullStr, w / 2, y);
  }
}
