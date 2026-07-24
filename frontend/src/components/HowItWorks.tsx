const steps = [
  {
    number: "1",
    title: "Le commerçant crée son programme",
    description:
      "En quelques minutes, définissez votre carte : nom du commerce, nombre de tampons et récompense. Aucune compétence technique requise.",
  },
  {
    number: "2",
    title: "Le client ajoute la carte à Google Wallet",
    description:
      "Partagez le lien par WhatsApp ou affichez un QR Code. Le client ajoute sa carte à Google Wallet en un clic, sans installer d'application.",
  },
  {
    number: "3",
    title: "Les tampons s'ajoutent par scan",
    description:
      "À chaque passage, scannez le QR Code du client pour ajouter un tampon. La récompense se débloque automatiquement.",
  },
];

export function HowItWorks() {
  return (
    <section id="etapes" className="bg-white py-20 sm:py-28">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-sm font-semibold uppercase tracking-widest text-brand-600">
            Comment ça marche
          </span>
          <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight text-brand-950 sm:text-4xl">
            Lancé en 3 étapes, sans papier
          </h2>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-8 md:grid-cols-3">
          {steps.map((step, index) => (
            <div key={step.number} className="relative">
              {index < steps.length - 1 && (
                <div
                  aria-hidden
                  className="absolute left-6 top-12 hidden h-px w-full bg-gradient-to-r from-brand-200 to-transparent md:block"
                />
              )}
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-600 font-display text-lg font-bold text-white shadow-lg shadow-brand-600/30">
                {step.number}
              </div>
              <h3 className="mt-6 font-display text-xl font-semibold text-brand-950">
                {step.title}
              </h3>
              <p className="mt-3 text-zinc-600 leading-relaxed">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
