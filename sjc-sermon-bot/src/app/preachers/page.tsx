import { PREACHERS } from "@/lib/preachers";
import { getAllSermons } from "@/lib/data";
import { PreacherCard } from "@/components/preacher/PreacherCard";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Our Preachers",
  description:
    "Meet the preachers of Saint John's Cathedral — their theological commitments, intellectual influences, and unique voices.",
};

export default function PreachersPage() {
  const sermons = getAllSermons();
  const preacherList = Object.values(PREACHERS);
  const preacherCounts = sermons.reduce(
    (acc, s) => {
      acc[s.preacher] = (acc[s.preacher] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10">
      <div className="mb-8">
        <h1 className="font-serif text-3xl sm:text-4xl font-bold">
          Our Preachers
        </h1>
        <p className="mt-2 text-ink-muted">
          The voices of Saint John&apos;s Cathedral — each with their own theological vision and intellectual world.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {preacherList.map((p) => (
          <PreacherCard
            key={p.slug}
            preacher={p}
            sermonCount={preacherCounts[p.name] || 0}
          />
        ))}
      </div>
    </div>
  );
}
