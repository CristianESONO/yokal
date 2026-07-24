import Image from "next/image";
import Link from "next/link";
import baobab from "../../public/img/baobab_2.png";
import phoneApp from "../../public/img/phone.png";

const oswald = { fontFamily: "var(--font-oswald)" } as const;

export function AboutUs() {
  return (
    <section className="relative overflow-hidden bg-brand-950 pb-20 pt-28 text-white">
      {/* Lignes verticales décoratives */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 z-0 mx-auto flex max-w-[1800px] justify-between px-6 opacity-10 md:px-12"
      >
        <div className="h-full w-px bg-white" />
        <div className="h-full w-px bg-white" />
        <div className="h-full w-px bg-white" />
        <div className="hidden h-full w-px bg-white lg:block" />
      </div>
      {/* Halo */}
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/4 top-1/2 h-[500px] w-[500px] -translate-y-1/2 rounded-full bg-brand-500 opacity-25 blur-[120px]"
      />

      {/* Hero principal */}
      <div className="relative z-10 mx-auto grid max-w-[1800px] grid-cols-1 items-center gap-12 px-6 md:px-12 lg:grid-cols-12 lg:gap-20">
        {/* Colonne gauche */}
        <div className="flex flex-col justify-center lg:col-span-7">
          <div className="mb-6 flex items-center gap-4">
            <span className="text-sm uppercase tracking-widest text-white/40">
              01 // Notre histoire
            </span>
            <div className="h-px w-12 bg-white/20" />
          </div>

          <h1
            style={oswald}
            className="mb-8 text-7xl font-semibold uppercase leading-[0.85] tracking-tight text-white md:text-[9rem]"
          >
            Yokalma
          </h1>

          {/* Onde sonore décorative */}
          <div className="mb-10 flex h-16 w-full max-w-md items-center text-accent/40">
            <svg
              viewBox="0 0 400 60"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              aria-hidden
            >
              <path
                d="M0 30 Q 10 30, 20 30 T 40 30 T 60 20 T 80 40 T 100 10 T 120 50 T 140 20 T 160 40 T 180 30 T 200 30 T 220 30 T 240 30"
                className="opacity-50"
              />
              <path d="M140 30 Q 150 10, 160 30 T 180 50 T 200 10 T 220 50 T 240 20 T 260 40 T 280 30 T 300 30 T 320 30" />
              <path
                d="M280 30 Q 290 35, 300 30 T 320 25 T 340 35 T 360 30 T 380 30 T 400 30"
                className="opacity-50"
              />
            </svg>
          </div>

          <p className="mb-12 max-w-md text-lg font-medium leading-relaxed text-white/80 md:text-xl">
            Nous remplaçons les cartes de fidélité papier par une carte digitale
            dans Google Wallet — pensée pour les commerces de proximité
            d&apos;Afrique de l&apos;Ouest.
          </p>

          <div className="flex flex-col items-start gap-10 sm:flex-row sm:items-center">
            <Link
              href="/#tarifs"
              className="group flex items-center gap-3 rounded-full bg-accent px-10 py-5 text-lg font-bold text-brand-950 shadow-[0_0_20px_rgba(250,204,21,0.25)] transition-transform hover:scale-105"
            >
              Créer mon programme
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden
                className="transition-transform group-hover:translate-x-1"
              >
                <path
                  d="M5 12h14m0 0-5-5m5 5-5 5"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </Link>
            <div className="flex items-baseline gap-3">
              <span style={oswald} className="text-4xl font-semibold">
                0
              </span>
              <span className="font-medium text-white/60">
                application à installer
              </span>
            </div>
          </div>
        </div>

        {/* Colonne droite : carte image */}
        <div className="relative lg:col-span-5">
          <div
            style={oswald}
            className="absolute -right-4 -top-12 z-0 select-none text-[12rem] font-bold leading-none text-white/5"
          >
            02
          </div>

          <div className="group relative aspect-[5/4] overflow-hidden rounded-[3rem] bg-brand-900 shadow-2xl shadow-black/30">
            <Image
              src={baobab}
              alt="Allée de baobabs en Afrique de l'Ouest"
              fill
              priority
              sizes="(max-width: 1024px) 100vw, 40vw"
              className="object-cover opacity-90 transition-transform duration-700 group-hover:scale-105"
            />

            <div className="absolute left-0 top-0 z-20 rounded-br-[3rem] bg-brand-950 p-4">
              <div className="flex h-20 w-20 items-center justify-center rounded-full border border-white/10 bg-[#111827] text-white transition-colors hover:bg-black">
                <svg
                  width="34"
                  height="34"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden
                  className="transition-transform duration-300 group-hover:rotate-45"
                >
                  <path
                    d="M7 17 17 7m0 0H8m9 0v9"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
            </div>

            <div className="absolute bottom-12 left-8 origin-bottom-left -rotate-90">
              <span
                style={oswald}
                className="text-5xl font-bold uppercase tracking-widest text-white/80 mix-blend-overlay"
              >
                Afrique
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Bandeau cartes */}
      <div className="relative z-10 mx-auto mt-20 grid max-w-[1800px] grid-cols-1 gap-6 px-6 md:px-12 lg:grid-cols-3">
        {/* Carte promo */}
        <div className="group relative h-80 overflow-hidden rounded-[2.5rem] bg-white p-8 text-brand-950 transition-transform duration-300 hover:-translate-y-1">
          <span
            style={oswald}
            className="absolute right-8 top-8 text-sm font-medium tracking-widest text-brand-950/30"
          >
            03 // DEPUIS
          </span>
          <div className="relative z-10 flex h-full max-w-[62%] flex-col justify-between">
            <div>
              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-full bg-brand-50 text-brand-600">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden>
                  <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.6" />
                  <path d="M10 9l5 3-5 3V9Z" fill="currentColor" />
                </svg>
              </div>
              <p className="mb-2 text-lg font-semibold leading-tight">
                La fidélité qui ne se perd jamais
              </p>
            </div>
            <h3 style={oswald} className="text-5xl font-bold text-brand-950">
              2025
            </h3>
          </div>
          <div className="absolute bottom-0 right-0 z-0 h-full w-1/2">
            <div className="absolute inset-0 z-10 bg-gradient-to-r from-white via-white/30 to-transparent" />
            <Image
              src={phoneApp}
              alt=""
              aria-hidden
              fill
              sizes="200px"
              className="object-contain object-right opacity-90"
            />
          </div>
        </div>

        {/* Carte features */}
        <div className="relative flex flex-col items-start gap-12 overflow-hidden rounded-[2.5rem] border border-white/5 bg-brand-900 p-8 md:flex-row md:items-center md:p-12 lg:col-span-2">
          <div className="absolute left-1/2 top-0 bottom-0 hidden w-px bg-white/5 md:block" />
          <div className="relative z-10 flex-1">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-accent">
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none" aria-hidden>
                <rect x="3" y="6" width="18" height="12" rx="3" stroke="currentColor" strokeWidth="1.6" />
                <path d="M3 10h18" stroke="currentColor" strokeWidth="1.6" />
              </svg>
            </div>
            <h4 style={oswald} className="mb-3 text-2xl font-semibold text-white">
              Google Wallet
            </h4>
            <p className="text-sm font-medium leading-relaxed text-white/50">
              La carte vit dans Google Wallet, toujours à portée de main. Aucune
              application à télécharger, aucun matériel à installer.
            </p>
          </div>
          <div className="relative z-10 flex-1">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-accent">
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none" aria-hidden>
                <path d="M12 3a9 9 0 0 0-7.7 13.6L3 21l4.5-1.2A9 9 0 1 0 12 3Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
              </svg>
            </div>
            <h4 style={oswald} className="mb-3 text-2xl font-semibold text-white">
              Partage WhatsApp
            </h4>
            <p className="text-sm font-medium leading-relaxed text-white/50">
              Envoyez votre carte par WhatsApp ou QR Code. Vos clients
              l&apos;ajoutent en un clic et reviennent grâce aux notifications.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default AboutUs;
