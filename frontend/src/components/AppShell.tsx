import { useEffect } from 'react';
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/auth/AuthProvider';
import { attachLifecycleFlush, setLearningSessionId, setTrackingEnabled, trackEvent, trackImmediate } from '@/analytics/track';
import { sessionApi } from '@/api/endpoints';
import { isEmbedded, referrerKind, withEmbed } from '@/lib/embed';
import { useUiStore, applyTheme } from '@/lib/store';
import { Button } from './primitives';
import { TutorPanel } from './TutorPanel';

export function AppShell() {
  const embedded = isEmbedded();
  const { status, user, logout } = useAuth();
  const location = useLocation();
  const theme = useUiStore((state) => state.theme);
  const setTheme = useUiStore((state) => state.setTheme);
  const setTrack = useUiStore((state) => state.setTrack);

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  useEffect(() => {
    if (user) setTrack(user.track_pref);
  }, [setTrack, user]);

  // A learning session is created once per sign-in-and-open, and only for authenticated learners.
  useEffect(() => {
    if (status !== 'authenticated') {
      setTrackingEnabled(false);
      return;
    }
    setTrackingEnabled(true);
    let cancelled = false;
    const detach = attachLifecycleFlush();

    void (async () => {
      try {
        const session = await sessionApi.start({
          is_embedded: embedded,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          viewport_width: window.innerWidth,
          referrer_kind: referrerKind(),
        });
        if (cancelled) return;
        setLearningSessionId(session.id);
        trackEvent('session_started', {}, { embedded });
      } catch {
        // Analytics must never block learning.
      }
    })();

    const onPageHide = () => {
      void trackImmediate('session_ended');
    };
    window.addEventListener('pagehide', onPageHide);

    return () => {
      cancelled = true;
      detach();
      window.removeEventListener('pagehide', onPageHide);
    };
  }, [embedded, status]);

  useEffect(() => {
    if (status === 'authenticated') {
      trackEvent('navigation', {}, { path: location.pathname });
    }
  }, [location.pathname, status]);

  return (
    <div className={`shell${embedded ? ' shell--embed' : ''}`}>
      <a className="skip-link" href="#main">
        Skip to content
      </a>

      <header className="shell__header no-print">
        <div className="shell__header-inner">
          <Link className="brand" to={withEmbed('/')}>
            <span className="brand__mark" aria-hidden="true">
              AI
            </span>
            <span className="brand__text">AIPassport</span>
          </Link>

          {!embedded ? (
            <nav className="nav" aria-label="Main">
              <NavLink
                to="/"
                end
                className={({ isActive }) => `nav__link${isActive ? ' nav__link--active' : ''}`}
              >
                Modules
              </NavLink>
              {status === 'authenticated' ? (
                <NavLink
                  to="/progress"
                  className={({ isActive }) => `nav__link${isActive ? ' nav__link--active' : ''}`}
                >
                  My progress
                </NavLink>
              ) : null}
            </nav>
          ) : null}

          <div className="shell__spacer" />

          <div className="shell__actions">
            <Button
              size="sm"
              variant="ghost"
              aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              {theme === 'dark' ? '☀' : '☾'}
            </Button>
            {status === 'authenticated' && user ? (
              <>
                {!embedded ? (
                  <Link className="nav__link" to="/account">
                    {user.display_name}
                  </Link>
                ) : (
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
                    {user.display_name}
                  </span>
                )}
                {!embedded ? (
                  <Button size="sm" variant="outline" onClick={() => void logout()}>
                    Sign out
                  </Button>
                ) : null}
              </>
            ) : status === 'anonymous' && !embedded ? (
              <>
                <Link className="nav__link" to="/sign-in">
                  Sign in
                </Link>
                <Link className="btn btn--primary btn--sm" to="/register">
                  Create account
                </Link>
              </>
            ) : null}
          </div>
        </div>
      </header>

      <main className="shell__main" id="main">
        <Outlet />
      </main>

      {!embedded ? (
        <footer className="shell__footer no-print">
          <div className="shell__footer-inner">
            <span>AIPassport · University of Florida</span>
            <span>Interactive AI literacy for clinical and biomedical research</span>
          </div>
        </footer>
      ) : null}

      {status === 'authenticated' ? <TutorPanel /> : null}
    </div>
  );
}
