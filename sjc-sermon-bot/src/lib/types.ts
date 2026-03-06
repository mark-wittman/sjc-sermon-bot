export interface CatalogEpisode {
  title: string;
  date: string;
  preacher: string | null;
  audio_url: string;
  description: string;
  duration: string;
  image_url: string;
  slug: string;
}

export interface Catalog {
  podcast_title: string;
  total_episodes: number;
  identified_count: number;
  episodes: CatalogEpisode[];
  preacher_counts: Record<string, number>;
}

export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
}

export interface Transcript {
  source_file: string;
  date: string;
  transcribed_at: string;
  whisperkit_model: string;
  full_text: string;
  segments: TranscriptSegment[];
  word_count: number;
}

export interface TemporalContext {
  date: string;
  title: string;
  preacher: string;
  context: string;
  generated_at: string;
  input_tokens: number;
  output_tokens: number;
}

export interface Reference {
  type: "thinker" | "book" | "scripture" | "tradition" | "implicit";
  name: string;
  context: string;
  significance: "central" | "supporting" | "passing";
}

export interface SermonReferences {
  date: string;
  title: string;
  references: Reference[];
}

export interface PreacherReferences {
  preacher: string;
  sermons: SermonReferences[];
}

export interface InfluenceMap {
  preacher: string;
  intellectual_profile: string;
  theological_commitments: string[];
  top_thinkers: { name: string; count: number; significance: string }[];
  scripture_preferences: { book: string; count: number }[];
  traditions: string[];
  rhetorical_styles: string[];
  adjacent_voices: { name: string; reason: string }[];
  voice_signature: {
    vocabulary: string;
    sentence_structure: string;
    humor: string;
    doubt_handling: string;
  };
  generative_prompt_seed: string;
}

export interface VoiceProfile {
  preacher: string;
  influence_map: InfluenceMap;
  sermon_count: number;
  date_range: { first: string; last: string };
}

export interface VoiceProfiles {
  generated_at: string;
  profiles: Record<string, VoiceProfile>;
}

export interface ProcessedSection {
  header: string;
  start_time: number;
  end_time: number;
  text: string;
}

export interface ProcessedTranscript {
  source_file: string;
  date: string;
  full_text: string;
  sections: ProcessedSection[];
  word_count: number;
}

export interface Sermon {
  title: string;
  date: string;
  preacher: string;
  slug: string;
  audio_url: string;
  description: string;
  duration: string;
  word_count?: number;
  transcript?: string;
  segments?: TranscriptSegment[];
  sections?: ProcessedSection[];
  context?: TemporalContext;
  references?: SermonReferences;
  insights?: {
    readings: { name: string; context: string }[];
    people: { name: string; context: string }[];
    theme: string;
  };
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: SermonSource[];
}

export interface SermonSource {
  title: string;
  date: string;
  preacher: string;
  slug: string;
  excerpt: string;
}

export interface SearchResult {
  title: string;
  date: string;
  preacher: string;
  slug: string;
  excerpt: string;
  score: number;
}
