import { useState } from 'react';
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom';
import { ApiError } from '@/api/client';
import { authApi } from '@/api/endpoints';
import type { Track } from '@/api/types';
import { useAuth } from '@/auth/AuthProvider';
import { Button, Callout, Select, TextInput } from '@/components/primitives';

function useNextPath(): string {
  const [params] = useSearchParams();
  const next = params.get('next');
  // Only accept in-app paths — never an absolute URL from a query parameter.
  return next && next.startsWith('/') && !next.startsWith('//') ? next : '/';
}

function fieldErrors(error: unknown): Record<string, string> {
  if (error instanceof ApiError && error.fields) {
    return Object.fromEntries(error.fields.map((field) => [field.field, field.message]));
  }
  return {};
}

export function SignInPage() {
  const { login, status } = useAuth();
  const navigate = useNavigate();
  const next = useNextPath();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (status === 'authenticated') return <Navigate to={next} replace />;

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
      navigate(next, { replace: true });
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.status === 429
            ? 'Too many attempts. Please wait a few minutes and try again.'
            : caught.message
          : 'Could not sign in. Please try again.',
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="content-width auth">
      <div className="auth__card">
        <h1 className="auth__title">Sign in</h1>
        <p className="auth__sub">Your progress and saved answers are waiting.</p>

        {error ? (
          <div style={{ marginBottom: 'var(--sp-4)' }}>
            <Callout tone="danger" title="Sign in failed">
              <p>{error}</p>
            </Callout>
          </div>
        ) : null}

        <form className="auth__form" onSubmit={submit}>
          <TextInput
            label="Email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <TextInput
            label="Password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <Button type="submit" variant="primary" block loading={busy}>
            Sign in
          </Button>
        </form>

        <p className="auth__foot">
          <Link to="/forgot-password">Forgot your password?</Link>
          <br />
          <span style={{ display: 'inline-block', marginTop: 'var(--sp-2)' }}>
            No account? <Link to="/register">Create one</Link>
          </span>
        </p>
      </div>
    </div>
  );
}

export function RegisterPage() {
  const { register, status } = useAuth();
  const navigate = useNavigate();
  const next = useNextPath();
  const [form, setForm] = useState({
    displayName: '',
    email: '',
    password: '',
    track: 'clinical' as Track,
  });
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  if (status === 'authenticated') return <Navigate to={next} replace />;

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setErrors({});
    try {
      await register({
        email: form.email,
        password: form.password,
        displayName: form.displayName,
        track: form.track,
      });
      navigate(next, { replace: true });
    } catch (caught) {
      setErrors(fieldErrors(caught));
      setError(
        caught instanceof ApiError ? caught.message : 'Could not create your account. Please try again.',
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="content-width auth">
      <div className="auth__card">
        <h1 className="auth__title">Create your account</h1>
        <p className="auth__sub">
          So your answers, activity results, and progress persist across devices.
        </p>

        {error ? (
          <div style={{ marginBottom: 'var(--sp-4)' }}>
            <Callout tone="danger" title="Could not create account">
              <p>{error}</p>
            </Callout>
          </div>
        ) : null}

        <form className="auth__form" onSubmit={submit}>
          <TextInput
            label="Your name"
            autoComplete="name"
            required
            value={form.displayName}
            error={errors.display_name}
            onChange={(event) => setForm({ ...form, displayName: event.target.value })}
          />
          <TextInput
            label="Email"
            type="email"
            autoComplete="email"
            required
            value={form.email}
            error={errors.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
          />
          <TextInput
            label="Password"
            type="password"
            autoComplete="new-password"
            required
            minLength={10}
            hint="At least 10 characters. A short phrase works well."
            value={form.password}
            error={errors.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
          />
          <Select
            label="Which examples should we use?"
            hint="This swaps datasets and terminology in some activities. You can change it later."
            value={form.track}
            options={[
              { value: 'clinical', label: 'Clinical — patients, EHR, imaging' },
              { value: 'basic', label: 'Basic science — cells, molecules, assays' },
            ]}
            onChange={(event) => setForm({ ...form, track: event.target.value as Track })}
          />
          <Button type="submit" variant="primary" block loading={busy}>
            Create account
          </Button>
        </form>

        <p className="auth__foot">
          Already have an account? <Link to="/sign-in">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    try {
      await authApi.requestPasswordReset({ email });
    } catch {
      // The response is intentionally identical either way — no account enumeration.
    } finally {
      setBusy(false);
      setSent(true);
    }
  };

  return (
    <div className="content-width auth">
      <div className="auth__card">
        <h1 className="auth__title">Reset your password</h1>
        {sent ? (
          <>
            <Callout tone="info" title="Check your email">
              <p>
                If an account exists for that address, a reset link is on its way. The link expires in
                one hour.
              </p>
            </Callout>
            <p className="auth__foot">
              <Link to="/sign-in">Back to sign in</Link>
            </p>
          </>
        ) : (
          <>
            <p className="auth__sub">We will email you a link to set a new password.</p>
            <form className="auth__form" onSubmit={submit}>
              <TextInput
                label="Email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
              <Button type="submit" variant="primary" block loading={busy}>
                Send reset link
              </Button>
            </form>
            <p className="auth__foot">
              <Link to="/sign-in">Back to sign in</Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}

export function ResetPasswordPage() {
  const [params] = useSearchParams();
  const token = params.get('token') ?? '';
  const [password, setPassword] = useState('');
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await authApi.confirmPasswordReset({ token, new_password: password });
      setDone(true);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Could not reset your password.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="content-width auth">
      <div className="auth__card">
        <h1 className="auth__title">Set a new password</h1>
        {done ? (
          <>
            <Callout tone="success" title="Password updated">
              <p>You can now sign in with your new password.</p>
            </Callout>
            <p className="auth__foot">
              <Link to="/sign-in">Sign in</Link>
            </p>
          </>
        ) : !token ? (
          <Callout tone="warning" title="Missing reset token">
            <p>
              Open the link from your email, or <Link to="/forgot-password">request a new one</Link>.
            </p>
          </Callout>
        ) : (
          <>
            {error ? (
              <div style={{ marginBottom: 'var(--sp-4)' }}>
                <Callout tone="danger" title="Could not reset password">
                  <p>{error}</p>
                </Callout>
              </div>
            ) : null}
            <form className="auth__form" onSubmit={submit}>
              <TextInput
                label="New password"
                type="password"
                autoComplete="new-password"
                required
                minLength={10}
                hint="At least 10 characters."
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
              <Button type="submit" variant="primary" block loading={busy}>
                Update password
              </Button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
