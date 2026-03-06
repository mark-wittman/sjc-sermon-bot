import { SermonCard } from "./SermonCard";
import type { Sermon } from "@/lib/types";

export function SermonGrid({ sermons }: { sermons: Sermon[] }) {
  if (sermons.length === 0) {
    return (
      <div className="text-center py-12 text-ink-muted">
        <p className="font-serif text-xl">No sermons found</p>
        <p className="text-sm mt-2">Try adjusting your filters or search.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {sermons.map((sermon) => (
        <SermonCard key={sermon.slug} sermon={sermon} />
      ))}
    </div>
  );
}
