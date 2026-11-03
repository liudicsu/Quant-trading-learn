import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { phases, lessonKey, phaseStats } from "@/lib/curriculum";
import { tr } from "@/lib/l10n";
import { LessonStatusDot } from "@/components/progress/LessonStatusDot";
import { PhaseProgress } from "@/components/progress/PhaseProgress";

export async function generateMetadata({ params }: PageProps<"/[locale]/curriculum">): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "curriculum" });
  return { title: t("title") };
}

export default async function CurriculumPage({ params }: PageProps<"/[locale]/curriculum">) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("curriculum");
  const tp = await getTranslations("phase");
  const tl = await getTranslations("lesson");

  return (
    <div className="space-y-12">
      <header className="max-w-3xl">
        <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">{t("title")}</h1>
        <p className="mt-4 text-lg text-zinc-400">{t("lead")}</p>
      </header>

      {phases.map((ph) => {
        const stats = phaseStats(ph);
        return (
          <section key={ph.id} className="scroll-mt-20" id={ph.slug}>
            <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="font-mono text-xs text-zinc-500">
                  {ph.id} · {t("phase")} · {tp("hours", { n: stats.hours })}
                </p>
                <h2 className="mt-1 text-xl font-semibold text-white">
                  <Link href={`/phase/${ph.slug}`} className="hover:text-sky-300">
                    {tr(ph.title, locale)}
                  </Link>
                </h2>
                <p className="mt-1 text-sm text-zinc-500">{ph.cluster}</p>
              </div>
              <div className="w-48">
                <PhaseProgress phaseId={ph.id} label={tp("progress")} />
              </div>
            </div>
            <ol className="divide-y divide-white/[0.06] overflow-hidden rounded-xl border border-white/10 bg-card">
              {ph.lessons.map((l, i) => (
                <li key={l.slug}>
                  <Link
                    href={`/phase/${ph.slug}/${l.slug}`}
                    className="group flex items-start gap-4 p-4 transition-colors hover:bg-white/[0.03]"
                  >
                    <span className="mt-0.5 w-6 shrink-0 font-mono text-sm text-zinc-500">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <div className="min-w-0 flex-1">
                      <h3 className="font-medium text-zinc-100 group-hover:text-white">{tr(l.title, locale)}</h3>
                      <p className="mt-1 text-sm text-zinc-400">{tr(l.summary, locale)}</p>
                      <p className="mt-2 text-xs text-zinc-500">
                        {tp("hours", { n: l.hours })}
                        {l.skippable ? ` · ${tp("skippable")}` : ""} ·{" "}
                        {l.status === "ready" ? tp("statusReady") : tp("statusOutline")}
                      </p>
                    </div>
                    <span className="mt-2">
                      <LessonStatusDot
                        lessonKey={lessonKey(ph.id, l.slug)}
                        labels={{ done: tl("statusDone"), todo: tl("statusTodo") }}
                      />
                    </span>
                  </Link>
                </li>
              ))}
            </ol>
          </section>
        );
      })}
    </div>
  );
}
