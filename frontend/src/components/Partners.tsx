const items = [
  { label: "Google Wallet", sub: "Carte intégrée" },
  { label: "WhatsApp", sub: "Partage en 1 clic" },
  { label: "QR Code", sub: "Tampon par scan" },
  { label: "Notifications", sub: "Vos clients reviennent" },
];

export function Partners() {
  return (
    <section className="border-b border-zinc-100 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <p className="text-center text-xs font-semibold uppercase tracking-widest text-zinc-400">
          Pensé pour les commerces de proximité en Afrique de l&apos;Ouest
        </p>
        <div className="mt-8 grid grid-cols-2 gap-6 sm:grid-cols-4">
          {items.map((item) => (
            <div
              key={item.label}
              className="flex flex-col items-center gap-1 text-center"
            >
              <span className="font-display text-lg font-semibold text-brand-900">
                {item.label}
              </span>
              <span className="text-sm text-zinc-500">{item.sub}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
