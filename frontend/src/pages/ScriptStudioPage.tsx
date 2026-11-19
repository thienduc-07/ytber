import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { RemotionPlayer } from '../components/video/RemotionPlayer';
import { StoryboardEditor } from '../components/storyboard/StoryboardEditor';
import { RenderModal } from '../components/video/RenderModal';
import { apiClient } from '../services/apiClient';
import type { SceneManifest, SceneItem, Project, GenreInfo, VoiceInfo } from '../types/database';
import { 
  Sparkles, Play, ArrowLeft, Save, Sliders, Volume2, Mic, Film, Check, BookOpen, Layers, Music, Headphones, Image as ImageIcon
} from 'lucide-react';

const DEFAULT_SCRIPT = `Bạn có biết rằng, cách đây hơn 70 năm, tại một thung lũng lòng chảo ở Tây Bắc, quân và dân Việt Nam đã làm nên một kỳ tích chấn động địa cầu? Đó chính là chiến thắng Điện Biên Phủ lịch sử năm 1954. Dưới sự chỉ huy tài ba của Đại tướng Võ Nguyên Giáp, toàn quân ta đã kiên cường vượt mọi gian khổ, kéo pháo qua đèo cao, bạt núi mở đường để làm nên chiến công hiển hách lừng lẫy năm châu. Ngày 7 tháng 5 năm 1954, lá cờ Quyết chiến Quyết thắng tung bay trên nóc hầm De Castries, đánh dấu mốc son chói lọi trong lịch sử dân tộc! Hãy bấm đăng ký kênh để đón xem những câu chuyện lịch sử tự hào tiếp theo!`;

export const ScriptStudioPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [scriptText, setScriptText] = useState(DEFAULT_SCRIPT);
  const [selectedGenre, setSelectedGenre] = useState('historical_doc');
  const [videoFormat, setVideoFormat] = useState<'short-form' | 'long-form'>('short-form');
  const [genres, setGenres] = useState<GenreInfo[]>([]);
  const [voices, setVoices] = useState<VoiceInfo[]>([]);
  const [voiceVoice, setVoiceVoice] = useState('vi-VN-NamMinhNeural');
  const [voiceRate, setVoiceRate] = useState('+0%');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSynthesizingVoice, setIsSynthesizingVoice] = useState(false);
  const [isDiscoveringAssets, setIsDiscoveringAssets] = useState(false);
  const [isVoiceTesting, setIsVoiceTesting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [activeSceneIndex, setActiveSceneIndex] = useState(0);
  const [showRenderModal, setShowRenderModal] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  // Initial manifest
  const [manifest, setManifest] = useState<SceneManifest>({
    episode_id: projectId || 'demo-ep',
    title: 'Chiến Thắng Điện Biên Phủ 1954',
    genre: 'historical_doc',
    video_format: 'short-form',
    aspect_ratio: '9:16',
    total_duration_sec: 58.0,
    total_frames: 1740,
    voice_config: {
      voice: 'vi-VN-NamMinhNeural',
      rate: '+0%',
      pitch: '+0Hz',
    },
    video_specs: {
      width: 1080,
      height: 1920,
      fps: 30,
    },
    audio_specs: {
      target_lufs: -14.0,
      true_peak: -1.0,
    },
    scenes: [
      {
        scene_order: 1,
        scene_type: 'hook',
        narration_text: 'Bạn có biết rằng, cách đây hơn 70 năm, tại một thung lũng lòng chảo ở Tây Bắc, quân và dân Việt Nam đã làm nên một kỳ tích chấn động địa cầu?',
        duration_seconds: 7.5,
        start_frame: 0,
        end_frame: 225,
        visual_method: 'archival',
        visual_config: {},
        subtitles_json: [],
        assets: [
          {
            asset_type: 'image',
            source_url: 'https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=1080&q=80',
            license_type: 'Public Domain',
            author_name: 'Archival Collection',
            attribution_text: 'Tư liệu lịch sử Việt Nam',
          }
        ],
      },
      {
        scene_order: 2,
        scene_type: 'context',
        narration_text: 'Đó chính là chiến thắng Điện Biên Phủ lịch sử năm 1954. Dưới sự chỉ huy tài ba của Đại tướng Võ Nguyên Giáp, toàn quân ta đã kiên cường vượt mọi gian khổ.',
        duration_seconds: 9.0,
        start_frame: 225,
        end_frame: 495,
        visual_method: 'photo',
        visual_config: {},
        subtitles_json: [],
        assets: [],
      },
      {
        scene_order: 3,
        scene_type: 'climax',
        narration_text: 'Toàn quân đã kéo pháo qua đèo cao, bạt núi mở đường để làm nên chiến công hiển hách lừng lẫy năm châu chấn động địa cầu.',
        duration_seconds: 8.5,
        start_frame: 495,
        end_frame: 750,
        visual_method: 'procedural',
        visual_config: {},
        subtitles_json: [],
        assets: [],
      },
      {
        scene_order: 4,
        scene_type: 'resolution',
        narration_text: 'Ngày 7 tháng 5 năm 1954, lá cờ Quyết chiến Quyết thắng tung bay trên nóc hầm De Castries, đánh dấu mốc son chói lọi trong lịch sử dân tộc!',
        duration_seconds: 9.5,
        start_frame: 750,
        end_frame: 1035,
        visual_method: 'archival',
        visual_config: {},
        subtitles_json: [],
        assets: [],
      },
      {
        scene_order: 5,
        scene_type: 'cta',
        narration_text: 'Hãy bấm đăng ký kênh để đón xem những câu chuyện lịch sử tự hào tiếp theo!',
        duration_seconds: 5.0,
        start_frame: 1035,
        end_frame: 1185,
        visual_method: 'toon',
        visual_config: {},
        subtitles_json: [],
        assets: [],
      },
    ],
  });

  const wordCount = scriptText.trim().split(/\s+/).filter(Boolean).length;
  const currentGenreObj = genres.find(g => g.genre_id === selectedGenre);
  const syllablesPerSec = currentGenreObj?.syllables_per_second || 3.8;
  const estimatedDurationSec = Math.round(wordCount / (syllablesPerSec / 1.15));

  useEffect(() => {
    loadInitialData();
  }, [projectId]);

  const loadInitialData = async () => {
    // 1. Load Genres & Voices
    const [fetchedGenres, fetchedVoices] = await Promise.all([
      apiClient.fetchGenres(),
      apiClient.fetchVoices(),
    ]);
    setGenres(fetchedGenres);
    setVoices(fetchedVoices);

    // 2. Load Project if given
    if (projectId) {
      try {
        const proj = await apiClient.getProject(projectId);
        setProject(proj);
        if (proj.genre) setSelectedGenre(proj.genre);
        if (proj.video_type) {
          setVideoFormat(proj.video_type);
          handleFormatChange(proj.video_type);
        }
      } catch (e) {
        console.warn('Could not load project from API, checking local storage:', e);
        const local = localStorage.getItem('demo_projects');
        if (local) {
          const list: Project[] = JSON.parse(local);
          const found = list.find((p) => p.id === projectId);
          if (found) setProject(found);
        }
      }
    }
  };

  const handleFormatChange = (fmt: 'short-form' | 'long-form') => {
    setVideoFormat(fmt);
    const isLong = fmt === 'long-form';
    setManifest(prev => ({
      ...prev,
      video_format: fmt,
      aspect_ratio: isLong ? '16:9' : '9:16',
      video_specs: {
        width: isLong ? 1920 : 1080,
        height: isLong ? 1080 : 1920,
        fps: 30,
      }
    }));
  };

  const handleAnalyzeScript = async () => {
    if (!scriptText.trim()) return;
    setIsAnalyzing(true);
    setNotice(null);

    try {
      const data = await apiClient.analyzeScript({
        script_text: scriptText,
        target_duration_seconds: estimatedDurationSec,
        genre: selectedGenre,
        video_format: videoFormat,
      });

      // Construct fresh SceneManifest from structured analysis
      const isLong = videoFormat === 'long-form';
      const fps = 30;
      let currentFrame = 0;

      const convertedScenes: SceneItem[] = data.scenes.map((s: any, idx: number) => {
        const durationSec = Number(s.duration_seconds) || 4.0;
        const frames = Math.round(durationSec * fps);
        const scene: SceneItem = {
          scene_id: s.scene_id || `scene_${String(idx + 1).padStart(3, '0')}`,
          scene_order: s.scene_order || idx + 1,
          chapter_order: s.chapter_order || 1,
          scene_type: s.scene_type || 'narrative',
          narration_text: s.narration_text || '',
          duration_seconds: durationSec,
          start_frame: currentFrame,
          end_frame: currentFrame + frames,
          visual_method: s.visual_method || 'photo',
          visual_description: s.visual_description || '',
          visual_config: {},
          subtitles_json: [],
          assets: (s.suggested_asset_keywords || []).map((k: string, kIdx: number) => ({
            id: `kwd_${kIdx}`,
            asset_type: 'image',
            source_url: '',
            license_type: 'Pending Discovery',
            author_name: k,
            attribution_text: `Từ khóa tìm kiếm: ${k}`
          })),
          camera_direction: s.camera_direction,
          transition: s.transition,
          sound_design: s.sound_design,
          source_references: s.source_references
        };
        currentFrame += frames;
        return scene;
      });

      const totalSec = convertedScenes.reduce((a, s) => a + s.duration_seconds, 0);

      setManifest({
        episode_id: projectId || 'ep_active',
        title: data.title || project?.title || 'Video AI',
        genre: data.genre || selectedGenre,
        video_format: videoFormat,
        aspect_ratio: isLong ? '16:9' : '9:16',
        total_duration_sec: totalSec,
        total_frames: currentFrame,
        voice_config: {
          voice: voiceVoice,
          rate: voiceRate,
          pitch: '+0Hz',
        },
        video_specs: {
          width: isLong ? 1920 : 1080,
          height: isLong ? 1080 : 1920,
          fps: 30,
        },
        audio_specs: {
          target_lufs: -14.0,
          true_peak: -1.0,
        },
        scenes: convertedScenes,
        chapters: data.chapters || []
      });

      setNotice(`Phân tích kịch bản thành công theo thể loại ${currentGenreObj?.display_name || selectedGenre}!`);
    } catch (err: any) {
      console.error('Error in analyzeScript:', err);
      setNotice(`Lỗi phân tích: ${err?.message || 'Vui lòng thử lại'}`);
    } finally {
      setIsAnalyzing(false);
      setTimeout(() => setNotice(null), 4000);
    }
  };

  const handleTestVoice = async () => {
    setIsVoiceTesting(true);
    try {
      const testSample = `Xin chào, đây là giọng đọc AI ${voiceVoice === 'vi-VN-NamMinhNeural' ? 'Nam Minh' : 'Hoài My'} của YTBER Studio.`;
      const tts = await apiClient.synthesizeVoice({
        text: testSample,
        voice: voiceVoice,
        rate: voiceRate,
      });

      const audio = new Audio(tts.audio_url);
      await audio.play();
      setNotice('Đang phát giọng đọc thử nghiệm chất lượng cao...');
    } catch (err: any) {
      setNotice(`Lỗi nghe thử giọng: ${err.message}`);
    } finally {
      setIsVoiceTesting(false);
      setTimeout(() => setNotice(null), 3000);
    }
  };

  const handleGenerateVoiceForScenes = async () => {
    setIsSynthesizingVoice(true);
    setNotice('Đang tổng hợp giọng đọc AI và tạo mốc phụ đề karaoke theo mili-giây...');
    
    try {
      const updatedScenes = [...manifest.scenes];
      let updatedCount = 0;

      for (let i = 0; i < updatedScenes.length; i++) {
        const scene = updatedScenes[i];
        if (!scene.narration_text.trim()) continue;

        try {
          const tts = await apiClient.synthesizeVoice({
            text: scene.narration_text,
            voice: voiceVoice,
            rate: voiceRate,
          });

          updatedScenes[i] = {
            ...scene,
            audio_url: tts.audio_url,
            duration_seconds: Math.max(3.0, tts.duration_seconds),
            subtitles_json: tts.words || [],
          };
          updatedCount++;
        } catch (e) {
          console.warn(`Lỗi tổng hợp giọng cảnh ${i + 1}:`, e);
        }
      }

      // Recalculate frame bounds
      let currF = 0;
      const reCalculated = updatedScenes.map(s => {
        const fCount = Math.round(s.duration_seconds * 30);
        const sc = { ...s, start_frame: currF, end_frame: currF + fCount };
        currF += fCount;
        return sc;
      });

      const totalDur = reCalculated.reduce((a, s) => a + s.duration_seconds, 0);

      setManifest(prev => ({
        ...prev,
        total_duration_sec: totalDur,
        total_frames: currF,
        scenes: reCalculated,
      }));

      setNotice(`Đã tạo giọng đọc & phụ đề mili-giây cho ${updatedCount}/${updatedScenes.length} cảnh!`);
    } catch (e: any) {
      setNotice(`Lỗi tổng hợp giọng đọc: ${e.message}`);
    } finally {
      setIsSynthesizingVoice(false);
      setTimeout(() => setNotice(null), 3500);
    }
  };

  const handleAutoDiscoverAssets = async () => {
    setIsDiscoveringAssets(true);
    setNotice('Đang tự động tìm kiếm và tải tư liệu thực từ Wikimedia & Openverse...');

    try {
      const updatedScenes = [...manifest.scenes];
      let matchedCount = 0;

      for (let i = 0; i < updatedScenes.length; i++) {
        const scene = updatedScenes[i];
        if (scene.assets?.[0]?.local_url) continue;

        const query =
          (scene as any).search_keywords?.[0] ||
          (scene as any).suggested_asset_keywords?.[0] ||
          scene.visual_description?.split(' ')[0] ||
          'Vietnam archival photography';

        try {
          const results = await apiClient.searchAssets(query, 5);
          if (results.length > 0) {
            const topAsset = results[0];
            const downloaded = await apiClient.downloadAsset({
              url: topAsset.source_url,
              title: topAsset.attribution_text?.replace('Ảnh: ', '') || query,
              creator: topAsset.author_name,
              license_type: topAsset.license_type,
              attribution_text: topAsset.attribution_text,
            });

            updatedScenes[i] = {
              ...scene,
              assets: [downloaded],
              visual_config: { ...scene.visual_config, imageUrl: downloaded.local_url }
            };
            matchedCount++;
          }
        } catch (err) {
          console.warn(`Lỗi tìm tư liệu cảnh ${i + 1}:`, err);
        }
      }

      setManifest(prev => ({
        ...prev,
        scenes: updatedScenes,
      }));
      setNotice(`Đã tìm kiếm và ghép thành công tư liệu thực cho ${matchedCount} cảnh!`);
    } catch (err: any) {
      setNotice(`Lỗi tìm tư liệu tự động: ${err.message}`);
    } finally {
      setIsDiscoveringAssets(false);
      setTimeout(() => setNotice(null), 3500);
    }
  };

  const handleSaveProject = async () => {
    setIsSaving(true);
    try {
      if (projectId) {
        await apiClient.updateManifest(projectId, manifest);
      }
      setNotice('Đã lưu toàn bộ tiến độ kịch bản vào cơ sở dữ liệu!');
    } catch (e: any) {
      setNotice(`Lỗi lưu dự án: ${e.message}`);
    } finally {
      setIsSaving(false);
      setTimeout(() => setNotice(null), 2500);
    }
  };

  return (
    <div className="min-h-screen bg-studio-bg flex flex-col">
      {/* Studio Header Bar */}
      <header className="sticky top-0 z-40 bg-studio-surface/90 backdrop-blur-md border-b border-studio-border px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
            className="w-9 h-9 rounded-xl bg-studio-card hover:bg-studio-border text-gray-400 hover:text-white flex items-center justify-center transition"
            title="Quay lại danh sách dự án"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-sm font-bold text-white flex items-center gap-2">
              <Film className="w-4 h-4 text-studio-primary" />
              {project?.title || manifest.title || 'Studio Video AI'}
              <span className="text-[10px] bg-studio-primary/20 text-studio-primary border border-studio-primary/30 px-2 py-0.5 rounded-full font-mono uppercase">
                {videoFormat}
              </span>
            </h1>
            <p className="text-[11px] text-gray-400">
              {manifest.aspect_ratio} ({manifest.video_specs.width}×{manifest.video_specs.height}) • 30 FPS • {manifest.scenes.length} cảnh • ~{Math.round(manifest.total_duration_sec)}s
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {notice && (
            <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-lg animate-fade-in">
              <Check className="w-3.5 h-3.5" />
              <span>{notice}</span>
            </div>
          )}

          <button
            onClick={handleSaveProject}
            disabled={isSaving}
            className="flex items-center gap-1.5 bg-studio-card hover:bg-studio-border text-gray-200 text-xs font-semibold px-3.5 py-2 rounded-xl transition border border-studio-border"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{isSaving ? 'Đang lưu...' : 'Lưu Dự Án'}</span>
          </button>

          <button
            onClick={() => setShowRenderModal(true)}
            className="flex items-center gap-2 bg-gradient-to-r from-studio-primary to-indigo-600 hover:from-indigo-500 hover:to-indigo-700 text-white text-xs font-bold px-4 py-2 rounded-xl shadow-lg transition hover:scale-105"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Kết Xuất MP4 (WebCodecs)</span>
          </button>
        </div>
      </header>

      {/* Main Studio Workspace */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 max-w-[1780px] w-full mx-auto">
        {/* Left Column (4 cols): Script, Genre & Voice Settings */}
        <section className="lg:col-span-4 flex flex-col gap-4">
          {/* Format & Genre Selection Card */}
          <div className="bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-xl flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-300 flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-studio-primary" />
                Định Dạng & Thể Loại
              </span>
              <div className="flex bg-studio-bg p-1 rounded-xl border border-studio-border text-xs">
                <button
                  onClick={() => handleFormatChange('short-form')}
                  className={`px-3 py-1 rounded-lg font-semibold transition ${
                    videoFormat === 'short-form' ? 'bg-studio-primary text-white' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Shorts (9:16)
                </button>
                <button
                  onClick={() => handleFormatChange('long-form')}
                  className={`px-3 py-1 rounded-lg font-semibold transition ${
                    videoFormat === 'long-form' ? 'bg-studio-primary text-white' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Long-form (16:9)
                </button>
              </div>
            </div>

            {/* 10 Genres Dropdown */}
            <div>
              <label className="block text-[11px] font-semibold text-gray-400 mb-1 flex items-center gap-1">
                <BookOpen className="w-3 h-3 text-studio-accent" /> Thể loại thông minh (Genre Intelligence):
              </label>
              <select
                value={selectedGenre}
                onChange={(e) => setSelectedGenre(e.target.value)}
                className="w-full bg-studio-bg border border-studio-border rounded-xl px-3 py-2 text-xs text-gray-200 focus:outline-none focus:border-studio-primary font-medium"
              >
                {genres.map(g => (
                  <option key={g.genre_id} value={g.genre_id}>
                    {g.display_name}
                  </option>
                ))}
              </select>
              {currentGenreObj && (
                <p className="text-[11px] text-gray-400 mt-1 italic leading-tight">
                  {currentGenreObj.description}
                </p>
              )}
            </div>
          </div>

          {/* Script Input Card */}
          <div className="bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-xl flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold text-white flex items-center gap-2">
                <Sliders className="w-4 h-4 text-studio-primary" />
                Nội Dung Kịch Bản
              </h2>
              <div className="text-[11px] text-gray-400 font-mono">
                {wordCount} từ • ~{estimatedDurationSec}s
              </div>
            </div>

            <textarea
              rows={8}
              value={scriptText}
              onChange={(e) => setScriptText(e.target.value)}
              placeholder="Nhập hoặc dán nội dung kịch bản video tiếng Việt tại đây..."
              className="w-full bg-studio-bg border border-studio-border rounded-xl p-3 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:border-studio-primary transition resize-none leading-relaxed"
            />

            {/* Voice & Pacing Control */}
            <div className="grid grid-cols-2 gap-3 pt-1">
              <div>
                <label className="block text-[11px] font-semibold text-gray-400 mb-1 flex items-center gap-1">
                  <Mic className="w-3 h-3 text-studio-accent" /> Giọng đọc Edge-TTS:
                </label>
                <select
                  value={voiceVoice}
                  onChange={(e) => setVoiceVoice(e.target.value)}
                  className="w-full bg-studio-bg border border-studio-border rounded-lg px-2.5 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-studio-primary"
                >
                  {voices.map(v => (
                    <option key={v.id} value={v.id}>{v.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-gray-400 mb-1 flex items-center gap-1">
                  <Volume2 className="w-3 h-3 text-studio-accent" /> Tốc độ nhịp:
                </label>
                <select
                  value={voiceRate}
                  onChange={(e) => setVoiceRate(e.target.value)}
                  className="w-full bg-studio-bg border border-studio-border rounded-lg px-2.5 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-studio-primary"
                >
                  <option value="-15%">Chậm rãi (-15%)</option>
                  <option value="+0%">Tiêu chuẩn (+0%)</option>
                  <option value="+15%">Nhanh / Cuốn (+15%)</option>
                </select>
              </div>
            </div>

            {/* Action Buttons: Preview Voice & Analyze Script */}
            <div className="flex gap-2 pt-1">
              <button
                type="button"
                onClick={handleTestVoice}
                disabled={isVoiceTesting}
                className="flex-1 py-2 bg-studio-card hover:bg-studio-border border border-studio-border text-gray-200 text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 transition"
              >
                <Headphones className="w-3.5 h-3.5 text-studio-accent" />
                <span>{isVoiceTesting ? 'Đang phát...' : 'Nghe Thử Giọng'}</span>
              </button>

              <button
                type="button"
                onClick={handleGenerateVoiceForScenes}
                disabled={isSynthesizingVoice}
                className="flex-1 py-2 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition"
              >
                <Music className="w-3.5 h-3.5" />
                <span>{isSynthesizingVoice ? 'Đang lồng tiếng...' : 'Lồng Tiếng Các Cảnh'}</span>
              </button>
            </div>

            <button
              type="button"
              onClick={handleAutoDiscoverAssets}
              disabled={isDiscoveringAssets}
              className="w-full py-2 bg-amber-600/20 hover:bg-amber-600/30 border border-amber-500/40 text-amber-300 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition"
            >
              <ImageIcon className="w-3.5 h-3.5" />
              <span>{isDiscoveringAssets ? 'Đang tìm & tải tư liệu thực...' : 'Tự Động Ghép Tư Liệu Thực'}</span>
            </button>

            <button
              onClick={handleAnalyzeScript}
              disabled={isAnalyzing}
              className="w-full py-3 bg-gradient-to-r from-studio-primary to-indigo-600 hover:from-indigo-500 hover:to-indigo-700 disabled:opacity-50 text-white font-bold rounded-xl shadow flex items-center justify-center gap-2 transition hover:scale-[1.01] mt-1 text-xs"
            >
              <Sparkles className="w-4 h-4 text-studio-highlight" />
              <span>{isAnalyzing ? 'Đang phân tích kịch bản theo thể loại...' : 'Phân Tích Kịch Bản Bằng AI'}</span>
            </button>
          </div>
        </section>

        {/* Middle Column (5 cols): Storyboard, Chapters & Scenes */}
        <section className="lg:col-span-5 flex flex-col gap-4 overflow-y-auto max-h-[calc(100vh-100px)] pr-1">
          {manifest.chapters && manifest.chapters.length > 1 && (
            <div className="bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-xl">
              <h3 className="text-xs font-bold text-white mb-2 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-studio-primary" />
                Cấu Trúc Chương (Long-Form Chapter Outline)
              </h3>
              <div className="flex flex-col gap-2">
                {manifest.chapters.map((ch, idx) => (
                  <div key={idx} className="bg-studio-bg border border-studio-border/70 rounded-xl p-2.5 flex items-start justify-between">
                    <div>
                      <div className="text-xs font-semibold text-gray-200">{ch.title}</div>
                      <div className="text-[11px] text-gray-400">{ch.summary}</div>
                    </div>
                    <span className="text-[10px] bg-studio-primary/20 text-studio-primary border border-studio-primary/30 px-2 py-0.5 rounded-full font-mono">
                      ~{Math.round(ch.estimated_duration_seconds)}s • {ch.scene_count} cảnh
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <StoryboardEditor
            manifest={manifest}
            onChange={(m) => setManifest(m)}
            onSelectScene={(idx) => setActiveSceneIndex(idx)}
            activeSceneIndex={activeSceneIndex}
          />
        </section>

        {/* Right Column (3 cols): Real-Time Canvas Player */}
        <section className="lg:col-span-3 flex flex-col items-center gap-4">
          <div className="bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-xl w-full flex flex-col items-center">
            <h3 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-3">
              Xem Trước Khung Hình ({manifest.aspect_ratio})
            </h3>

            {/* Player Canvas */}
            <div className={`w-full ${manifest.video_format === 'long-form' ? 'aspect-[16/9] max-w-[340px]' : 'aspect-[9/16] max-w-[260px]'} rounded-xl overflow-hidden shadow-2xl border border-studio-border relative bg-black`}>
              <RemotionPlayer
                manifest={manifest}
                currentTimeSec={
                  manifest.scenes
                    .slice(0, activeSceneIndex)
                    .reduce((a, s) => a + s.duration_seconds, 0)
                }
              />
            </div>

            <div className="w-full mt-4 flex flex-col gap-2">
              <button
                onClick={() => setShowRenderModal(true)}
                className="w-full py-2.5 bg-studio-primary hover:bg-indigo-600 text-white font-bold rounded-xl shadow text-xs flex items-center justify-center gap-1.5 transition"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                Kết Xuất Video MP4 ({manifest.aspect_ratio})
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Render Modal */}
      <RenderModal
        manifest={manifest}
        isOpen={showRenderModal}
        onClose={() => setShowRenderModal(false)}
      />
    </div>
  );
};
