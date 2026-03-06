import Link from "next/link";
import { getAllSermons } from "@/lib/data";
import { PREACHERS } from "@/lib/preachers";
import { SermonCard } from "@/components/sermon/SermonCard";
import { PreacherCard } from "@/components/preacher/PreacherCard";
import { CrossIcon } from "@/components/ui/CrossIcon";

export default function HomePage() {
  const sermons = getAllSermons();
  const recentSermons = sermons.slice(0, 6);
  const preacherList = Object.values(PREACHERS);
  const preacherCounts = sermons.reduce(
    (acc, s) => {
      acc[s.preacher] = (acc[s.preacher] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div>
      {/* Hero */}
      <section className="relative bg-gradient-to-b from-cathedral-red to-cathedral-red-light text-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-20 sm:py-28 text-center">
          <CrossIcon className="w-8 h-12 mx-auto mb-6 opacity-60" />
          <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight">
            Explore the Sermons of
            <br />
            Saint John&apos;s Cathedral
          </h1>
          <p className="mt-4 text-lg sm:text-xl text-white/80 max-w-2xl mx-auto">
            Search, discover, and engage with the preaching tradition of Denver&apos;s cathedral parish
          </p>

          <div className="mt-8 max-w-xl mx-auto">
            <Link
              href="/sermons"
              className="inline-block w-full sm:w-auto"
            >
              <div className="flex items-center bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg px-5 py-3 text-left hover:bg-white/20 transition-colors">
                <svg className="w-5 h-5 text-white/60 mr-3 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span className="text-white/60">Search {sermons.length} sermons...</span>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* Recent Sermons */}
      <section className="mx-auto max-w-6xl px-4 sm:px-6 py-14">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-serif text-2xl font-semibold">Recent Sermons</h2>
          <Link
            href="/sermons"
            className="text-sm text-cathedral-red hover:text-cathedral-red-light transition-colors"
          >
            View all &rarr;
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {recentSermons.map((sermon) => (
            <SermonCard key={sermon.slug} sermon={sermon} />
          ))}
        </div>
      </section>

      {/* Preachers */}
      <section className="mx-auto max-w-6xl px-4 sm:px-6 py-14 border-t border-border-light">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-serif text-2xl font-semibold">Our Preachers</h2>
          <Link
            href="/preachers"
            className="text-sm text-cathedral-red hover:text-cathedral-red-light transition-colors"
          >
            View profiles &rarr;
          </Link>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {preacherList.map((p) => (
            <PreacherCard
              key={p.slug}
              preacher={p}
              sermonCount={preacherCounts[p.name] || 0}
            />
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-4 sm:px-6 py-14 border-t border-border-light">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            href="/chat"
            className="group p-6 bg-white rounded-lg border border-border hover:shadow-md hover:border-cathedral-red/20 transition-all"
          >
            <div className="w-10 h-10 rounded-lg bg-cathedral-red/10 flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-cathedral-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="font-serif text-lg font-semibold group-hover:text-cathedral-red transition-colors">
              Ask a Question
            </h3>
            <p className="mt-2 text-sm text-ink-muted leading-relaxed">
              Ask theological questions and get answers grounded in real sermons, with citations.
            </p>
          </Link>

          <Link
            href="/preachers"
            className="group p-6 bg-white rounded-lg border border-border hover:shadow-md hover:border-cathedral-red/20 transition-all"
          >
            <div className="w-10 h-10 rounded-lg bg-cathedral-red/10 flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-cathedral-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 className="font-serif text-lg font-semibold group-hover:text-cathedral-red transition-colors">
              Explore Preachers
            </h3>
            <p className="mt-2 text-sm text-ink-muted leading-relaxed">
              Discover each preacher&apos;s intellectual influences, theological commitments, and unique voice.
            </p>
          </Link>

          <Link
            href="/generate"
            className="group p-6 bg-white rounded-lg border border-border hover:shadow-md hover:border-cathedral-red/20 transition-all"
          >
            <div className="w-10 h-10 rounded-lg bg-cathedral-red/10 flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-cathedral-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <h3 className="font-serif text-lg font-semibold group-hover:text-cathedral-red transition-colors">
              Sermon Generator
            </h3>
            <p className="mt-2 text-sm text-ink-muted leading-relaxed">
              Generate a sermon in any preacher&apos;s voice for a given occasion and lectionary readings.
            </p>
          </Link>
        </div>
      </section>
    </div>
  );
}
