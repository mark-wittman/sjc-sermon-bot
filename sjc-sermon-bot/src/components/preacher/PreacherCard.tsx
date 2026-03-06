import Link from "next/link";
import type { PreacherInfo } from "@/lib/preachers";

export function PreacherCard({
  preacher,
  sermonCount,
}: {
  preacher: PreacherInfo;
  sermonCount?: number;
}) {
  return (
    <Link
      href={`/preachers/${preacher.slug}`}
      className="group block bg-white rounded-lg border border-border hover:shadow-md transition-all duration-200 overflow-hidden"
    >
      <div className="h-1.5" style={{ backgroundColor: preacher.color }} />
      <div className="p-5 text-center">
        <div
          className="w-16 h-16 rounded-full mx-auto mb-3 flex items-center justify-center text-white font-serif text-xl font-bold"
          style={{ backgroundColor: preacher.color }}
        >
          {preacher.name
            .split(" ")
            .map((n) => n[0])
            .join("")}
        </div>
        <h3 className="font-serif text-lg font-semibold text-ink group-hover:text-cathedral-red transition-colors">
          {preacher.name}
        </h3>
        <p className="text-sm text-ink-muted mt-0.5">{preacher.role}</p>
        {sermonCount !== undefined && (
          <p className="text-xs text-ink-muted mt-2">
            {sermonCount} sermon{sermonCount !== 1 ? "s" : ""}
          </p>
        )}
      </div>
    </Link>
  );
}
