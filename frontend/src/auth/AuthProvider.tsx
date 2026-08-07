/**
 * Authentication state.
 *
 * On mount the provider attempts a silent refresh using the HttpOnly cookie, which is what makes a
 * page reload keep the learner signed in without any token in localStorage.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { api, onAuthExpired, setAccessToken } from '@/api/client';
import { authApi, userApi } from '@/api/endpoints';
import type { Track, User } from '@/api/types';

type AuthStatus = 'loading' | 'authenticated' | 'anonymous';

type AuthContextValue = {
  status: AuthStatus;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (input: {
    email: string;
    password: string;
    displayName: string;
    track: Track;
  }) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (input: { display_name?: string; track_pref?: Track }) => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [user, setUser] = useState<User | null>(null);
  const refreshTimer = useRef<number | null>(null);

  const clearTimer = useCallback(() => {
    if (refreshTimer.current !== null) {
      window.clearTimeout(refreshTimer.current);
      refreshTimer.current = null;
    }
  }, []);

  // Refresh shortly before the access token expires so an active learner is never bounced.
  const scheduleRefresh = useCallback(
    (expiresInSeconds: number) => {
      clearTimer();
      const delay = Math.max(15, expiresInSeconds - 60) * 1000;
      refreshTimer.current = window.setTimeout(() => {
        void api.refresh().then((ok) => {
          if (ok) scheduleRefresh(expiresInSeconds);
        });
      }, delay);
    },
    [clearTimer],
  );

  useEffect(() => {
    let cancelled = false;

    void (async () => {
      const refreshed = await api.refresh();
      if (cancelled) return;
      if (!refreshed) {
        setStatus('anonymous');
        return;
      }
      try {
        const me = await userApi.me();
        if (cancelled) return;
        setUser(me);
        setStatus('authenticated');
        scheduleRefresh(15 * 60);
      } catch {
        if (!cancelled) setStatus('anonymous');
      }
    })();

    const unsubscribe = onAuthExpired(() => {
      setUser(null);
      setStatus('anonymous');
      clearTimer();
    });

    return () => {
      cancelled = true;
      unsubscribe();
      clearTimer();
    };
  }, [clearTimer, scheduleRefresh]);

  const login = useCallback(
    async (email: string, password: string) => {
      const result = await authApi.login({ email, password });
      setAccessToken(result.access_token, result.csrf_token);
      setUser(result.user);
      setStatus('authenticated');
      scheduleRefresh(result.expires_in);
    },
    [scheduleRefresh],
  );

  const register = useCallback(
    async ({
      email,
      password,
      displayName,
      track,
    }: {
      email: string;
      password: string;
      displayName: string;
      track: Track;
    }) => {
      const result = await authApi.register({
        email,
        password,
        display_name: displayName,
        track_pref: track,
      });
      setAccessToken(result.access_token, result.csrf_token);
      setUser(result.user);
      setStatus('authenticated');
      scheduleRefresh(result.expires_in);
    },
    [scheduleRefresh],
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // Signing out locally matters even if the network call fails.
    }
    setAccessToken(null, null);
    setUser(null);
    setStatus('anonymous');
    clearTimer();
  }, [clearTimer]);

  const updateProfile = useCallback(
    async (input: { display_name?: string; track_pref?: Track }) => {
      const updated = await userApi.update(input);
      setUser(updated);
    },
    [],
  );

  const value = useMemo<AuthContextValue>(
    () => ({ status, user, login, register, logout, updateProfile }),
    [status, user, login, register, logout, updateProfile],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside <AuthProvider>');
  return context;
}
