import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface ThemeConfig {
  accentColor: string;
  accentRgb: string;
  backgroundType: 'solid' | 'image';
  backgroundImage: string;
  backgroundDimmer: number;
  theme: 'dark' | 'light' | 'system';
  glassOpacity: number;
  borderOpacity: number;
  fontScale: number;
}

const ACCENT_COLORS = [
  { name: 'Blue', value: '#3B82F6', rgb: '59, 130, 246' },
  { name: 'Cyan', value: '#06B6D4', rgb: '6, 182, 212' },
  { name: 'Emerald', value: '#10B981', rgb: '16, 185, 129' },
  { name: 'Violet', value: '#8B5CF6', rgb: '139, 92, 246' },
  { name: 'Rose', value: '#F43F5E', rgb: '244, 63, 94' },
  { name: 'Amber', value: '#F59E0B', rgb: '245, 158, 11' },
  { name: 'Orange', value: '#F97316', rgb: '249, 115, 22' },
  { name: 'Pink', value: '#EC4899', rgb: '236, 72, 153' },
];

const DEFAULT_CONFIG: ThemeConfig = {
  accentColor: '#3B82F6',
  accentRgb: '59, 130, 246',
  backgroundType: 'solid',
  backgroundImage: '',
  backgroundDimmer: 0.7,
  theme: 'dark',
  glassOpacity: 0.03,
  borderOpacity: 0.1,
  fontScale: 1,
};

function loadConfig(): ThemeConfig {
  if (!browser) return DEFAULT_CONFIG;
  try {
    const saved = localStorage.getItem('fb_theme_config');
    if (saved) {
      const parsed = JSON.parse(saved);
      // Merge with defaults to handle new fields
      return { ...DEFAULT_CONFIG, ...parsed };
    }
  } catch {
    // ignore
  }
  return DEFAULT_CONFIG;
}

function createThemeStore() {
  const config = loadConfig();
  const { subscribe, set, update } = writable<ThemeConfig>(config);

  return {
    subscribe,
    set: (value: ThemeConfig) => {
      if (browser) {
        localStorage.setItem('fb_theme_config', JSON.stringify(value));
        applyTheme(value);
      }
      set(value);
    },
    update: (fn: (c: ThemeConfig) => ThemeConfig) => {
      update((current) => {
        const next = fn(current);
        if (browser) {
          localStorage.setItem('fb_theme_config', JSON.stringify(next));
          applyTheme(next);
        }
        return next;
      });
    },
    reset: () => {
      if (browser) {
        localStorage.removeItem('fb_theme_config');
        applyTheme(DEFAULT_CONFIG);
      }
      set(DEFAULT_CONFIG);
    },
  };
}

export const theme = createThemeStore();
export const accentColors = ACCENT_COLORS;

export function applyTheme(config: ThemeConfig) {
  if (!browser) return;
  const root = document.documentElement;

  // Apply accent color
  root.style.setProperty('--accent-primary', config.accentColor);
  root.style.setProperty('--accent-rgb', config.accentRgb);

  // Apply glass opacity
  root.style.setProperty('--glass-opacity', String(config.glassOpacity));
  root.style.setProperty('--border-opacity', String(config.borderOpacity));

  // Apply font scale
  root.style.setProperty('--font-scale', String(config.fontScale));

  // Apply background
  if (config.backgroundType === 'image' && config.backgroundImage) {
    root.style.setProperty('--bg-image', `url(${config.backgroundImage})`);
    root.style.setProperty('--bg-dimmer', String(config.backgroundDimmer));
    document.body.classList.add('bg-image-mode');
  } else {
    root.style.removeProperty('--bg-image');
    document.body.classList.remove('bg-image-mode');
  }

  // Apply dark/light theme
  if (config.theme === 'light') {
    root.classList.remove('dark');
    root.classList.add('light');
  } else if (config.theme === 'dark') {
    root.classList.remove('light');
    root.classList.add('dark');
  } else {
    // system
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDark) {
      root.classList.remove('light');
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
      root.classList.add('light');
    }
  }
}

// Initialize theme on load
if (browser) {
  const config = loadConfig();
  applyTheme(config);

  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    const current = loadConfig();
    if (current.theme === 'system') {
      applyTheme(current);
    }
  });
}
