export type UserTier = 'free' | 'pro';

export interface UserProfile {
  id: string;
  user_id: string;
  full_name: string | null;
  avatar_url: string | null;
  tier: UserTier;
  created_at: string;
}

export interface Project {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: 'draft' | 'ready' | 'rendering' | 'completed';
  video_type?: 'short-form' | 'long-form';
  genre?: string;
  created_at: string;
  updated_at: string;
}

export interface VoiceConfig {
  voice: string;
  rate: string;
  pitch: string;
}

export interface VideoSpecs {
  width: number;
  height: number;
  fps: number;
}

export interface AudioSpecs {
  target_lufs: number;
  true_peak: number;
}

export interface SubtitleItem {
  word: string;
  start_ms: number;
  end_ms: number;
}

export interface SceneAsset {
  id?: string;
  asset_type: 'image' | 'video' | 'audio' | 'svg';
  source_url: string;
  local_url?: string;
  license_type: string;
  author_name?: string;
  attribution_text?: string;
  preview_url?: string;
  full_url?: string;
}

export interface SoundDesignItem {
  sfx_type: string;
  description: string;
  volume: number;
  duck_narration: boolean;
}

export interface SceneItem {
  id?: string;
  scene_id?: string;
  scene_order: number;
  chapter_order?: number;
  scene_type: string;
  narration_text: string;
  duration_seconds: number;
  start_frame: number;
  end_frame: number;
  visual_method: 'photo' | 'stock' | 'archival' | 'map' | 'svg' | 'infographic' | 'procedural' | 'parallax' | 'toon';
  visual_description?: string;
  visual_config: Record<string, any>;
  subtitles_json: SubtitleItem[];
  assets?: SceneAsset[];
  audio_url?: string;
  camera_direction?: string;
  transition?: string;
  sound_design?: SoundDesignItem[];
  source_references?: string[];
}

export interface ChapterItem {
  chapter_order: number;
  title: string;
  summary: string;
  estimated_duration_seconds: number;
  scene_count?: number;
  scenes?: SceneItem[];
}

export interface SceneManifest {
  episode_id: string;
  title: string;
  genre?: string;
  video_format?: 'short-form' | 'long-form';
  aspect_ratio?: string;
  total_duration_sec: number;
  total_frames: number;
  voice_config: VoiceConfig;
  video_specs: VideoSpecs;
  audio_specs: AudioSpecs;
  scenes: SceneItem[];
  chapters?: ChapterItem[];
}

export interface Episode {
  id: string;
  project_id: string;
  user_id: string;
  title: string;
  script_raw: string;
  voice_config: VoiceConfig;
  video_specs: VideoSpecs;
  audio_specs: AudioSpecs;
  manifest_json: SceneManifest | null;
  status: 'draft' | 'analyzed' | 'rendering' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface UserQuota {
  user_id: string;
  usage_date: string;
  script_generations_count: number;
  tts_seconds_count: number;
}

export interface GenreInfo {
  genre_id: string;
  display_name: string;
  description: string;
  syllables_per_second: number;
  preferred_visuals: string[];
}

export interface VoiceInfo {
  id: string;
  name: string;
  gender: string;
  locale: string;
}
