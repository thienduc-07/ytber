import { supabase } from './supabase';
import type { Project, SceneManifest, SceneAsset, GenreInfo, VoiceInfo } from '../types/database';

const rawBase = (import.meta.env.VITE_API_BASE_URL as string) || '';
const API_BASE = rawBase ? (rawBase.endsWith('/api/v1') ? rawBase : `${rawBase.replace(/\/$/, '')}/api/v1`) : '/api/v1';

export async function getAuthHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  try {
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    } else {
      // Local development or unauthenticated fallback token
      const localToken = localStorage.getItem('ytber_access_token') || localStorage.getItem('ytber_guest_token');
      if (localToken) {
        headers['Authorization'] = `Bearer ${localToken}`;
      } else {
        const guestToken = 'demo-guest-session-token';
        localStorage.setItem('ytber_guest_token', guestToken);
        headers['Authorization'] = `Bearer ${guestToken}`;
      }
    }
  } catch (e) {
    console.warn('Could not read auth session for API request:', e);
    headers['Authorization'] = 'Bearer demo-guest-session-token';
  }

  return headers;
}

export interface ResearchFact {
  statement: string;
  source_name: string;
  source_url: string;
  fact_type: string;
}

export interface ResearchEntity {
  name: string;
  entity_type: string;
  significance: string;
  animated_representation: string;
}

export interface NarrativeStrategy {
  hook_angle: string;
  core_conflict: string;
  climax_point: string;
  takeaway_message: string;
  pacing_guidelines: string;
}

export interface TopicResearchReport {
  topic: string;
  subject: string;
  category: string;
  target_audience: string;
  context: string;
  verified_facts: ResearchFact[];
  key_entities: ResearchEntity[];
  storytelling_angles: string[];
  misconceptions: string[];
  claims_needing_verification: string[];
  narrative_strategy: NarrativeStrategy;
  recommended_duration_sec: number;
  recommended_style: string;
}

export interface AnalyzeScriptParams {
  script_text: string;
  target_duration_seconds?: number;
  genre?: string;
  video_format?: 'short-form' | 'long-form';
  visual_style_preference?: string;
}

export interface AnalyzeScriptResponse {
  title: string;
  genre: string;
  video_format: 'short-form' | 'long-form';
  aspect_ratio: string;
  estimated_syllables: number;
  estimated_duration_seconds: number;
  hook_summary: string;
  scenes: any[];
  chapters: any[];
  entities: any[];
  ai_provider_used: string;
}

export interface TTSResponse {
  audio_id: string;
  normalized_text: string;
  audio_url: string;
  duration_seconds: number;
  words: Array<{ word: string; start_ms: number; end_ms: number }>;
  provider: string;
  sample_rate: number;
  format: string;
}

export interface GenerateMovieParams {
  script_text: string;
  genre?: string;
  video_format?: 'short-form' | 'long-form';
  voice?: string;
  rate?: string;
  pitch?: string;
  visual_style?: string;
}

export interface FilmBlueprint {
  title: string;
  genre: string;
  video_format: string;
  aspect_ratio: string;
  estimated_duration_seconds: number;
  character_bible: Record<string, any>;
  environment_bible: Record<string, any>;
  dramatic_arc: string;
  scenes: Array<{
    scene_order: number;
    scene_id: string;
    scene_type: string;
    narrative_stage: string;
    narration_text: string;
    estimated_duration: number;
    visual_query: string;
    visual_method: string;
    visual_description: string;
    camera_direction: string;
    transition: string;
    environment_setting: string;
    ambient_profile: string;
    sfx_cues: any[];
    suggested_asset_keywords?: string[];
  }>;
}

export const apiClient = {
  // 1. Genres
  async fetchGenres(): Promise<GenreInfo[]> {
    try {
      const res = await fetch(`${API_BASE}/script/genres`);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Failed to fetch remote genres, using local fallback:', e);
    }
    return [
      { genre_id: 'general', display_name: 'Kể Chuyện Đa Năng', description: 'Cấu trúc 3 hồi kinh điển, cân bằng giữa hình ảnh và lời kể.', syllables_per_second: 4.0, preferred_visuals: ['photo', 'stock'] },
      { genre_id: 'historical_doc', display_name: 'Tài Liệu Lịch Sử', description: 'Biên niên sử hào hùng, tư liệu lưu trữ, bản đồ và chứng nhân.', syllables_per_second: 3.8, preferred_visuals: ['archival', 'map'] },
      { genre_id: 'economics', display_name: 'Kinh Tế & Tài Chính', description: 'Số liệu sắc bén, biểu đồ trực quan, so sánh tăng trưởng vĩ mô.', syllables_per_second: 4.2, preferred_visuals: ['infographic', 'svg'] },
      { genre_id: 'horror', display_name: 'Kinh Dị & Bí Ẩn', description: 'Không khí u ám, leo thang căng thẳng, khoảng lặng nghẹt thở.', syllables_per_second: 3.2, preferred_visuals: ['archival', 'parallax'] },
      { genre_id: 'science', display_name: 'Khoa Học & Công Nghệ', description: 'Giải thích cơ chế vật lý, nguyên lý cơ học, sơ đồ vector.', syllables_per_second: 3.9, preferred_visuals: ['svg', 'procedural'] },
      { genre_id: 'education', display_name: 'Giáo Dục & Bài Học', description: 'Hệ thống bài học dễ hiểu, danh sách gạch đầu dòng trực quan.', syllables_per_second: 3.7, preferred_visuals: ['infographic', 'toon'] },
      { genre_id: 'news', display_name: 'Thời Sự Nóng', description: 'Nhịp độ dồn dập, sự kiện nóng, định vị địa lý nhanh.', syllables_per_second: 4.4, preferred_visuals: ['stock', 'map'] },
      { genre_id: 'biography', display_name: 'Tiểu Sử Danh Nhân', description: 'Chân dung nhân vật 2.5D, dấu mốc cuộc đời và di sản.', syllables_per_second: 3.6, preferred_visuals: ['parallax', 'archival'] },
      { genre_id: 'business', display_name: 'Kinh Doanh & Khởi Nghiệp', description: 'Chiến lược kinh doanh, bài học từ các tập đoàn lớn.', syllables_per_second: 4.1, preferred_visuals: ['stock', 'infographic'] },
      { genre_id: 'crime', display_name: 'Phá Án & Điều Tra', description: 'Hồ sơ vụ án, chứng cứ hiện trường, chân dung nghi phạm.', syllables_per_second: 3.4, preferred_visuals: ['archival', 'map'] },
    ];
  },

  // 2. Script Analysis
  async analyzeScript(params: AnalyzeScriptParams): Promise<AnalyzeScriptResponse> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/script/analyze`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        script_text: params.script_text,
        target_duration_seconds: params.target_duration_seconds || 60,
        genre: params.genre || 'general',
        video_format: params.video_format || 'short-form',
        visual_style_preference: params.visual_style_preference || 'adaptive',
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Phân tích kịch bản thất bại (${res.status})`);
    }

    return await res.json();
  },

  // 2.1 AI Content Research & Narrative Intelligence
  async researchTopic(topic: string, category?: string): Promise<TopicResearchReport> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/research/topic`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ topic, category: category || 'general' }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Nghiên cứu chủ đề thất bại (${res.status})`);
    }
    return await res.json();
  },

  // 3. Asset Discovery
  async searchAssets(query: string, limit: number = 10): Promise<SceneAsset[]> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/assets/search?q=${encodeURIComponent(query)}&limit=${limit}`, {
      headers,
    });

    if (!res.ok) {
      throw new Error(`Tìm kiếm tư liệu thất bại (${res.status})`);
    }

    const data = await res.json();
    const rawAssets: any[] = data.assets || [];
    return rawAssets.map((a) => ({
      id: a.asset_id,
      asset_type: a.media_type === 'video' ? 'video' : 'image',
      source_url: a.download_url || a.full_url || a.preview_url,
      preview_url: a.preview_url,
      full_url: a.download_url || a.full_url,
      license_type: a.license || a.license_type || 'Public Domain',
      author_name: a.creator || a.author_name || 'Tác giả tư liệu',
      attribution_text: a.attribution_text || `Ảnh: ${a.title}`,
    }));
  },

  async downloadAsset(asset: {
    url: string;
    title?: string;
    provider?: string;
    license_type?: string;
    license_url?: string;
    creator?: string;
    attribution_required?: boolean;
    attribution_text?: string;
  }): Promise<SceneAsset> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/assets/download`, {
      method: 'POST',
      headers,
      body: JSON.stringify(asset),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Tải tư liệu thất bại (${res.status})`);
    }

    const data = await res.json();
    return {
      id: data.asset_id,
      asset_type: data.media_type === 'video' ? 'video' : 'image',
      source_url: asset.url,
      local_url: data.local_url,
      preview_url: data.local_url,
      full_url: data.local_url,
      license_type: data.license_type,
      author_name: data.creator,
      attribution_text: data.attribution_text,
    };
  },

  async generateAttributionManifest(filenames: string[]): Promise<any> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/assets/attribution-manifest`, {
      method: 'POST',
      headers,
      body: JSON.stringify(filenames),
    });

    if (!res.ok) {
      throw new Error(`Tạo manifest bản quyền thất bại (${res.status})`);
    }

    return await res.json();
  },

  // 4. Voice Studio & Real Speech Synthesis
  async fetchVoices(): Promise<VoiceInfo[]> {
    try {
      const res = await fetch(`${API_BASE}/tts/voices`);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Could not fetch voices, using default:', e);
    }
    return [
      { id: 'vi-VN-NamMinhNeural', name: 'Nam Minh (Giọng Nam - Miền Bắc)', gender: 'Male', locale: 'vi-VN' },
      { id: 'vi-VN-HoaiMyNeural', name: 'Hoài My (Giọng Nữ - Miền Bắc)', gender: 'Female', locale: 'vi-VN' },
    ];
  },

  async synthesizeVoice(params: {
    text: string;
    voice?: string;
    rate?: string;
    pitch?: string;
  }): Promise<TTSResponse> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/tts/synthesize`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        text: params.text,
        voice: params.voice || 'vi-VN-NamMinhNeural',
        rate: params.rate || '+0%',
        pitch: params.pitch || '+0Hz',
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Lồng tiếng thất bại (${res.status})`);
    }

    const data: TTSResponse = await res.json();
    if (data.audio_url && data.audio_url.startsWith('/') && rawBase) {
      data.audio_url = `${rawBase.replace(/\/$/, '')}${data.audio_url}`;
    }
    return data;
  },

  // 5. Projects CRUD
  async listProjects(): Promise<Project[]> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/projects`, { headers });
    if (!res.ok) {
      throw new Error(`Tải danh sách dự án thất bại (${res.status})`);
    }
    return await res.json();
  },

  async createProject(params: {
    title: string;
    description?: string;
    video_type?: 'short-form' | 'long-form';
    genre?: string;
  }): Promise<Project> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers,
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      throw new Error(`Tạo dự án thất bại (${res.status})`);
    }
    return await res.json();
  },

  async getProject(projectId: string): Promise<Project> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/projects/${projectId}`, { headers });
    if (!res.ok) {
      throw new Error(`Tải thông tin dự án thất bại (${res.status})`);
    }
    return await res.json();
  },

  async deleteProject(projectId: string): Promise<void> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/projects/${projectId}`, {
      method: 'DELETE',
      headers,
    });
    if (!res.ok && res.status !== 204) {
      throw new Error(`Xóa dự án thất bại (${res.status})`);
    }
  },

  async updateManifest(episodeId: string, manifest: SceneManifest): Promise<any> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/episodes/${episodeId}/manifest`, {
      method: 'PUT',
      headers,
      body: JSON.stringify({ manifest_json: manifest }),
    });
    if (!res.ok) {
      throw new Error(`Lưu kịch bản phân cảnh thất bại (${res.status})`);
    }
    return await res.json();
  },

  // 6. Zero-Touch AI Movie Director (1-Click Full Production Pipeline)
  async generateMovie(params: GenerateMovieParams): Promise<SceneManifest> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/director/generate-movie`, {
      method: 'POST',
      headers,
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Sản xuất phim tự động thất bại (${res.status})`);
    }
    return await res.json();
  },

  async getFilmBlueprint(params: { script_text: string; genre?: string; video_format?: string }): Promise<FilmBlueprint> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/director/blueprint`, {
      method: 'POST',
      headers,
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Tạo bản thiết kế phim thất bại (${res.status})`);
    }
    return await res.json();
  },

  // 7. Soundscape Presets & SFX Search Engine
  async fetchSoundscapePresets(): Promise<any[]> {
    try {
      const res = await fetch(`${API_BASE}/soundscape/presets`);
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Could not fetch soundscape presets:', e);
    }
    return [];
  },

  async searchSFX(query: string = '', category?: string): Promise<any[]> {
    const url = new URL(`${API_BASE}/soundscape/search`, window.location.origin);
    if (query) url.searchParams.set('q', query);
    if (category) url.searchParams.set('category', category);
    const res = await fetch(url.toString().replace(window.location.origin, ''));
    if (!res.ok) throw new Error(`Tìm kiếm âm thanh thất bại (${res.status})`);
    return await res.json();
  },

  // 8. VoiceStudio Integration & TTS Configuration
  async fetchTTSSettings(): Promise<any> {
    const res = await fetch(`${API_BASE}/tts/settings`);
    if (!res.ok) throw new Error(`Lấy cấu hình TTS thất bại (${res.status})`);
    return await res.json();
  },

  async updateTTSSettings(params: {
    voicestudio_url?: string;
    engine_mode?: string;
    voicestudio_enabled?: boolean;
    allow_offline_fallback?: boolean;
  }): Promise<any> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}/tts/settings`, {
      method: 'POST',
      headers,
      body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error(`Cập nhật cấu hình TTS thất bại (${res.status})`);
    return await res.json();
  },

  async checkVoiceStudioStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/tts/voicestudio/status`);
    if (!res.ok) throw new Error(`Kiểm tra VoiceStudio thất bại (${res.status})`);
    return await res.json();
  },
};
