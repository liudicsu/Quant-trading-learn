import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";
import { getPhase, lessonKey, phases, phaseStats } from "@/lib/curriculum";
import { tr } from "@/lib/l10n";
import { PhaseProgress } from "@/components/progress/PhaseProgress";
import { LessonStatusDot } from "@/components/progress/LessonStatusDot";
import { PhaseTabs } from "@/components/course/PhaseTabs";
import { TaskChecklist } from "@/components/progress/TaskChecklist";

export const dynamicParams = false;

export function generateStaticParams() {
  return routing.locales.flatMap((locale) => phases.map((p) => ({ locale, phase: p.slug })));
}

export async function generateMetadata({ params }: PageProps<"/[locale]/phase/[phase]">): Promise<Metadata> {
  const { locale, phase: slug } = await params;
  const phase = getPhase(slug);
  if (!phase) return {};
  return { title: `${phase.id} · ${tr(phase.title, locale)}`, description: tr(phase.goal, locale) };
}

export default async function PhasePage({ params }: PageProps<"/[locale]/phase/[phase]">) {
  const { locale, phase: slug } = await params;
  setRequestLocale(locale);
  const phase = getPhase(slug);
  if (!phase) notFound();
  const t = await getTranslations("phase");
  const tl = await getTranslations("lesson");
  const stats = phaseStats(phase);

  return (
    <div className="space-y-12">
      <PhaseTabs currentId={phase.id} />
      <header className="max-w-3xl">
        <span className="font-mono text-xs text-zinc-500">{phase.id}</span>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{tr(phase.title, locale)}</h1>
        <p className="mt-5 text-xs font-medium uppercase tracking-wider text-zinc-500">{t("goal")}</p>
        <p className="mt-1.5 text-lg leading-relaxed text-zinc-300">{tr(phase.goal, locale)}</p>
        <p className="mt-2 text-sm text-zinc-500">{phase.cluster}</p>
        <p className="mt-4 text-sm text-zinc-400">
          {t("stats", { lessons: stats.lessons, hours: stats.hours, tasks: stats.tasks })}
        </p>
        <div className="mt-6 max-w-md">
          <PhaseProgress phaseId={phase.id} label={t("progress")} />
        </div>
      </header>

      <section>
        <h2 className="text-sm font-medium text-zinc-400">{t("lessons")}</h2>
        <ol className="mt-4 divide-y divide-white/[0.06] overflow-hidden rounded-xl border border-white/10 bg-card">
          {phase.lessons.map((l, i) => (
            <li key={l.slug}>
              <Link
                href={`/phase/${phase.slug}/${l.slug}`}
                className="group flex items-start gap-4 p-5 transition-colors hover:bg-white/[0.03]"
              >
                <span className="mt-0.5 w-6 shrink-0 font-mono text-sm text-zinc-500">{String(i + 1).padStart(2, "0")}</span>
                <div className="min-w-0 flex-1">
                  <h3 className="font-medium text-zinc-100 group-hover:text-white">{tr(l.title, locale)}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-zinc-400">{tr(l.summary, locale)}</p>
                  <p className="mt-2 text-xs text-zinc-500">
                    {t("hours", { n: l.hours })} · {l.tasks.length} {tl("tasks")}
                    {l.skippable ? ` · ${t("skippable")}` : ""} ·{" "}
                    {l.status === "ready" ? t("statusReady") : t("statusOutline")}
                  </p>
                </div>
                <span className="mt-2">
                  <LessonStatusDot
                    lessonKey={lessonKey(phase.id, l.slug)}
                    labels={{ done: tl("statusDone"), todo: tl("statusTodo") }}
                  />
                </span>
              </Link>
            </li>
          ))}
        </ol>
        <div className="mt-6">
          <Link
            href={`/phase/${phase.slug}/${phase.lessons[0].slug}`}
            className="inline-flex h-10 items-center rounded-xl bg-white px-4 text-sm font-medium text-black hover:bg-zinc-200"
          >
            {t("start")} →
          </Link>
        </div>
      </section>

      <section id="done-when" className="max-w-3xl scroll-mt-20">
        <TaskChecklist
          lessonKey={`${phase.id}/phase-done`}
          title={t("milestones")}
          tasks={phase.lessons.flatMap((l) =>
            (l.doneWhen ?? []).map((d, i) => ({
              id: `${l.slug}-dw${i}`,
              text: `${tr(l.title, locale)}: ${tr(d, locale)}`,
            })),
          )}
        />
      </section>
    </div>
  );
}
