export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error' | 'offline';

const LABEL: Record<SaveStatus, string> = {
  idle: '',
  saving: 'Saving…',
  saved: 'Saved',
  error: 'Could not save — retrying',
  offline: 'Saved on this device — will sync when you reconnect',
};

export function SaveState({ status }: { status: SaveStatus }) {
  if (status === 'idle') return <span className="save-state" aria-hidden="true" />;
  const modifier =
    status === 'saved' ? ' save-state--saved' : ' save-state--error';
  return (
    <span className={`save-state${modifier}`} role="status">
      {status === 'saving' ? (
        <span className="spinner" aria-hidden="true" style={{ width: 12, height: 12 }} />
      ) : (
        <span className="save-state__dot" aria-hidden="true" />
      )}
      {LABEL[status]}
    </span>
  );
}
