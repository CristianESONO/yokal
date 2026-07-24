import { REGISTER_URL } from "../lib/appLinks";

export function Cta() {
  return (
    <section className="bg-white">
      <div className="mx-auto max-w-7xl px-4 pb-8 pt-8 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-brand-950 px-6 py-14 text-center sm:px-12 sm:py-20">
          <div
            aria-hidden
            className="absolute -right-16 -top-16 h-64 w-64 rounded-full bg-accent/20 blur-3xl"
          />
          <div
            aria-hidden
            className="absolute -bottom-20 -left-10 h-64 w-64 rounded-full bg-brand-500/30 blur-3xl"
          />
          <h2 className="relative font-display text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Lancez votre carte de fidélité aujourd&apos;hui
          </h2>
          <p className="relative mx-auto mt-4 max-w-xl text-lg text-white/75">
            Rejoignez les commerces qui fidélisent leurs clients sans papier.
            Gratuit jusqu&apos;à 5 clients, sans carte bancaire.
          </p>
          <div className="relative mt-8 flex flex-col justify-center gap-3 sm:flex-row">
            <a
              href={REGISTER_URL}
              className="inline-flex items-center justify-center rounded-full bg-accent px-7 py-3.5 text-sm font-semibold text-brand-950 shadow-xl shadow-brand-950/40 transition-transform hover:-translate-y-0.5"
            >
              Créer mon programme
            </a>
            <a
              href="#etapes"
              className="inline-flex items-center justify-center rounded-full border border-white/25 px-7 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-white/10"
            >
              Voir une démo
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
