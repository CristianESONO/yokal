import type { Metadata } from "next";
import { SiteHeader } from "@/components/SiteHeader";
import { ContactForm } from "@/components/ContactForm";
import { Footer } from "@/components/footer";

export const metadata: Metadata = {
  title: "Contact — Yokalma",
  description:
    "Une question sur Yokalma, une demande de démo ou de partenariat ? Contactez l'équipe par formulaire, e-mail ou WhatsApp. Nous répondons sous 24 h ouvrées.",
};

const channels = [
  {
    label: "E-mail",
    value: "contact@yokalma.com",
    href: "mailto:contact@yokalma.com",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden>
        <rect x="3" y="5" width="18" height="14" rx="3" stroke="currentColor" strokeWidth="1.6" />
        <path d="m4 7 8 6 8-6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    label: "WhatsApp",
    value: "+221 77 883 39 37",
    href: "https://wa.me/221778833937",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden>
        <path d="M12 3a9 9 0 0 0-7.7 13.6L3 21l4.5-1.2A9 9 0 1 0 12 3Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
        <path d="M9 9c0 3.3 2.7 6 6 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    label: "Téléphone",
    value: "+221 77 883 39 37",
    href: "tel:+221778833937",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden>
        <path d="M6 4h3l1.5 4-2 1.5a11 11 0 0 0 5 5l1.5-2 4 1.5V17a2 2 0 0 1-2 2A14 14 0 0 1 5 6a2 2 0 0 1 1-2Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      </svg>
    ),
  },
];

export default function ContactPage() {
  return (
    <div className="flex flex-1 flex-col bg-white">
      <SiteHeader />

      {/* Intro */}
      <section className="relative overflow-hidden bg-brand-950 pt-32 text-white sm:pt-36">
        <div
          aria-hidden
          className="absolute -right-24 -top-24 h-80 w-80 rounded-full bg-accent/15 blur-3xl"
        />
        <div
          aria-hidden
          className="absolute -bottom-24 -left-16 h-72 w-72 rounded-full bg-brand-500/30 blur-3xl"
        />
        <div className="relative mx-auto max-w-4xl px-4 pb-20 text-center sm:px-6 sm:pb-24 lg:px-8">
          <span className="inline-flex items-center rounded-full border border-white/15 bg-white/10 px-4 py-2 text-xs font-medium uppercase tracking-wider text-white/90 backdrop-blur">
            Contact
          </span>
          <h1 className="mt-6 font-display text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
            Parlons de votre commerce
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-white/75">
            Une démo, une question sur les offres ou un projet de partenariat ?
            Écrivez-nous — notre équipe vous répond sous 24 h ouvrées.
          </p>
        </div>
      </section>

      {/* Coordonnées + formulaire */}
      <section className="bg-white py-20 sm:py-24">
        <div className="mx-auto grid max-w-7xl grid-cols-1 gap-12 px-4 sm:px-6 lg:grid-cols-5 lg:gap-16 lg:px-8">
          {/* Coordonnées */}
          <div className="lg:col-span-2">
            <h2 className="font-display text-2xl font-semibold text-brand-950">
              Nos canaux
            </h2>
            <p className="mt-3 text-slate-600">
              Choisissez le moyen qui vous convient. Pour une réponse rapide,
              WhatsApp reste le plus direct.
            </p>

            <div className="mt-8 space-y-4">
              {channels.map((channel) => (
                <a
                  key={channel.label}
                  href={channel.href}
                  className="flex items-center gap-4 rounded-2xl border border-zinc-100 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
                >
                  <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
                    {channel.icon}
                  </span>
                  <span>
                    <span className="block text-xs uppercase tracking-widest text-slate-400">
                      {channel.label}
                    </span>
                    <span className="block font-medium text-brand-950">
                      {channel.value}
                    </span>
                  </span>
                </a>
              ))}
            </div>

            <div className="mt-8 rounded-2xl bg-brand-50 p-5">
              <h3 className="font-display text-sm font-semibold uppercase tracking-widest text-brand-700">
                Horaires
              </h3>
              <p className="mt-2 text-sm text-slate-600">
                Du lundi au vendredi, 9 h – 18 h (GMT). Support WhatsApp aussi le
                samedi matin.
              </p>
            </div>
          </div>

          {/* Formulaire */}
          <div className="lg:col-span-3">
            <ContactForm />
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
