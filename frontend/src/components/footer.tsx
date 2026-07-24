import { Logo } from "./Logo";
import { LOGIN_URL } from "../lib/appLinks";

const linkColumns = [
  {
    links: [
      { label: "Fonctionnalités", href: "#fonctionnalites" },
      { label: "Comment ça marche", href: "#etapes" },
      { label: "Tarifs", href: "#tarifs" },
      { label: "Connexion", href: LOGIN_URL },
    ],
  },
  {
    links: [
      { label: "À propos", href: "/a-propos" },
      { label: "Contact", href: "/contact" },
      { label: "Devenir partenaire", href: "#" },
      { label: "Aide", href: "#" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="w-full bg-brand-950 text-white">
      <div className="mx-auto w-full max-w-7xl px-4 py-24 sm:px-6 sm:py-32 lg:px-8">
        <div className="grid grid-cols-1 gap-14 lg:grid-cols-3">
          {/* Marque */}
          <div className="flex flex-col justify-between">
            <div>
              <Logo className="text-white" />
              <p className="mt-4 max-w-xs text-sm leading-relaxed text-white/70">
                La carte de fidélité qui ne se perd jamais.
              </p>
            </div>
            <div className="mt-6 space-y-1">
              <p className="text-sm text-white/70">+221 77 883 39 37</p>
              <p className="text-2xl font-light tracking-tight sm:text-3xl">
                contact@yokalma.com
              </p>
            </div>
          </div>

          {/* Newsletter */}
          <div>
            <h4 className="font-display text-2xl font-light tracking-tight sm:text-3xl">
              Restez informé
            </h4>
            <p className="mt-2 text-sm text-white/70">
              Recevez nos conseils pour fidéliser vos clients et les nouveautés
              Yokalma.
            </p>
            <form className="mt-5">
              <div className="flex items-center gap-3 border-b border-white/20 pb-2">
                <label htmlFor="newsletter-email" className="sr-only">
                  Adresse e-mail
                </label>
                <input
                  id="newsletter-email"
                  type="email"
                  placeholder="Votre e-mail"
                  className="flex-1 bg-transparent text-sm text-white placeholder-white/60 focus:outline-none"
                />
                <button
                  type="submit"
                  aria-label="S'inscrire à la newsletter"
                  className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-accent text-brand-950 transition-colors hover:bg-amber-300"
                >
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    aria-hidden
                  >
                    <path
                      d="M5 12h14m0 0-7-7m7 7-7 7"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </button>
              </div>
            </form>
          </div>

          {/* Liens */}
          <div className="grid grid-cols-2 gap-8">
            {linkColumns.map((column, index) => (
              <ul key={index} className="space-y-2">
                {column.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm font-medium text-white/80 transition hover:text-white"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            ))}
          </div>
        </div>

        {/* Barre du bas */}
        <div className="mt-16 grid grid-cols-1 items-center gap-4 border-t border-white/10 pt-10 sm:grid-cols-3">
          <p className="text-xs text-white/70">
            © {new Date().getFullYear()} Yokalma. Tous droits réservés.
          </p>
          <p className="text-sm text-white/70 sm:text-center">
            Pensé pour les commerces de proximité en Afrique de l&apos;Ouest.
          </p>
          <div className="flex items-center justify-start gap-4 sm:ml-auto sm:justify-end">
            <a
              href="#"
              className="text-xs font-medium text-white/80 transition hover:text-white"
            >
              Confidentialité
            </a>
            <a
              href="#"
              className="text-xs font-medium text-white/80 transition hover:text-white"
            >
              Conditions
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
