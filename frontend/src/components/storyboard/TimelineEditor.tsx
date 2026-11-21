import React, { useState, useRef, useEffect } from 'react';
import type { SceneManifest, SceneItem } from '../../types/database';
import { apiClient } from '../../services/apiClient';
import {
  Play, Pause, Plus, Trash2, Volume2, Mic, Music, Sparkles,
  ChevronLeft, ChevronRight, ZoomIn, ZoomOut,
  Film, Search, X
} from 'lucide-react';

interface TimelineEditorProps {
  manifest: SceneManifest;
  onChange: (updatedManifest: SceneManifest) => void;
  activeSceneIndex: number;
  onSelectScene: (index: number) => void;
  currentTimeSec?: number;
  onSeekTime?: (timeSec: number) => void;
}

const VISUAL_METHODS = [
  { id: 'toon', label: 'Hoạt Họa 2.5D (Articulated Rig & Parallax)', icon: '🎨' },
  { id: 'map', label: 'Bản Đồ Vector & Tuyến Hành Quân', icon: '🗺️' },
  { id: 'infographic', label: 'Infographic Số Liệu & Biểu Đồ Động', icon: '📊' },
  { id: 'archival', label: 'Tư Liệu Trực Quan Lịch Sử', icon: '🏛️' },
  { id: 'photo', label: 'Ảnh Minh Họa', icon: '📷' },
  { id: 'stock', label: 'Thước Phim (Stock Footage)', icon: '🎬' },
];

const SOUNDSCAPE_PRESETS = [
  { id: 'horror_creepy', label: '👻 Kinh dị / Chuyện ma (Gió hú, tiếng bước chân kẽo kẹt, cửa hé, tiếng tim)' },
  { id: 'crime_noir', label: '🕵️ Trinh thám / Phá án (Mưa đêm, máy chữ lạch cạch, chớp máy ảnh)' },
  { id: 'comedy_cartoon', label: '🎭 Hoạt họa / Hài hước (Lò xo boing, còi trượt, bong bóng nổ)' },
  { id: 'epic_action', label: '⚡ Hành động / Trailer (Va đập chấn động, whoosh nhanh, dồn dập)' },
  { id: 'lofi_chill', label: '🌸 Lofi / Thư giãn (Đĩa than tí tách, chuông gió, mưa nhẹ)' },
  { id: 'ancient_dynasty', label: '🏛️ Cổ trang / Cung đình (Đàn tranh, chuông đồng, bước chân ngự đạo)' },
  { id: 'tropical_forest', label: '🌲 Rừng nhiệt đới (Ve sầu, gió tán lá, chim hót, bước chân lá)' },
  { id: 'mountain_battlefield', label: '⚔️ Chiến trường đèo núi (Gió hú, rền đại bác, bước chân bùn)' },
  { id: 'financial_floor', label: '📈 Thị trường tài chính (Chuông vàng, văn phòng giao dịch)' },
  { id: 'cyber_tech_lab', label: '💻 Phòng công nghệ (Server hum, data stream whoosh)' },
  { id: 'cyberpunk_neon', label: '🌃 Thành thị tương lai (Mưa neon, còi xe bay, tiếng synth ngầm)' },
  { id: 'deep_space', label: '🚀 Vũ trụ / Thiên văn (Sub-bass, cosmic wash)' },
  { id: 'green_wind_farm', label: '🍃 Đồng cỏ sinh thái (Gió turbine, thiên nhiên xanh)' },
  { id: 'ocean_voyage', label: '🌊 Biển khơi / Hải trình (Sóng vỗ mạn thuyền, hải âu xa xăm)' },
];

export const TimelineEditor: React.FC<TimelineEditorProps> = ({
  manifest,
  onChange,
  activeSceneIndex,
  onSelectScene,
  currentTimeSec = 0,
  onSeekTime
}) => {
  const [zoomScale, setZoomScale] = useState(24); // pixels per second
  const [presets, setPresets] = useState<{ id: string; label: string }[]>(SOUNDSCAPE_PRESETS);
  const [sfxModalSceneIndex, setSfxModalSceneIndex] = useState<number | null>(null);
  const [sfxQuery, setSfxQuery] = useState('');
  const [sfxCategory, setSfxCategory] = useState('');
  const [sfxResults, setSfxResults] = useState<any[]>([]);
  const [isSearchingSFX, setIsSearchingSFX] = useState(false);
  const [playingAudioId, setPlayingAudioId] = useState<string | null>(null);
  const [isAutoEnriching, setIsAutoEnriching] = useState(false);

  const timelineContainerRef = useRef<HTMLDivElement>(null);
  const audioPreviewRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    apiClient.fetchSoundscapePresets().then(res => {
      if (res && res.length > 0) {
        setPresets(res.map((p: any) => ({
          id: p.id,
          label: p.name || p.label
        })));
      }
    }).catch(err => console.warn('Could not load remote soundscapes:', err));
  }, []);

  const totalDuration = manifest.scenes.reduce((acc, s) => acc + s.duration_seconds, 0) || 10;
  const totalWidth = Math.max(800, Math.round(totalDuration * zoomScale));

  // Compute start offsets for each scene
  let runningSec = 0;
  const sceneOffsets = manifest.scenes.map(s => {
    const start = runningSec;
    runningSec += s.duration_seconds;
    return { start, duration: s.duration_seconds, end: runningSec };
  });

  const handleUpdateScene = (index: number, updates: Partial<SceneItem>) => {
    const updatedScenes = [...manifest.scenes];
    updatedScenes[index] = { ...updatedScenes[index], ...updates };

    const newTotalDuration = updatedScenes.reduce((acc, s) => acc + s.duration_seconds, 0);
    const fps = manifest.video_specs?.fps || 30;

    // Recalculate frame bounds
    let currFrame = 0;
    const finalScenes = updatedScenes.map(sc => {
      const fCount = Math.round(sc.duration_seconds * fps);
      const res = { ...sc, start_frame: currFrame, end_frame: currFrame + fCount };
      currFrame += fCount;
      return res;
    });

    onChange({
      ...manifest,
      total_duration_sec: Math.round(newTotalDuration * 100) / 100,
      total_frames: currFrame,
      scenes: finalScenes,
    });
  };

  const handleAdjustDuration = (index: number, delta: number) => {
    const current = manifest.scenes[index].duration_seconds;
    const nextDur = Math.max(2.0, Math.min(60.0, Math.round((current + delta) * 10) / 10));
    handleUpdateScene(index, { duration_seconds: nextDur });
  };

  const handleMoveScene = (index: number, direction: 'left' | 'right') => {
    const newIdx = direction === 'left' ? index - 1 : index + 1;
    if (newIdx < 0 || newIdx >= manifest.scenes.length) return;

    const scenes = [...manifest.scenes];
    const temp = scenes[index];
    scenes[index] = scenes[newIdx];
    scenes[newIdx] = temp;

    // Re-index scene_order
    const reordered = scenes.map((s, i) => ({ ...s, scene_order: i + 1 }));
    onChange({
      ...manifest,
      scenes: reordered,
    });
    onSelectScene(newIdx);
  };

  const handleAddSceneAt = (index: number) => {
    const newScene: SceneItem = {
      scene_order: index + 2,
      scene_type: 'body',
      narration_text: 'Nội dung tiếp theo của cảnh mới...',
      duration_seconds: 4.5,
      start_frame: 0,
      end_frame: 135,
      visual_method: 'toon',
      visual_config: {},
      subtitles_json: [],
      assets: [],
    };

    const scenes = [...manifest.scenes];
    scenes.splice(index + 1, 0, newScene);
    const reordered = scenes.map((s, i) => ({ ...s, scene_order: i + 1 }));

    const totalDur = reordered.reduce((a, s) => a + s.duration_seconds, 0);
    onChange({
      ...manifest,
      total_duration_sec: totalDur,
      total_frames: Math.round(totalDur * 30),
      scenes: reordered,
    });
    onSelectScene(index + 1);
  };

  const handleDeleteScene = (index: number) => {
    if (manifest.scenes.length <= 1) return;
    const scenes = manifest.scenes.filter((_, i) => i !== index).map((s, i) => ({ ...s, scene_order: i + 1 }));
    const totalDur = scenes.reduce((a, s) => a + s.duration_seconds, 0);
    onChange({
      ...manifest,
      total_duration_sec: totalDur,
      total_frames: Math.round(totalDur * 30),
      scenes,
    });
    onSelectScene(Math.max(0, index - 1));
  };

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!timelineContainerRef.current) return;
    const rect = timelineContainerRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left + timelineContainerRef.current.scrollLeft - 100; // 100px is track header width
    if (clickX < 0) return;

    const clickedSec = Math.max(0, Math.min(totalDuration, clickX / zoomScale));
    onSeekTime?.(clickedSec);

    // Find and select scene at click
    let accum = 0;
    for (let i = 0; i < manifest.scenes.length; i++) {
      accum += manifest.scenes[i].duration_seconds;
      if (clickedSec <= accum) {
        onSelectScene(i);
        break;
      }
    }
  };

  const handlePlayAudio = (url: string, id: string) => {
    if (playingAudioId === id && audioPreviewRef.current) {
      audioPreviewRef.current.pause();
      setPlayingAudioId(null);
      return;
    }

    if (audioPreviewRef.current) {
      audioPreviewRef.current.pause();
    }

    const audio = new Audio(url);
    audioPreviewRef.current = audio;
    setPlayingAudioId(id);
    audio.play().catch(e => console.warn('Audio play failed:', e));
    audio.onended = () => setPlayingAudioId(null);
  };

  const handleSearchSFX = async (q: string, cat?: string) => {
    setIsSearchingSFX(true);
    try {
      const results = await apiClient.searchSFX(q, cat || undefined);
      setSfxResults(results);
    } catch (e) {
      console.warn('SFX search failed:', e);
    } finally {
      setIsSearchingSFX(false);
    }
  };

  const handleAddSFX = (sfx: any) => {
    if (sfxModalSceneIndex === null) return;
    const scene = manifest.scenes[sfxModalSceneIndex];
    const existing = (scene as any).sound_design || [];
    const newCue = {
      sfx_id: sfx.id,
      sfx_type: sfx.action_type || sfx.category || 'sfx',
      description: sfx.name,
      start_time_offset_ms: 300,
      volume: sfx.volume || 0.6,
      duck_narration: false,
    };
    handleUpdateScene(sfxModalSceneIndex, {
      sound_design: [...existing, newCue]
    } as any);
    setSfxModalSceneIndex(null);
  };

  const handleRemoveSFX = (sceneIdx: number, sfxIdx: number) => {
    const scene = manifest.scenes[sceneIdx];
    const existing = (scene as any).sound_design || [];
    const updated = existing.filter((_: any, i: number) => i !== sfxIdx);
    handleUpdateScene(sceneIdx, { sound_design: updated } as any);
  };

  const handleAutoEnrich = async () => {
    setIsAutoEnriching(true);
    try {
      const enriched = await apiClient.autoEnrichSoundscape(manifest);
      onChange(enriched);
    } catch (e) {
      console.warn('Auto enrich soundscape failed:', e);
    } finally {
      setIsAutoEnriching(false);
    }
  };

  const activeScene = manifest.scenes[activeSceneIndex] || manifest.scenes[0];
  const activeOffset = sceneOffsets[activeSceneIndex] || { start: 0, duration: 5, end: 5 };

  // Generate ruler tick marks
  const tickStep = zoomScale > 35 ? 1 : zoomScale > 15 ? 5 : 10;
  const rulerTicks: number[] = [];
  for (let s = 0; s <= totalDuration + tickStep; s += tickStep) {
    rulerTicks.push(s);
  }

  return (
    <div className="flex flex-col gap-3 bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-2xl">
      {/* Timeline Header Controls */}
      <div className="flex items-center justify-between border-b border-studio-border/60 pb-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-studio-primary/20 border border-studio-primary/40 flex items-center justify-center text-studio-primary font-bold text-sm">
            NLE
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              Timeline Chuyên Nghiệp (DaVinci / CapCut Multi-Track)
              <span className="text-[10px] bg-studio-accent/20 text-studio-accent px-2 py-0.5 rounded-full font-mono">
                {manifest.scenes.length} Clips • {Math.round(totalDuration)}s
              </span>
            </h3>
            <p className="text-[11px] text-gray-400">
              Điều chỉnh mốc thời gian, hoán đổi cảnh, thêm hiệu ứng SFX & nhạc nền trực quan
            </p>
          </div>
        </div>

        {/* Zoom & Quick Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleAutoEnrich}
            disabled={isAutoEnriching}
            className="flex items-center gap-1.5 text-xs font-semibold bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 text-white px-3 py-1.5 rounded-lg transition shadow"
            title="AI tự động phân tích kịch bản và gán nhạc nền & sound effects chân thực cho từng cảnh"
          >
            <Music className="w-3.5 h-3.5" />
            <span>{isAutoEnriching ? 'Đang phối âm...' : 'AI Phối Âm & SFX'}</span>
          </button>

          <div className="flex items-center bg-studio-bg border border-studio-border rounded-lg p-0.5">
            <button
              onClick={() => setZoomScale(prev => Math.max(12, prev - 6))}
              className="p-1.5 text-gray-400 hover:text-white rounded transition"
              title="Thu nhỏ timeline"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-[10px] font-mono text-gray-300 px-2">
              {Math.round((zoomScale / 24) * 100)}%
            </span>
            <button
              onClick={() => setZoomScale(prev => Math.min(60, prev + 6))}
              className="p-1.5 text-gray-400 hover:text-white rounded transition"
              title="Phóng to timeline"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>

          <button
            onClick={() => handleAddSceneAt(manifest.scenes.length - 1)}
            className="flex items-center gap-1 text-xs font-semibold bg-studio-primary hover:bg-indigo-600 text-white px-2.5 py-1.5 rounded-lg transition shadow"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Thêm Cảnh</span>
          </button>
        </div>
      </div>

      {/* Interactive Multi-Track Timeline Canvas */}
      <div
        ref={timelineContainerRef}
        onClick={handleTimelineClick}
        className="w-full overflow-x-auto bg-[#0a0f1d] border border-studio-border/80 rounded-xl relative select-none scrollbar-thin scrollbar-thumb-studio-border"
        style={{ minHeight: '260px' }}
      >
        <div style={{ width: `${totalWidth + 120}px` }} className="relative flex flex-col py-1">
          {/* 1. Timecode Ruler */}
          <div className="h-7 border-b border-gray-800 flex items-center relative pl-[100px] bg-studio-card/40">
            {rulerTicks.map(t => (
              <div
                key={t}
                className="absolute top-0 bottom-0 flex flex-col justify-end"
                style={{ left: `${100 + t * zoomScale}px` }}
              >
                <span className="text-[9px] font-mono text-gray-500 -ml-2 mb-1">
                  {Math.floor(t / 60)}:{(t % 60).toString().padStart(2, '0')}s
                </span>
                <div className="w-[1px] h-2 bg-gray-700" />
              </div>
            ))}
          </div>

          {/* Scrubbing Playhead Red Needle */}
          <div
            className="absolute top-0 bottom-0 w-[2px] bg-red-500 z-30 pointer-events-none transition-all duration-75 shadow-[0_0_8px_rgba(239,68,68,0.8)]"
            style={{ left: `${100 + currentTimeSec * zoomScale}px` }}
          >
            <div className="w-3 h-3 bg-red-500 rounded-b -ml-[5px] flex items-center justify-center shadow">
              <div className="w-1 h-1 bg-white rounded-full" />
            </div>
          </div>

          {/* 2. Track V1: Video & Animation Grammars */}
          <div className="flex items-center min-h-[58px] border-b border-gray-800/80 relative">
            <div className="w-[100px] flex-shrink-0 px-2 py-1 flex items-center gap-1.5 text-xs font-bold text-sky-400 bg-[#0d1527] h-full border-r border-gray-800 sticky left-0 z-20">
              <Film className="w-3.5 h-3.5 text-sky-400" />
              <span>V1 Video</span>
            </div>

            <div className="relative flex items-center h-full flex-1">
              {manifest.scenes.map((scene, idx) => {
                const offset = sceneOffsets[idx];
                const widthPx = Math.max(50, offset.duration * zoomScale);
                const isSelected = idx === activeSceneIndex;
                const methodObj = VISUAL_METHODS.find(m => m.id === scene.visual_method) || VISUAL_METHODS[0];

                return (
                  <div
                    key={idx}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectScene(idx);
                      onSeekTime?.(offset.start);
                    }}
                    style={{
                      position: 'absolute',
                      left: `${offset.start * zoomScale}px`,
                      width: `${widthPx - 2}px`,
                    }}
                    className={`h-[50px] rounded-lg p-1.5 flex flex-col justify-between cursor-pointer transition border ${
                      isSelected
                        ? 'bg-sky-950/80 border-sky-400 ring-2 ring-sky-500/50 shadow-lg z-10'
                        : 'bg-sky-950/30 border-sky-800/50 hover:border-sky-600 hover:bg-sky-950/50'
                    }`}
                  >
                    <div className="flex items-center justify-between text-[11px] font-bold text-white truncate">
                      <span className="flex items-center gap-1 truncate">
                        <span>{methodObj.icon}</span>
                        <span className="truncate">Cảnh {idx + 1}: {scene.scene_type}</span>
                      </span>
                      <span className="text-[10px] font-mono text-sky-300 ml-1 flex-shrink-0">
                        {scene.duration_seconds.toFixed(1)}s
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-gray-400">
                      <span className="truncate max-w-[120px] italic">
                        {scene.narration_text.slice(0, 20)}...
                      </span>
                      <div className="flex items-center gap-0.5 opacity-80 hover:opacity-100" onClick={e => e.stopPropagation()}>
                        <button
                          onClick={() => handleAdjustDuration(idx, -0.5)}
                          className="px-1 bg-black/40 hover:bg-black text-[9px] rounded"
                          title="Giảm 0.5s"
                        >
                          -
                        </button>
                        <button
                          onClick={() => handleAdjustDuration(idx, 0.5)}
                          className="px-1 bg-black/40 hover:bg-black text-[9px] rounded"
                          title="Tăng 0.5s"
                        >
                          +
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 3. Track T1: Subtitles & Captions */}
          <div className="flex items-center min-h-[42px] border-b border-gray-800/80 relative">
            <div className="w-[100px] flex-shrink-0 px-2 py-1 flex items-center gap-1.5 text-xs font-bold text-amber-400 bg-[#121722] h-full border-r border-gray-800 sticky left-0 z-20">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>T1 Phụ đề</span>
            </div>

            <div className="relative flex items-center h-full flex-1">
              {manifest.scenes.map((scene, idx) => {
                const offset = sceneOffsets[idx];
                const widthPx = Math.max(50, offset.duration * zoomScale);
                const hasSubs = scene.subtitles_json && scene.subtitles_json.length > 0;

                return (
                  <div
                    key={idx}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectScene(idx);
                    }}
                    style={{
                      position: 'absolute',
                      left: `${offset.start * zoomScale}px`,
                      width: `${widthPx - 2}px`,
                    }}
                    className="h-[34px] rounded-md bg-amber-950/20 border border-amber-800/40 px-2 py-1 flex items-center justify-between cursor-pointer hover:bg-amber-950/40"
                  >
                    <span className="text-[10px] text-amber-300 font-mono truncate flex items-center gap-1">
                      <span>💬</span>
                      <span className="truncate">
                        {scene.narration_text.slice(0, 24)}...
                      </span>
                    </span>
                    <span className="text-[9px] text-amber-400/80 font-mono flex-shrink-0">
                      {hasSubs ? `${scene.subtitles_json?.length} từ` : 'Auto-Sync'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 4. Track A1: Voiceover Track (Speech Audio) */}
          <div className="flex items-center min-h-[46px] border-b border-gray-800/80 relative">
            <div className="w-[100px] flex-shrink-0 px-2 py-1 flex items-center gap-1.5 text-xs font-bold text-emerald-400 bg-[#0e191b] h-full border-r border-gray-800 sticky left-0 z-20">
              <Mic className="w-3.5 h-3.5 text-emerald-400" />
              <span>A1 Giọng đọc</span>
            </div>

            <div className="relative flex items-center h-full flex-1">
              {manifest.scenes.map((scene, idx) => {
                const offset = sceneOffsets[idx];
                const widthPx = Math.max(50, offset.duration * zoomScale);
                const audioUrl = scene.audio_url || (scene.audio_id ? `/api/v1/tts/audio/${scene.audio_id}.mp3` : '');
                const isPlaying = playingAudioId === `voice_${idx}`;

                return (
                  <div
                    key={idx}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectScene(idx);
                    }}
                    style={{
                      position: 'absolute',
                      left: `${offset.start * zoomScale}px`,
                      width: `${widthPx - 2}px`,
                    }}
                    className="h-[38px] rounded-md bg-emerald-950/30 border border-emerald-800/40 px-2 py-1 flex items-center justify-between cursor-pointer hover:bg-emerald-950/50"
                  >
                    <div className="flex items-center gap-1.5 truncate">
                      {audioUrl && (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePlayAudio(audioUrl, `voice_${idx}`);
                          }}
                          className="w-5 h-5 rounded-full bg-emerald-500/20 hover:bg-emerald-500/40 text-emerald-300 flex items-center justify-center flex-shrink-0"
                          title="Nghe thử lời đọc cảnh này"
                        >
                          {isPlaying ? <Pause className="w-2.5 h-2.5" /> : <Play className="w-2.5 h-2.5 fill-current" />}
                        </button>
                      )}
                      <span className="text-[10px] text-emerald-300 font-mono truncate">
                        {manifest.voice_config?.voice?.includes('HoaiMy') ? 'Hoài My' : 'Nam Minh'}
                      </span>
                    </div>

                    <div className="flex items-center gap-1 text-[9px] text-emerald-400/80 font-mono">
                      <span>48kHz</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 5. Track A2: Action SFX Track */}
          <div className="flex items-center min-h-[46px] border-b border-gray-800/80 relative">
            <div className="w-[100px] flex-shrink-0 px-2 py-1 flex items-center gap-1.5 text-xs font-bold text-purple-400 bg-[#161226] h-full border-r border-gray-800 sticky left-0 z-20">
              <Volume2 className="w-3.5 h-3.5 text-purple-400" />
              <span>A2 SFX</span>
            </div>

            <div className="relative flex items-center h-full flex-1">
              {manifest.scenes.map((scene, idx) => {
                const offset = sceneOffsets[idx];
                const widthPx = Math.max(50, offset.duration * zoomScale);
                const sfxList = (scene as any).sound_design || [];

                return (
                  <div
                    key={idx}
                    style={{
                      position: 'absolute',
                      left: `${offset.start * zoomScale}px`,
                      width: `${widthPx - 2}px`,
                    }}
                    className="h-[38px] rounded-md bg-purple-950/20 border border-purple-900/40 px-1.5 py-0.5 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-1 overflow-hidden">
                      {sfxList.map((sfx: any, sIdx: number) => (
                        <span
                          key={sIdx}
                          className="px-1.5 py-0.5 rounded bg-purple-600/30 border border-purple-500/40 text-[9px] text-purple-200 font-medium truncate flex items-center gap-1"
                          title={`${sfx.description || sfx.sfx_type} (${sfx.start_time_offset_ms || 0}ms)`}
                        >
                          <span>⚡</span>
                          <span className="truncate max-w-[60px]">{sfx.description || sfx.sfx_type}</span>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRemoveSFX(idx, sIdx);
                            }}
                            className="text-purple-400 hover:text-red-400 ml-0.5"
                          >
                            ×
                          </button>
                        </span>
                      ))}

                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSfxModalSceneIndex(idx);
                          handleSearchSFX('');
                        }}
                        className="px-1.5 py-0.5 rounded bg-purple-500/10 hover:bg-purple-500/30 text-purple-300 text-[9px] border border-purple-500/20 flex items-center gap-0.5 transition"
                        title="Thêm sound effect vào cảnh này"
                      >
                        <Plus className="w-2.5 h-2.5" /> SFX
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 6. Track A3: BGM & Soundscape Bed */}
          <div className="flex items-center min-h-[44px] relative">
            <div className="w-[100px] flex-shrink-0 px-2 py-1 flex items-center gap-1.5 text-xs font-bold text-indigo-400 bg-[#11122a] h-full border-r border-gray-800 sticky left-0 z-20">
              <Music className="w-3.5 h-3.5 text-indigo-400" />
              <span>A3 BGM</span>
            </div>

            <div className="relative flex items-center h-full flex-1">
              {manifest.scenes.map((scene, idx) => {
                const offset = sceneOffsets[idx];
                const widthPx = Math.max(50, offset.duration * zoomScale);
                const theme = scene.music_direction || 'epic_heroic';

                return (
                  <div
                    key={idx}
                    style={{
                      position: 'absolute',
                      left: `${offset.start * zoomScale}px`,
                      width: `${widthPx - 2}px`,
                    }}
                    className="h-[36px] rounded-md bg-indigo-950/20 border border-indigo-900/40 px-2 py-1 flex items-center justify-between"
                  >
                    <span className="text-[10px] text-indigo-300 font-mono truncate flex items-center gap-1">
                      <span>🎵</span>
                      <span className="truncate">{theme}</span>
                    </span>
                    <span className="text-[9px] text-indigo-400/70 font-mono">
                      -17dB Duck
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Clip Property Inspector & Editing Strip */}
      {activeScene && (
        <div className="bg-studio-bg border border-studio-border rounded-xl p-3.5 flex flex-col gap-3">
          <div className="flex items-center justify-between border-b border-studio-border/50 pb-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-md bg-studio-primary/20 text-studio-primary border border-studio-primary/40 flex items-center justify-center text-xs font-bold">
                {activeSceneIndex + 1}
              </span>
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Chi Tiết Cảnh {activeSceneIndex + 1}: {activeScene.scene_type}
              </span>
              <span className="text-xs text-gray-400 font-mono">
                ({activeOffset.start.toFixed(1)}s → {activeOffset.end.toFixed(1)}s • {activeScene.duration_seconds.toFixed(1)}s)
              </span>
            </div>

            <div className="flex items-center gap-1.5">
              <button
                disabled={activeSceneIndex === 0}
                onClick={() => handleMoveScene(activeSceneIndex, 'left')}
                className="p-1.5 bg-studio-card hover:bg-studio-border text-gray-300 disabled:opacity-30 rounded-lg transition"
                title="Đổi chỗ cảnh này sang trái"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <button
                disabled={activeSceneIndex === manifest.scenes.length - 1}
                onClick={() => handleMoveScene(activeSceneIndex, 'right')}
                className="p-1.5 bg-studio-card hover:bg-studio-border text-gray-300 disabled:opacity-30 rounded-lg transition"
                title="Đổi chỗ cảnh này sang phải"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
              <button
                disabled={manifest.scenes.length <= 1}
                onClick={() => handleDeleteScene(activeSceneIndex)}
                className="p-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 disabled:opacity-30 rounded-lg transition"
                title="Xóa cảnh này"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Quick Inspector Fields: Narration, Visual Modality & Soundscape */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* 1. Narration Text */}
            <div className="md:col-span-2 flex flex-col gap-1.5">
              <label className="text-[11px] font-semibold text-gray-400 flex items-center justify-between">
                <span>Lời thuyết minh (Narration Script):</span>
                <span className="text-[10px] font-mono text-emerald-400">
                  {activeScene.narration_text.split(' ').filter(Boolean).length} từ
                </span>
              </label>
              <textarea
                rows={2}
                value={activeScene.narration_text}
                onChange={(e) => handleUpdateScene(activeSceneIndex, { narration_text: e.target.value })}
                className="w-full bg-[#0a0f1d] border border-studio-border rounded-lg p-2 text-xs text-gray-200 focus:outline-none focus:border-studio-primary transition resize-none leading-relaxed"
                placeholder="Nhập lời đọc tiếng Việt cho cảnh này..."
              />
            </div>

            {/* 2. Visual Method Selector */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[11px] font-semibold text-gray-400">Phong cách hình ảnh bằng Code:</label>
              <select
                value={activeScene.visual_method || 'toon'}
                onChange={(e) => handleUpdateScene(activeSceneIndex, { visual_method: e.target.value as any })}
                className="w-full bg-[#0a0f1d] border border-studio-border rounded-lg px-2.5 py-2 text-xs text-sky-300 focus:outline-none focus:border-studio-primary font-medium"
              >
                {VISUAL_METHODS.map(m => (
                  <option key={m.id} value={m.id}>
                    {m.icon} {m.label}
                  </option>
                ))}
              </select>

              {/* Soundscape Preset */}
              <label className="text-[11px] font-semibold text-gray-400 mt-1">Không gian âm thanh (Soundscape):</label>
              <select
                value={activeScene.music_direction || 'tropical_forest'}
                onChange={(e) => handleUpdateScene(activeSceneIndex, { music_direction: e.target.value })}
                className="w-full bg-[#0a0f1d] border border-studio-border rounded-lg px-2.5 py-1.5 text-xs text-indigo-300 focus:outline-none focus:border-studio-primary font-medium"
              >
                {presets.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* SFX Search & Add Modal */}
      {sfxModalSceneIndex !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-studio-surface border border-studio-border rounded-2xl max-w-lg w-full p-5 shadow-2xl flex flex-col gap-3 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-studio-border pb-2.5">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Volume2 className="w-4 h-4 text-purple-400" />
                Kho Hiệu Ứng Âm Thanh Thực Tế (SFX Library)
              </h3>
              <button
                onClick={() => setSfxModalSceneIndex(null)}
                className="text-gray-400 hover:text-white p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Search Input */}
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-gray-400" />
                <input
                  type="text"
                  value={sfxQuery}
                  onChange={(e) => setSfxQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearchSFX(sfxQuery, sfxCategory)}
                  placeholder="Tìm kiếm: whoosh, đại bác, bước chân, sấm, chuông, ma..."
                  className="w-full bg-studio-bg border border-studio-border rounded-lg pl-9 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-studio-primary"
                />
              </div>
              <button
                onClick={() => handleSearchSFX(sfxQuery, sfxCategory)}
                disabled={isSearchingSFX}
                className="px-3 py-1.5 bg-studio-primary hover:bg-indigo-600 text-white text-xs font-semibold rounded-lg transition"
              >
                Tìm
              </button>
            </div>

            {/* Quick Categories */}
            <div className="flex flex-wrap gap-1.5 text-[10px]">
              {['horror', 'transition', 'crime', 'historical', 'weather', 'comedy'].map(cat => (
                <button
                  key={cat}
                  onClick={() => {
                    setSfxCategory(cat);
                    handleSearchSFX(sfxQuery, cat);
                  }}
                  className={`px-2 py-1 rounded-md border transition ${
                    sfxCategory === cat
                      ? 'bg-purple-600 border-purple-500 text-white'
                      : 'bg-studio-bg border-studio-border text-gray-400 hover:text-white'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* SFX List */}
            <div className="flex flex-col gap-2 mt-1 max-h-[300px] overflow-y-auto">
              {sfxResults.map(sfx => (
                <div
                  key={sfx.id}
                  className="bg-studio-bg border border-studio-border rounded-xl p-2.5 flex items-center justify-between hover:border-purple-500/50 transition"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-base">{sfx.category === 'horror' ? '👻' : sfx.category === 'transition' ? '⚡' : '🎵'}</span>
                    <div>
                      <div className="text-xs font-bold text-white">{sfx.name}</div>
                      <div className="text-[10px] text-gray-400">
                        {sfx.category} • {((sfx.duration_ms || 1000) / 1000).toFixed(1)}s
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => {
                        const url = apiClient.getSFXAudioUrl(sfx.id);
                        handlePlayAudio(url, sfx.id);
                      }}
                      className="px-2 py-1 bg-studio-card hover:bg-studio-border text-gray-200 text-xs rounded transition flex items-center gap-1"
                    >
                      {playingAudioId === sfx.id ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3 fill-current" />}
                      <span>Thử</span>
                    </button>
                    <button
                      onClick={() => handleAddSFX(sfx)}
                      className="px-2.5 py-1 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded transition flex items-center gap-1"
                    >
                      <Plus className="w-3 h-3" />
                      <span>Thêm</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
