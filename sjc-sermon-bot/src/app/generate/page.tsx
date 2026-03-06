"use client";

import { useState, useRef, useEffect } from "react";
import { PREACHERS } from "@/lib/preachers";

export default function GeneratePage() {
  const [preacher, setPreacher] = useState("");
  const [occasion, setOccasion] = useState("");
  const [readings, setReadings] = useState("");
  const [theme, setTheme] = useState("");
  const [currentEvents, setCurrentEvents] = useState("");
  const [generatedText, setGeneratedText] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const outputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [generatedText]);

  const handleGenerate = async () => {
    if (!preacher || !occasion || !readings) return;
    setIsGenerating(true);
    setGeneratedText("");

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          preacher,
          occasion,
          readings,
          theme,
          current_events: currentEvents,
        }),
      });

      if (!response.ok) throw new Error("Generation failed");

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") continue;
            try {
              const parsed = JSON.parse(data);
              if (parsed.type === "text") {
                setGeneratedText((prev) => prev + parsed.content);
              }
            } catch {
              // Skip malformed JSON
            }
          }
        }
      }
    } catch {
      setGeneratedText(
        "Sorry, sermon generation failed. Please make sure the backend is running."
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const wordCount = generatedText
    .split(/\s+/)
    .filter((w) => w.length > 0).length;
  const preacherList = Object.values(PREACHERS);
  const selectedPreacher = preacher
    ? PREACHERS[preacher]
    : null;

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10">
      {/* Disclaimer */}
      <div className="mb-8 bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <div>
            <p className="text-sm font-medium text-amber-800">
              AI-Generated Content
            </p>
            <p className="text-sm text-amber-700 mt-0.5">
              Sermons generated here are for educational and exploratory purposes
              only. They should not be used in worship without thorough human
              review and adaptation.
            </p>
          </div>
        </div>
      </div>

      <div className="mb-8">
        <h1 className="font-serif text-3xl sm:text-4xl font-bold">
          Sermon Generator
        </h1>
        <p className="mt-2 text-ink-muted">
          Generate a sermon in the voice of a Saint John&apos;s preacher for a
          given occasion and set of readings.
        </p>
      </div>

      <div className="lg:grid lg:grid-cols-5 lg:gap-8">
        {/* Form */}
        <div className="lg:col-span-2 space-y-5">
          <div>
            <label className="block text-sm font-medium mb-1.5">
              Preacher <span className="text-cathedral-red">*</span>
            </label>
            <select
              value={preacher}
              onChange={(e) => setPreacher(e.target.value)}
              className="w-full px-3 py-2.5 rounded-lg border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-cathedral-red/20 focus:border-cathedral-red"
            >
              <option value="">Select a preacher...</option>
              {preacherList.map((p) => (
                <option key={p.name} value={p.name}>
                  {p.name} — {p.role}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">
              Occasion <span className="text-cathedral-red">*</span>
            </label>
            <input
              type="text"
              value={occasion}
              onChange={(e) => setOccasion(e.target.value)}
              placeholder="e.g., The Third Sunday of Advent"
              className="w-full px-3 py-2.5 rounded-lg border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-cathedral-red/20 focus:border-cathedral-red"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">
              Readings <span className="text-cathedral-red">*</span>
            </label>
            <textarea
              value={readings}
              onChange={(e) => setReadings(e.target.value)}
              rows={3}
              placeholder="e.g., Isaiah 35:1-10; Luke 1:46b-55; James 5:7-10; Matthew 11:2-11"
              className="w-full px-3 py-2.5 rounded-lg border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-cathedral-red/20 focus:border-cathedral-red resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">
              Theme <span className="text-ink-muted font-normal">(optional)</span>
            </label>
            <input
              type="text"
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              placeholder="e.g., hope in the midst of waiting"
              className="w-full px-3 py-2.5 rounded-lg border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-cathedral-red/20 focus:border-cathedral-red"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">
              Current Events{" "}
              <span className="text-ink-muted font-normal">(optional)</span>
            </label>
            <textarea
              value={currentEvents}
              onChange={(e) => setCurrentEvents(e.target.value)}
              rows={2}
              placeholder="Any current events to weave in..."
              className="w-full px-3 py-2.5 rounded-lg border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-cathedral-red/20 focus:border-cathedral-red resize-none"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={!preacher || !occasion || !readings || isGenerating}
            className="w-full py-3 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-50"
            style={{
              backgroundColor: selectedPreacher?.color || "#7D1721",
            }}
          >
            {isGenerating ? "Generating..." : "Generate Sermon"}
          </button>
        </div>

        {/* Output */}
        <div className="lg:col-span-3 mt-8 lg:mt-0">
          <div
            ref={outputRef}
            className="bg-white rounded-lg border border-border p-6 sm:p-8 min-h-[400px] max-h-[70vh] overflow-y-auto"
          >
            {generatedText ? (
              <>
                <div className="prose prose-sm max-w-none text-ink-light leading-relaxed font-serif">
                  {generatedText.split("\n\n").map((para, i) => (
                    <p key={i}>{para}</p>
                  ))}
                </div>
                {!isGenerating && (
                  <div className="mt-6 pt-4 border-t border-border-light text-xs text-ink-muted">
                    {wordCount} words &middot; Generated in the voice of{" "}
                    {preacher}
                  </div>
                )}
              </>
            ) : (
              <div className="flex items-center justify-center h-full text-ink-muted text-sm">
                <p>
                  {isGenerating
                    ? "Generating sermon..."
                    : "Your generated sermon will appear here."}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
