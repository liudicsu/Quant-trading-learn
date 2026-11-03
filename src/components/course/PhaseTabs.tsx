import { Link } from "@/i18n/navigation";
import { phases } from "@/lib/curriculum";

export function PhaseTabs({ currentId }: { currentId: string }) {
  return (
    <nav aria-label="phases" className="-mx-1 flex gap-1 overflow-x-auto pb-1">
      {phases.map((p) => (
        <Link
          key={p.id}
          href={`/phase/${p.slug}`}
          aria-current={p.id === currentId ? "page" : undefined}
          className={`shrink-0 rounded-lg px-3 py-1.5 text-sm transition-colors ${
            p.id === currentId ? "bg-white/10 text-white" : "text-zinc-300 hover:bg-white/5"
          }`}
        >
          {p.id}
        </Link>
      ))}
    </nav>
  );
}
