import Image from "next/image";
import kfc from "../../public/img/kfc.png";

const points = [
  "Une notification quand une récompense est prête à être réclamée.",
  "Un rappel automatique pour les clients qui ne sont pas revenus.",
  "Vos offres et promotions affichées directement sur leur téléphone.",
];

export function Notifications() {
  return (
    <section className="overflow-hidden bg-white py-20 sm:py-28">
      <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-4 sm:px-6 lg:grid-cols-2 lg:gap-16 lg:px-8">
        {/* Texte */}
        <div>
          <span className="text-sm font-semibold uppercase tracking-widest text-brand-600">
            Notifications
          </span>
          <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight text-brand-950 sm:text-4xl">
            Des notifications qui font revenir vos clients
          </h2>
          <p className="mt-5 text-lg leading-relaxed text-slate-600">
            La carte vit dans Google Wallet : vous pouvez donc toucher vos
            clients directement sur leur téléphone, sans application ni campagne
            SMS coûteuse. Chaque notification est une occasion de les faire
            revenir.
          </p>

          <ul className="mt-8 space-y-4">
            {points.map((point) => (
              <li key={point} className="flex items-start gap-3">
                <span className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-50 text-brand-600">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden>
                    <path
                      d="m5 13 4 4L19 7"
                      stroke="currentColor"
                      strokeWidth="2.4"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
                <span className="text-slate-700">{point}</span>
              </li>
            ))}
          </ul>

          <a
            href="#tarifs"
            className="mt-9 inline-flex items-center gap-2 rounded-full bg-brand-600 px-7 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/25 transition-transform hover:-translate-y-0.5"
          >
            Activer les notifications
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path
                d="M5 12h14m0 0-5-5m5 5-5 5"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </a>
        </div>

        {/* Visuel */}
        <div className="relative">
          <div
            aria-hidden
            className="absolute left-1/2 top-1/2 -z-10 h-[440px] w-[440px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-brand-100/70 blur-3xl"
          />
          <Image
            src={kfc}
            alt="Un téléphone affichant une notification de programme de fidélité et un autre affichant une carte de fidélité dans Google Wallet"
            sizes="(max-width: 1024px) 90vw, 45vw"
            className="mx-auto w-full max-w-lg drop-shadow-2xl"
          />
        </div>
      </div>
    </section>
  );
}
