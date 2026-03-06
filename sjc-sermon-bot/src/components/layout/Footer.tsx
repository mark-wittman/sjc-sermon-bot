import Link from "next/link";
import { CrossIcon } from "@/components/ui/CrossIcon";
import { CATHEDRAL_URL } from "@/lib/constants";

export function Footer() {
  return (
    <footer className="border-t border-border bg-cream mt-auto">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-2 text-cathedral-red mb-3">
              <CrossIcon className="w-4 h-5" />
              <span className="font-serif text-base font-semibold">
                Saint John&apos;s Cathedral
              </span>
            </div>
            <p className="text-sm text-ink-muted leading-relaxed">
              1350 Washington Street
              <br />
              Denver, Colorado 80203
            </p>
            <a
              href={CATHEDRAL_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-cathedral-red hover:text-cathedral-red-light mt-2 inline-block"
            >
              sjcathedral.org
            </a>
          </div>

          <div>
            <h4 className="font-serif text-base font-semibold mb-3">
              Explore
            </h4>
            <div className="space-y-2">
              <Link
                href="/sermons"
                className="block text-sm text-ink-muted hover:text-cathedral-red transition-colors"
              >
                Sermon Archive
              </Link>
              <Link
                href="/preachers"
                className="block text-sm text-ink-muted hover:text-cathedral-red transition-colors"
              >
                Our Preachers
              </Link>
              <Link
                href="/chat"
                className="block text-sm text-ink-muted hover:text-cathedral-red transition-colors"
              >
                Ask a Question
              </Link>
              <Link
                href="/generate"
                className="block text-sm text-ink-muted hover:text-cathedral-red transition-colors"
              >
                Sermon Generator
              </Link>
            </div>
          </div>

          <div>
            <h4 className="font-serif text-base font-semibold mb-3">About</h4>
            <p className="text-sm text-ink-muted leading-relaxed">
              This sermon explorer uses AI to make the preaching tradition of
              Saint John&apos;s Cathedral searchable and interactive. It is not
              an official publication of the cathedral.
            </p>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-border-light text-center text-xs text-ink-muted">
          Built with care for the congregation of Saint John&apos;s Cathedral
        </div>
      </div>
    </footer>
  );
}
