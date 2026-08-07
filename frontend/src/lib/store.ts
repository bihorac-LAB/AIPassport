import { create } from 'zustand';
import type { Track } from '@/api/types';

/**
 * Small amount of purely-client state. Everything durable lives on the server.
 */
type UiState = {
  tutorOpen: boolean;
  theme: 'system' | 'light' | 'dark';
  /** Mirrors the user's saved preference so activities can read it without a fetch. */
  track: Track;
  toggleTutor: () => void;
  setTutorOpen: (open: boolean) => void;
  setTheme: (theme: 'system' | 'light' | 'dark') => void;
  setTrack: (track: Track) => void;
};

const THEME_KEY = 'aip.theme';

function readTheme(): 'system' | 'light' | 'dark' {
  try {
    const stored = window.localStorage.getItem(THEME_KEY);
    return stored === 'light' || stored === 'dark' ? stored : 'system';
  } catch {
    return 'system';
  }
}

export function applyTheme(theme: 'system' | 'light' | 'dark'): void {
  const root = document.documentElement;
  if (theme === 'system') root.removeAttribute('data-theme');
  else root.setAttribute('data-theme', theme);
  try {
    window.localStorage.setItem(THEME_KEY, theme);
  } catch {
    /* ignore */
  }
}

export const useUiStore = create<UiState>((set) => ({
  tutorOpen: false,
  theme: typeof window === 'undefined' ? 'system' : readTheme(),
  track: 'clinical',
  toggleTutor: () => set((state) => ({ tutorOpen: !state.tutorOpen })),
  setTutorOpen: (open) => set({ tutorOpen: open }),
  setTheme: (theme) => {
    applyTheme(theme);
    set({ theme });
  },
  setTrack: (track) => set({ track }),
}));
