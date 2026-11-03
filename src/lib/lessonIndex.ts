import { months } from "./curriculum";
import type { Lesson, Month } from "./types";

export function findLessonBySlug(slug: string): { month: Month; lesson: Lesson } | undefined {
  for (const month of months) {
    const lesson = month.lessons.find((l) => l.slug === slug);
    if (lesson) return { month, lesson };
  }
  return undefined;
}

export function lessonHref(slug: string): string {
  const found = findLessonBySlug(slug);
  if (!found) throw new Error(`Unknown lesson slug "${slug}"`);
  return `/month/${found.month.slug}/${slug}`;
}
