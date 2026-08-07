import { useState } from 'react';
import { ApiError } from '@/api/client';
import { authApi } from '@/api/endpoints';
import type { Track } from '@/api/types';
import { useAuth } from '@/auth/AuthProvider';
import { Button, Callout, Select, TextInput } from '@/components/primitives';

export default function AccountPage() {
  const { user, updateProfile, logout } = useAuth();
  const [displayName, setDisplayName] = useState(user?.display_name ?? '');
  const [track, setTrack] = useState<Track>(user?.track_pref ?? 'clinical');
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  const [passwords, setPasswords] = useState({ current: '', next: '' });
  const [passwordMessage, setPasswordMessage] = useState<{ tone: 'success' | 'danger'; text: string } | null>(
    null,
  );

  if (!user) return null;

  const saveProfile = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setSaved(false);
    try {
      await updateProfile({ display_name: displayName, track_pref: track });
      setSaved(true);
    } finally {
      setBusy(false);
    }
  };

  const changePassword = async (event: React.FormEvent) => {
    event.preventDefault();
    setPasswordMessage(null);
    try {
      await authApi.changePassword({
        current_password: passwords.current,
        new_password: passwords.next,
      });
      setPasswordMessage({
        tone: 'success',
        text: 'Password updated. For your security, all sessions were signed out — please sign in again.',
      });
      setPasswords({ current: '', next: '' });
      window.setTimeout(() => void logout(), 2500);
    } catch (caught) {
      setPasswordMessage({
        tone: 'danger',
        text: caught instanceof ApiError ? caught.message : 'Could not change your password.',
      });
    }
  };

  return (
    <div className="content-width page">
      <div className="page__header">
        <h1 className="page__title">Account</h1>
        <p className="page__lede">{user.email}</p>
      </div>

      <div style={{ display: 'grid', gap: 'var(--sp-6)', maxWidth: '34rem' }}>
        <form className="card" onSubmit={saveProfile}>
          <h2 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--sp-4)' }}>Profile</h2>
          <div style={{ display: 'grid', gap: 'var(--sp-4)' }}>
            <TextInput
              label="Display name"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
            />
            <Select
              label="Example context"
              hint="Swaps datasets and terminology in some activities."
              value={track}
              options={[
                { value: 'clinical', label: 'Clinical' },
                { value: 'basic', label: 'Basic science' },
              ]}
              onChange={(event) => setTrack(event.target.value as Track)}
            />
            <div style={{ display: 'flex', gap: 'var(--sp-3)', alignItems: 'center' }}>
              <Button type="submit" variant="primary" loading={busy}>
                Save
              </Button>
              {saved ? (
                <span className="save-state save-state--saved" role="status">
                  <span className="save-state__dot" aria-hidden="true" />
                  Saved
                </span>
              ) : null}
            </div>
          </div>
        </form>

        <form className="card" onSubmit={changePassword}>
          <h2 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--sp-4)' }}>Password</h2>
          {passwordMessage ? (
            <div style={{ marginBottom: 'var(--sp-4)' }}>
              <Callout tone={passwordMessage.tone}>
                <p>{passwordMessage.text}</p>
              </Callout>
            </div>
          ) : null}
          <div style={{ display: 'grid', gap: 'var(--sp-4)' }}>
            <TextInput
              label="Current password"
              type="password"
              autoComplete="current-password"
              required
              value={passwords.current}
              onChange={(event) => setPasswords({ ...passwords, current: event.target.value })}
            />
            <TextInput
              label="New password"
              type="password"
              autoComplete="new-password"
              required
              minLength={10}
              hint="At least 10 characters. Changing it signs out all your other sessions."
              value={passwords.next}
              onChange={(event) => setPasswords({ ...passwords, next: event.target.value })}
            />
            <Button type="submit" variant="outline">
              Change password
            </Button>
          </div>
        </form>

        <div className="card">
          <h2 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--sp-2)' }}>Sessions</h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginBottom: 'var(--sp-4)' }}>
            Sign out everywhere if you have used a shared computer.
          </p>
          <div style={{ display: 'flex', gap: 'var(--sp-3)', flexWrap: 'wrap' }}>
            <Button variant="outline" onClick={() => void logout()}>
              Sign out
            </Button>
            <Button
              variant="danger"
              onClick={async () => {
                await authApi.logoutAll().catch(() => undefined);
                await logout();
              }}
            >
              Sign out of all devices
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
