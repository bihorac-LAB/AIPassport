export function Spinner({ label = 'Loading' }: { label?: string }) {
  return (
    <p
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--sp-3)',
        color: 'var(--text-muted)',
        fontSize: 'var(--text-sm)',
      }}
    >
      <span className="spinner" aria-hidden="true" />
      <span role="status">{label}…</span>
    </p>
  );
}

export function LoadingPage({ label = 'Loading' }: { label?: string }) {
  return (
    <div className="content-width page">
      <Spinner label={label} />
    </div>
  );
}
