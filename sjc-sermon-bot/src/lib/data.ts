import { readFileSync, existsSync, readdirSync } from "fs";
import { join } from "path";
import type {
  Catalog,
  CatalogEpisode,
  Transcript,
  ProcessedTranscript,
  TemporalContext,
  VoiceProfiles,
  InfluenceMap,
  PreacherReferences,
  Sermon,
} from "./types";
import { slugify } from "./formatters";

const DATA_DIR = join(process.cwd(), "data");

function readJSON<T>(path: string): T | null {
  if (!existsSync(path)) return null;
  return JSON.parse(readFileSync(path, "utf-8"));
}

export function getCatalog(): Catalog | null {
  return readJSON<Catalog>(join(DATA_DIR, "catalog.json"));
}

export function getTranscript(filename: string): Transcript | null {
  return readJSON<Transcript>(join(DATA_DIR, "transcripts", filename));
}

export function getContext(filename: string): TemporalContext | null {
  return readJSON<TemporalContext>(join(DATA_DIR, "context", filename));
}

export function getProcessedTranscript(
  filename: string
): ProcessedTranscript | null {
  return readJSON<ProcessedTranscript>(
    join(DATA_DIR, "processed_transcripts", filename)
  );
}

export function getVoiceProfiles(): VoiceProfiles | null {
  return readJSON<VoiceProfiles>(
    join(DATA_DIR, "references", "voice_profiles.json")
  );
}

export function getInfluenceMap(preacher: string): InfluenceMap | null {
  return readJSON<InfluenceMap>(
    join(DATA_DIR, "references", `${preacher}_influence_map.json`)
  );
}

export function getPreacherReferences(
  preacher: string
): PreacherReferences | null {
  return readJSON<PreacherReferences>(
    join(DATA_DIR, "references", `${preacher}_references.json`)
  );
}

function makeSlug(episode: CatalogEpisode): string {
  return slugify(`${episode.date}-${episode.title}`);
}

// Clean WhisperKit tokens from raw transcript text (fallback when no processed version)
function cleanTranscriptText(text: string): string {
  return text
    .replace(/<\|startoftranscript\|>/g, "")
    .replace(/<\|endoftext\|>/g, "")
    .replace(/<\|en\|>/g, "")
    .replace(/<\|transcribe\|>/g, "")
    .replace(/<\|\d+\.?\d*\|>/g, "")
    .replace(/ {2,}/g, " ")
    .trim();
}

export function getAllSermons(): Sermon[] {
  const catalog = getCatalog();
  if (!catalog) return [];

  const transcriptDir = join(DATA_DIR, "transcripts");
  const processedDir = join(DATA_DIR, "processed_transcripts");
  const contextDir = join(DATA_DIR, "context");

  const transcriptFiles = existsSync(transcriptDir)
    ? readdirSync(transcriptDir).filter((f) => f.endsWith(".json"))
    : [];
  const processedFiles = existsSync(processedDir)
    ? readdirSync(processedDir).filter((f) => f.endsWith(".json"))
    : [];
  const contextFiles = existsSync(contextDir)
    ? readdirSync(contextDir).filter((f) => f.endsWith(".json"))
    : [];

  const transcriptMap = new Map<string, string>();
  for (const f of transcriptFiles) {
    const t = readJSON<Transcript>(join(transcriptDir, f));
    if (t) {
      transcriptMap.set(t.date, f);
    }
  }

  const processedMap = new Map<string, string>();
  for (const f of processedFiles) {
    const p = readJSON<ProcessedTranscript>(join(processedDir, f));
    if (p) {
      processedMap.set(p.date, f);
    }
  }

  const contextMap = new Map<string, string>();
  for (const f of contextFiles) {
    const c = readJSON<TemporalContext>(join(contextDir, f));
    if (c) {
      contextMap.set(c.date, f);
    }
  }

  return catalog.episodes
    .filter((ep) => ep.preacher)
    .map((ep) => {
      const slug = makeSlug(ep);

      // Prefer processed transcript, fall back to raw
      const processedFile = processedMap.get(ep.date);
      const processed = processedFile
        ? readJSON<ProcessedTranscript>(join(processedDir, processedFile))
        : null;

      const transcriptFile = transcriptMap.get(ep.date);
      const transcript = transcriptFile
        ? readJSON<Transcript>(join(transcriptDir, transcriptFile))
        : null;

      const contextFile = contextMap.get(ep.date);
      const context = contextFile
        ? readJSON<TemporalContext>(join(contextDir, contextFile))
        : null;

      // Use processed text if available, otherwise clean raw text
      const fullText = processed
        ? processed.full_text
        : transcript
          ? cleanTranscriptText(transcript.full_text)
          : undefined;

      return {
        title: ep.title,
        date: ep.date,
        preacher: ep.preacher!,
        slug,
        audio_url: ep.audio_url,
        description: ep.description,
        duration: ep.duration,
        word_count: processed?.word_count ?? transcript?.word_count,
        transcript: fullText,
        sections: processed?.sections,
        context: context || undefined,
      };
    });
}

export function getSermonBySlug(slug: string): Sermon | null {
  const sermons = getAllSermons();
  return sermons.find((s) => s.slug === slug) || null;
}

export function getSermonSlugs(): string[] {
  return getAllSermons().map((s) => s.slug);
}
