export function Logo({ className = "" }: { className?: string }) {
  return (
    <a
      href="#"
      className={`inline-flex items-center gap-0.5 font-display text-2xl font-bold tracking-tight ${className}`}
      aria-label="Yokalma — accueil"
    >
      <span>yokalma</span>
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden
        className="-mt-3 text-accent"
      >
        <path
          d="M12 2c.4 3.9 1.7 6.4 3.6 8 1.6 1.4 3.7 2.1 6.4 2.4-3.9.4-6.4 1.7-8 3.6-1.4 1.6-2.1 3.7-2.4 6.4-.4-3.9-1.7-6.4-3.6-8-1.6-1.4-3.7-2.1-6.4-2.4 3.9-.4 6.4-1.7 8-3.6C11 8.8 11.7 6.7 12 2Z"
          fill="currentColor"
        />
      </svg>
    </a>
  );
}
