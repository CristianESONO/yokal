"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const STORAGE_KEY = "yk-sound";
const INTERACTIVE = "button, a, [role=button], input[type=submit], input[type=button], summary";

export function ClickSound() {
  const ctxRef = useRef<AudioContext | null>(null);
  const lastPlay = useRef(0);
  const [enabled, setEnabled] = useState(true);
  const [mounted, setMounted] = useState(false);

  // Lit la préférence sauvegardée
  useEffect(() => {
    setMounted(true);
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved !== null) setEnabled(saved === "on");
  }, []);

  // Synthétise un « cling » de cloche (2 harmoniques, décroissance rapide)
  const playCling = useCallback(() => {
    const now = performance.now();
    if (now - lastPlay.current < 60) return; // anti-spam
    lastPlay.current = now;

    if (!ctxRef.current) {
      const AudioCtx =
        window.AudioContext ||
        (window as unknown as { webkitAudioContext: typeof AudioContext })
          .webkitAudioContext;
      ctxRef.current = new AudioCtx();
    }
    const ctx = ctxRef.current;
    if (ctx.state === "suspended") void ctx.resume();

    const t = ctx.currentTime;
    // Do6 + Sol6 : un tintement clair et court
    [1046.5, 1568.0].forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.value = freq;
      const peak = i === 0 ? 0.16 : 0.08;
      gain.gain.setValueAtTime(0.0001, t);
      gain.gain.exponentialRampToValueAtTime(peak, t + 0.005);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.18);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(t);
      osc.stop(t + 0.2);
    });
  }, []);

  // Écoute globale des clics sur les éléments interactifs
  useEffect(() => {
    if (!enabled) return;
    const handler = (e: MouseEvent) => {
      const target = e.target as HTMLElement | null;
      if (target?.closest(INTERACTIVE)) playCling();
    };
    document.addEventListener("click", handler);
    return () => document.removeEventListener("click", handler);
  }, [enabled, playCling]);

  const toggle = () => {
    setEnabled((prev) => {
      const next = !prev;
      window.localStorage.setItem(STORAGE_KEY, next ? "on" : "off");
      if (next) playCling(); // feedback immédiat à l'activation
      return next;
    });
  };

  if (!mounted) return null;

  return (
    <button
      type="button"
      onClick={toggle}
      aria-pressed={enabled}
      aria-label={enabled ? "Couper le son des clics" : "Activer le son des clics"}
      title={enabled ? "Son des clics activé" : "Son des clics coupé"}
      className="fixed bottom-4 right-4 z-50 flex h-11 w-11 items-center justify-center rounded-full border border-black/5 bg-white/90 text-brand-900 shadow-lg shadow-black/10 backdrop-blur transition-transform hover:-translate-y-0.5"
    >
      {enabled ? (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M4 9v6h4l5 4V5L8 9H4Z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
          <path
            d="M16 9a3.5 3.5 0 0 1 0 6M18.5 6.5a7 7 0 0 1 0 11"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
      ) : (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M4 9v6h4l5 4V5L8 9H4Z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
          <path
            d="m16 9 5 6m0-6-5 6"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
      )}
    </button>
  );
}
