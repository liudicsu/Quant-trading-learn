import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { LocaleSwitcher } from "./LocaleSwitcher";
import { NavLink } from "./NavLink";

export async function Header() {
  const t = await getTranslations("nav");
  const site = await getTranslations("site");
  return (
    <header className="sticky top-0 z-40 border-b border-white/[0.06] bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-4 sm:px-6">
        <Link href="/" className="flex shrink-0 items-center gap-2 text-sm font-semibold text-white">
          <svg aria-hidden viewBox="0 0 24 24" className="h-5 w-5 text-sky-400" fill="none" stroke="currentColor" strokeWidth="1.6">
            <path d="M3 17l4-6 4 3 5-8 5 11" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M3 20h18" strokeLinecap="round" />
          </svg>
          <span>{site("name")}</span>
        </Link>
        <nav className="ml-2 hidden items-center gap-0.5 md:flex">
          <NavLink href="/curriculum" match="/curriculum">{t("curriculum")}</NavLink>
          <NavLink href="/phase/foundations" match="/phase">{t("roadmap")}</NavLink>
          <NavLink href="/about">{t("about")}</NavLink>
        </nav>
        <div className="ml-auto flex shrink-0 items-center gap-2">
          <LocaleSwitcher />
        </div>
      </div>
      <nav className="flex items-center gap-1 overflow-x-auto border-t border-white/[0.06] px-3 py-1.5 md:hidden">
        <NavLink href="/curriculum" match="/curriculum">{t("curriculum")}</NavLink>
        <NavLink href="/phase/foundations" match="/phase">{t("roadmap")}</NavLink>
        <NavLink href="/about">{t("about")}</NavLink>
      </nav>
    </header>
  );
}
