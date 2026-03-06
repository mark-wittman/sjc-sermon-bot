export function CrossIcon({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 32"
      fill="currentColor"
      className={className}
      aria-hidden="true"
    >
      <rect x="10" y="0" width="4" height="32" />
      <rect x="2" y="8" width="20" height="4" />
    </svg>
  );
}
