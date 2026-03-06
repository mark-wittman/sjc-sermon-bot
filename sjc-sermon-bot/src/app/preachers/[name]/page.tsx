import { notFound } from "next/navigation";
import Link from "next/link";
import { PREACHERS, getPreacherBySlug } from "@/lib/preachers";
import {
  getAllSermons,
  getInfluenceMap,
  getVoiceProfiles,
} from "@/lib/data";
import { SermonCard } from "@/components/sermon/SermonCard";
import type { Metadata } from "next";

export async function generateStaticParams() {
  return Object.values(PREACHERS).map((p) => ({ name: p.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ name: string }>;
}): Promise<Metadata> {
  const { name } = await params;
  const preacher = getPreacherBySlug(name);
  if (!preacher) return { title: "Preacher Not Found" };
  return {
    title: preacher.name,
    description: `Explore the sermons and intellectual world of ${preacher.name}, ${preacher.role} at Saint John's Cathedral.`,
  };
}

function BarChart({
  items,
  color,
}: {
  items: { label: string; value: number }[];
  color: string;
}) {
  const max = Math.max(...items.map((i) => i.value));
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2">
          <span className="text-xs text-ink-light w-32 truncate text-right shrink-0">
            {item.label}
          </span>
          <div className="flex-1 bg-border-light rounded-full h-4 overflow-hidden">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${(item.value / max) * 100}%`,
                backgroundColor: color,
              }}
            />
          </div>
          <span className="text-xs text-ink-muted w-8">{item.value}</span>
        </div>
      ))}
    </div>
  );
}

export default async function PreacherProfilePage({
  params,
}: {
  params: Promise<{ name: string }>;
}) {
  const { name } = await params;
  const preacher = getPreacherBySlug(name);
  if (!preacher) notFound();

  const sermons = getAllSermons().filter(
    (s) => s.preacher === preacher.name
  );
  const influenceMap = getInfluenceMap(preacher.name);
  const voiceProfiles = getVoiceProfiles();
  const profile = voiceProfiles?.profiles?.[preacher.name];

  const recentSermons = sermons.slice(0, 6);

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10">
      <Link
        href="/preachers"
        className="inline-flex items-center text-sm text-ink-muted hover:text-cathedral-red transition-colors mb-6"
      >
        <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        All preachers
      </Link>

      {/* Header */}
      <div className="flex items-start gap-5 mb-10">
        <div
          className="w-20 h-20 sm:w-24 sm:h-24 rounded-full flex items-center justify-center text-white font-serif text-2xl sm:text-3xl font-bold shrink-0"
          style={{ backgroundColor: preacher.color }}
        >
          {preacher.name
            .split(" ")
            .map((n) => n[0])
            .join("")}
        </div>
        <div>
          <h1 className="font-serif text-3xl sm:text-4xl font-bold">
            {preacher.name}
          </h1>
          <p className="text-ink-muted mt-1">{preacher.role}</p>
          <p className="text-sm text-ink-muted mt-1">
            {sermons.length} sermon{sermons.length !== 1 ? "s" : ""} in the archive
          </p>
        </div>
      </div>

      <div className="lg:grid lg:grid-cols-3 lg:gap-10">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-8">
          {/* Intellectual Profile */}
          {influenceMap?.intellectual_profile && (
            <section className="bg-white rounded-lg border border-border p-6">
              <h2 className="font-serif text-xl font-semibold mb-4">
                Intellectual Portrait
              </h2>
              <div className="text-sm text-ink-light leading-relaxed space-y-3">
                {influenceMap.intellectual_profile
                  .split("\n")
                  .filter((l) => l.trim())
                  .map((para, i) => (
                    <p key={i}>{para}</p>
                  ))}
              </div>
            </section>
          )}

          {/* Top Thinkers */}
          {influenceMap?.top_thinkers && influenceMap.top_thinkers.length > 0 && (
            <section className="bg-white rounded-lg border border-border p-6">
              <h2 className="font-serif text-xl font-semibold mb-4">
                Key Influences
              </h2>
              <BarChart
                items={influenceMap.top_thinkers.slice(0, 10).map((t) => ({
                  label: t.name,
                  value: t.count,
                }))}
                color={preacher.color}
              />
            </section>
          )}

          {/* Scripture Preferences */}
          {influenceMap?.scripture_preferences &&
            influenceMap.scripture_preferences.length > 0 && (
              <section className="bg-white rounded-lg border border-border p-6">
                <h2 className="font-serif text-xl font-semibold mb-4">
                  Scripture Preferences
                </h2>
                <BarChart
                  items={influenceMap.scripture_preferences
                    .slice(0, 10)
                    .map((s) => ({
                      label: s.book,
                      value: s.count,
                    }))}
                  color={preacher.color}
                />
              </section>
            )}

          {/* Recent Sermons */}
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-serif text-xl font-semibold">
                Recent Sermons
              </h2>
              <Link
                href={`/sermons?preacher=${encodeURIComponent(preacher.name)}`}
                className="text-sm text-cathedral-red hover:text-cathedral-red-light transition-colors"
              >
                View all &rarr;
              </Link>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {recentSermons.map((s) => (
                <SermonCard key={s.slug} sermon={s} />
              ))}
            </div>
          </section>
        </div>

        {/* Sidebar */}
        <aside className="mt-8 lg:mt-0 space-y-6">
          {/* Theological Commitments */}
          {influenceMap?.theological_commitments &&
            influenceMap.theological_commitments.length > 0 && (
              <div className="bg-white rounded-lg border border-border p-5">
                <h3 className="font-serif text-base font-semibold mb-3">
                  Theological Commitments
                </h3>
                <ul className="space-y-1.5">
                  {influenceMap.theological_commitments.map((c, i) => (
                    <li
                      key={i}
                      className="text-sm text-ink-light flex items-start gap-2"
                    >
                      <span
                        className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0"
                        style={{ backgroundColor: preacher.color }}
                      />
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            )}

          {/* Voice Signature */}
          {influenceMap?.voice_signature && (
            <div className="bg-white rounded-lg border border-border p-5">
              <h3 className="font-serif text-base font-semibold mb-3">
                Voice Signature
              </h3>
              <div className="space-y-3 text-sm text-ink-light">
                <div>
                  <p className="font-medium text-ink text-xs uppercase tracking-wide mb-1">
                    Vocabulary
                  </p>
                  <p>{influenceMap.voice_signature.vocabulary}</p>
                </div>
                <div>
                  <p className="font-medium text-ink text-xs uppercase tracking-wide mb-1">
                    Sentence Structure
                  </p>
                  <p>{influenceMap.voice_signature.sentence_structure}</p>
                </div>
                <div>
                  <p className="font-medium text-ink text-xs uppercase tracking-wide mb-1">
                    Use of Humor
                  </p>
                  <p>{influenceMap.voice_signature.humor}</p>
                </div>
                <div>
                  <p className="font-medium text-ink text-xs uppercase tracking-wide mb-1">
                    Approach to Doubt
                  </p>
                  <p>{influenceMap.voice_signature.doubt_handling}</p>
                </div>
              </div>
            </div>
          )}

          {/* Traditions */}
          {influenceMap?.traditions && influenceMap.traditions.length > 0 && (
            <div className="bg-white rounded-lg border border-border p-5">
              <h3 className="font-serif text-base font-semibold mb-3">
                Intellectual Traditions
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {influenceMap.traditions.map((t, i) => (
                  <span
                    key={i}
                    className="inline-block px-2.5 py-1 rounded-full text-xs border border-border text-ink-light"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Adjacent Voices */}
          {influenceMap?.adjacent_voices &&
            influenceMap.adjacent_voices.length > 0 && (
              <div className="bg-white rounded-lg border border-border p-5">
                <h3 className="font-serif text-base font-semibold mb-3">
                  You Might Also Explore
                </h3>
                <ul className="space-y-2">
                  {influenceMap.adjacent_voices.slice(0, 5).map((v, i) => (
                    <li key={i} className="text-sm">
                      <span className="font-medium text-ink">{v.name}</span>
                      <span className="text-ink-muted"> — {v.reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
        </aside>
      </div>
    </div>
  );
}
