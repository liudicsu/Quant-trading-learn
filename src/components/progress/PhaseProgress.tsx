"use client";

import { phases } from "@/lib/curriculum";
import { phaseProgressStats, useHydrated, useProgress } from "@/lib/progress";
import { ProgressBar } from "./ProgressBar";

export function PhaseProgress({ phaseId, label }: { phaseId: string; label: string }) {
  const progress = useProgress();
  const hydrated = useHydrated();
  const phase = phases.find((entry) => entry.id === phaseId);
  const percent = hydrated && phase ? phaseProgressStats(progress, phase).percent : 0;
  return <ProgressBar value={percent} label={label} />;
}
