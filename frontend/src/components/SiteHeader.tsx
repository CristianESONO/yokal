import Link from "next/link";
import { Logo } from "./Logo";
import { LOGIN_URL } from "../lib/appLinks";

const navLinks = [
  { label: "À propos", href: "/a-propos" },
  { label: "Fonctionnalités", href: "/#fonctionnalites" },
  { label: "Comment ça marche", href: "/#etapes" },
  { label: "Tarifs", href: "/#tarifs" },
  { label: "Contact", href: "/contact" },
];

export function SiteHeader() {
  return (
    <header className="pointer-events-none fixed inset-x-0 top-4 z-50 px-4">
      <nav className="pointer-events-auto mx-auto flex max-w-6xl items-center justify-between gap-4 rounded-full border border-black/5 bg-white/80 py-3 pl-6 pr-3 shadow-lg shadow-black/5 backdrop-blur-md">
        <Logo className="text-brand-950" />
        <div className="hidden items-center gap-8 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-slate-600 transition-colors hover:text-brand-700"
            >
              {link.label}
            </Link>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <a
            href={LOGIN_URL}
            className="hidden text-sm font-medium text-slate-600 transition-colors hover:text-brand-700 sm:inline-block"
          >
            Connexion
          </a>
          <Link
            href="/#tarifs"
            className="inline-flex items-center rounded-full bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/25 transition-transform hover:-translate-y-0.5"
          >
            Commencer
          </Link>
        </div>
      </nav>
    </header>
  );
}
