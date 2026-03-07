"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import type { ProcessedSection, TranscriptSegment } from "@/lib/types";

function formatTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function SermonTranscriptPlayer({
  audioUrl,
  transcript,
  segments,
  sections,
}: {
  audioUrl?: string;
  transcript?: string;
  segments?: TranscriptSegment[];
  sections?: ProcessedSection[];
}) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const activeSegRef = useRef<HTMLSpanElement>(null);
  const transcriptRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);

  const seekTo = (time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      audioRef.current.play();
    }
  };

  // Track playback time and find the active segment
  const handleTimeUpdate = useCallback(() => {
    if (!audioRef.current || !segments?.length) return;
    const t = audioRef.current.currentTime;

    // Binary-ish search: segments are sorted by start time
    let idx = -1;
    for (let i = 0; i < segments.length; i++) {
      if (t >= segments[i].start && t < segments[i].end) {
        idx = i;
        break;
      }
      // Handle gaps: if we're past this segment but before the next
      if (
        t >= segments[i].end &&
        (i === segments.length - 1 || t < segments[i + 1].start)
      ) {
        idx = i;
        break;
      }
    }
    setActiveIndex(idx);
  }, [segments]);

  // Auto-scroll the active segment into view
  useEffect(() => {
    if (activeIndex >= 0 && isPlaying && activeSegRef.current && transcriptRef.current) {
      const container = transcriptRef.current;
      const el = activeSegRef.current;
      const containerRect = container.getBoundingClientRect();
      const elRect = el.getBoundingClientRect();

      // Only scroll if the element is outside the visible area
      if (elRect.top < containerRect.top || elRect.bottom > containerRect.bottom) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }
  }, [activeIndex, isPlaying]);

  // Attach play/pause listeners
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onPlay = () => setIsPlaying(true);
    const onPause = () => setIsPlaying(false);

    audio.addEventListener("play", onPlay);
    audio.addEventListener("pause", onPause);
    audio.addEventListener("timeupdate", handleTimeUpdate);

    return () => {
      audio.removeEventListener("play", onPlay);
      audio.removeEventListener("pause", onPause);
      audio.removeEventListener("timeupdate", handleTimeUpdate);
    };
  }, [handleTimeUpdate]);

  // Render segments as clickable spans with highlight
  const hasTimedSegments = segments && segments.length > 0 && audioUrl;

  // Group timed segments into paragraphs (~4-6 sentences each)
  const segmentParagraphs = hasTimedSegments
    ? (() => {
        const paragraphs: number[][] = [];
        let current: number[] = [];
        let sentenceCount = 0;
        for (let i = 0; i < segments.length; i++) {
          current.push(i);
          const text = segments[i].text;
          // Count sentence endings
          if (/[.!?]["']?\s*$/.test(text)) {
            sentenceCount++;
            if (sentenceCount >= 5) {
              paragraphs.push(current);
              current = [];
              sentenceCount = 0;
            }
          }
        }
        if (current.length > 0) paragraphs.push(current);
        return paragraphs;
      })()
    : [];

  return (
    <>
      {/* Audio Player */}
      {audioUrl && (
        <div className="mb-8 bg-white rounded-lg border border-border p-4 sticky top-0 z-10">
          <audio ref={audioRef} controls className="w-full" preload="none">
            <source src={audioUrl} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}

      {/* Transcript */}
      {transcript || hasTimedSegments ? (
        <div
          ref={transcriptRef}
          className="bg-white rounded-lg border border-border p-6 sm:p-8"
        >
          <h2 className="font-serif text-xl font-semibold mb-4">Transcript</h2>

          {hasTimedSegments ? (
            <div className="text-sm text-ink-light leading-relaxed space-y-4">
              {segmentParagraphs.map((indices, pi) => (
                <p key={pi}>
                  {indices.map((i) => (
                    <span
                      key={i}
                      ref={i === activeIndex ? activeSegRef : undefined}
                      onClick={() => seekTo(segments[i].start)}
                      className={`cursor-pointer transition-colors duration-300 hover:text-ink ${
                        i === activeIndex && isPlaying
                          ? "bg-cathedral-red/10 text-ink font-medium rounded px-0.5 -mx-0.5"
                          : ""
                      }`}
                    >
                      {segments[i].text}{" "}
                    </span>
                  ))}
                </p>
              ))}
            </div>
          ) : sections && sections.length > 0 ? (
            <div className="space-y-6">
              {sections.map((section, i) => (
                <div key={i}>
                  <div className="flex items-baseline gap-2 mb-2">
                    <h3 className="font-serif text-base font-semibold text-ink">
                      {section.header}
                    </h3>
                    {audioUrl && (
                      <button
                        onClick={() => seekTo(section.start_time)}
                        className="text-xs text-cathedral-red hover:text-cathedral-red-light transition-colors font-mono shrink-0"
                        title={`Jump to ${formatTimestamp(section.start_time)}`}
                      >
                        {formatTimestamp(section.start_time)}
                      </button>
                    )}
                  </div>
                  <div className="prose prose-sm max-w-none text-ink-light leading-relaxed">
                    {section.text.split("\n\n").map((para, j) => (
                      <p key={j}>{para}</p>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="prose prose-sm max-w-none text-ink-light leading-relaxed">
              {(() => {
                const text = transcript ?? "";
                // If text has real paragraph breaks use them, otherwise split by sentences
                if (text.includes("\n\n")) {
                  return text.split("\n\n").map((para, i) => <p key={i}>{para}</p>);
                }
                // Split into ~5-sentence paragraphs
                const sentences = text.match(/[^.!?]*[.!?]+[\s]*/g) || [text];
                const paras: string[] = [];
                for (let i = 0; i < sentences.length; i += 5) {
                  paras.push(sentences.slice(i, i + 5).join("").trim());
                }
                return paras.map((p, i) => <p key={i}>{p}</p>);
              })()}
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-border p-6 text-center text-ink-muted">
          <p className="font-serif text-lg">Transcript not yet available</p>
          <p className="text-sm mt-1">
            Check back after the transcription pipeline completes.
          </p>
        </div>
      )}
    </>
  );
}
