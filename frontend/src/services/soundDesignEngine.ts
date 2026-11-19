import type { SceneManifest } from '../types/database';

export interface AudioMixProgress {
  status: string;
  percent: number;
}

export class SoundDesignEngine {
  private static readonly SAMPLE_RATE = 48000;

  /**
   * Generates a 3-layer audio mix (Voiceover + BGM + SFX) with dynamic ducking.
   * Returns interleaved stereo Float32Array PCM at 48kHz.
   */
  public static async synthesizeCompleteAudio(
    manifest: SceneManifest,
    voiceBuffers: Map<number, AudioBuffer | null>,
    totalSamples: number,
    fps: number,
    onProgress?: (progress: AudioMixProgress) => void
  ): Promise<Float32Array> {
    const sampleRate = this.SAMPLE_RATE;

    // Allocate master stereo buffer (L, R)
    const masterL = new Float32Array(totalSamples);
    const masterR = new Float32Array(totalSamples);

    // Track active voiceover intervals across the video for dynamic ducking
    const voiceIntervals: Array<{ startSample: number; endSample: number }> = [];

    // Calculate scene start sample offsets
    let accumulatedSamples = 0;
    const sceneSampleStarts: number[] = [];
    for (let sIdx = 0; sIdx < manifest.scenes.length; sIdx++) {
      sceneSampleStarts.push(accumulatedSamples);
      const scene = manifest.scenes[sIdx];
      const sceneFrames = Math.max(1, Math.round(scene.duration_seconds * fps));
      const sceneSamples = Math.round((sceneFrames / fps) * sampleRate);
      accumulatedSamples += sceneSamples;
    }

    // -------------------------------------------------------------
    // LAYER 1: VOICEOVER (Actual Edge-TTS Decoded Speech)
    // -------------------------------------------------------------
    if (onProgress) onProgress({ status: 'Đang phối ghép giọng đọc AI Layer 1...', percent: 15 });

    for (let sIdx = 0; sIdx < manifest.scenes.length; sIdx++) {
      const vBuf = voiceBuffers.get(sIdx);
      const startSample = sceneSampleStarts[sIdx];

      if (vBuf && vBuf.length > 0) {
        const vLen = Math.min(vBuf.length, totalSamples - startSample);
        const vChan0 = vBuf.getChannelData(0);
        const vChan1 = vBuf.numberOfChannels > 1 ? vBuf.getChannelData(1) : vChan0;

        for (let i = 0; i < vLen; i++) {
          const targetIdx = startSample + i;
          if (targetIdx < totalSamples) {
            masterL[targetIdx] += vChan0[i] * 1.0;
            masterR[targetIdx] += vChan1[i] * 1.0;
          }
        }

        voiceIntervals.push({
          startSample: startSample,
          endSample: Math.min(totalSamples, startSample + vLen)
        });
      }
    }

    // -------------------------------------------------------------
    // LAYER 2: BACKGROUND MUSIC (Genre & Theme Synthesized BGM)
    // -------------------------------------------------------------
    if (onProgress) onProgress({ status: 'Đang hòa âm nhạc nền điện ảnh Layer 2...', percent: 45 });

    const genre = manifest.genre || manifest.topic_category || 'general';
    this.synthesizeBGM(masterL, masterR, totalSamples, sampleRate, genre, voiceIntervals);

    // -------------------------------------------------------------
    // LAYER 3: CONTEXTUAL SOUND EFFECTS (SFX)
    // -------------------------------------------------------------
    if (onProgress) onProgress({ status: 'Đang khởi tạo hiệu ứng âm thanh ngữ cảnh Layer 3...', percent: 75 });

    for (let sIdx = 0; sIdx < manifest.scenes.length; sIdx++) {
      const scene = manifest.scenes[sIdx];
      const sceneStartSample = sceneSampleStarts[sIdx];
      const sfxList = scene.sound_effects || scene.sound_design || [];

      for (const cue of sfxList) {
        const cueStartSample = sceneStartSample + Math.round((cue.start_time_offset_ms || 0) * (sampleRate / 1000));
        this.synthesizeSFX(masterL, masterR, totalSamples, sampleRate, cue.sfx_type, cueStartSample, cue.volume || 0.35);
      }
    }

    // -------------------------------------------------------------
    // MASTERING & DYNAMIC LIMITING
    // -------------------------------------------------------------
    if (onProgress) onProgress({ status: 'Đang hoàn thiện âm thanh đa kênh (Mastering)...', percent: 95 });

    const interleaved = new Float32Array(totalSamples * 2);
    for (let i = 0; i < totalSamples; i++) {
      // Soft-clipping limiter (tanh) to prevent digital distortion
      interleaved[i * 2] = Math.tanh(masterL[i] * 0.95);
      interleaved[i * 2 + 1] = Math.tanh(masterR[i] * 0.95);
    }

    return interleaved;
  }

  /**
   * Synthesizes thematic background music with dynamic ducking during speech
   */
  private static synthesizeBGM(
    outL: Float32Array,
    outR: Float32Array,
    totalSamples: number,
    sampleRate: number,
    genre: string,
    voiceIntervals: Array<{ startSample: number; endSample: number }>
  ) {
    const isHistorical = genre.includes('historical') || genre.includes('history');
    const isEconomics = genre.includes('economics') || genre.includes('finance');
    const isScience = genre.includes('science') || genre.includes('space');
    const isTech = genre.includes('tech');

    // Chords root frequencies
    // Historical / Heroic: D minor (146.8Hz) -> Bb (116.5Hz) -> F (174.6Hz) -> C (130.8Hz)
    // Economics / Tech: A minor (110Hz) -> F (87.3Hz) -> C (130.8Hz) -> G (98Hz)
    const chordRoots = isHistorical
      ? [146.8, 116.5, 174.6, 130.8]
      : isEconomics
      ? [110.0, 87.3, 130.8, 98.0]
      : isScience
      ? [130.8, 98.0, 164.8, 110.0]
      : [130.8, 98.0, 110.0, 87.3];

    const chordDurationSec = 4.0;
    const fadeSamples = Math.round(0.15 * sampleRate); // 150ms ducking fade

    for (let i = 0; i < totalSamples; i++) {
      const t = i / sampleRate;

      // 1. Calculate Dynamic Ducking Gain
      let duckGain = 1.0;
      for (const interval of voiceIntervals) {
        if (i >= interval.startSample - fadeSamples && i <= interval.endSample + fadeSamples) {
          if (i < interval.startSample) {
            // Fade out
            const progress = (i - (interval.startSample - fadeSamples)) / fadeSamples;
            duckGain = 1.0 - progress * 0.85; // Duck to 0.15 (-17dB)
          } else if (i > interval.endSample) {
            // Fade in
            const progress = (i - interval.endSample) / fadeSamples;
            duckGain = 0.15 + progress * 0.85;
          } else {
            // Fully ducked during narration
            duckGain = 0.15;
          }
          break;
        }
      }

      // 2. Synthesize Musical Harmony
      const chordIdx = Math.floor(t / chordDurationSec) % chordRoots.length;
      const rootFreq = chordRoots[chordIdx];

      // Bass drone & warmth
      const bass = Math.sin(2 * Math.PI * rootFreq * t) * 0.14;
      const fifth = Math.sin(2 * Math.PI * (rootFreq * 1.5) * t) * 0.08;
      const octave = Math.sin(2 * Math.PI * (rootFreq * 2.0) * t) * 0.05;

      let rhythm = 0;
      if (isHistorical) {
        // Martial March Cadence: 112 BPM snare & timpani pulse
        const beatT = (t * (112 / 60)) % 1.0;
        if (beatT < 0.1) {
          rhythm = Math.sin(2 * Math.PI * 65 * t) * 0.16; // Timpani thud
        }
      } else if (isEconomics || isTech) {
        // Modern 124 BPM Electronic Clock Tick & Pad
        const beatT = (t * (124 / 60)) % 1.0;
        if (beatT < 0.06) {
          rhythm = Math.sin(2 * Math.PI * 880 * t) * 0.06; // Clock tick
        }
      }

      const sampleL = (bass + fifth + rhythm) * duckGain * 0.55;
      const sampleR = (bass + octave + rhythm) * duckGain * 0.55;

      outL[i] += sampleL;
      outR[i] += sampleR;
    }
  }

  /**
   * Synthesizes contextual sound effects (SFX) using Web Audio mathematical DSP
   */
  private static synthesizeSFX(
    outL: Float32Array,
    outR: Float32Array,
    totalSamples: number,
    sampleRate: number,
    sfxType: string,
    startSample: number,
    volume: number
  ) {
    if (startSample >= totalSamples) return;

    if (sfxType === 'whoosh') {
      // Sweeping wind whoosh (350ms duration)
      const durSamples = Math.round(0.35 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const envelope = Math.sin(t * Math.PI); // Smooth bell envelope
        // Sweeping noise frequency
        const freq = 250 + Math.sin(t * Math.PI) * 1800;
        const noise = (Math.random() * 2 - 1) * Math.sin(2 * Math.PI * freq * (i / sampleRate));
        const sample = noise * envelope * volume * 0.6;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    } else if (sfxType === 'impact' || sfxType === 'cannon') {
      // Heavy impact / cannon punch (500ms duration)
      const durSamples = Math.round(0.55 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const envelope = Math.exp(-t * 8); // Rapid decay
        // Exponential pitch drop from 180Hz down to 45Hz
        const currentFreq = 45 + 135 * Math.exp(-t * 12);
        const boom = Math.sin(2 * Math.PI * currentFreq * (i / sampleRate));
        const crack = (Math.random() * 2 - 1) * Math.exp(-t * 25) * 0.3; // Initial transient crack
        const sample = (boom + crack) * envelope * volume * 0.85;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    } else if (sfxType === 'coin' || sfxType === 'mechanical') {
      // Crisp metallic chime / click (400ms duration)
      const durSamples = Math.round(0.4 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const envelope = Math.exp(-t * 10);
        // Dual resonant bell frequencies
        const ring1 = Math.sin(2 * Math.PI * 2093 * (i / sampleRate));
        const ring2 = Math.sin(2 * Math.PI * 2637 * (i / sampleRate));
        const sample = (ring1 * 0.6 + ring2 * 0.4) * envelope * volume * 0.4;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    } else if (sfxType === 'cheer') {
      // Crowd cheer frequency swell (1.2s duration)
      const durSamples = Math.round(1.2 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const envelope = Math.sin(t * Math.PI);
        // Layered formant vocal noises
        const formant1 = Math.sin(2 * Math.PI * 450 * (i / sampleRate));
        const formant2 = Math.sin(2 * Math.PI * 850 * (i / sampleRate));
        const crowdNoise = (Math.random() * 2 - 1) * 0.5;
        const sample = (formant1 + formant2 + crowdNoise) * envelope * volume * 0.45;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    } else {
      // Default: Ambient whoosh / atmospheric rise (400ms)
      const durSamples = Math.round(0.4 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const envelope = Math.sin(t * Math.PI);
        const sample = (Math.random() * 2 - 1) * envelope * volume * 0.25;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    }
  }
}
