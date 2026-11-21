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

export interface CharacterProfile {
  character_id: string;
  name: string;
  role: string;
  body_proportions: string;
  costume_description: string;
  color_scheme: string[];
  facial_features?: string;
  distinguishing_props?: string[];
}

export interface EnvironmentSpec {
  setting_name: string;
  environment_type: string;
  time_of_day: string;
  weather_particles: string;
  primary_colors: string[];
}

export interface AnimationDirective {
  character_action: string;
  object_action: string;
  parallax_enabled: boolean;
  motion_intensity: number;
  zoom_ratio?: number;
}

export interface SoundDesignItem {
  sfx_id?: string;
  sfx_type: string;
  description: string;
  start_time_offset_ms?: number;
  volume: number;
  duck_narration: boolean;
}

export interface SceneItem {
  id?: string;
  scene_id?: string;
  scene_order: number;
  chapter_order?: number;
  narrative_purpose?: string;
  scene_type: string;
  narration_text: string;
  duration_seconds: number;
  start_frame: number;
  end_frame: number;
  visual_method: 'photo' | 'stock' | 'archival' | 'map' | 'svg' | 'infographic' | 'procedural' | 'parallax' | 'toon' | 'anatomy' | 'schematic' | 'presenter';
  visual_description?: string;
  environment?: EnvironmentSpec;
  character_descriptions?: string[];
  character_poses?: string[];
  props?: string[];
  camera_angle?: string;
  camera_movement?: string;
  camera_direction?: string;
  animation_instructions?: AnimationDirective;
  lighting?: string;
  color_palette?: string[];
  visual_config: Record<string, any>;
  subtitles_json: SubtitleItem[];
  assets?: SceneAsset[];
  audio_url?: string;
  audio_id?: string;
  audio_filename?: string;
  transition?: string;
  transition_type?: string;
  music_direction?: string;
  sound_design?: SoundDesignItem[];
  sound_effects?: SoundDesignItem[];
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
  main_subject?: string;
  topic_category?: string;
  context_era?: string;
  narrative_arc?: string;
  emotional_tone?: string;
  target_audience?: string;
  visual_style_preset?: string;
  character_registry?: Record<string, CharacterProfile>;
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
  display_name?: string;
  gender: string;
  locale: string;
  description?: string;
}
