import { notFound } from "next/navigation";
import { getAllSermons, getSermonBySlug } from "@/lib/data";
import { formatDate, formatWordCount } from "@/lib/formatters";
import { getPreacherByName } from "@/lib/preachers";
import Link from "next/link";
import { SermonTranscriptPlayer } from "@/components/sermon/SermonTranscriptPlayer";

export async function generateStaticParams() {
  return getAllSermons().map((s) => ({ slug: s.slug }));
}

export default async function SermonDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const sermon = getSermonBySlug(slug);
  if (!sermon) notFound();

  const preacher = getPreacherByName(sermon.preacher);

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10">
      <Link
        href="/sermons"
        className="inline-flex items-center text-sm text-ink-muted hover:text-cathedral-red transition-colors mb-6"
      >
        <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to sermons
      </Link>

      <div className="lg:grid lg:grid-cols-3 lg:gap-10">
        {/* Main content */}
        <div className="lg:col-span-2">
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              {preacher && (
                <Link
                  href={`/preachers/${preacher.slug}`}
                  className="inline-block px-2.5 py-0.5 rounded text-xs font-medium text-white hover:opacity-90 transition-opacity"
                  style={{ backgroundColor: preacher.color }}
                >
                  {preacher.name}
                </Link>
              )}
              <span className="text-sm text-ink-muted">
                {formatDate(sermon.date)}
              </span>
            </div>
            <h1 className="font-serif text-3xl sm:text-4xl font-bold leading-tight">
              {sermon.title}
            </h1>
            {sermon.word_count && (
              <p className="mt-2 text-sm text-ink-muted">
                {formatWordCount(sermon.word_count)}
                {sermon.duration && ` · ${sermon.duration}`}
              </p>
            )}
          </div>

          <SermonTranscriptPlayer
            audioUrl={sermon.audio_url}
            transcript={sermon.transcript}
            segments={sermon.segments}
            sections={sermon.sections}
          />
        </div>

        {/* Sidebar */}
        <aside className="mt-8 lg:mt-0 space-y-6">
          {/* Preacher mini card */}
          {preacher && (
            <Link
              href={`/preachers/${preacher.slug}`}
              className="block bg-white rounded-lg border border-border p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center text-white font-serif font-bold"
                  style={{ backgroundColor: preacher.color }}
                >
                  {preacher.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
                <div>
                  <p className="font-serif font-semibold">{preacher.name}</p>
                  <p className="text-xs text-ink-muted">{preacher.role}</p>
                </div>
              </div>
            </Link>
          )}

          {/* Sermon Insights */}
          {sermon.insights && (
            <div className="bg-white rounded-lg border border-border p-5">
              <h3 className="font-serif text-base font-semibold mb-3">
                Sermon Insights
              </h3>

              {sermon.insights.readings.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-xs font-semibold uppercase tracking-wide text-ink-muted mb-2">
                    Readings
                  </h4>
                  <ul className="space-y-1.5">
                    {sermon.insights.readings.map((r, i) => (
                      <li key={i} className="text-sm group">
                        <span className="font-medium text-ink">{r.name}</span>
                        <p className="text-xs text-ink-light leading-relaxed mt-0.5">
                          {r.context}
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {sermon.insights.people.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-xs font-semibold uppercase tracking-wide text-ink-muted mb-2">
                    Referenced
                  </h4>
                  <ul className="space-y-1.5">
                    {sermon.insights.people.map((p, i) => (
                      <li key={i} className="text-sm group">
                        <span className="font-medium text-ink">{p.name}</span>
                        <p className="text-xs text-ink-light leading-relaxed mt-0.5">
                          {p.context}
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {sermon.insights.theme && (
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wide text-ink-muted mb-2">
                    Theme
                  </h4>
                  <p className="text-sm text-ink-light leading-relaxed">
                    {sermon.insights.theme}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Description */}
          {sermon.description && (
            <div className="bg-white rounded-lg border border-border p-5">
              <h3 className="font-serif text-base font-semibold mb-3">
                About this sermon
              </h3>
              <p className="text-sm text-ink-light leading-relaxed">
                {sermon.description}
              </p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
