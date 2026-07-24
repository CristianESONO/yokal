"use client";

import { useState } from "react";
import { REGISTER_URL } from "../lib/appLinks";

type PlanKey = "gratuit" | "boutique" | "premium" | "entreprise";

type Plan = {
  key: PlanKey;
  badge: string;
  price: string;
  unit: string;
  description: string;
  metrics: { clients: string; programmes: string; support: string };
  features: string[];
  cta: string;
  note: string;
};

const plans: Record<PlanKey, Plan> = {
  gratuit: {
    key: "gratuit",
    badge: "Gratuit",
    price: "0",
    unit: "FCFA / mois",
    description:
      "Un environnement léger pour tester Yokalma et lancer votre première carte de fidélité.",
    metrics: { clients: "5", programmes: "1", support: "E-mail" },
    features: [
      "1 carte de fidélité",
      "Partage WhatsApp & QR Code",
      "Carte Google Wallet",
      "Support par e-mail",
    ],
    cta: "Commencer gratuitement",
    note: "Idéal pour découvrir Yokalma",
  },
  boutique: {
    key: "boutique",
    badge: "Boutique",
    price: "5 000",
    unit: "FCFA / mois",
    description:
      "Pensé pour les commerces qui fidélisent au quotidien, avec notifications et statistiques.",
    metrics: { clients: "Illimités", programmes: "1", support: "WhatsApp" },
    features: [
      "Clients illimités",
      "Notifications Google Wallet",
      "Statistiques de fidélité",
      "Support par WhatsApp",
    ],
    cta: "Choisir Boutique",
    note: "Le choix des commerces de proximité",
  },
  premium: {
    key: "premium",
    badge: "Premium",
    price: "10 000",
    unit: "FCFA / mois",
    description:
      "Pour aller plus loin dans la relation client, avec plusieurs programmes et campagnes ciblées.",
    metrics: { clients: "Illimités", programmes: "Plusieurs", support: "Prioritaire" },
    features: [
      "Tout de l'offre Boutique",
      "Plusieurs programmes de fidélité",
      "Offres et campagnes ciblées",
      "Statistiques avancées",
    ],
    cta: "Choisir Premium",
    note: "Pour développer votre fidélisation",
  },
  entreprise: {
    key: "entreprise",
    badge: "Entreprise",
    price: "Sur devis",
    unit: "selon vos besoins",
    description:
      "Un environnement complet pour les réseaux et franchises multi-boutiques, avec accompagnement dédié.",
    metrics: { clients: "Illimités", programmes: "Multi-sites", support: "Dédié" },
    features: [
      "Multi-établissements",
      "Comptes et rôles d'équipe",
      "Intégrations sur mesure",
      "Accompagnement dédié",
    ],
    cta: "Nous contacter",
    note: "Pour les réseaux et franchises",
  },
};

const planOrder: PlanKey[] = ["gratuit", "boutique", "premium", "entreprise"];

const testimonials = [
  {
    quote:
      "Avant, mes clients perdaient toujours leur carte papier. Avec Yokalma, tout est dans leur téléphone et ils reviennent plus souvent.",
    author: "Boulangerie Le Bon Pain — Dakar",
    highlighted: true,
  },
  {
    quote:
      "Je partage la carte par WhatsApp en deux secondes. Mes clients l'adoptent tout de suite, sans rien installer.",
    author: "Restaurant Chez Fatou — Abidjan",
  },
  {
    quote:
      "Les notifications Google Wallet ramènent mes clients. Mon salon est plein le week-end grâce aux rappels.",
    author: "Salon Élégance — Cotonou",
  },
];

export function Pricing2() {
  const [active, setActive] = useState<PlanKey>("boutique");
  const plan = plans[active];

  return (
    <section id="tarifs" className="relative overflow-hidden bg-brand-50 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 md:px-12">
        <div className="grid grid-cols-1 items-center gap-16 md:grid-cols-2 lg:gap-24">
          {/* Colonne gauche : titre + témoignages */}
          <div>
            <div className="mb-8 h-0.5 w-16 rounded-full bg-gradient-to-r from-brand-500 to-brand-200" />
            <span className="text-sm font-semibold uppercase tracking-widest text-brand-600">
              Tarifs
            </span>
            <h2 className="mt-3 mb-14 font-display text-3xl font-light tracking-tight text-brand-950 md:text-4xl">
              Ils fidélisent déjà avec Yokalma
            </h2>

            <div className="flex flex-col gap-10">
              {testimonials.map((t) => (
                <div
                  key={t.author}
                  className={`group relative border-l pl-8 ${
                    t.highlighted ? "border-brand-400/60" : "border-brand-200"
                  }`}
                >
                  <div
                    className={`absolute left-[-4px] top-1 h-2 w-2 rounded-full ${
                      t.highlighted
                        ? "bg-brand-500"
                        : "bg-brand-300 opacity-0 transition-opacity group-hover:opacity-100"
                    }`}
                  />
                  <p className="mb-5 text-lg font-light italic leading-relaxed text-slate-600">
                    “{t.quote}”
                  </p>
                  <div className="text-[10px] font-medium uppercase tracking-widest text-brand-950">
                    {t.author}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Colonne droite : panneau tarifaire interactif */}
          <div className="relative">
            <div
              aria-hidden
              className="pointer-events-none absolute -inset-8 rounded-[4rem] bg-white/40 blur-3xl"
            />
            <div className="relative flex min-h-[650px] flex-col justify-between rounded-[3rem] border border-white/70 bg-white/70 p-8 shadow-[0_30px_100px_rgba(30,64,175,0.15)] backdrop-blur-2xl md:p-12">
              {/* Haut */}
              <div>
                <div className="mb-8 flex flex-col gap-6">
                  <div className="flex items-center justify-between gap-6">
                    <h3 className="font-display text-2xl font-light tracking-tight text-brand-950">
                      Choisissez votre offre
                    </h3>
                    <div className="rounded-full border border-brand-300/50 px-4 py-1.5 text-[10px] font-medium uppercase tracking-widest text-brand-600">
                      {plan.badge}
                    </div>
                  </div>

                  {/* Onglets */}
                  <div className="flex w-fit max-w-full flex-wrap gap-1 rounded-full border border-brand-100 bg-white/80 p-1.5 shadow-sm">
                    {planOrder.map((key) => {
                      const isActive = key === active;
                      return (
                        <button
                          key={key}
                          type="button"
                          onClick={() => setActive(key)}
                          aria-pressed={isActive}
                          className={`rounded-full px-4 py-2 text-[10px] font-medium uppercase tracking-widest transition-all ${
                            isActive
                              ? "bg-brand-950 text-white"
                              : "text-slate-500 hover:text-brand-950"
                          }`}
                        >
                          {plans[key].badge}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Prix */}
                <div className="mb-10">
                  <div className="mb-4 flex items-baseline gap-3">
                    <span className="font-display text-5xl font-light tracking-tight text-brand-950 md:text-6xl">
                      {plan.price}
                    </span>
                    <span className="text-xs font-light uppercase tracking-widest text-slate-500">
                      {plan.unit}
                    </span>
                  </div>
                  <p className="max-w-lg text-sm font-light leading-relaxed text-slate-500 md:text-base">
                    {plan.description}
                  </p>
                </div>

                {/* Métriques */}
                <div className="mb-10 grid grid-cols-3 gap-3">
                  {[
                    { label: "Clients", value: plan.metrics.clients },
                    { label: "Programmes", value: plan.metrics.programmes },
                    { label: "Support", value: plan.metrics.support },
                  ].map((m) => (
                    <div
                      key={m.label}
                      className="rounded-2xl border border-brand-100 bg-white/80 p-4"
                    >
                      <div className="mb-2 text-[10px] uppercase tracking-widest text-slate-400">
                        {m.label}
                      </div>
                      <div className="text-base font-light tracking-tight text-brand-950">
                        {m.value}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Fonctionnalités */}
                <div className="mb-10 space-y-4">
                  {plan.features.map((feature) => (
                    <div
                      key={feature}
                      className="flex items-center gap-4 text-sm font-light text-slate-600"
                    >
                      <span className="h-1.5 w-1.5 rounded-full bg-brand-500" />
                      {feature}
                    </div>
                  ))}
                </div>
              </div>

              {/* Bas */}
              <div className="space-y-4">
                <a
                  href={REGISTER_URL}
                  className="block w-full rounded-2xl bg-gradient-to-r from-brand-700 to-brand-500 py-4 text-center text-[10px] font-semibold uppercase tracking-widest text-white transition-all hover:shadow-[0_10px_40px_rgba(30,64,175,0.35)]"
                >
                  {plan.cta}
                </a>
                <div className="text-center text-[11px] tracking-wide text-slate-400">
                  {plan.note}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Pricing2;
