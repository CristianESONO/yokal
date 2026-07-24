type Feature = {
  title: string;
  description: string;
  icon: React.ReactNode;
};

const iconClass = "h-6 w-6 text-brand-600";

const features: Feature[] = [
  {
    title: "Plus de cartes perdues",
    description:
      "La carte vit dans Google Wallet, toujours à portée de main. Fini les cartons oubliés, déchirés ou jetés.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className={iconClass} aria-hidden>
        <rect x="3" y="6" width="18" height="12" rx="3" stroke="currentColor" strokeWidth="1.6" />
        <path d="M3 10h18" stroke="currentColor" strokeWidth="1.6" />
      </svg>
    ),
  },
  {
    title: "Partage par WhatsApp",
    description:
      "Envoyez votre carte de fidélité à vos clients par WhatsApp ou QR Code. Ils l'ajoutent en un seul clic.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className={iconClass} aria-hidden>
        <path d="M12 3a9 9 0 0 0-7.7 13.6L3 21l4.5-1.2A9 9 0 1 0 12 3Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
        <path d="M9 9c0 3.3 2.7 6 6 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "Notifications qui font revenir",
    description:
      "Google Wallet envoie des notifications à vos clients : nouvelle offre, tampon manquant, récompense prête à réclamer.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className={iconClass} aria-hidden>
        <path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
        <path d="M10 19a2 2 0 0 0 4 0" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "Tampons par simple scan",
    description:
      "Ajoutez un tampon en scannant le QR Code du client. Rapide au comptoir, sans matériel supplémentaire.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className={iconClass} aria-hidden>
        <path d="M4 7V5a1 1 0 0 1 1-1h2M17 4h2a1 1 0 0 1 1 1v2M20 17v2a1 1 0 0 1-1 1h-2M7 20H5a1 1 0 0 1-1-1v-2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        <path d="M4 12h16" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "Statistiques en temps réel",
    description:
      "Suivez vos clients fidèles, le nombre de cartes ajoutées et les récompenses distribuées, depuis un tableau de bord clair.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className={iconClass} aria-hidden>
        <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "Aucune app à installer",
    description:
      "Vos clients n'ont rien à télécharger : la carte s'ajoute directement à Google Wallet, déjà présent sur leur téléphone.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className={iconClass} aria-hidden>
        <path d="m5 13 4 4L19 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
];

export function Features() {
  return (
    <section id="fonctionnalites" className="bg-zinc-50 py-20 sm:py-28">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-sm font-semibold uppercase tracking-widest text-brand-600">
            Fonctionnalités
          </span>
          <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight text-brand-950 sm:text-4xl">
            Tout ce qu&apos;il faut pour fidéliser vos clients
          </h2>
          <p className="mt-4 text-lg text-zinc-600">
            Une solution simple, sans matériel ni application, qui transforme
            chaque passage en caisse en client fidèle.
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-2xl border border-zinc-100 bg-white p-7 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-50">
                {feature.icon}
              </div>
              <h3 className="mt-5 font-display text-lg font-semibold text-brand-950">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
