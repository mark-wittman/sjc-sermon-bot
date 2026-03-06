import Link from "next/link";
import { formatDateShort, formatWordCount } from "@/lib/formatters";
import { getPreacherColor } from "@/lib/preachers";
import type { Sermon } from "@/lib/types";

export function SermonCard({ sermon }: { sermon: Sermon }) {
  const color = getPreacherColor(sermon.preacher);

  return (
    <Link
      href={`/sermons/${sermon.slug}`}
      className="group block bg-white rounded-lg border border-border hover:border-border-light hover:shadow-md transition-all duration-200 overflow-hidden"
    >
      <div className="h-1" style={{ backgroundColor: color }} />
      <div className="p-5">
        <div className="flex items-center gap-2 mb-2">
          <span
            className="inline-block px-2 py-0.5 rounded text-xs font-medium text-white"
            style={{ backgroundColor: color }}
          >
            {sermon.preacher}
          </span>
          <span className="text-xs text-ink-muted">
            {formatDateShort(sermon.date)}
          </span>
        </div>
        <h3 className="font-serif text-lg font-semibold text-ink group-hover:text-cathedral-red transition-colors leading-snug">
          {sermon.title}
        </h3>
        {sermon.word_count && (
          <p className="mt-2 text-xs text-ink-muted">
            {formatWordCount(sermon.word_count)}
          </p>
        )}
      </div>
    </Link>
  );
}
