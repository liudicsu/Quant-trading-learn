import type { Metadata } from "next";
import type { ComponentProps, ComponentType, ReactNode } from "react";
import type { MDXComponents } from "mdx/types";
import { notFound } from "next/navigation";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";
import { withBasePath, withPageSlash } from "@/lib/basePath";
import { getLesson, lessonKey, phases } from "@/lib/curriculum";
import { asLocale, tr } from "@/lib/l10n";
import { findLessonBySlug, lessonHref } from "@/lib/lessonIndex";
import { lessonToc } from "@/lib/toc";
import { TaskChecklist } from "@/components/progress/TaskChecklist";
import { LessonCompleteButton } from "@/components/progress/LessonCompleteButton";
import { LessonStatusDot } from "@/components/progress/LessonStatusDot";
import { PhaseProgress } from "@/components/progress/PhaseProgress";
import { Quiz } from "@/components/mdx/Quiz";
import { Callout } from "@/components/mdx/Callout";
import { Formula } from "@/components/mdx/Formula";
import { H2 } from "@/components/lesson/Heading";
import { CodeBlock } from "@/components/mdx/CodeBlock";
import { Toc } from "@/components/lesson/Toc";
import { LessonIntro } from "@/components/lesson/LessonIntro";
import { Summary } from "@/components/mdx/Summary";

export const dynamicParams = false;

export function generateStaticParams() {
  return routing.locales.flatMap((locale) =>
    phases.flatMap((p) => p.lessons.map((l) => ({ locale, phase: p.slug, lesson: l.slug }))),
  );
}

type Params = PageProps<"/[locale]/phase/[phase]/[lesson]">;

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale, phase, lesson } = await params;
  const found = getLesson(phase, lesson);
  if (!found) return {};
  return { title: tr(found.lesson.title, locale), description: tr(found.lesson.summary, locale) };
}

async function loadContent(phaseId: string, slug: string, locale: string) {
  try {
    const mod = (await import(`@/content/${phaseId.toLowerCase()}/${slug}/${locale}.mdx`)) as {
      default: ComponentType<{ components?: MDXComponents }>;
    };
    return mod.default;
  } catch {
    return null;
  }
}

export default async function LessonPage({ params }: Params) {
  const { locale, phase: phaseSlug, lesson: lessonSlug } = await params;
  setRequestLocale(locale);
  const found = getLesson(phaseSlug, lessonSlug);
  if (!found) notFound();
  const { phase, lesson, index, prev, next } = found;
  const key = lessonKey(phase.id, lesson.slug);
  const loc = asLocale(locale);
  const t = await getTranslations("lesson");
  const tp = await getTranslations("phase");
  const tn = await getTranslations("nav");
  const Content = await loadContent(phase.id, lesson.slug, loc);
  if (!Content) notFound();
  const toc = await lessonToc(phase.id, lesson.slug, loc);

  const components: MDXComponents = {
    Quiz: (props: Omit<ComponentProps<typeof Quiz>, "lessonKey">) => <Quiz lessonKey={key} {...props} />,
    Callout,
    Formula,
    h2: H2,
    pre: CodeBlock,
    a: ({ href, ...rest }: ComponentProps<"a">) => (
      <a href={typeof href === "string" ? withPageSlash(withBasePath(href)) : href} {...rest} />
    ),
    img: ({ src, alt, ...rest }: ComponentProps<"img">) => (
      // eslint-disable-next-line @next/next/no-img-element
      <img src={typeof src === "string" ? withBasePath(src) : src} alt={alt ?? ""} loading="lazy" {...rest} />
    ),
    Summary: ({ children }: { children: ReactNode }) => <Summary title={t("summary")}>{children}</Summary>,
  };

  return (
    <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_260px] lg:gap-12">
      <article className="min-w-0 max-w-3xl">
        <nav className="flex flex-wrap items-center gap-1.5 text-xs text-zinc-500">
          <Link href="/" className="hover:text-zinc-300">{tn("home")}</Link>
          <span>/</span>
          <Link href={`/phase/${phase.slug}`} className="hover:text-zinc-300">
            {phase.id}
          </Link>
          <span>/</span>
          <span className="text-zinc-400">
            {t("lesson", { n: index + 1 })} {t("of", { total: phase.lessons.length })}
          </span>
        </nav>
        <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{tr(lesson.title, locale)}</h1>
        <p className="mt-4 text-lg leading-relaxed text-zinc-400">{tr(lesson.summary, locale)}</p>
        <p className="mt-3 text-xs text-zinc-500">
          {tp("hours", { n: lesson.hours })} · {lesson.tasks.length} {t("tasks")}
          {lesson.skippable ? ` · ${tp("skippable")}` : ""} ·{" "}
          {lesson.status === "ready" ? tp("statusReady") : tp("statusOutline")}
        </p>

        <LessonIntro
          objectives={lesson.goals.map((o) => tr(o, locale))}
          prereqs={lesson.prereqs.map((slug) => {
            const foundPrereq = findLessonBySlug(slug);
            if (!foundPrereq) throw new Error(`Unknown prerequisite "${slug}" in ${key}`);
            return {
              href: lessonHref(slug),
              label: `${foundPrereq.phase.id} · ${tr(foundPrereq.lesson.title, locale)}`,
            };
          })}
          labels={{
            objectives: t("objectives"),
            prereqs: t("prereqs"),
            none: t("noPrereqs"),
          }}
        />

        <Toc items={toc} title={t("onThisPage")} variant="inline" />

        <div className="prose-lesson mt-10">
          <Content components={components} />
        </div>

        <section id="tasks" className="mt-14 scroll-mt-20">
          <TaskChecklist
            lessonKey={key}
            title={t("tasks")}
            tasks={lesson.tasks.map((task) => ({ id: task.id, text: tr(task.text, locale) }))}
          />
        </section>

        <div className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-white/[0.06] pt-8">
          <LessonCompleteButton lessonKey={key} labels={{ markDone: t("markDone"), done: t("done") }} />
        </div>

        <nav className="mt-8 grid gap-3 sm:grid-cols-2" aria-label="lesson navigation">
          {prev ? (
            <Link
              href={`/phase/${phase.slug}/${prev.slug}`}
              className="group rounded-xl border border-white/10 p-4 transition-colors hover:border-white/20 hover:bg-white/[0.03]"
            >
              <span className="text-xs text-zinc-500">← {t("prev")}</span>
              <span className="mt-1 block text-sm font-medium text-zinc-200 group-hover:text-white">{tr(prev.title, locale)}</span>
            </Link>
          ) : (
            <Link
              href={`/phase/${phase.slug}`}
              className="group rounded-xl border border-white/10 p-4 transition-colors hover:border-white/20 hover:bg-white/[0.03]"
            >
              <span className="text-xs text-zinc-500">← {t("backToMonth")}</span>
              <span className="mt-1 block text-sm font-medium text-zinc-200 group-hover:text-white">{tr(phase.title, locale)}</span>
            </Link>
          )}
          {next ? (
            <Link
              href={`/phase/${phase.slug}/${next.slug}`}
              className="group rounded-xl border border-white/10 p-4 text-right transition-colors hover:border-white/20 hover:bg-white/[0.03] sm:col-start-2"
            >
              <span className="text-xs text-zinc-500">{t("next")} →</span>
              <span className="mt-1 block text-sm font-medium text-zinc-200 group-hover:text-white">{tr(next.title, locale)}</span>
            </Link>
          ) : (
            <Link
              href="/curriculum"
              className="group rounded-xl border border-sky-400/30 bg-sky-400/[0.04] p-4 text-right transition-colors hover:border-sky-400/60 sm:col-start-2"
            >
              <span className="text-xs text-sky-300/80">{t("finishMonth")} →</span>
              <span className="mt-1 block text-sm font-medium text-zinc-100">{tn("curriculum")}</span>
            </Link>
          )}
        </nav>
      </article>

      <aside className="mt-16 lg:mt-0">
        <div className="space-y-5 lg:sticky lg:top-20 lg:max-h-[calc(100vh-6rem)] lg:overflow-y-auto lg:pb-8">
          <Link href={`/phase/${phase.slug}`} className="block text-xs text-zinc-500 hover:text-zinc-300">
            {phase.id} · {tr(phase.title, locale)}
          </Link>
          <PhaseProgress phaseId={phase.id} label={tp("progress")} />
          <ol className="space-y-0.5">
            {phase.lessons.map((l, i) => {
              const active = l.slug === lesson.slug;
              return (
                <li key={l.slug}>
                  <Link
                    href={`/phase/${phase.slug}/${l.slug}`}
                    aria-current={active ? "page" : undefined}
                    className={`flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors ${
                      active ? "bg-white/[0.07] text-white" : "text-zinc-400 hover:bg-white/[0.04] hover:text-zinc-200"
                    }`}
                  >
                    <LessonStatusDot
                      lessonKey={lessonKey(phase.id, l.slug)}
                      labels={{ done: t("statusDone"), todo: t("statusTodo") }}
                    />
                    <span className="font-mono text-xs text-zinc-500">{i + 1}</span>
                    <span className="min-w-0 flex-1 truncate">{tr(l.title, locale)}</span>
                  </Link>
                </li>
              );
            })}
          </ol>
          <div className="hidden border-t border-white/[0.06] pt-4 lg:block">
            <Toc items={toc} title={t("onThisPage")} variant="side" />
          </div>
          <div className="space-y-1 border-t border-white/[0.06] pt-4 text-xs">
            <a href="#tasks" className="block text-zinc-500 hover:text-zinc-300">
              ↓ {t("tasks")}
            </a>
          </div>
        </div>
      </aside>
    </div>
  );
}
