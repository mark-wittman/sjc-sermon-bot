import { NextResponse } from "next/server";
import { getAllSermons } from "@/lib/data";

export async function GET() {
  const sermons = getAllSermons().map((s) => ({
    title: s.title,
    date: s.date,
    preacher: s.preacher,
    slug: s.slug,
    description: s.description,
    duration: s.duration,
    word_count: s.word_count,
    audio_url: s.audio_url,
  }));

  return NextResponse.json(sermons);
}
