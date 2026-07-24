import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { AboutUs } from "@/components/AboutUs";
import { Footer } from "@/components/footer";

export const metadata: Metadata = {
  title: "À propos — Yokalma",
  description:
    "Yokalma remplace les cartes de fidélité papier par une carte digitale dans Google Wallet. Découvrez notre mission : aider les commerces de proximité d'Afrique de l'Ouest à fidéliser leurs clients, simplement.",
};

const values = [
  {
    title: "Simplicité",
    description:
      "Aucune application à installer, aucun matériel à acheter. Une carte s'ajoute en un clic, un tampon s'ajoute d'un scan.",
  },
  {
    title: "Proximité",
    description:
      "Pensé pour les boulangeries, restaurants, salons et boutiques d'Afrique de l'Ouest, avec le partage par WhatsApp au cœur de l'expérience.",
  },
  {
    title: "Fidélité durable",
    description:
      "Les notifications Google Wallet rappellent vos offres à vos clients et les font revenir, naturellement.",
  },
  {
    title: "Accessible",
    description:
      "Un modèle gratuit pour démarrer, des offres claires en FCFA, sans engagement et sans surprise.",
  },
];

const stats = [
  { value: "0", label: "Application à installer" },
  { value: "1 clic", label: "Pour ajouter sa carte" },
  { value: "100%", label: "Dans Google Wallet" },
  { value: "FCFA", label: "Des tarifs adaptés" },
];

export default function AProposPage() {
  return (
    <div className="flex flex-1 flex-col bg-white">
      <SiteHeader />

      {/* Hero éditorial */}
      <AboutUs />

      {/* Mission */}
      <section className="bg-white py-20 sm:py-28">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <span className="text-sm font-semibold uppercase tracking-widest text-brand-600">
            Notre mission
          </span>
          <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight text-brand-950 sm:text-4xl">
            Donner aux commerces de proximité les outils des grandes enseignes
          </h2>
          <div className="mt-6 space-y-5 text-lg leading-relaxed text-slate-600">
            <p>
              En Afrique de l&apos;Ouest, les boulangeries, restaurants, salons
              et boutiques font vivre les quartiers. Pourtant, fidéliser leurs
              clients reste compliqué : cartes papier perdues, tampons oubliés,
              aucune donnée pour comprendre qui revient.
            </p>
            <p>
              Yokalma change cela. Le commerçant crée son programme en quelques
              minutes, le client ajoute sa carte à Google Wallet sans rien
              installer, et chaque passage se transforme en tampon d&apos;un
              simple scan. Les notifications font revenir les clients, et les
              statistiques aident le commerçant à mieux les connaître.
            </p>
            <p>
              Notre objectif : rendre la fidélisation aussi simple qu&apos;un
              message WhatsApp, accessible à tous les commerces, où qu&apos;ils
              soient.
            </p>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-brand-50 py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 lg:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="font-display text-3xl font-semibold text-brand-700 sm:text-4xl">
                  {stat.value}
                </div>
                <div className="mt-2 text-sm text-slate-500">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Valeurs */}
      <section className="bg-white py-20 sm:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <span className="text-sm font-semibold uppercase tracking-widest text-brand-600">
              Nos valeurs
            </span>
            <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight text-brand-950 sm:text-4xl">
              Ce qui guide Yokalma
            </h2>
          </div>
          <div className="mt-14 grid grid-cols-1 gap-6 sm:grid-cols-2">
            {values.map((value) => (
              <div
                key={value.title}
                className="rounded-2xl border border-zinc-100 bg-white p-7 shadow-sm"
              >
                <h3 className="font-display text-xl font-semibold text-brand-950">
                  {value.title}
                </h3>
                <p className="mt-3 leading-relaxed text-slate-600">
                  {value.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-white">
        <div className="mx-auto max-w-7xl px-4 pb-8 sm:px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-3xl bg-brand-950 px-6 py-14 text-center sm:px-12 sm:py-20">
            <div
              aria-hidden
              className="absolute -right-16 -top-16 h-64 w-64 rounded-full bg-accent/20 blur-3xl"
            />
            <h2 className="relative font-display text-3xl font-semibold tracking-tight text-white sm:text-4xl">
              Prêt à fidéliser autrement ?
            </h2>
            <p className="relative mx-auto mt-4 max-w-xl text-lg text-white/75">
              Lancez votre carte de fidélité digitale aujourd&apos;hui. Gratuit
              jusqu&apos;à 5 clients, sans carte bancaire.
            </p>
            <div className="relative mt-8 flex flex-col justify-center gap-3 sm:flex-row">
              <Link
                href="/#tarifs"
                className="inline-flex items-center justify-center rounded-full bg-accent px-7 py-3.5 text-sm font-semibold text-brand-950 shadow-xl shadow-brand-950/40 transition-transform hover:-translate-y-0.5"
              >
                Créer mon programme
              </Link>
              <Link
                href="/#etapes"
                className="inline-flex items-center justify-center rounded-full border border-white/25 px-7 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-white/10"
              >
                Voir comment ça marche
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
