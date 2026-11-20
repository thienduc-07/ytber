import React, { useState } from 'react';
import type { SceneItem, SceneManifest, SceneAsset } from '../../types/database';
import { apiClient } from '../../services/apiClient';
import { 
  Plus, Trash2, Image as ImageIcon, Search, Check, Clock, Layers, Volume2, Music
} from 'lucide-react';

interface StoryboardEditorProps {
  manifest: SceneManifest;
  onChange: (updatedManifest: SceneManifest) => void;
  onSelectScene?: (sceneIndex: number) => void;
  activeSceneIndex?: number;
}

const VISUAL_METHODS = [
  { id: 'toon', label: 'Hoạt Họa 2.5D (Articulated Rig & Parallax)' },
  { id: 'map', label: 'Bản Đồ Vector & Tuyến Hành Quân' },
  { id: 'infographic', label: 'Infographic Số Liệu & Biểu Đồ Động' },
  { id: 'archival', label: 'Tư Liệu Trực Quan' },
  { id: 'photo', label: 'Ảnh Minh Họa' },
  { id: 'stock', label: 'Thước Phim (Stock Footage)' },
];

const SOUNDSCAPE_PRESETS = [
  { id: 'horror_creepy', label: '👻 Kinh dị / Chuyện ma (Gió hú, tiếng bước chân kẽo kẹt, cửa hé, tiếng tim)' },
  { id: 'crime_noir', label: '🕵️ Trinh thám / Phá án (Mưa đêm, máy chữ lạch cạch, chớp máy ảnh)' },
  { id: 'comedy_cartoon', label: '🎭 Hài hước / Hoạt họa (Tiếng lò xo boing, còi trượt, bong bóng)' },
  { id: 'epic_action', label: '⚡ Hành động / Trailer (Va đập chấn động, whoosh nhanh, dồn nhịp)' },
  { id: 'lofi_chill', label: '🌸 Lofi / Thư giãn (Tiếng đĩa than, chuông gió, mưa nhẹ)' },
  { id: 'tropical_forest', label: '🌲 Rừng nhiệt đới (Ve sầu, gió tán lá, chim, bước chân lá)' },
  { id: 'mountain_battlefield', label: '⚔️ Chiến trường đèo núi (Gió hú, rền đại bác, bước chân bùn)' },
  { id: 'financial_floor', label: '📈 Thị trường tài chính (Chuông vàng, văn phòng giao dịch)' },
  { id: 'cyber_tech_lab', label: '💻 Phòng công nghệ (Server hum, data stream)' },
  { id: 'deep_space', label: '🚀 Vũ trụ / Thiên văn (Sub-bass, cosmic wash)' },
  { id: 'green_wind_farm', label: '🍃 Đồng cỏ sinh thái (Gió turbine, thiên nhiên xanh)' },
];

export const StoryboardEditor: React.FC<StoryboardEditorProps> = ({
  manifest,
  onChange,
  onSelectScene,
  activeSceneIndex = 0,
}) => {
  const [assetModalSceneIndex, setAssetModalSceneIndex] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SceneAsset[]>([]);

  // SFX Search Modal State
  const [sfxModalSceneIndex, setSfxModalSceneIndex] = useState<number | null>(null);
  const [sfxSearchQuery, setSfxSearchQuery] = useState('');
  const [sfxCategory, setSfxCategory] = useState<string>('');
  const [isSearchingSFX, setIsSearchingSFX] = useState(false);
  const [sfxResults, setSfxResults] = useState<any[]>([]);
  const [isAutoEnriching, setIsAutoEnriching] = useState(false);

  const handleAutoEnrich = async () => {
    setIsAutoEnriching(true);
    try {
      const enriched = await apiClient.autoEnrichSoundscape(manifest);
      onChange(enriched);
    } catch (e: any) {
      console.warn('Auto enrich soundscape failed:', e);
    } finally {
      setIsAutoEnriching(false);
    }
  };

  const handlePlaySFXPreview = (sfxId: string) => {
    try {
      const audioUrl = apiClient.getSFXAudioUrl(sfxId);
      const audio = new Audio(audioUrl);
      audio.volume = 0.7;
      audio.play().catch((err) => console.warn('SFX preview playback failed:', err));
    } catch (e) {
      console.warn('Could not play SFX:', e);
    }
  };

  const handleSearchSFX = async (q: string, cat?: string) => {
    setIsSearchingSFX(true);
    try {
      const results = await apiClient.searchSFX(q, cat || undefined);
      setSfxResults(results);
    } catch (e) {
      console.warn('Lỗi tìm kiếm SFX:', e);
    } finally {
      setIsSearchingSFX(false);
    }
  };

  const handleAddSFXToScene = (sfx: any) => {
    if (sfxModalSceneIndex === null) return;
    const scene = manifest.scenes[sfxModalSceneIndex];
    const existing = (scene as any).sound_design || [];
    const newCue = {
      sfx_id: sfx.id,
      sfx_type: sfx.action_type || sfx.category,
      description: sfx.name,
      start_time_offset_ms: 300,
      volume: sfx.volume || 0.5,
      duck_narration: false,
    };
    handleUpdateScene(sfxModalSceneIndex, {
      sound_design: [...existing, newCue],
    } as any);
    setSfxModalSceneIndex(null);
  };

  const handleUpdateScene = (index: number, updates: Partial<SceneItem>) => {
    const updatedScenes = [...manifest.scenes];
    updatedScenes[index] = { ...updatedScenes[index], ...updates };
    
    // Recalculate manifest total duration
    const totalDuration = updatedScenes.reduce((acc, s) => acc + s.duration_seconds, 0);
    const totalFrames = Math.round(totalDuration * (manifest.video_specs.fps || 30));

    onChange({
      ...manifest,
      total_duration_sec: totalDuration,
      total_frames: totalFrames,
      scenes: updatedScenes,
    });
  };

  const handleAddScene = () => {
    const newSceneOrder = manifest.scenes.length + 1;
    const newScene: SceneItem = {
      scene_order: newSceneOrder,
      scene_type: 'body',
      narration_text: 'Nội dung tiếp theo của câu chuyện...',
      duration_seconds: 5.0,
      start_frame: manifest.total_frames,
      end_frame: manifest.total_frames + 150,
      visual_method: 'photo',
      visual_config: {},
      subtitles_json: [],
      assets: [],
    };

    const updatedScenes = [...manifest.scenes, newScene];
    const totalDuration = updatedScenes.reduce((acc, s) => acc + s.duration_seconds, 0);

    onChange({
      ...manifest,
      total_duration_sec: totalDuration,
      total_frames: Math.round(totalDuration * (manifest.video_specs.fps || 30)),
      scenes: updatedScenes,
    });
  };

  const handleDeleteScene = (index: number) => {
    if (manifest.scenes.length <= 1) return;
    const updatedScenes = manifest.scenes.filter((_, idx) => idx !== index);
    const totalDuration = updatedScenes.reduce((acc, s) => acc + s.duration_seconds, 0);

    onChange({
      ...manifest,
      total_duration_sec: totalDuration,
      total_frames: Math.round(totalDuration * (manifest.video_specs.fps || 30)),
      scenes: updatedScenes,
    });
  };

  const handleSearchAssets = async (query: string) => {
    if (!query.trim()) return;
    setIsSearching(true);
    try {
      const assets = await apiClient.searchAssets(query, 12);
      setSearchResults(assets);
    } catch (err: any) {
      console.warn('Asset discovery API error:', err);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleAssignAsset = async (asset: SceneAsset) => {
    if (assetModalSceneIndex === null) return;
    const targetScene = manifest.scenes[assetModalSceneIndex];
    let finalAsset = asset;

    // Download asset to local secure storage if not yet downloaded
    if (!asset.local_url && asset.source_url) {
      try {
        finalAsset = await apiClient.downloadAsset({
          url: asset.source_url,
          title: asset.attribution_text?.replace('Ảnh: ', '') || 'Tư liệu',
          creator: asset.author_name,
          license_type: asset.license_type,
          attribution_text: asset.attribution_text
        });
      } catch (e) {
        console.warn('Could not download asset to local storage, using direct URL:', e);
      }
    }

    handleUpdateScene(assetModalSceneIndex, {
      assets: [finalAsset],
      visual_config: { ...targetScene.visual_config, imageUrl: finalAsset.local_url || finalAsset.source_url }
    });
    setAssetModalSceneIndex(null);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-studio-accent" />
          <h2 className="text-base font-bold text-white">Phân Cảnh Kịch Bản (Storyboard)</h2>
          <span className="text-xs bg-studio-card text-gray-400 px-2 py-0.5 rounded-full border border-studio-border">
            {manifest.scenes.length} cảnh • {Math.round(manifest.total_duration_sec)}s
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleAutoEnrich}
            disabled={isAutoEnriching}
            className="flex items-center gap-1.5 text-xs font-semibold bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 text-white px-3 py-1.5 rounded-lg transition shadow"
            title="Tự động phân tích kịch bản và gán nhạc nền & sound effects chân thực cho từng cảnh"
          >
            <Music className="w-3.5 h-3.5" />
            {isAutoEnriching ? 'Đang phối âm...' : 'AI Tự Động Phối Âm & SFX'}
          </button>
          <button
            onClick={handleAddScene}
            className="flex items-center gap-1.5 text-xs font-semibold bg-studio-primary hover:bg-indigo-600 text-white px-3 py-1.5 rounded-lg transition shadow"
          >
            <Plus className="w-3.5 h-3.5" />
            Thêm Cảnh
          </button>
        </div>
      </div>

      {/* Scene list cards */}
      <div className="space-y-3">
        {manifest.scenes.map((scene, idx) => {
          const isActive = idx === activeSceneIndex;
          return (
            <div
              key={idx}
              onClick={() => onSelectScene?.(idx)}
              className={`p-4 rounded-xl border transition cursor-pointer ${
                isActive
                  ? 'bg-studio-surface border-studio-primary ring-1 ring-studio-primary'
                  : 'bg-studio-card/70 border-studio-border hover:border-gray-600'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-md bg-studio-border flex items-center justify-center text-xs font-bold text-gray-300">
                    {idx + 1}
                  </span>
                  <span className="text-xs font-semibold uppercase tracking-wider text-studio-accent bg-studio-accent/10 px-2 py-0.5 rounded">
                    {scene.scene_type}
                  </span>
                  <div className="flex items-center gap-1 text-xs text-gray-400">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{scene.duration_seconds.toFixed(1)}s</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setAssetModalSceneIndex(idx);
                      setSearchQuery(scene.narration_text.split(' ').slice(0, 4).join(' '));
                    }}
                    className="flex items-center gap-1 text-xs bg-studio-border/60 hover:bg-studio-border text-gray-200 px-2.5 py-1 rounded-md transition"
                    title="Chọn tư liệu hình ảnh / video"
                  >
                    <ImageIcon className="w-3.5 h-3.5 text-studio-primary" />
                    <span>{scene.assets && scene.assets.length > 0 ? 'Đã gán tư liệu' : 'Gán tư liệu'}</span>
                  </button>

                  {manifest.scenes.length > 1 && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteScene(idx);
                      }}
                      className="text-gray-500 hover:text-red-400 p-1 transition"
                      title="Xóa cảnh"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>

              {/* Narration text input */}
              <textarea
                value={scene.narration_text}
                onChange={(e) => handleUpdateScene(idx, { narration_text: e.target.value })}
                rows={2}
                className="w-full bg-studio-bg border border-studio-border rounded-lg p-2.5 text-sm text-gray-200 focus:outline-none focus:border-studio-primary transition resize-none"
                placeholder="Lời thuyết minh tiếng Việt cho cảnh này..."
              />

              {/* Visual modality & Soundscape selectors */}
              <div className="mt-2.5 flex flex-col gap-2 text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">Hình ảnh:</span>
                    <select
                      value={scene.visual_method}
                      onChange={(e) => handleUpdateScene(idx, { visual_method: e.target.value as any })}
                      className="bg-studio-bg border border-studio-border rounded px-2 py-1 text-xs text-gray-200 focus:outline-none focus:border-studio-primary"
                    >
                      {VISUAL_METHODS.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {scene.assets && scene.assets[0] && (
                    <div className="flex items-center gap-1.5 text-gray-400 text-[11px] truncate max-w-xs" title={scene.assets[0].attribution_text || ''}>
                      <span className="w-2 h-2 rounded-full bg-emerald-400 flex-shrink-0" />
                      <span className="text-[10px] bg-emerald-950/60 text-emerald-300 border border-emerald-500/30 px-1.5 py-0.5 rounded font-mono uppercase">
                        {(scene.assets[0] as any).provider || 'Tư liệu'}
                      </span>
                      <span className="truncate">{scene.assets[0].attribution_text || scene.assets[0].license_type}</span>
                    </div>
                  )}
                </div>

                {/* Environmental Soundscape Selector */}
                <div className="flex items-center gap-2 pt-1 border-t border-studio-border/50">
                  <span className="text-gray-400 flex items-center gap-1">
                    <Volume2 className="w-3 h-3 text-studio-accent" />
                    Âm thanh môi trường:
                  </span>
                  <select
                    value={scene.music_direction || 'tropical_forest'}
                    onChange={(e) => handleUpdateScene(idx, { music_direction: e.target.value })}
                    className="flex-1 bg-studio-bg border border-studio-border rounded px-2 py-1 text-xs text-emerald-300 focus:outline-none focus:border-studio-primary font-medium"
                  >
                    {SOUNDSCAPE_PRESETS.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Sound Effects (SFX) Badge List & Search */}
                <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-studio-border/50">
                  <span className="text-[11px] text-gray-400 flex items-center gap-1">
                    <Music className="w-3 h-3 text-studio-accent" />
                    Hiệu ứng SFX:
                  </span>
                  {((scene as any).sound_design || []).map((sfx: any, sfxIdx: number) => (
                    <span key={sfxIdx} className="text-[10px] bg-studio-bg border border-studio-border text-emerald-400 px-2 py-0.5 rounded-md flex items-center gap-1">
                      🎵 {sfx.description || sfx.sfx_id}
                      <button
                        onClick={() => {
                          const updatedSfx = [...((scene as any).sound_design || [])];
                          updatedSfx.splice(sfxIdx, 1);
                          handleUpdateScene(idx, { sound_design: updatedSfx } as any);
                        }}
                        className="hover:text-red-400 text-gray-500 font-bold ml-0.5"
                        title="Xóa hiệu ứng này"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                  <button
                    onClick={() => {
                      setSfxModalSceneIndex(idx);
                      handleSearchSFX('', '');
                    }}
                    className="text-[10px] bg-studio-primary/20 hover:bg-studio-primary/30 border border-studio-primary/40 text-studio-primary font-semibold px-2 py-0.5 rounded-md transition flex items-center gap-1"
                  >
                    + Thêm SFX
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Asset Search & Attachment Modal */}
      {assetModalSceneIndex !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-studio-surface border border-studio-border rounded-2xl max-w-2xl w-full p-6 shadow-2xl flex flex-col gap-4 max-h-[85vh]">
            <div className="flex items-center justify-between border-b border-studio-border pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Search className="w-4 h-4 text-studio-primary" />
                  Tìm Kiếm Tư Liệu Mở (Wikimedia Commons & CC0)
                </h3>
                <p className="text-xs text-gray-400">Tư liệu có bản quyền công cộng hoặc CC-BY dùng hợp pháp $0</p>
              </div>
              <button
                onClick={() => setAssetModalSceneIndex(null)}
                className="text-gray-400 hover:text-white p-1"
              >
                ✕
              </button>
            </div>

            {/* Search Bar */}
            <div className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearchAssets(searchQuery)}
                placeholder="Nhập từ khóa tìm kiếm tư liệu (vd: Ha Long Bay, Hanoi Old Quarter)..."
                className="flex-1 bg-studio-bg border border-studio-border rounded-xl px-3.5 py-2 text-sm text-gray-100 focus:outline-none focus:border-studio-primary"
              />
              <button
                onClick={() => handleSearchAssets(searchQuery)}
                disabled={isSearching}
                className="px-4 py-2 bg-studio-primary hover:bg-indigo-600 disabled:opacity-50 text-white text-sm font-semibold rounded-xl flex items-center gap-1.5 transition"
              >
                <Search className="w-4 h-4" />
                {isSearching ? 'Đang tìm...' : 'Tìm kiếm'}
              </button>
            </div>

            {/* Search results grid */}
            <div className="flex-1 overflow-y-auto grid grid-cols-2 gap-3 min-h-[260px] p-1">
              {searchResults.map((res, i) => (
                <div
                  key={i}
                  className="bg-studio-card border border-studio-border rounded-xl overflow-hidden hover:border-studio-primary transition group flex flex-col justify-between"
                >
                  <div className="h-32 bg-black overflow-hidden relative">
                    <img
                      src={res.source_url}
                      alt={res.attribution_text || 'Asset'}
                      className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
                    />
                    <span className="absolute top-2 left-2 bg-black/70 text-[10px] text-emerald-300 px-2 py-0.5 rounded font-mono">
                      {res.license_type}
                    </span>
                  </div>

                  <div className="p-2.5 flex items-center justify-between">
                    <div className="truncate text-xs text-gray-300 mr-2">
                      <p className="font-semibold truncate">{res.author_name || 'Public Contributor'}</p>
                      <p className="text-[10px] text-gray-400 truncate">{res.attribution_text}</p>
                    </div>
                    <button
                      onClick={() => handleAssignAsset(res)}
                      className="px-2.5 py-1 bg-studio-primary hover:bg-indigo-600 text-white text-xs font-semibold rounded-lg flex items-center gap-1 transition flex-shrink-0"
                    >
                      <Check className="w-3 h-3" />
                      Gán
                    </button>
                  </div>
                </div>
              ))}

              {searchResults.length === 0 && !isSearching && (
                <div className="col-span-2 flex flex-col items-center justify-center text-gray-500 py-10">
                  <ImageIcon className="w-8 h-8 mb-2 opacity-50" />
                  <p className="text-xs">Nhập từ khóa và bấm Tìm kiếm để khám phá kho tư liệu mở</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SFX Search & Discovery Modal */}
      {sfxModalSceneIndex !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-studio-surface border border-studio-border rounded-2xl max-w-2xl w-full p-6 shadow-2xl flex flex-col gap-4 max-h-[85vh]">
            <div className="flex items-center justify-between border-b border-studio-border pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Music className="w-4 h-4 text-emerald-400" />
                  Kho Hiệu Ứng Âm Thanh & SFX Môi Trường
                </h3>
                <p className="text-xs text-gray-400">Tự động tìm kiếm SFX ma quái, kinh dị, tiếng bước chân, cửa kẽo kẹt, whoosh, sấm sét</p>
              </div>
              <button
                onClick={() => setSfxModalSceneIndex(null)}
                className="text-gray-400 hover:text-white p-1 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            {/* Category Filter Chips */}
            <div className="flex flex-wrap gap-1.5">
              {[
                { id: '', label: 'Tất cả' },
                { id: 'horror', label: '👻 Kinh dị / Chuyện ma' },
                { id: 'transition', label: '⚡ Whoosh chuyển cảnh' },
                { id: 'crime', label: '🕵️ Phá án / Trinh thám' },
                { id: 'weather', label: '⛈️ Thời tiết & Sấm sét' },
                { id: 'comedy', label: '🎭 Hoạt họa / Hài hước' },
                { id: 'historical', label: '⚔️ Lịch sử & Đại bác' },
              ].map((c) => (
                <button
                  key={c.id}
                  onClick={() => {
                    setSfxCategory(c.id);
                    handleSearchSFX(sfxSearchQuery, c.id);
                  }}
                  className={`text-xs px-2.5 py-1 rounded-lg border transition ${
                    sfxCategory === c.id
                      ? 'bg-studio-primary border-studio-primary text-white font-semibold'
                      : 'bg-studio-bg border-studio-border text-gray-400 hover:text-white'
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>

            {/* Search Bar */}
            <div className="flex gap-2">
              <input
                type="text"
                value={sfxSearchQuery}
                onChange={(e) => setSfxSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearchSFX(sfxSearchQuery, sfxCategory)}
                placeholder="Tìm tiếng ma, cửa kẽo kẹt, bước chân, sấm, tim, whoosh..."
                className="flex-1 bg-studio-bg border border-studio-border rounded-xl px-3.5 py-2 text-sm text-gray-100 focus:outline-none focus:border-studio-primary"
              />
              <button
                onClick={() => handleSearchSFX(sfxSearchQuery, sfxCategory)}
                disabled={isSearchingSFX}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl flex items-center gap-1.5 transition"
              >
                <Search className="w-4 h-4" />
                {isSearchingSFX ? 'Đang tìm...' : 'Tìm SFX'}
              </button>
            </div>

            {/* SFX Results List */}
            <div className="flex-1 overflow-y-auto flex flex-col gap-2 min-h-[260px] p-1">
              {sfxResults.map((sfx) => (
                <div
                  key={sfx.id}
                  className="bg-studio-bg border border-studio-border/70 rounded-xl p-3 flex items-center justify-between hover:border-emerald-500/50 transition group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 text-lg">
                      {sfx.category === 'horror' ? '👻' : sfx.category === 'transition' ? '⚡' : sfx.category === 'crime' ? '🕵️' : '🎵'}
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white group-hover:text-emerald-300 transition">{sfx.name}</h4>
                      <p className="text-[11px] text-gray-400">
                        Thể loại: <span className="text-emerald-400">{sfx.category}</span> • Thời lượng: {((sfx.duration_ms || 1000) / 1000).toFixed(1)}s • Tags: {(sfx.tags || []).slice(0, 3).join(', ')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handlePlaySFXPreview(sfx.id)}
                      className="px-2.5 py-1.5 bg-studio-card hover:bg-studio-border text-gray-200 hover:text-white text-xs font-semibold rounded-lg flex items-center gap-1 transition border border-studio-border"
                      title="Nghe thử âm thanh thực tế"
                    >
                      <Volume2 className="w-3.5 h-3.5 text-emerald-400" />
                      Nghe thử
                    </button>
                    <button
                      onClick={() => handleAddSFXToScene(sfx)}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg flex items-center gap-1 transition shadow"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      Thêm vào cảnh
                    </button>
                  </div>
                </div>
              ))}

              {sfxResults.length === 0 && !isSearchingSFX && (
                <div className="flex flex-col items-center justify-center text-gray-500 py-10">
                  <Music className="w-8 h-8 mb-2 opacity-50" />
                  <p className="text-xs">Không tìm thấy hiệu ứng phù hợp. Hãy thử tìm từ khóa khác!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
