import { phases } from "./curriculum";
import type { Lesson, Phase } from "./types";

export function findLessonBySlug(slug: string): { phase: Phase; lesson: Lesson } | undefined {
  for (const phase of phases) {
    const lesson = phase.lessons.find((l) => l.slug === slug);
    if (lesson) return { phase, lesson };
  }
  return undefined;
}

export function lessonHref(slug: string): string {
  const found = findLessonBySlug(slug);
  if (!found) throw new Error(`Unknown lesson slug "${slug}"`);
  return `/phase/${found.phase.slug}/${slug}`;
}
