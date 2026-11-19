import type { SceneManifest } from '../types/database';

export interface AudioMixProgress {
  status: string;
  percent: number;
}

export class SoundDesignEngine {
  private static readonly SAMPLE_RATE = 48000;

  /**
   * Generates a 3-layer environmental audio production:
   * Layer 1: Voiceover (Actual Edge-TTS Decoded Speech) - MANDATORY
   * Layer 2: Environmental Soundscape (Nature/Forest, Insects, Birds, Wind, Rain, City)
   * Layer 3: Action-to-Sound SFX (Footsteps on surfaces, foliage rustle, impacts, whooshes)
   * Dedicated Bus: Thematic Background Music (BGM) with -17dB Dynamic Ducking during speech.
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

    // -------------------------------------------------------------
    // 0. MANDATORY NARRATION VALIDATION
    // -------------------------------------------------------------
    let requiredNarrationScenes = 0;
    let loadedVoiceScenes = 0;

    for (let sIdx = 0; sIdx < manifest.scenes.length; sIdx++) {
      const scene = manifest.scenes[sIdx];
      if (scene.narration_text && scene.narration_text.trim().length > 8) {
        requiredNarrationScenes++;
        const buf = voiceBuffers.get(sIdx);
        if (buf && buf.length > 0) {
          loadedVoiceScenes++;
        }
      }
    }

    if (requiredNarrationScenes > 0 && loadedVoiceScenes === 0) {
      throw new Error(
        'LỖI SẢN XUẤT ÂM THANH: Toàn bộ video thiếu giọng đọc tiếng Việt thực tế. ' +
        'Hệ thống yêu cầu phải có giọng đọc AI được tổng hợp thành công trước khi kết xuất video.'
      );
    }

    // Allocate master stereo buses
    const voiceL = new Float32Array(totalSamples);
    const voiceR = new Float32Array(totalSamples);
    const ambientL = new Float32Array(totalSamples);
    const ambientR = new Float32Array(totalSamples);
    const sfxL = new Float32Array(totalSamples);
    const sfxR = new Float32Array(totalSamples);
    const bgmL = new Float32Array(totalSamples);
    const bgmR = new Float32Array(totalSamples);

    // Track active voice intervals for dynamic ducking
    const voiceIntervals: Array<{ startSample: number; endSample: number }> = [];

    // Calculate scene start sample offsets
    let accumulatedSamples = 0;
    const sceneSampleStarts: number[] = [];
    const sceneSampleLengths: number[] = [];
    for (let sIdx = 0; sIdx < manifest.scenes.length; sIdx++) {
      sceneSampleStarts.push(accumulatedSamples);
      const scene = manifest.scenes[sIdx];
      const sceneFrames = Math.max(1, Math.round(scene.duration_seconds * fps));
      const sceneSamples = Math.round((sceneFrames / fps) * sampleRate);
      sceneSampleLengths.push(sceneSamples);
      accumulatedSamples += sceneSamples;
    }

    // -------------------------------------------------------------
    // LAYER 1: VOICEOVER (Actual Edge-TTS Decoded Speech)
    // -------------------------------------------------------------
    if (onProgress) onProgress({ status: 'Đang hòa âm giọng đọc AI tiếng Việt (Layer 1: Voiceover)...', percent: 20 });

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
            voiceL[targetIdx] += vChan0[i] * 1.05;
            voiceR[targetIdx] += vChan1[i] * 1.05;
          }
        }

        voiceIntervals.push({
          startSample: startSample,
          endSample: Math.min(totalSamples, startSample + vLen)
        });
      }
    }

    // -------------------------------------------------------------
    // LAYER 2: ENVIRONMENTAL SOUNDSCAPE (Acoustic Ambience)
    // -------------------------------------------------------------
    if (onProgress) onProgress({ status: 'Đang khởi tạo không gian âm học môi trường (Layer 2: Environment)...', percent: 45 });

    for (let sIdx = 0; sIdx < manifest.scenes.length; sIdx++) {
      const scene = manifest.scenes[sIdx];
      const startSample = sceneSampleStarts[sIdx];
      const lenSamples = sceneSampleLengths[sIdx];
      const desc = ((scene.visual_description || '') + ' ' + (scene.narration_text || '')).toLowerCase();

      // Determine environmental soundscape type
      let envType = 'tropical_forest';
      if (desc.includes('điện biên') || desc.includes('pháo') || desc.includes('hào') || desc.includes('quân')) {
        envType = 'mountain_battlefield';
      } else if (desc.includes('lạm phát') || desc.includes('kinh tế') || desc.includes('tiền tệ') || desc.includes('thị trường')) {
        envType = 'financial_floor';
      } else if (desc.includes('ai') || desc.includes('trí tuệ') || desc.includes('nơ-ron') || desc.includes('chip') || desc.includes('công nghệ')) {
        envType = 'cyber_tech_lab';
      } else if (desc.includes('vũ trụ') || desc.includes('mặt trời') || desc.includes('hành tinh') || desc.includes('sao')) {
        envType = 'deep_space';
      } else if (desc.includes('gió') || desc.includes('năng lượng') || desc.includes('khí hậu')) {
        envType = 'green_wind_farm';
      }

      this.synthesizeEnvironmentalSoundscape(ambientL, ambientR, startSample, lenSamples, totalSamples, sampleRate, envType);
    }

    // -------------------------------------------------------------
    // LAYER 3: ACTION-TO-SOUND SFX (Footsteps & Synchronized Events)
    // -------------------------------------------------------------
    if (onProgress) onProgress({ status: 'Đang đồng bộ âm thanh hành động & bước chân (Layer 3: Action SFX)...', percent: 65 });

    for (let sIdx = 0; sIdx < manifest.scenes.length; sIdx++) {
      const scene = manifest.scenes[sIdx];
      const sceneStartSample = sceneSampleStarts[sIdx];
      const sceneDurSec = scene.duration_seconds;
      const desc = ((scene.visual_description || '') + ' ' + (scene.narration_text || '')).toLowerCase();

      // Synchronize character footsteps with walking cycle (2.2Hz step frequency)
      const isWalking = !desc.includes('infographic') && !desc.includes('biểu đồ') && (desc.includes('đi') || desc.includes('bước') || desc.includes('hành quân') || desc.includes('rừng') || true);
      if (isWalking) {
        const stepIntervalSamples = Math.round(sampleRate * 0.45); // ~450ms per step
        const sceneTotalSamples = Math.round(sceneDurSec * sampleRate);
        const sfxType = desc.includes('rừng') || desc.includes('lá') ? 'footsteps_leaves' : 'footsteps_soil';

        for (let stepOffset = Math.round(sampleRate * 0.3); stepOffset < sceneTotalSamples - sampleRate * 0.4; stepOffset += stepIntervalSamples) {
          this.synthesizeSFX(sfxL, sfxR, totalSamples, sampleRate, sfxType, sceneStartSample + stepOffset, 0.42);
        }
      }

      // Contextual sound effects from scene directives
      const sfxList = scene.sound_effects || scene.sound_design || [];
      for (const cue of sfxList) {
        const cueStartSample = sceneStartSample + Math.round((cue.start_time_offset_ms || 0) * (sampleRate / 1000));
        this.synthesizeSFX(sfxL, sfxR, totalSamples, sampleRate, cue.sfx_type, cueStartSample, cue.volume || 0.40);
      }
    }

    // -------------------------------------------------------------
    // DEDICATED BUS: THEMATIC BACKGROUND MUSIC (BGM) WITH DUCKING
    // -------------------------------------------------------------
    if (onProgress) onProgress({ status: 'Đang phối khí nhạc nền điện ảnh & Dynamic Ducking (-17dB)...', percent: 85 });

    const genre = manifest.genre || manifest.topic_category || 'general';
    this.synthesizeBGM(bgmL, bgmR, totalSamples, sampleRate, genre, voiceIntervals);

    // -------------------------------------------------------------
    // FINAL MIXING & SOFT-CLIPPING LIMITER
    // -------------------------------------------------------------
    if (onProgress) onProgress({ status: 'Đang hoàn thiện âm thanh đa kênh (Mastering 48kHz Stereo)...', percent: 95 });

    const interleaved = new Float32Array(totalSamples * 2);
    const fadeSamples = Math.round(0.15 * sampleRate);

    for (let i = 0; i < totalSamples; i++) {
      // Dynamic Ducking envelope on background environment
      let duckGain = 1.0;
      for (const interval of voiceIntervals) {
        if (i >= interval.startSample - fadeSamples && i <= interval.endSample + fadeSamples) {
          if (i < interval.startSample) {
            const p = (i - (interval.startSample - fadeSamples)) / fadeSamples;
            duckGain = 1.0 - p * 0.55; // Ambient ducks by 55% during voice
          } else if (i > interval.endSample) {
            const p = (i - interval.endSample) / fadeSamples;
            duckGain = 0.45 + p * 0.55;
          } else {
            duckGain = 0.45;
          }
          break;
        }
      }

      // Mix 4 Audio Buses:
      // Voice (1.0) + Environmental Ambience (ducked) + Action SFX (crisp) + Music Bus (already ducked -17dB)
      const mixedL = voiceL[i] + (ambientL[i] * duckGain) + sfxL[i] + bgmL[i];
      const mixedR = voiceR[i] + (ambientR[i] * duckGain) + sfxR[i] + bgmR[i];

      // Soft-clipping limiter (tanh) prevents digital overs while preserving dynamic warmth
      interleaved[i * 2] = Math.tanh(mixedL * 0.95);
      interleaved[i * 2 + 1] = Math.tanh(mixedR * 0.95);
    }

    return interleaved;
  }

  /**
   * Layer 2: Synthesizes rich environmental acoustic soundscapes based on scene context
   */
  private static synthesizeEnvironmentalSoundscape(
    outL: Float32Array,
    outR: Float32Array,
    startSample: number,
    lenSamples: number,
    totalSamples: number,
    sampleRate: number,
    envType: string
  ) {
    const endSample = Math.min(totalSamples, startSample + lenSamples);

    if (envType === 'tropical_forest') {
      // Dense Tropical Forest: High-frequency cicadas/insects + gentle canopy wind + intermittent bird calls
      for (let i = startSample; i < endSample; i++) {
        const t = (i - startSample) / sampleRate;

        // 1. Cicadas & Crickets: 5400Hz frequency with 9Hz amplitude modulation
        const insectLfo = 0.5 + 0.5 * Math.sin(2 * Math.PI * 9.2 * t);
        const cicadaWave = Math.sin(2 * Math.PI * 5400 * t) + 0.4 * Math.sin(2 * Math.PI * 6200 * t);
        const cicada = cicadaWave * insectLfo * 0.045;

        // 2. Canopy Wind: Low-frequency filtered pink noise modulated by 0.18Hz wave
        const windLfo = 0.6 + 0.4 * Math.sin(2 * Math.PI * 0.18 * t);
        const windNoise = (Math.sin(2 * Math.PI * 340 * t) + 0.5 * Math.sin(2 * Math.PI * 520 * t)) * windLfo * 0.035;

        // 3. Intermittent Distant Birds (Chirping burst every 2.8s)
        let birdChirp = 0;
        const birdCycle = t % 2.8;
        if (birdCycle < 0.22) {
          const birdT = birdCycle / 0.22;
          const birdFreq = 2600 + Math.sin(birdT * Math.PI) * 1100;
          birdChirp = Math.sin(2 * Math.PI * birdFreq * t) * Math.sin(birdT * Math.PI) * 0.04;
        }

        const ambL = cicada + windNoise + birdChirp;
        const ambR = cicada * 0.9 + windNoise * 1.1 + birdChirp * 0.85;

        outL[i] += ambL;
        outR[i] += ambR;
      }
    } else if (envType === 'mountain_battlefield') {
      // Mountain Battlefield: Heavy trench wind + sub-bass distant rumble
      for (let i = startSample; i < endSample; i++) {
        const t = (i - startSample) / sampleRate;
        const gustLfo = 0.5 + 0.5 * Math.sin(2 * Math.PI * 0.12 * t);
        const valleyWind = Math.sin(2 * Math.PI * 180 * t) * gustLfo * 0.06;
        const trenchRumble = Math.sin(2 * Math.PI * 55 * t) * 0.04;

        outL[i] += valleyWind + trenchRumble;
        outR[i] += valleyWind * 1.05 + trenchRumble * 0.95;
      }
    } else if (envType === 'financial_floor' || envType === 'cyber_tech_lab') {
      // Tech Lab / Office: Subtle clean server room tone (60Hz + 120Hz harmonics)
      for (let i = startSample; i < endSample; i++) {
        const t = (i - startSample) / sampleRate;
        const serverHum = (Math.sin(2 * Math.PI * 60 * t) * 0.03 + Math.sin(2 * Math.PI * 120 * t) * 0.015);
        outL[i] += serverHum;
        outR[i] += serverHum;
      }
    } else if (envType === 'deep_space') {
      // Cosmic Sub-bass: 48Hz resonant ethereal wash
      for (let i = startSample; i < endSample; i++) {
        const t = (i - startSample) / sampleRate;
        const cosmic = Math.sin(2 * Math.PI * 48 * t) * 0.05 + Math.sin(2 * Math.PI * 96 * t) * 0.02;
        outL[i] += cosmic;
        outR[i] += cosmic;
      }
    } else {
      // Gentle Breeze
      for (let i = startSample; i < endSample; i++) {
        const t = (i - startSample) / sampleRate;
        const breeze = Math.sin(2 * Math.PI * 260 * t) * 0.03;
        outL[i] += breeze;
        outR[i] += breeze;
      }
    }
  }

  /**
   * Synthesizes thematic background music with -17dB dynamic ducking during speech
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
    const chordRoots = isHistorical
      ? [146.8, 116.5, 174.6, 130.8]  // D minor -> Bb -> F -> C
      : isEconomics
      ? [110.0, 87.3, 130.8, 98.0]    // A minor -> F -> C -> G
      : isScience
      ? [130.8, 98.0, 164.8, 110.0]   // C -> G -> E -> A
      : [130.8, 98.0, 110.0, 87.3];

    const chordDurationSec = 4.0;
    const fadeSamples = Math.round(0.15 * sampleRate); // 150ms crossfade

    for (let i = 0; i < totalSamples; i++) {
      const t = i / sampleRate;

      // 1. Dynamic Ducking (-17dB / 0.15 gain during active voice)
      let duckGain = 1.0;
      for (const interval of voiceIntervals) {
        if (i >= interval.startSample - fadeSamples && i <= interval.endSample + fadeSamples) {
          if (i < interval.startSample) {
            const p = (i - (interval.startSample - fadeSamples)) / fadeSamples;
            duckGain = 1.0 - p * 0.85;
          } else if (i > interval.endSample) {
            const p = (i - interval.endSample) / fadeSamples;
            duckGain = 0.15 + p * 0.85;
          } else {
            duckGain = 0.15;
          }
          break;
        }
      }

      // 2. Harmonic Musical Chords & Progression
      const chordIdx = Math.floor(t / chordDurationSec) % chordRoots.length;
      const rootFreq = chordRoots[chordIdx];

      const bass = Math.sin(2 * Math.PI * rootFreq * t) * 0.13;
      const fifth = Math.sin(2 * Math.PI * (rootFreq * 1.5) * t) * 0.07;
      const octave = Math.sin(2 * Math.PI * (rootFreq * 2.0) * t) * 0.05;

      let rhythm = 0;
      if (isHistorical) {
        // 112 BPM Timpani & Martial Drum Cadence
        const beatT = (t * (112 / 60)) % 1.0;
        if (beatT < 0.10) {
          rhythm = Math.sin(2 * Math.PI * 65 * t) * 0.14;
        }
      } else if (isEconomics || isTech) {
        // 124 BPM Precision Clock Pulse
        const beatT = (t * (124 / 60)) % 1.0;
        if (beatT < 0.05) {
          rhythm = Math.sin(2 * Math.PI * 880 * t) * 0.05;
        }
      }

      const sampleL = (bass + fifth + rhythm) * duckGain * 0.50;
      const sampleR = (bass + octave + rhythm) * duckGain * 0.50;

      outL[i] += sampleL;
      outR[i] += sampleR;
    }
  }

  /**
   * Layer 3: Synthesizes action SFX (footsteps, foliage rustle, whooshes, impacts, coins)
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
    if (startSample >= totalSamples || startSample < 0) return;

    if (sfxType === 'footsteps_leaves' || sfxType === 'footsteps') {
      // Character walking on dry leaves: 140ms crisp dry crunch with subtle low-frequency ground contact
      const durSamples = Math.round(0.14 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const envelope = Math.exp(-t * 9) * Math.sin(t * Math.PI);
        // Crunchy high-frequency dry leaf crackle (2800-4800Hz)
        const crackle = (Math.random() * 2 - 1) * Math.sin(2 * Math.PI * 3400 * (i / sampleRate));
        // Ground thud
        const thud = Math.sin(2 * Math.PI * 85 * (i / sampleRate)) * 0.35;
        const sample = (crackle * 0.65 + thud) * envelope * volume * 0.40;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    } else if (sfxType === 'footsteps_soil') {
      // Character walking on soil / gravel: 160ms deeper earthy step
      const durSamples = Math.round(0.16 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const envelope = Math.exp(-t * 8);
        const gravel = (Math.random() * 2 - 1) * 0.3;
        const thud = Math.sin(2 * Math.PI * 110 * (i / sampleRate)) * 0.6;
        const sample = (gravel + thud) * envelope * volume * 0.45;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    } else if (sfxType === 'foliage_rustle') {
      // Foliage and branch rustle: 600ms textured rustle
      const durSamples = Math.round(0.60 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const envelope = Math.sin(t * Math.PI);
        const rustle = (Math.random() * 2 - 1) * Math.sin(2 * Math.PI * 2200 * (i / sampleRate));
        const sample = rustle * envelope * volume * 0.30;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    } else if (sfxType === 'bird_chirp') {
      // Melodic bird chirp: 250ms chirping glide
      const durSamples = Math.round(0.25 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const freq = 2800 + Math.sin(t * Math.PI) * 900;
        const sample = Math.sin(2 * Math.PI * freq * (i / sampleRate)) * Math.sin(t * Math.PI) * volume * 0.35;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    } else if (sfxType === 'whoosh' || sfxType === 'whoosh_pan') {
      // Sweeping camera pan whoosh: 350ms duration
      const durSamples = Math.round(0.35 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const envelope = Math.sin(t * Math.PI);
        const freq = 280 + Math.sin(t * Math.PI) * 1600;
        const noise = (Math.random() * 2 - 1) * Math.sin(2 * Math.PI * freq * (i / sampleRate));
        const sample = noise * envelope * volume * 0.55;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    } else if (sfxType === 'cannon' || sfxType === 'impact') {
      // Cannon punch / heavy impact: 550ms duration
      const durSamples = Math.round(0.55 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const envelope = Math.exp(-t * 8);
        const currentFreq = 45 + 135 * Math.exp(-t * 12);
        const boom = Math.sin(2 * Math.PI * currentFreq * (i / sampleRate));
        const crack = (Math.random() * 2 - 1) * Math.exp(-t * 25) * 0.35;
        const sample = (boom + crack) * envelope * volume * 0.85;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    } else if (sfxType === 'coin' || sfxType === 'coin_chime') {
      // Crisp metallic chime: 400ms duration
      const durSamples = Math.round(0.4 * sampleRate);
      for (let i = 0; i < durSamples && startSample + i < totalSamples; i++) {
        const t = i / durSamples;
        const envelope = Math.exp(-t * 10);
        const ring1 = Math.sin(2 * Math.PI * 2093 * (i / sampleRate));
        const ring2 = Math.sin(2 * Math.PI * 2637 * (i / sampleRate));
        const sample = (ring1 * 0.6 + ring2 * 0.4) * envelope * volume * 0.45;
        outL[startSample + i] += sample;
        outR[startSample + i] += sample;
      }
    } else {
      // Default: Ambient whoosh / atmospheric rise
      const durSamples = Math.round(0.35 * sampleRate);
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
