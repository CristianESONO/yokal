"use client";

import { useState } from "react";

// Adresse pro de réception (repli mailto). L'envoi automatique passe par Web3Forms.
const CONTACT_EMAIL = "contact@linkup.sn";
// Clé Web3Forms (créée avec contact@linkup.sn). À renseigner dans .env.local :
// NEXT_PUBLIC_WEB3FORMS_ACCESS_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
const ACCESS_KEY = process.env.NEXT_PUBLIC_WEB3FORMS_ACCESS_KEY;

const subjectLabels: Record<string, string> = {
  demo: "Demander une démo",
  offre: "Question sur les offres",
  partenariat: "Devenir partenaire",
  support: "Support technique",
  autre: "Autre",
};

const inputClass =
  "w-full rounded-xl border border-zinc-200 bg-white px-4 py-3 text-sm text-brand-950 shadow-sm outline-none transition-colors placeholder:text-slate-400 focus:border-brand-400 focus:ring-2 focus:ring-brand-100";

type Status = "idle" | "sending" | "success" | "error";

export function ContactForm() {
  const [status, setStatus] = useState<Status>("idle");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);

    const name = (data.get("name") as string) || "";
    const business = (data.get("business") as string) || "";
    const email = (data.get("email") as string) || "";
    const phone = (data.get("phone") as string) || "";
    const subjectKey = (data.get("subject") as string) || "autre";
    const message = (data.get("message") as string) || "";
    const subjectLabel = subjectLabels[subjectKey] ?? subjectKey;
    const subject = `Yokalma — ${subjectLabel} — ${name}`;

    // Envoi automatique via Web3Forms si une clé est configurée
    if (ACCESS_KEY) {
      setStatus("sending");
      try {
        const res = await fetch("https://api.web3forms.com/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({
            access_key: ACCESS_KEY,
            subject,
            from_name: "Formulaire Yokalma",
            replyto: email,
            Nom: name,
            Commerce: business || "—",
            "E-mail": email,
            "Téléphone / WhatsApp": phone || "—",
            Sujet: subjectLabel,
            Message: message,
          }),
        });
        const result = await res.json();
        if (result.success) {
          setStatus("success");
          form.reset();
        } else {
          setStatus("error");
        }
      } catch {
        setStatus("error");
      }
      return;
    }

    // Repli : ouvre l'application mail du visiteur, message pré-rempli
    const body = [
      `Nom : ${name}`,
      `Commerce : ${business || "—"}`,
      `E-mail : ${email}`,
      `Téléphone / WhatsApp : ${phone || "—"}`,
      `Sujet : ${subjectLabel}`,
      "",
      "Message :",
      message,
    ].join("\n");
    window.location.href = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(
      subject,
    )}&body=${encodeURIComponent(body)}`;
    setStatus("success");
  };

  if (status === "success") {
    const automatic = Boolean(ACCESS_KEY);
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-3xl border border-brand-100 bg-brand-50 p-10 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-600 text-white">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden>
            <path
              d="m5 13 4 4L19 7"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        <h3 className="mt-5 font-display text-2xl font-semibold text-brand-950">
          {automatic ? "Message envoyé, merci !" : "Votre message est prêt !"}
        </h3>
        <p className="mt-3 max-w-sm text-slate-600">
          {automatic ? (
            <>Nous avons bien reçu votre message et vous répondons sous 24 h ouvrées.</>
          ) : (
            <>
              Votre application e-mail vient de s&apos;ouvrir avec le message
              pré-rempli — appuyez sur « Envoyer ». Sinon, écrivez-nous à{" "}
              <a
                href={`mailto:${CONTACT_EMAIL}`}
                className="font-medium text-brand-700 underline"
              >
                {CONTACT_EMAIL}
              </a>
              .
            </>
          )}
        </p>
        <button
          type="button"
          onClick={() => setStatus("idle")}
          className="mt-6 inline-flex items-center rounded-full border border-brand-200 px-6 py-2.5 text-sm font-semibold text-brand-700 transition-colors hover:bg-white"
        >
          Envoyer un autre message
        </button>
      </div>
    );
  }

  const sending = status === "sending";

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-3xl border border-zinc-100 bg-white p-6 shadow-sm sm:p-8"
    >
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div className="sm:col-span-1">
          <label htmlFor="name" className="mb-1.5 block text-sm font-medium text-brand-950">
            Nom complet
          </label>
          <input id="name" name="name" type="text" required placeholder="Aminata Diallo" className={inputClass} />
        </div>
        <div className="sm:col-span-1">
          <label htmlFor="business" className="mb-1.5 block text-sm font-medium text-brand-950">
            Nom du commerce
          </label>
          <input id="business" name="business" type="text" placeholder="Boulangerie Le Bon Pain" className={inputClass} />
        </div>
        <div className="sm:col-span-1">
          <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-brand-950">
            E-mail
          </label>
          <input id="email" name="email" type="email" required placeholder="vous@exemple.com" className={inputClass} />
        </div>
        <div className="sm:col-span-1">
          <label htmlFor="phone" className="mb-1.5 block text-sm font-medium text-brand-950">
            Téléphone / WhatsApp
          </label>
          <input id="phone" name="phone" type="tel" placeholder="+221 77 000 00 00" className={inputClass} />
        </div>
        <div className="sm:col-span-2">
          <label htmlFor="subject" className="mb-1.5 block text-sm font-medium text-brand-950">
            Sujet
          </label>
          <select id="subject" name="subject" defaultValue="demo" className={inputClass}>
            <option value="demo">Demander une démo</option>
            <option value="offre">Question sur les offres</option>
            <option value="partenariat">Devenir partenaire</option>
            <option value="support">Support technique</option>
            <option value="autre">Autre</option>
          </select>
        </div>
        <div className="sm:col-span-2">
          <label htmlFor="message" className="mb-1.5 block text-sm font-medium text-brand-950">
            Votre message
          </label>
          <textarea
            id="message"
            name="message"
            required
            rows={5}
            placeholder="Parlez-nous de votre commerce et de ce que vous cherchez…"
            className={`${inputClass} resize-none`}
          />
        </div>
      </div>

      {status === "error" && (
        <p className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600">
          L&apos;envoi a échoué. Réessayez, ou écrivez-nous directement à{" "}
          <a href={`mailto:${CONTACT_EMAIL}`} className="font-medium underline">
            {CONTACT_EMAIL}
          </a>
          .
        </p>
      )}

      <button
        type="submit"
        disabled={sending}
        className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-full bg-brand-600 px-7 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/25 transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
      >
        {sending ? "Envoi en cours…" : "Envoyer le message"}
        {!sending && (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
            <path
              d="M5 12h14m0 0-5-5m5 5-5 5"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </button>
      <p className="mt-3 text-xs text-slate-400">
        En envoyant ce formulaire, vous acceptez d&apos;être recontacté par
        l&apos;équipe Yokalma.
      </p>
    </form>
  );
}
