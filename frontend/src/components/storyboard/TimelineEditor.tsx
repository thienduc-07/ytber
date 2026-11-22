import React, { useState, useRef, useEffect } from 'react';
import type { SceneManifest, SceneItem } from '../../types/database';
import { apiClient } from '../../services/apiClient';
import {
  Play, Pause, Plus, Trash2, Volume2, VolumeX, Mic, Music, Sparkles,
  ChevronLeft, ChevronRight, ZoomIn, ZoomOut,
  Film, Search, X, Scissors, Copy, Magnet, Lock, Unlock,
  MoveHorizontal, Clock
} from 'lucide-react';

interface TimelineEditorProps {
  manifest: SceneManifest;
  onChange: (updatedManifest: SceneManifest) => void;
  activeSceneIndex: number;
  onSelectScene: (index: number) => void;
  currentTimeSec?: number;
  onSeekTime?: (timeSec: number) => void;
}

export const VISUAL_METHODS = [
  { id: 'anatomy', label: '🫀 Giải Phẫu & Cơ Quan Nội Tạng (Anatomical Heart/Organs)', icon: '🫀' },
  { id: 'schematic', label: '🔬 Sơ Đồ Nguyên Lý Khoa Học (Technical Blueprint & Radar)', icon: '🔬' },
  { id: 'horror', label: '👻 Phim Ma & Kinh Dị (Haunted House, Fog & Moon)', icon: '👻' },
  { id: 'presenter', label: '👨‍⚕️ Người Thuyết Minh Chuyên Gia (Doctor/Presenter Lip-Sync)', icon: '👨‍⚕️' },
  { id: 'toon', label: '🎨 Hoạt Họa 2.5D (Articulated Rig & Parallax)', icon: '🎨' },
  { id: 'map', label: '🗺️ Bản Đồ Vector & Tuyến Hành Quân', icon: '🗺️' },
  { id: 'infographic', label: '📊 Infographic Số Liệu & Biểu Đồ Động', icon: '📊' },
  { id: 'archival', label: '🏛️ Tư Liệu Trực Quan Lịch Sử', icon: '🏛️' },
  { id: 'photo', label: '📷 Ảnh Minh Họa', icon: '📷' },
  { id: 'stock', label: '🎬 Thước Phim (Stock Footage)', icon: '🎬' },
];

export const CAMERA_DIRECTIONS = [
  { id: 'push_in', label: '🔍 Push-In (Zoom sâu vào chi tiết)' },
  { id: 'pull_out', label: '🔭 Pull-Out (Lùi góc nhìn toàn cảnh)' },
  { id: 'pan_left', label: '⬅️ Lia Cam Trái (Pan Left)' },
  { id: 'pan_right', label: '➡️ Lia Cam Phải (Pan Right)' },
  { id: 'slow_push_in', label: '✨ Slow Push (Tiến chậm điện ảnh)' },
  { id: 'static', label: '⏸️ Tĩnh (Góc quay cố định)' },
];

const SOUNDSCAPE_PRESETS = [
  { id: 'medical_heartbeat', label: '🫀 Y học / Tim mạch (Tiếng nhịp tim 72 BPM, monitor ECG beep, lưu huyết)' },
  { id: 'science_tech_lab', label: '🔬 Phòng thí nghiệm khoa học (Laser scan, máy tính lượng tử, server hum)' },
  { id: 'horror_creepy', label: '👻 Kinh dị / Chuyện ma (Gió hú, tiếng bước chân kẽo kẹt, cửa hé, tiếng tim)' },
  { id: 'crime_noir', label: '🕵️ Trinh thám / Phá án (Mưa đêm, máy chữ lạch cạch, chớp máy ảnh)' },
  { id: 'comedy_cartoon', label: '🎭 Hoạt họa / Hài hước (Lò xo boing, còi trượt, bong bóng nổ)' },
  { id: 'epic_action', label: '⚡ Hành động / Trailer (Va đập chấn động, whoosh nhanh, dồn dập)' },
  { id: 'lofi_chill', label: '🌸 Lofi / Thư giãn (Đĩa than tí tách, chuông gió, mưa nhẹ)' },
  { id: 'ancient_dynasty', label: '🏛️ Cổ trang / Cung đình (Đàn tranh, chuông đồng, bước chân ngự đạo)' },
  { id: 'tropical_forest', label: '🌲 Rừng nhiệt đới (Ve sầu, gió tán lá, chim hót, bước chân lá)' },
  { id: 'mountain_battlefield', label: '⚔️ Chiến trường đèo núi (Gió hú, rền đại bác, bước chân bùn)' },
  { id: 'financial_floor', label: '📈 Thị trường tài chính (Chuông vàng, văn phòng giao dịch)' },
  { id: 'cyberpunk_neon', label: '🌃 Thành thị tương lai (Mưa neon, còi xe bay, tiếng synth ngầm)' },
  { id: 'deep_space', label: '🚀 Vũ trụ / Thiên văn (Sub-bass, cosmic wash)' },
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
  // Zoom & Navigation
  const [zoomScale, setZoomScale] = useState(28); // pixels per second
  const [magneticSnap, setMagneticSnap] = useState(true);
  const [presets, setPresets] = useState<{ id: string; label: string }[]>(SOUNDSCAPE_PRESETS);

  // Track state (Mute / Lock)
  const [lockedTracks, setLockedTracks] = useState<{ [key: string]: boolean }>({});
  const [mutedTracks, setMutedTracks] = useState<{ [key: string]: boolean }>({});

  // Active Tool: 'select' (V) | 'razor' (B)
  const [activeTool, setActiveTool] = useState<'select' | 'razor'>('select');

  // Drag-and-drop scene reordering
  const [draggingSceneIdx, setDraggingSceneIdx] = useState<number | null>(null);
  const [dragOverSceneIdx, setDragOverSceneIdx] = useState<number | null>(null);

  // Playhead smooth dragging & scrubbing
  const [isScrubbingPlayhead, setIsScrubbingPlayhead] = useState(false);

  // Interactive Resizing / Trimming State
  const [isTrimming, setIsTrimming] = useState(false);
  const trimRef = useRef<{
    sceneIndex: number;
    edge: 'left' | 'right';
    startX: number;
    initialDur: number;
  } | null>(null);

  // Draggable SFX State
  const [isDraggingSFX, setIsDraggingSFX] = useState(false);
  const dragSFXRef = useRef<{
    sceneIndex: number;
    sfxIndex: number;
    startX: number;
    initialOffsetMs: number;
  } | null>(null);

  // SFX Modal Search
  const [sfxModalSceneIndex, setSfxModalSceneIndex] = useState<number | null>(null);
  const [sfxQuery, setSfxQuery] = useState('');
  const [sfxCategory, setSfxCategory] = useState('');
  const [sfxResults, setSfxResults] = useState<any[]>([]);
  const [isSearchingSFX, setIsSearchingSFX] = useState(false);

  // Audio Previews
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
  const totalWidth = Math.max(900, Math.round(totalDuration * zoomScale));

  // Compute start offsets for each scene
  let runningSec = 0;
  const sceneOffsets = manifest.scenes.map(s => {
    const start = runningSec;
    runningSec += s.duration_seconds;
    return { start, duration: s.duration_seconds, end: runningSec };
  });

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

  // 1. Interactive Mouse Trim Handler (DaVinci Drag Handle)
  const handleStartTrim = (e: React.MouseEvent, sceneIndex: number, edge: 'left' | 'right') => {
    e.stopPropagation();
    e.preventDefault();
    setIsTrimming(true);
    trimRef.current = {
      sceneIndex,
      edge,
      startX: e.clientX,
      initialDur: manifest.scenes[sceneIndex].duration_seconds
    };
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isTrimming && trimRef.current) {
        const { sceneIndex, edge, startX, initialDur } = trimRef.current;
        const deltaPx = e.clientX - startX;
        const deltaSec = deltaPx / zoomScale;

        let nextDur = initialDur;
        if (edge === 'right') {
          nextDur = Math.max(1.5, Math.min(60.0, Math.round((initialDur + deltaSec) * 10) / 10));
        } else {
          nextDur = Math.max(1.5, Math.min(60.0, Math.round((initialDur - deltaSec) * 10) / 10));
        }

        handleUpdateScene(sceneIndex, { duration_seconds: nextDur });
      }

      if (isDraggingSFX && dragSFXRef.current) {
        const { sceneIndex, sfxIndex, startX, initialOffsetMs } = dragSFXRef.current;
        const deltaPx = e.clientX - startX;
        const deltaMs = Math.round((deltaPx / zoomScale) * 1000);
        const sceneDurMs = manifest.scenes[sceneIndex].duration_seconds * 1000;

        const nextOffset = Math.max(0, Math.min(sceneDurMs - 200, initialOffsetMs + deltaMs));
        const scene = manifest.scenes[sceneIndex];
        const existing = [...((scene as any).sound_design || [])];
        if (existing[sfxIndex]) {
          existing[sfxIndex] = { ...existing[sfxIndex], start_time_offset_ms: nextOffset };
          handleUpdateScene(sceneIndex, { sound_design: existing } as any);
        }
      }
    };

    const handleMouseUp = () => {
      if (isTrimming) {
        setIsTrimming(false);
        trimRef.current = null;
      }
      if (isDraggingSFX) {
        setIsDraggingSFX(false);
        dragSFXRef.current = null;
      }
    };

    if (isTrimming || isDraggingSFX) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isTrimming, isDraggingSFX, zoomScale, manifest]);

  // Scene Reordering via Drag-and-Drop
  const handleDropReorder = (targetIdx: number) => {
    if (draggingSceneIdx === null || draggingSceneIdx === targetIdx) {
      setDraggingSceneIdx(null);
      setDragOverSceneIdx(null);
      return;
    }
    const newScenes = [...manifest.scenes];
    const [movedScene] = newScenes.splice(draggingSceneIdx, 1);
    newScenes.splice(targetIdx, 0, movedScene);

    const fps = manifest.video_specs?.fps || 30;
    let currentFrame = 0;
    const updatedScenes = newScenes.map((s, i) => {
      const frameCount = Math.round(s.duration_seconds * fps);
      const sc = {
        ...s,
        scene_order: i + 1,
        start_frame: currentFrame,
        end_frame: currentFrame + frameCount,
      };
      currentFrame += frameCount;
      return sc;
    });

    onChange({
      ...manifest,
      scenes: updatedScenes,
    });
    onSelectScene(targetIdx);
    setDraggingSceneIdx(null);
    setDragOverSceneIdx(null);
  };

  // Continuous Smooth Ruler & Playhead Scrubbing
  const updatePlayheadFromClientX = (clientX: number) => {
    if (!timelineContainerRef.current) return;
    const rect = timelineContainerRef.current.getBoundingClientRect();
    const scrollLeft = timelineContainerRef.current.scrollLeft;
    const clickX = clientX - rect.left + scrollLeft - 110;
    const clampedSec = Math.max(0, Math.min(totalDuration, clickX / zoomScale));
    onSeekTime?.(clampedSec);

    // Sync active scene
    for (let i = 0; i < sceneOffsets.length; i++) {
      if (clampedSec >= sceneOffsets[i].start && clampedSec < sceneOffsets[i].end) {
        onSelectScene(i);
        break;
      }
    }
  };

  const handleStartScrubbing = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsScrubbingPlayhead(true);
    updatePlayheadFromClientX(e.clientX);
  };

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      if (isScrubbingPlayhead) {
        updatePlayheadFromClientX(e.clientX);
      }
    };
    const onMouseUp = () => {
      if (isScrubbingPlayhead) {
        setIsScrubbingPlayhead(false);
      }
    };
    if (isScrubbingPlayhead) {
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, [isScrubbingPlayhead, totalDuration, zoomScale, sceneOffsets]);

  // 2. Razor / Split Tool (Cắt lát clip tại vị trí playhead)
  const handleSplitAtPlayhead = () => {
    if (currentTimeSec <= 0.2 || currentTimeSec >= totalDuration - 0.2) return;

    // Find which scene encompasses currentTimeSec
    let sceneIdx = -1;
    let sceneStart = 0;
    for (let i = 0; i < sceneOffsets.length; i++) {
      if (currentTimeSec >= sceneOffsets[i].start && currentTimeSec < sceneOffsets[i].end) {
        sceneIdx = i;
        sceneStart = sceneOffsets[i].start;
        break;
      }
    }

    if (sceneIdx === -1) return;

    const originalScene = manifest.scenes[sceneIdx];
    const cutOffsetSec = currentTimeSec - sceneStart;
    if (cutOffsetSec < 1.0 || (originalScene.duration_seconds - cutOffsetSec) < 1.0) {
      alert('Không thể cắt quá gần mép đầu hoặc mép cuối clip (tối thiểu 1.0 giây).');
      return;
    }

    // Split into Part A and Part B
    const partA_dur = Math.round(cutOffsetSec * 10) / 10;
    const partB_dur = Math.round((originalScene.duration_seconds - cutOffsetSec) * 10) / 10;

    const words = originalScene.narration_text.split(' ');
    const halfIdx = Math.floor(words.length / 2);
    const textA = words.slice(0, halfIdx).join(' ') || originalScene.narration_text;
    const textB = words.slice(halfIdx).join(' ') || originalScene.narration_text;

    const sceneA: SceneItem = {
      ...originalScene,
      narration_text: textA,
      duration_seconds: partA_dur,
    };

    const sceneB: SceneItem = {
      ...originalScene,
      scene_order: sceneIdx + 2,
      scene_id: `scene_${String(sceneIdx + 2).padStart(3, '0')}`,
      narration_text: textB,
      duration_seconds: partB_dur,
    };

    const newScenes = [...manifest.scenes];
    newScenes.splice(sceneIdx, 1, sceneA, sceneB);
    const reordered = newScenes.map((s, idx) => ({ ...s, scene_order: idx + 1 }));

    const fps = manifest.video_specs?.fps || 30;
    let curF = 0;
    const finalScenes = reordered.map(sc => {
      const fc = Math.round(sc.duration_seconds * fps);
      const res = { ...sc, start_frame: curF, end_frame: curF + fc };
      curF += fc;
      return res;
    });

    onChange({
      ...manifest,
      scenes: finalScenes,
    });
    onSelectScene(sceneIdx + 1);
  };

  // 3. Duplicate Scene
  const handleDuplicateScene = (index: number) => {
    const target = manifest.scenes[index];
    const cloned: SceneItem = {
      ...target,
      scene_id: `scene_${String(index + 2).padStart(3, '0')}`,
      scene_order: index + 2,
    };

    const newScenes = [...manifest.scenes];
    newScenes.splice(index + 1, 0, cloned);
    const reordered = newScenes.map((s, i) => ({ ...s, scene_order: i + 1 }));
    const totalDur = reordered.reduce((a, s) => a + s.duration_seconds, 0);

    onChange({
      ...manifest,
      total_duration_sec: totalDur,
      total_frames: Math.round(totalDur * 30),
      scenes: reordered,
    });
    onSelectScene(index + 1);
  };

  // 4. Delete Scene (Ripple Delete)
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
    const clickX = e.clientX - rect.left + timelineContainerRef.current.scrollLeft - 110; // 110px header width
    if (clickX < 0) return;

    let clickedSec = Math.max(0, Math.min(totalDuration, clickX / zoomScale));

    // Magnetic Snapping to closest clip boundary
    if (magneticSnap) {
      for (const off of sceneOffsets) {
        if (Math.abs(clickedSec - off.start) < 0.25) {
          clickedSec = off.start;
          break;
        }
        if (Math.abs(clickedSec - off.end) < 0.25) {
          clickedSec = off.end;
          break;
        }
      }
    }

    onSeekTime?.(clickedSec);

    // Select scene at click
    for (let i = 0; i < sceneOffsets.length; i++) {
      if (clickedSec >= sceneOffsets[i].start && clickedSec <= sceneOffsets[i].end) {
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

  // Ruler tick marks
  const tickStep = zoomScale > 35 ? 1 : zoomScale > 18 ? 2 : 5;
  const rulerTicks: number[] = [];
  for (let s = 0; s <= totalDuration + tickStep; s += tickStep) {
    rulerTicks.push(s);
  }

  return (
    <div className="flex flex-col gap-3 bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-2xl">
      {/* DaVinci / CapCut Top Control Header */}
      <div className="flex items-center justify-between border-b border-studio-border/60 pb-3 flex-wrap gap-2">
        <div className="flex items-center gap-3">
          {/* DaVinci Digital Timecode LCD */}
          <div className="flex items-center gap-2 bg-[#050811] border border-studio-border rounded-xl px-3 py-1.5 shadow-inner">
            <Clock className="w-4 h-4 text-emerald-400" />
            <span className="font-mono font-bold text-base text-emerald-400 tracking-wider">
              {formatTimecode(currentTimeSec)}
            </span>
            <span className="text-[10px] text-gray-500 font-mono">/ {formatTimecode(totalDuration)}</span>
          </div>

          {/* DaVinci Editing Toolstrip */}
          <div className="flex items-center bg-[#070b16] border border-studio-border rounded-xl p-0.5">
            <button
              onClick={() => setActiveTool('select')}
              className={`p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition ${
                activeTool === 'select' ? 'bg-studio-primary text-white shadow' : 'text-gray-400 hover:text-white'
              }`}
              title="Công cụ chọn (Select Tool - V)"
            >
              <MoveHorizontal className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Chọn</span>
            </button>
            <button
              onClick={handleSplitAtPlayhead}
              className="p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 text-gray-400 hover:text-amber-400 hover:bg-amber-500/10 transition"
              title="Cắt lát clip tại vị trí con trỏ (Razor Cut Tool - B)"
            >
              <Scissors className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Cắt Clip</span>
            </button>
            <button
              onClick={() => handleDuplicateScene(activeSceneIndex)}
              className="p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 text-gray-400 hover:text-sky-400 hover:bg-sky-500/10 transition"
              title="Nhân bản cảnh đang chọn (Duplicate - D)"
            >
              <Copy className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Nhân bản</span>
            </button>
            <button
              disabled={manifest.scenes.length <= 1}
              onClick={() => handleDeleteScene(activeSceneIndex)}
              className="p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 text-gray-400 hover:text-red-400 hover:bg-red-500/10 disabled:opacity-30 transition"
              title="Xóa cảnh đang chọn (Ripple Delete)"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Magnetic Snapping Toggle */}
          <button
            onClick={() => setMagneticSnap(!magneticSnap)}
            className={`p-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1 transition ${
              magneticSnap
                ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
                : 'bg-studio-bg border-studio-border text-gray-400 hover:text-white'
            }`}
            title={magneticSnap ? 'Nam châm từ tính: BẬT (Tự động hít vào mép clip)' : 'Nam châm từ tính: TẮT'}
          >
            <Magnet className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Từ tính</span>
          </button>
        </div>

        {/* Zoom & Quick Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleAutoEnrich}
            disabled={isAutoEnriching}
            className="flex items-center gap-1.5 text-xs font-semibold bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 text-white px-3 py-1.5 rounded-xl transition shadow"
            title="AI tự động phân tích kịch bản và gán nhạc nền & sound effects chân thực cho từng cảnh"
          >
            <Music className="w-3.5 h-3.5" />
            <span>{isAutoEnriching ? 'Đang phối âm...' : 'AI Phối Âm & SFX'}</span>
          </button>

          <div className="flex items-center bg-[#070b16] border border-studio-border rounded-xl p-0.5">
            <button
              onClick={() => setZoomScale(prev => Math.max(12, prev - 6))}
              className="p-1.5 text-gray-400 hover:text-white rounded-lg transition"
              title="Thu nhỏ timeline"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-[10px] font-mono text-gray-300 px-2">
              {Math.round((zoomScale / 28) * 100)}%
            </span>
            <button
              onClick={() => setZoomScale(prev => Math.min(80, prev + 6))}
              className="p-1.5 text-gray-400 hover:text-white rounded-lg transition"
              title="Phóng to timeline"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>

          <button
            onClick={() => {
              const newScene: SceneItem = {
                scene_order: manifest.scenes.length + 1,
                scene_type: 'body',
                narration_text: 'Nội dung tiếp theo của cảnh mới...',
                duration_seconds: 4.5,
                start_frame: 0,
                end_frame: 135,
                visual_method: 'anatomy',
                visual_config: {},
                subtitles_json: [],
                assets: [],
              };
              const newScenes = [...manifest.scenes, newScene];
              const totalDur = newScenes.reduce((a, s) => a + s.duration_seconds, 0);
              onChange({
                ...manifest,
                total_duration_sec: totalDur,
                total_frames: Math.round(totalDur * 30),
                scenes: newScenes,
              });
              onSelectScene(newScenes.length - 1);
            }}
            className="flex items-center gap-1 text-xs font-semibold bg-studio-primary hover:bg-indigo-600 text-white px-3 py-1.5 rounded-xl transition shadow"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Thêm Cảnh</span>
          </button>
        </div>
      </div>

      {/* Multi-Track Interactive Timeline Canvas */}
      <div
        ref={timelineContainerRef}
        onClick={handleTimelineClick}
        className="w-full overflow-x-auto bg-[#070b16] border border-studio-border/90 rounded-2xl relative select-none scrollbar-thin scrollbar-thumb-studio-border"
        style={{ minHeight: '300px' }}
      >
        <div style={{ width: `${totalWidth + 140}px` }} className="relative flex flex-col py-1">
          {/* 1. Timecode Ruler */}
          <div 
            onMouseDown={handleStartScrubbing}
            className="h-8 border-b border-gray-800 flex items-center relative pl-[110px] bg-[#0c1222]/80 cursor-ew-resize select-none"
            title="Kéo chuột trên thanh thước để tua nhanh video từng giây"
          >
            {rulerTicks.map(t => (
              <div
                key={t}
                className="absolute top-0 bottom-0 flex flex-col justify-end pointer-events-none"
                style={{ left: `${110 + t * zoomScale}px` }}
              >
                <span className="text-[9px] font-mono text-gray-500 -ml-2 mb-1">
                  {Math.floor(t / 60)}:{(t % 60).toString().padStart(2, '0')}s
                </span>
                <div className="w-[1px] h-2.5 bg-gray-700" />
              </div>
            ))}
          </div>

          {/* Scrubbing Playhead Red Needle (Draggable across timeline) */}
          <div
            onMouseDown={handleStartScrubbing}
            className="absolute top-0 bottom-0 w-[2px] bg-red-500 z-40 cursor-ew-resize shadow-[0_0_12px_rgba(239,68,68,1)]"
            style={{ left: `${110 + currentTimeSec * zoomScale}px` }}
          >
            <div 
              className="w-4 h-5 bg-red-500 hover:bg-red-400 rounded-b -ml-[7px] flex items-center justify-center shadow-xl cursor-grab active:cursor-grabbing transition"
              title={`Playhead: ${formatTimecode(currentTimeSec)} (Kéo để tua từng giây)`}
            >
              <div className="w-1.5 h-1.5 bg-white rounded-full pointer-events-none" />
            </div>
          </div>

          {/* 2. Track V1: Video & Animation Grammars */}
          <div className="flex items-center min-h-[64px] border-b border-gray-800/80 relative">
            <div className="w-[110px] flex-shrink-0 px-2 py-1 flex items-center justify-between text-xs font-bold text-sky-400 bg-[#0c1527] h-full border-r border-gray-800 sticky left-0 z-30">
              <div className="flex items-center gap-1.5">
                <Film className="w-3.5 h-3.5 text-sky-400" />
                <span>V1 Video</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setLockedTracks(prev => ({ ...prev, V1: !prev.V1 }));
                }}
                className="text-gray-500 hover:text-white"
              >
                {lockedTracks['V1'] ? <Lock className="w-3 h-3 text-amber-400" /> : <Unlock className="w-3 h-3" />}
              </button>
            </div>

            <div className="relative flex items-center h-full flex-1">
              {manifest.scenes.map((scene, idx) => {
                const offset = sceneOffsets[idx];
                const widthPx = Math.max(60, offset.duration * zoomScale);
                const isSelected = idx === activeSceneIndex;
                const isDragTarget = dragOverSceneIdx === idx && draggingSceneIdx !== idx;
                const isBeingDragged = draggingSceneIdx === idx;
                const methodObj = VISUAL_METHODS.find(m => m.id === scene.visual_method) || VISUAL_METHODS[0];

                return (
                  <div
                    key={idx}
                    draggable={!isTrimming}
                    onDragStart={(e) => {
                      e.dataTransfer.setData('text/plain', String(idx));
                      setDraggingSceneIdx(idx);
                    }}
                    onDragOver={(e) => {
                      e.preventDefault();
                      if (dragOverSceneIdx !== idx) setDragOverSceneIdx(idx);
                    }}
                    onDragLeave={() => {
                      if (dragOverSceneIdx === idx) setDragOverSceneIdx(null);
                    }}
                    onDrop={(e) => {
                      e.preventDefault();
                      handleDropReorder(idx);
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectScene(idx);
                      const rect = e.currentTarget.getBoundingClientRect();
                      const relX = Math.max(0, e.clientX - rect.left);
                      const inClipSec = relX / zoomScale;
                      const targetSec = Math.min(offset.end, Math.max(offset.start, offset.start + inClipSec));
                      onSeekTime?.(targetSec);
                    }}
                    style={{
                      position: 'absolute',
                      left: `${offset.start * zoomScale}px`,
                      width: `${widthPx - 2}px`,
                    }}
                    className={`h-[56px] rounded-xl p-2 flex flex-col justify-between cursor-pointer transition border relative group ${
                      isDragTarget
                        ? 'border-2 border-amber-400 bg-amber-950/80 ring-4 ring-amber-400/40 shadow-2xl scale-105 z-30'
                        : isBeingDragged
                        ? 'opacity-40 border-dashed border-gray-500'
                        : isSelected
                        ? 'bg-sky-950/90 border-sky-400 ring-2 ring-sky-500/50 shadow-xl z-20'
                        : 'bg-sky-950/40 border-sky-800/60 hover:border-sky-500 hover:bg-sky-950/60'
                    }`}
                    title="Kéo thả ngang để đổi thứ tự cảnh (Drag to Reorder scenes)"
                  >
                    {/* Left Trim Handle */}
                    <div
                      onMouseDown={(e) => handleStartTrim(e, idx, 'left')}
                      className="absolute left-0 top-0 bottom-0 w-2.5 bg-sky-500/0 hover:bg-sky-400/80 rounded-l-xl cursor-ew-resize transition flex items-center justify-center opacity-0 group-hover:opacity-100 z-30"
                      title="Kéo để chỉnh điểm bắt đầu clip (Trim In)"
                    >
                      <div className="w-[1.5px] h-4 bg-white/80" />
                    </div>

                    <div className="flex items-center justify-between text-[11px] font-bold text-white truncate pl-1">
                      <span className="flex items-center gap-1.5 truncate">
                        <span>{methodObj.icon}</span>
                        <span className="truncate">C{idx + 1}: {methodObj.label.split(' ')[1] || scene.scene_type}</span>
                      </span>
                      <span className="text-[10px] font-mono text-sky-300 ml-1 flex-shrink-0 bg-sky-900/60 px-1 rounded">
                        {scene.duration_seconds.toFixed(1)}s
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-gray-400 pl-1">
                      <span className="truncate max-w-[140px] italic">
                        {scene.narration_text.slice(0, 22)}...
                      </span>
                      <span className="text-[9px] font-mono text-gray-500">
                        {scene.camera_direction || 'push_in'}
                      </span>
                    </div>

                    {/* Right Trim Handle */}
                    <div
                      onMouseDown={(e) => handleStartTrim(e, idx, 'right')}
                      className="absolute right-0 top-0 bottom-0 w-2.5 bg-sky-500/0 hover:bg-sky-400/80 rounded-r-xl cursor-ew-resize transition flex items-center justify-center opacity-0 group-hover:opacity-100 z-30"
                      title="Kéo để chỉnh thời lượng clip (Trim Out)"
                    >
                      <div className="w-[1.5px] h-4 bg-white/80" />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 3. Track T1: Subtitles & Captions */}
          <div className="flex items-center min-h-[46px] border-b border-gray-800/80 relative">
            <div className="w-[110px] flex-shrink-0 px-2 py-1 flex items-center justify-between text-xs font-bold text-amber-400 bg-[#141824] h-full border-r border-gray-800 sticky left-0 z-30">
              <div className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>T1 Phụ đề</span>
              </div>
            </div>

            <div className="relative flex items-center h-full flex-1">
              {manifest.scenes.map((scene, idx) => {
                const offset = sceneOffsets[idx];
                const widthPx = Math.max(60, offset.duration * zoomScale);
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
                    className="h-[36px] rounded-lg bg-amber-950/30 border border-amber-800/50 px-2 py-1 flex items-center justify-between cursor-pointer hover:bg-amber-950/50 transition"
                  >
                    <span className="text-[10px] text-amber-300 font-mono truncate flex items-center gap-1">
                      <span>💬</span>
                      <span className="truncate">
                        {scene.narration_text.slice(0, 24)}...
                      </span>
                    </span>
                    <span className="text-[9px] text-amber-400/80 font-mono flex-shrink-0 bg-amber-900/40 px-1 rounded">
                      {hasSubs ? `${scene.subtitles_json?.length} từ (Khung cam)` : 'Auto-Sync'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 4. Track A1: Voiceover Track with Waveform Visualization */}
          <div className="flex items-center min-h-[52px] border-b border-gray-800/80 relative">
            <div className="w-[110px] flex-shrink-0 px-2 py-1 flex items-center justify-between text-xs font-bold text-emerald-400 bg-[#0d1c1c] h-full border-r border-gray-800 sticky left-0 z-30">
              <div className="flex items-center gap-1.5">
                <Mic className="w-3.5 h-3.5 text-emerald-400" />
                <span>A1 Lồng tiếng</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setMutedTracks(prev => ({ ...prev, A1: !prev.A1 }));
                }}
                className="text-gray-500 hover:text-white"
              >
                {mutedTracks['A1'] ? <VolumeX className="w-3 h-3 text-red-400" /> : <Volume2 className="w-3 h-3" />}
              </button>
            </div>

            <div className="relative flex items-center h-full flex-1">
              {manifest.scenes.map((scene, idx) => {
                const offset = sceneOffsets[idx];
                const widthPx = Math.max(60, offset.duration * zoomScale);
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
                    className="h-[44px] rounded-xl bg-emerald-950/40 border border-emerald-800/50 px-2 py-1 flex items-center justify-between cursor-pointer hover:bg-emerald-950/60 transition overflow-hidden relative"
                  >
                    {/* Simulated High-Fidelity Audio Waveform Path */}
                    <div className="absolute inset-0 opacity-25 flex items-center justify-around pointer-events-none px-2">
                      {Array.from({ length: Math.max(10, Math.floor(widthPx / 6)) }).map((_, barIdx) => {
                        const heightPercent = 20 + Math.sin(barIdx * 0.8) * 45 + ((barIdx % 3) * 15);
                        return (
                          <div
                            key={barIdx}
                            style={{ height: `${Math.max(15, Math.min(95, heightPercent))}%` }}
                            className="w-[2px] bg-emerald-400 rounded-full"
                          />
                        );
                      })}
                    </div>

                    <div className="flex items-center gap-1.5 truncate z-10">
                      {audioUrl && (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePlayAudio(audioUrl, `voice_${idx}`);
                          }}
                          className="w-5 h-5 rounded-full bg-emerald-500/20 hover:bg-emerald-500/50 text-emerald-300 flex items-center justify-center flex-shrink-0 transition"
                          title="Nghe thử giọng đọc cảnh này"
                        >
                          {isPlaying ? <Pause className="w-2.5 h-2.5" /> : <Play className="w-2.5 h-2.5 fill-current" />}
                        </button>
                      )}
                      <span className="text-[10px] text-emerald-300 font-mono font-bold truncate">
                        {manifest.voice_config?.voice?.includes('HoaiMy') ? 'Hoài My' : manifest.voice_config?.voice?.includes('NamGiap') ? 'Nam Giáp' : manifest.voice_config?.voice?.includes('MaiNgoc') ? 'Mai Ngọc' : 'Nam Minh'}
                      </span>
                    </div>

                    <div className="flex items-center gap-1 text-[9px] text-emerald-400/90 font-mono z-10 bg-emerald-950/80 px-1 rounded">
                      <span>48kHz AAC</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 5. Track A2: Action SFX Track with Draggable Sound Cues */}
          <div className="flex items-center min-h-[50px] border-b border-gray-800/80 relative">
            <div className="w-[110px] flex-shrink-0 px-2 py-1 flex items-center justify-between text-xs font-bold text-purple-400 bg-[#161228] h-full border-r border-gray-800 sticky left-0 z-30">
              <div className="flex items-center gap-1.5">
                <Volume2 className="w-3.5 h-3.5 text-purple-400" />
                <span>A2 SFX</span>
              </div>
            </div>

            <div className="relative flex items-center h-full flex-1">
              {manifest.scenes.map((scene, idx) => {
                const offset = sceneOffsets[idx];
                const widthPx = Math.max(60, offset.duration * zoomScale);
                const sfxList = (scene as any).sound_design || [];

                return (
                  <div
                    key={idx}
                    style={{
                      position: 'absolute',
                      left: `${offset.start * zoomScale}px`,
                      width: `${widthPx - 2}px`,
                    }}
                    className="h-[42px] rounded-xl bg-purple-950/25 border border-purple-900/40 px-1.5 py-0.5 flex items-center justify-between relative"
                  >
                    <div className="flex items-center gap-1.5 overflow-hidden w-full">
                      {sfxList.map((sfx: any, sIdx: number) => {
                        const cueOffsetSec = (sfx.start_time_offset_ms || 300) / 1000;
                        const cueLeftPx = Math.max(0, Math.min(widthPx - 70, cueOffsetSec * zoomScale));

                        return (
                          <div
                            key={sIdx}
                            onMouseDown={(e) => {
                              e.stopPropagation();
                              setIsDraggingSFX(true);
                              dragSFXRef.current = {
                                sceneIndex: idx,
                                sfxIndex: sIdx,
                                startX: e.clientX,
                                initialOffsetMs: sfx.start_time_offset_ms || 300,
                              };
                            }}
                            style={{
                              position: 'absolute',
                              left: `${cueLeftPx}px`,
                            }}
                            className="px-2 py-1 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 border border-purple-400 text-[9px] text-white font-bold truncate flex items-center gap-1 shadow cursor-grab active:cursor-grabbing z-20"
                            title={`Kéo chuột để chỉnh thời điểm phát (${sfx.start_time_offset_ms || 0}ms)`}
                          >
                            <span>⚡</span>
                            <span className="truncate max-w-[65px]">{sfx.description || sfx.sfx_type}</span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleRemoveSFX(idx, sIdx);
                              }}
                              className="text-purple-200 hover:text-red-300 ml-1 font-bold"
                            >
                              ×
                            </button>
                          </div>
                        );
                      })}

                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSfxModalSceneIndex(idx);
                          handleSearchSFX('');
                        }}
                        className="ml-auto px-2 py-1 rounded-lg bg-purple-500/20 hover:bg-purple-500/40 text-purple-300 text-[9px] font-bold border border-purple-500/30 flex items-center gap-0.5 transition"
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
          <div className="flex items-center min-h-[46px] relative">
            <div className="w-[110px] flex-shrink-0 px-2 py-1 flex items-center justify-between text-xs font-bold text-indigo-400 bg-[#12142d] h-full border-r border-gray-800 sticky left-0 z-30">
              <div className="flex items-center gap-1.5">
                <Music className="w-3.5 h-3.5 text-indigo-400" />
                <span>A3 BGM</span>
              </div>
            </div>

            <div className="relative flex items-center h-full flex-1">
              {manifest.scenes.map((scene, idx) => {
                const offset = sceneOffsets[idx];
                const widthPx = Math.max(60, offset.duration * zoomScale);
                const theme = scene.music_direction || 'epic_heroic';

                return (
                  <div
                    key={idx}
                    style={{
                      position: 'absolute',
                      left: `${offset.start * zoomScale}px`,
                      width: `${widthPx - 2}px`,
                    }}
                    className="h-[38px] rounded-xl bg-indigo-950/25 border border-indigo-900/40 px-2 py-1 flex items-center justify-between"
                  >
                    <span className="text-[10px] text-indigo-300 font-mono truncate flex items-center gap-1">
                      <span>🎵</span>
                      <span className="truncate">{theme}</span>
                    </span>
                    <span className="text-[9px] text-indigo-400/80 font-mono bg-indigo-900/40 px-1 rounded">
                      -17dB Duck
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* DaVinci Inspector Drawer Panel for Selected Clip */}
      {activeScene && (
        <div className="bg-[#070b16] border border-studio-border rounded-2xl p-4 flex flex-col gap-3.5 shadow-xl">
          <div className="flex items-center justify-between border-b border-studio-border/50 pb-2.5 flex-wrap gap-2">
            <div className="flex items-center gap-2.5">
              <span className="w-7 h-7 rounded-lg bg-sky-500/20 text-sky-400 border border-sky-500/40 flex items-center justify-center text-xs font-black">
                {activeSceneIndex + 1}
              </span>
              <div>
                <div className="text-xs font-bold text-white flex items-center gap-2">
                  <span>CLIP {activeSceneIndex + 1}: {activeScene.scene_type.toUpperCase()}</span>
                  <span className="text-[10px] bg-sky-500/20 text-sky-400 px-2 py-0.5 rounded-full font-mono">
                    {activeOffset.start.toFixed(1)}s → {activeOffset.end.toFixed(1)}s ({activeScene.duration_seconds.toFixed(1)}s)
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1.5">
              <button
                disabled={activeSceneIndex === 0}
                onClick={() => {
                  const scenes = [...manifest.scenes];
                  const temp = scenes[activeSceneIndex];
                  scenes[activeSceneIndex] = scenes[activeSceneIndex - 1];
                  scenes[activeSceneIndex - 1] = temp;
                  onChange({ ...manifest, scenes: scenes.map((s, i) => ({ ...s, scene_order: i + 1 })) });
                  onSelectScene(activeSceneIndex - 1);
                }}
                className="p-1.5 bg-studio-card hover:bg-studio-border text-gray-300 disabled:opacity-30 rounded-xl transition"
                title="Đổi chỗ cảnh này sang trái"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={activeSceneIndex === manifest.scenes.length - 1}
                onClick={() => {
                  const scenes = [...manifest.scenes];
                  const temp = scenes[activeSceneIndex];
                  scenes[activeSceneIndex] = scenes[activeSceneIndex + 1];
                  scenes[activeSceneIndex + 1] = temp;
                  onChange({ ...manifest, scenes: scenes.map((s, i) => ({ ...s, scene_order: i + 1 })) });
                  onSelectScene(activeSceneIndex + 1);
                }}
                className="p-1.5 bg-studio-card hover:bg-studio-border text-gray-300 disabled:opacity-30 rounded-xl transition"
                title="Đổi chỗ cảnh này sang phải"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick Inspector Form Grid */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-3.5">
            {/* 1. Narration Text (6 cols) */}
            <div className="md:col-span-6 flex flex-col gap-1.5">
              <label className="text-[11px] font-semibold text-gray-400 flex items-center justify-between">
                <span>Lời thoại kịch bản (Narration):</span>
                <span className="text-[10px] font-mono text-emerald-400">
                  {activeScene.narration_text.split(' ').filter(Boolean).length} từ (~{(activeScene.narration_text.split(' ').filter(Boolean).length / 3.5).toFixed(1)}s)
                </span>
              </label>
              <textarea
                rows={3}
                value={activeScene.narration_text}
                onChange={(e) => handleUpdateScene(activeSceneIndex, { narration_text: e.target.value })}
                className="w-full bg-[#050811] border border-studio-border rounded-xl p-2.5 text-xs text-gray-200 focus:outline-none focus:border-studio-primary transition resize-none leading-relaxed"
                placeholder="Nhập lời đọc tiếng Việt cho cảnh này..."
              />
            </div>

            {/* 2. Visual Method Selector (3 cols) */}
            <div className="md:col-span-3 flex flex-col gap-1.5">
              <label className="text-[11px] font-semibold text-gray-400">Phong cách hình ảnh Code:</label>
              <select
                value={activeScene.visual_method || 'anatomy'}
                onChange={(e) => handleUpdateScene(activeSceneIndex, { visual_method: e.target.value as any })}
                className="w-full bg-[#050811] border border-studio-border rounded-xl px-2.5 py-2 text-xs text-sky-300 focus:outline-none focus:border-studio-primary font-medium"
              >
                {VISUAL_METHODS.map(m => (
                  <option key={m.id} value={m.id}>
                    {m.icon} {m.label}
                  </option>
                ))}
              </select>

              <label className="text-[11px] font-semibold text-gray-400 mt-1">Chuyển động máy quay (Camera):</label>
              <select
                value={activeScene.camera_direction || 'push_in'}
                onChange={(e) => handleUpdateScene(activeSceneIndex, { camera_direction: e.target.value as any })}
                className="w-full bg-[#050811] border border-studio-border rounded-xl px-2.5 py-2 text-xs text-amber-300 focus:outline-none focus:border-studio-primary font-medium"
              >
                {CAMERA_DIRECTIONS.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>

            {/* 3. Soundscape & Duration Controls (3 cols) */}
            <div className="md:col-span-3 flex flex-col gap-1.5">
              <label className="text-[11px] font-semibold text-gray-400 flex items-center justify-between">
                <span>Thời lượng clip:</span>
                <span className="font-mono text-white text-xs">{activeScene.duration_seconds.toFixed(1)}s</span>
              </label>
              <input
                type="range"
                min="1.5"
                max="30.0"
                step="0.5"
                value={activeScene.duration_seconds}
                onChange={(e) => handleUpdateScene(activeSceneIndex, { duration_seconds: parseFloat(e.target.value) })}
                className="w-full accent-studio-primary cursor-pointer"
              />

              <label className="text-[11px] font-semibold text-gray-400 mt-1">Âm hưởng (Soundscape):</label>
              <select
                value={activeScene.music_direction || 'medical_heartbeat'}
                onChange={(e) => handleUpdateScene(activeSceneIndex, { music_direction: e.target.value })}
                className="w-full bg-[#050811] border border-studio-border rounded-xl px-2.5 py-1.5 text-xs text-indigo-300 focus:outline-none focus:border-studio-primary font-medium truncate"
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
          <div className="bg-studio-surface border border-studio-border rounded-2xl max-w-lg w-full p-5 shadow-2xl flex flex-col gap-3.5 max-h-[85vh] overflow-y-auto">
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
                  placeholder="Tìm kiếm: tim, nhịp tim, laser, bíp, whoosh, sấm..."
                  className="w-full bg-[#050811] border border-studio-border rounded-xl pl-9 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-studio-primary"
                />
              </div>
              <button
                onClick={() => handleSearchSFX(sfxQuery, sfxCategory)}
                disabled={isSearchingSFX}
                className="px-3.5 py-1.5 bg-studio-primary hover:bg-indigo-600 text-white text-xs font-semibold rounded-xl transition shadow"
              >
                Tìm
              </button>
            </div>

            {/* Quick Categories */}
            <div className="flex flex-wrap gap-1.5 text-[10px]">
              {['medical', 'science', 'horror', 'transition', 'crime', 'weather', 'comedy'].map(cat => (
                <button
                  key={cat}
                  onClick={() => {
                    setSfxCategory(cat);
                    handleSearchSFX(sfxQuery, cat);
                  }}
                  className={`px-2.5 py-1 rounded-lg border transition capitalize ${
                    sfxCategory === cat
                      ? 'bg-purple-600 border-purple-500 text-white'
                      : 'bg-[#050811] border-studio-border text-gray-400 hover:text-white'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* SFX List */}
            <div className="flex flex-col gap-2 mt-1 max-h-[320px] overflow-y-auto">
              {sfxResults.map(sfx => (
                <div
                  key={sfx.id}
                  className="bg-[#050811] border border-studio-border rounded-xl p-2.5 flex items-center justify-between hover:border-purple-500/50 transition"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="text-lg">
                      {sfx.id?.includes('heart') ? '🫀' : sfx.id?.includes('ecg') ? '⚡' : sfx.category === 'horror' ? '👻' : '🎵'}
                    </span>
                    <div>
                      <div className="text-xs font-bold text-white">{sfx.name}</div>
                      <div className="text-[10px] text-gray-400">
                        {sfx.category} • {((sfx.duration_ms || 1000) / 1000).toFixed(1)}s
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        const url = apiClient.getSFXAudioUrl(sfx.id);
                        handlePlayAudio(url, sfx.id);
                      }}
                      className="px-2.5 py-1 bg-studio-card hover:bg-studio-border text-gray-200 text-xs rounded-lg transition flex items-center gap-1 font-semibold"
                    >
                      {playingAudioId === sfx.id ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3 fill-current" />}
                      <span>Thử</span>
                    </button>
                    <button
                      onClick={() => handleAddSFX(sfx)}
                      className="px-3 py-1 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-lg transition flex items-center gap-1 shadow"
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
