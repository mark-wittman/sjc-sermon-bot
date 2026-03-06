"use client";

import { useState, useMemo, useEffect } from "react";
import { SermonGrid } from "@/components/sermon/SermonGrid";
import { SermonFilters } from "@/components/sermon/SermonFilters";
import type { Sermon } from "@/lib/types";

export default function SermonsPage() {
  const [sermons, setSermons] = useState<Sermon[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPreachers, setSelectedPreachers] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<"date" | "title">("date");

  useEffect(() => {
    fetch("/api/sermons")
      .then((r) => r.json())
      .then((data) => {
        setSermons(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    let result = sermons;

    if (selectedPreachers.length > 0) {
      result = result.filter((s) => selectedPreachers.includes(s.preacher));
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (s) =>
          s.title.toLowerCase().includes(q) ||
          s.preacher.toLowerCase().includes(q) ||
          s.description?.toLowerCase().includes(q)
      );
    }

    if (sortBy === "date") {
      result = [...result].sort(
        (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
      );
    } else {
      result = [...result].sort((a, b) => a.title.localeCompare(b.title));
    }

    return result;
  }, [sermons, searchQuery, selectedPreachers, sortBy]);

  const handlePreacherToggle = (name: string) => {
    setSelectedPreachers((prev) =>
      prev.includes(name) ? prev.filter((p) => p !== name) : [...prev, name]
    );
  };

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10">
      <div className="mb-8">
        <h1 className="font-serif text-3xl sm:text-4xl font-bold">
          Sermon Archive
        </h1>
        <p className="mt-2 text-ink-muted">
          {loading
            ? "Loading..."
            : `${sermons.length} sermons from Saint John's Cathedral`}
        </p>
      </div>

      <div className="mb-8">
        <SermonFilters
          selectedPreachers={selectedPreachers}
          onPreacherToggle={handlePreacherToggle}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          sortBy={sortBy}
          onSortChange={setSortBy}
        />
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="bg-white rounded-lg border border-border p-5 animate-pulse"
            >
              <div className="h-1 bg-border-light rounded mb-4" />
              <div className="h-4 bg-border-light rounded w-1/3 mb-2" />
              <div className="h-5 bg-border-light rounded w-3/4 mb-1" />
              <div className="h-5 bg-border-light rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : (
        <>
          <p className="text-sm text-ink-muted mb-4">
            Showing {filtered.length} of {sermons.length} sermons
          </p>
          <SermonGrid sermons={filtered} />
        </>
      )}
    </div>
  );
}
