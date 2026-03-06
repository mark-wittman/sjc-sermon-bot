"use client";

import { PREACHERS } from "@/lib/preachers";

interface SermonFiltersProps {
  selectedPreachers: string[];
  onPreacherToggle: (name: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  sortBy: "date" | "title";
  onSortChange: (sort: "date" | "title") => void;
}

export function SermonFilters({
  selectedPreachers,
  onPreacherToggle,
  searchQuery,
  onSearchChange,
  sortBy,
  onSortChange,
}: SermonFiltersProps) {
  const preacherList = Object.values(PREACHERS);

  return (
    <div className="space-y-4">
      <div className="relative">
        <svg
          className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-muted"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search sermons by title, text, or topic..."
          className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-border bg-white text-sm placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-cathedral-red/20 focus:border-cathedral-red transition-colors"
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-ink-muted font-medium uppercase tracking-wide">
          Preacher:
        </span>
        {preacherList.map((p) => {
          const active = selectedPreachers.includes(p.name);
          return (
            <button
              key={p.name}
              onClick={() => onPreacherToggle(p.name)}
              className="px-3 py-1 rounded-full text-xs font-medium border transition-all duration-150"
              style={{
                backgroundColor: active ? p.color : "transparent",
                borderColor: active ? p.color : "#e5e5e5",
                color: active ? "#fff" : "#4a4a4a",
              }}
            >
              {p.name.split(" ")[1]}
            </button>
          );
        })}

        <div className="ml-auto">
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value as "date" | "title")}
            className="text-xs border border-border rounded px-2 py-1 bg-white text-ink-light"
          >
            <option value="date">Newest first</option>
            <option value="title">A-Z</option>
          </select>
        </div>
      </div>
    </div>
  );
}
