"use client";

import { useRef } from "react";
import type { ProcessedSection } from "@/lib/types";

function formatTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function SermonTranscriptPlayer({
  audioUrl,
  transcript,
  sections,
}: {
  audioUrl?: string;
  transcript?: string;
  sections?: ProcessedSection[];
}) {
  const audioRef = useRef<HTMLAudioElement>(null);

  const seekTo = (time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      audioRef.current.play();
    }
  };

  return (
    <>
      {/* Audio Player */}
      {audioUrl && (
        <div className="mb-8 bg-white rounded-lg border border-border p-4">
          <audio ref={audioRef} controls className="w-full" preload="none">
            <source src={audioUrl} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}

      {/* Transcript */}
      {transcript ? (
        <div className="bg-white rounded-lg border border-border p-6 sm:p-8">
          <h2 className="font-serif text-xl font-semibold mb-4">Transcript</h2>

          {sections && sections.length > 0 ? (
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
              {transcript.split("\n\n").map((para, i) => (
                <p key={i}>{para}</p>
              ))}
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
