import { Muxer, ArrayBufferTarget } from 'mp4-muxer';
import type { SceneManifest, SceneItem, SubtitleItem } from '../types/database';
import { AnimationEngine } from './animationEngine';
import { SoundDesignEngine } from './soundDesignEngine';
import { getAuthHeaders } from './apiClient';

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

  /**
   * Preloads and decodes image assets with createImageBitmap
   */
  private async preloadSceneAssets(
    manifest: SceneManifest,
    onProgress?: (status: string) => void
  ): Promise<Map<number, ImageBitmap | null>> {
    const bitmaps = new Map<number, ImageBitmap | null>();

    for (let i = 0; i < manifest.scenes.length; i++) {
      if (this.cancelled) break;
      const scene = manifest.scenes[i];
      const assetUrl =
        scene.assets?.[0]?.local_url ||
        scene.assets?.[0]?.source_url ||
        scene.assets?.[0]?.preview_url ||
        scene.visual_config?.imageUrl;

      if (assetUrl) {
        if (onProgress) {
          onProgress(`Đang tải và giải mã hình ảnh cảnh ${i + 1}/${manifest.scenes.length}...`);
        }
        try {
          const res = await fetch(assetUrl, { mode: 'cors' });
          if (res.ok) {
            const blob = await res.blob();
            // Verify blob is an image
            if (blob.type.startsWith('image/') || blob.size > 0) {
              const bmp = await createImageBitmap(blob);
              bitmaps.set(i, bmp);
              continue;
            }
          }
        } catch (err) {
          console.warn(`Could not preload asset image for scene ${i + 1} (${assetUrl}):`, err);
        }
      }
      bitmaps.set(i, null);
    }

    return bitmaps;
  }

  /**
   * Preloads and decodes actual audio files into PCM AudioBuffers.
   * Strictly enforces real speech availability: fails if narration audio cannot be loaded.
   */
  private async preloadAudioBuffers(
    manifest: SceneManifest,
    audioCtx: AudioContext,
    onProgress?: (status: string) => void
  ): Promise<Map<number, AudioBuffer | null>> {
    const buffers = new Map<number, AudioBuffer | null>();
    const authHeaders = await getAuthHeaders();

    for (let i = 0; i < manifest.scenes.length; i++) {
      if (this.cancelled) break;
      const scene = manifest.scenes[i];
      const audioUrl = scene.audio_url;

      if (audioUrl) {
        if (onProgress) {
          onProgress(`Đang nạp giọng đọc AI cảnh ${i + 1}/${manifest.scenes.length}...`);
        }
        try {
          const res = await fetch(audioUrl, { headers: authHeaders });
          if (res.ok) {
            const arrayBuf = await res.arrayBuffer();
            if (arrayBuf.byteLength < 100) {
              throw new Error(`Tệp âm thanh cảnh ${i + 1} quá nhỏ hoặc rỗng (${arrayBuf.byteLength} bytes)`);
            }
            const decoded = await audioCtx.decodeAudioData(arrayBuf);
            if (decoded.length === 0 || decoded.duration < 0.1) {
              throw new Error(`Tệp âm thanh cảnh ${i + 1} không chứa tín hiệu giọng đọc hợp lệ`);
            }
            buffers.set(i, decoded);
            continue;
          } else {
            throw new Error(`Máy chủ từ chối tải tệp âm thanh (Mã lỗi HTTP ${res.status})`);
          }
        } catch (err: any) {
          console.error(`Không thể giải mã tệp âm thanh cảnh ${i + 1} (${audioUrl}):`, err);
          throw new Error(`Lỗi tải giọng đọc cảnh ${i + 1}: ${err.message}. Yêu cầu phải có giọng đọc thực tế để sản xuất video.`);
        }
      } else if (scene.narration_text && scene.narration_text.trim().length > 10) {
        throw new Error(`Cảnh ${i + 1} có lời thoại nhưng chưa được lồng tiếng. Vui lòng bấm 'Lồng Tiếng Các Cảnh' trước khi kết xuất.`);
      }

      buffers.set(i, null);
    }

    return buffers;
  }

  /**
   * Determines whether character is speaking at local normalized scene time (localT: 0..1)
   */
  private isSpeechActiveAt(scene: SceneItem, localT: number): boolean {
    const currentSec = localT * scene.duration_seconds;
    if (scene.subtitles_json && scene.subtitles_json.length > 0) {
      const currentMs = currentSec * 1000;
      return scene.subtitles_json.some((c) => currentMs >= c.start_ms - 50 && currentMs <= c.end_ms + 50);
    }
    return !!scene.audio_url && localT <= 0.85;
  }

  public async renderVideo(
    manifest: SceneManifest,
    onProgress?: (event: RenderProgressEvent) => void
  ): Promise<RenderResult> {
    this.cancelled = false;

    if (typeof window === 'undefined' || !('VideoEncoder' in window) || !('AudioEncoder' in window)) {
      throw new Error('WebCodecs is not supported in this environment. Please use a modern Chromium-based browser.');
    }

    const width = manifest.video_specs?.width ?? 1080;
    const height = manifest.video_specs?.height ?? 1920;
    const fps = manifest.video_specs?.fps ?? 30;

    if (width <= 0 || height <= 0 || fps <= 0) {
      throw new Error(`Invalid video specifications: ${width}x${height}@${fps}fps. Dimensions and frame rate must be positive numbers.`);
    }

    // Calculate exact frame counts per scene and total frames
    const sceneFrameCounts = manifest.scenes.map((s) => Math.max(1, Math.round(s.duration_seconds * fps)));
    const totalFrames = Math.max(90, sceneFrameCounts.reduce((acc, count) => acc + count, 0));
    const exactDurationSec = totalFrames / fps;
    const sampleRate = 48000;
    const totalAudioSamples = Math.round(exactDurationSec * sampleRate);

    // Setup Canvas
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d', { alpha: false, desynchronized: true });
    if (!ctx) throw new Error('Could not acquire 2D canvas context');

    // Preload Real Media Assets and Audio
    if (onProgress) {
      onProgress({
        percent: 2,
        currentFrame: 0,
        totalFrames: totalFrames,
        effectiveFps: 0,
        estimatedRemainingSec: 0,
        statusText: 'Đang chuẩn bị và nạp trước tư liệu hình ảnh...',
      });
    }

    const preloadedBitmaps = await this.preloadSceneAssets(manifest, (statusText) => {
      if (onProgress) {
        onProgress({
          percent: 5,
          currentFrame: 0,
          totalFrames: totalFrames,
          effectiveFps: 0,
          estimatedRemainingSec: 0,
          statusText,
        });
      }
    });

    // Audio Context for PCM decoding
    let audioCtx: AudioContext | null = null;
    let preloadedAudios = new Map<number, AudioBuffer | null>();
    try {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioContextClass) {
        audioCtx = new AudioContextClass({ sampleRate: 48000 });
        preloadedAudios = await this.preloadAudioBuffers(manifest, audioCtx, (statusText) => {
          if (onProgress) {
            onProgress({
              percent: 8,
              currentFrame: 0,
              totalFrames: totalFrames,
              effectiveFps: 0,
              estimatedRemainingSec: 0,
              statusText,
            });
          }
        });
      }
    } catch (e) {
      console.warn('Web Audio Context initialization warning:', e);
    }

    // Setup MP4 Muxer with Fast Start (in-memory) for video & audio tracks
    const muxer = new Muxer({
      target: new ArrayBufferTarget(),
      video: {
        codec: 'avc',
        width: width,
        height: height,
        frameRate: fps,
      },
      audio: {
        codec: 'aac',
        numberOfChannels: 2,
        sampleRate: sampleRate,
      },
      fastStart: 'in-memory',
      firstTimestampBehavior: 'offset',
    });

    let encodingError: Error | null = null;
    let videoChunksCount = 0;
    let audioChunksCount = 0;

    // Setup VideoEncoder configuration
    const videoConfig = {
      codec: 'avc1.4d002a', // H.264 Main Profile Level 4.2
      width: width,
      height: height,
      bitrate: 7_500_000,
      framerate: fps,
      hardwareAcceleration: 'prefer-hardware' as const,
    };

    let videoEncoder: any = null;
    let audioEncoder: any = null;

    try {
      videoEncoder = new (window as any).VideoEncoder({
        output: (chunk: EncodedVideoChunk, meta?: EncodedVideoChunkMetadata) => {
          try {
            if (typeof chunk.duration === 'number' && Number.isFinite(chunk.duration) && chunk.duration >= 0) {
              muxer.addVideoChunk(chunk, meta);
            } else {
              const data = new Uint8Array(chunk.byteLength);
              chunk.copyTo(data);
              const fallbackDurationUs = Math.round(1_000_000 / fps);
              muxer.addVideoChunkRaw(data, chunk.type, chunk.timestamp, fallbackDurationUs, meta);
            }
            videoChunksCount++;
          } catch (err: any) {
            console.error('Muxer addVideoChunk error:', err);
            encodingError = err instanceof Error ? err : new Error(String(err));
          }
        },
        error: (e: any) => {
          console.error('VideoEncoder error:', e);
          encodingError = e instanceof Error ? e : new Error(String(e));
        },
      });
      videoEncoder.configure(videoConfig);

      // Setup AudioEncoder (48kHz Stereo AAC)
      const audioConfig = {
        codec: 'mp4a.40.2',
        sampleRate: sampleRate,
        numberOfChannels: 2,
        bitrate: 192000,
      };

      audioEncoder = new (window as any).AudioEncoder({
        output: (chunk: EncodedAudioChunk, meta?: EncodedAudioChunkMetadata) => {
          try {
            if (typeof chunk.duration === 'number' && Number.isFinite(chunk.duration) && chunk.duration >= 0) {
              muxer.addAudioChunk(chunk, meta);
            } else {
              const data = new Uint8Array(chunk.byteLength);
              chunk.copyTo(data);
              const fallbackDurationUs = Math.round((1024 * 1_000_000) / sampleRate);
              muxer.addAudioChunkRaw(data, chunk.type, chunk.timestamp, fallbackDurationUs, meta);
            }
            audioChunksCount++;
          } catch (err: any) {
            console.error('Muxer addAudioChunk error:', err);
            encodingError = err instanceof Error ? err : new Error(String(err));
          }
        },
        error: (e: any) => {
          console.error('AudioEncoder error:', e);
          encodingError = e instanceof Error ? e : new Error(String(e));
        },
      });
      audioEncoder.configure(audioConfig);

      // 1. Synthesize Complete 3-Layer Audio (Narration Speech + Dynamic BGM Bed + SFX Cues)
      if (onProgress) {
        onProgress({
          percent: 5,
          currentFrame: 0,
          totalFrames: totalFrames,
          effectiveFps: 0,
          estimatedRemainingSec: 0,
          statusText: 'Đang phối âm 3 lớp (Thuyết minh + Nhạc nền BGM + Hiệu ứng SFX)...',
        });
      }

      const interleavedAudio = await SoundDesignEngine.synthesizeCompleteAudio(
        manifest,
        preloadedAudios,
        totalAudioSamples,
        fps,
        (p) => {
          if (onProgress) {
            onProgress({
              percent: Math.round(5 + (p.percent / 100) * 10),
              currentFrame: 0,
              totalFrames: totalFrames,
              effectiveFps: 0,
              estimatedRemainingSec: 0,
              statusText: p.status,
            });
          }
        }
      );

      // Encode audio chunks (48000 stereo sample frames at a time)
      let samplesProcessed = 0;
      while (samplesProcessed < totalAudioSamples) {
        if (this.cancelled) throw new Error('Video rendering was cancelled');
        if (encodingError) throw encodingError;

        const chunkSize = Math.min(48000, totalAudioSamples - samplesProcessed);
        const pcmInterleaved = interleavedAudio.subarray(samplesProcessed * 2, (samplesProcessed + chunkSize) * 2);

        const timestampMicro = Math.round((samplesProcessed * 1_000_000) / sampleRate);
        const audioData = new (window as any).AudioData({
          format: 'f32',
          sampleRate: sampleRate,
          numberOfFrames: chunkSize,
          numberOfChannels: 2,
          timestamp: timestampMicro,
          data: pcmInterleaved,
        });

        audioEncoder.encode(audioData);
        audioData.close();

        samplesProcessed += chunkSize;
      }

      const startTime = performance.now();

      // 2. Render & Encode Visual Frames with 100% Animated Visuals & Synchronized Subtitles
      let sceneStartFrame = 0;
      for (let sIdx = 0; sIdx < manifest.scenes.length; sIdx++) {
        const scene = manifest.scenes[sIdx];
        const sceneFrames = sceneFrameCounts[sIdx];
        const currentBmp = preloadedBitmaps.get(sIdx);
        const nextBmp = sIdx + 1 < manifest.scenes.length ? preloadedBitmaps.get(sIdx + 1) : null;

        for (let f = 0; f < sceneFrames; f++) {
          if (this.cancelled) {
            throw new Error('Video rendering was cancelled');
          }
          if (encodingError) {
            throw encodingError;
          }

          const globalFrame = sceneStartFrame + f;
          const globalT = globalFrame / fps;
          const localT = f / sceneFrames;

          // Render 100% Animated Visuals (Parallax, Characters, Maps, Infographics, Particles)
          const isSpeaking = this.isSpeechActiveAt(scene, localT);
          AnimationEngine.renderScene(
            ctx,
            width,
            height,
            scene,
            localT,
            globalT,
            manifest.character_registry,
            isSpeaking,
            currentBmp
          );

          // Scene Transition (Crossfade in last 15 frames if dissolve/fade)
          const transitionFrames = 15;
          const framesRemaining = sceneFrames - f;
          if (framesRemaining <= transitionFrames && sIdx + 1 < manifest.scenes.length && scene.transition !== 'cut') {
            const nextScene = manifest.scenes[sIdx + 1];
            const blendAlpha = (transitionFrames - framesRemaining) / transitionFrames;
            ctx.save();
            ctx.globalAlpha = Math.min(1.0, Math.max(0.0, blendAlpha));
            AnimationEngine.renderScene(
              ctx,
              width,
              height,
              nextScene,
              0,
              globalT,
              manifest.character_registry,
              false,
              nextBmp
            );
            ctx.restore();
          }

          // Render Animated Vietnamese Karaoke Subtitles (Synced with Phase 2 Word Boundaries)
          this.renderSubtitles(ctx, width, height, scene, localT);

          // Create and encode VideoFrame
          const timestampMicro = Math.round((globalFrame * 1_000_000) / fps);
          const durationMicro = Math.round(1_000_000 / fps);
          const frame = new (window as any).VideoFrame(canvas, {
            timestamp: timestampMicro,
            duration: durationMicro,
          });

          if (videoEncoder.encodeQueueSize > 5) {
            await new Promise((r) => setTimeout(r, 4));
          }

          if (this.cancelled) {
            frame.close();
            throw new Error('Video rendering was cancelled');
          }
          if (encodingError) {
            frame.close();
            throw encodingError;
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
              statusText: `Đang kết xuất hoạt hình ${globalFrame + 1}/${totalFrames} (Cảnh ${scene.scene_order}: ${scene.visual_method || 'Hoạt hình 2D'})`,
            });
          }
        }
        sceneStartFrame += sceneFrames;
      }

      await videoEncoder.flush();
      await audioEncoder.flush();

      if (this.cancelled) {
        throw new Error('Video rendering was cancelled');
      }
      if (encodingError) {
        throw encodingError;
      }

      if (videoChunksCount === 0) {
        throw new Error('No video chunks were encoded');
      }
      if (audioChunksCount === 0) {
        throw new Error('No audio chunks were encoded');
      }

      // Finalize MP4 muxer into standard MP4 container
      muxer.finalize();
      const { buffer } = muxer.target;
      const outputBlob = new Blob([buffer], { type: 'video/mp4' });

      if (outputBlob.size === 0) {
        throw new Error('Muxed MP4 output file is empty');
      }

      const endTime = performance.now();
      const renderDurationSec = (endTime - startTime) / 1000;
      const finalFps = totalFrames / Math.max(0.1, renderDurationSec);

      if (onProgress) {
        onProgress({
          percent: 100,
          currentFrame: totalFrames,
          totalFrames: totalFrames,
          effectiveFps: Math.round(finalFps),
          estimatedRemainingSec: 0,
          statusText: 'Hoàn tất kết xuất video MP4 với hình ảnh và âm thanh thực!',
        });
      }

      return {
        blob: outputBlob,
        durationSec: exactDurationSec,
        effectiveFps: Math.round(finalFps * 10) / 10,
        totalFrames: totalFrames,
        fileSizeBytes: outputBlob.size,
      };
    } finally {
      // Clean up ImageBitmap resources to prevent memory leaks
      preloadedBitmaps.forEach((bmp) => {
        if (bmp) {
          try {
            bmp.close();
          } catch {
            // ignore
          }
        }
      });
      if (audioCtx && audioCtx.state !== 'closed') {
        try {
          audioCtx.close();
        } catch {
          // ignore
        }
      }
      if (videoEncoder && videoEncoder.state !== 'closed') {
        try {
          videoEncoder.close();
        } catch {
          // ignore
        }
      }
      if (audioEncoder && audioEncoder.state !== 'closed') {
        try {
          audioEncoder.close();
        } catch {
          // ignore
        }
      }
      canvas.width = 0;
      canvas.height = 0;
    }
  }



  /**
   * Renders synchronized Vietnamese animated subtitles using Phase 2 word cues
   */
  private renderSubtitles(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    scene: SceneItem,
    t: number
  ) {
    const text = scene.narration_text.trim();
    if (!text) return;

    // Check if word-level cues exist from Phase 2 Edge-TTS
    const cues: SubtitleItem[] = scene.subtitles_json || [];
    const localMs = Math.round(t * scene.duration_seconds * 1000);

    let activeWordIndex = -1;
    if (cues.length > 0) {
      activeWordIndex = cues.findIndex((c) => localMs >= c.start_ms && localMs <= c.end_ms);
      if (activeWordIndex === -1) {
        // Fallback to closest preceding word
        for (let i = cues.length - 1; i >= 0; i--) {
          if (localMs >= cues[i].start_ms) {
            activeWordIndex = i;
            break;
          }
        }
      }
    }

    const words = text.split(/\s+/).filter(Boolean);
    if (words.length === 0) return;

    if (activeWordIndex === -1) {
      activeWordIndex = Math.min(words.length - 1, Math.floor(t * words.length));
    }

    // Dynamic vertical positioning based on aspect ratio
    const y = Math.round(h * 0.78);
    const subH = Math.min(180, Math.round(h * 0.16));
    const cardW = Math.round(w * 0.88);
    const cardX = Math.round((w - cardW) / 2);

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Bounding subtitle card backdrop
    ctx.fillStyle = 'rgba(10, 8, 16, 0.85)';
    ctx.roundRect(cardX, y - subH / 2, cardW, subH, 24);
    ctx.fill();
    ctx.strokeStyle = '#2A2238';
    ctx.lineWidth = 3;
    ctx.stroke();

    // Group text into phrases of 4 to 6 words for clear readability
    const wordsPerChunk = w > h ? 6 : 4;
    const chunkStart = Math.floor(activeWordIndex / wordsPerChunk) * wordsPerChunk;
    const currentChunk = words.slice(chunkStart, chunkStart + wordsPerChunk);
    const relativeActive = activeWordIndex - chunkStart;

    const fontSize = Math.round(Math.min(w, h) * 0.046);
    ctx.font = `bold ${fontSize}px "Be Vietnam Pro", sans-serif`;

    // Measure and render words with active karaoke word highlight
    const spaceWidth = ctx.measureText(' ').width;
    const wordWidths = currentChunk.map((wd) => ctx.measureText(wd).width);
    const totalChunkWidth = wordWidths.reduce((a, b) => a + b, 0) + (currentChunk.length - 1) * spaceWidth;

    let startX = (w - totalChunkWidth) / 2;

    ctx.textAlign = 'left';
    for (let idx = 0; idx < currentChunk.length; idx++) {
      const wd = currentChunk[idx];
      const isWordActive = idx === relativeActive;

      // Dark stroke outline
      ctx.strokeStyle = '#050308';
      ctx.lineWidth = 8;
      ctx.lineJoin = 'round';
      ctx.strokeText(wd, startX, y);

      // Active word highlighted in bright yellow (#FFDF00), others in white (#FFFFFF)
      ctx.fillStyle = isWordActive ? '#FFDF00' : '#FFFFFF';
      ctx.fillText(wd, startX, y);

      startX += wordWidths[idx] + spaceWidth;
    }
  }
}
