import Image from "next/image";
import baobab from "../../public/img/baobab_2.png";
import phoneApp from "../../public/img/d5.png";

export function Hero() {
  return (
    <section className="relative isolate overflow-hidden">
      {/* Fond : allée de baobabs (Afrique de l'Ouest) */}
      <Image
        src={baobab}
        alt=""
        aria-hidden
        fill
        priority
        placeholder="blur"
        sizes="100vw"
        className="-z-20 object-cover object-center"
      />
      {/* Voile de marque pour la lisibilité */}
      <div className="absolute inset-0 -z-10 bg-gradient-to-br from-brand-950/95 via-brand-900/85 to-brand-700/55" />
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(120%_90%_at_15%_10%,rgba(7,20,56,0.55),transparent_60%)]" />

      {/* Contenu du hero */}
      <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-10 px-4 pb-16 pt-32 sm:px-6 lg:grid-cols-12 lg:gap-8 lg:px-8 lg:pb-24 lg:pt-40">
        {/* Colonne gauche : texte */}
        <div className="lg:col-span-6">
          <span className="yk-fade-up inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-xs font-medium uppercase tracking-wider text-white/90 backdrop-blur">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden
              className="text-accent"
            >
              <path
                d="M3 8.5A2.5 2.5 0 0 1 5.5 6H18a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V8.5Z"
                stroke="currentColor"
                strokeWidth="1.6"
              />
              <path
                d="M16 12.5h3.5"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
              />
            </svg>
            Compatible Google Wallet
          </span>

          <h1 className="yk-fade-up mt-6 font-display text-4xl font-semibold leading-[1.05] tracking-tight text-white sm:text-5xl lg:text-6xl">
            La carte de fidélité qui&nbsp;
            <span className="bg-gradient-to-r from-accent to-amber-200 bg-clip-text text-transparent">
              ne se perd jamais
            </span>
          </h1>

          <p className="yk-fade-up mt-6 max-w-xl text-lg leading-relaxed text-white/75">
            Yokalma remplace les cartes papier par une carte digitale dans
            Google Wallet. Vos clients l&apos;ajoutent en un clic, vous ajoutez
            les tampons d&apos;un simple scan de QR Code. Sans application à
            installer.
          </p>

          <div className="yk-fade-up mt-8 flex flex-col gap-3 sm:flex-row">
            <a
              href="#tarifs"
              className="group inline-flex items-center justify-center gap-2 rounded-full bg-accent px-7 py-3.5 text-sm font-semibold text-brand-950 shadow-xl shadow-brand-950/30 transition-transform hover:-translate-y-0.5"
            >
              Créer mon programme
              <svg
                width="18"
                height="18"
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
            </a>
            <a
              href="#etapes"
              className="inline-flex items-center justify-center gap-2 rounded-full border border-white/25 px-7 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-white/10"
            >
              Voir comment ça marche
            </a>
          </div>

          <ul className="yk-fade-up mt-8 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-white/70">
            {[
              "Sans application à installer",
              "Partage par WhatsApp",
              "Gratuit jusqu'à 5 clients",
            ].map((item) => (
              <li key={item} className="flex items-center gap-2">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden
                  className="text-accent"
                >
                  <path
                    d="m5 13 4 4L19 7"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* Colonne droite : mockup téléphone Yokalma */}
        <div className="relative lg:col-span-6">
          <div
            aria-hidden
            className="absolute left-1/2 top-1/2 -z-10 h-[560px] w-[560px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent/20 blur-3xl"
          />
          <Image
            src={phoneApp}
            alt="Application Yokalma affichant une carte de fidélité Café Délices dans Google Wallet, avec 6 tampons sur 10"
            priority
            width={800}
            height={800}
            unoptimized
            className="yk-float mx-auto w-full max-w-lg drop-shadow-2xl lg:max-w-2xl lg:scale-110 lg:-mr-6"
          />
        </div>
      </div>
    </section>
  );
}
