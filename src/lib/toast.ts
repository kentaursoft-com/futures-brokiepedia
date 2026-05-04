import { writable } from 'svelte/store';

export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
}

function createToastStore() {
  const { subscribe, update } = writable<Toast[]>([]);

  return {
    subscribe,
    add: (message: string, type: Toast['type'] = 'info', duration = 4000) => {
      const id = crypto.randomUUID();
      const toast: Toast = { id, message, type, duration };
      update((toasts) => [...toasts, toast]);
      
      // Auto-remove
      setTimeout(() => {
        update((toasts) => toasts.filter((t) => t.id !== id));
      }, duration);
      
      return id;
    },
    remove: (id: string) => {
      update((toasts) => toasts.filter((t) => t.id !== id));
    },
    success: (message: string, duration?: number) => {
      return createToastStore().add(message, 'success', duration);
    },
    error: (message: string, duration?: number) => {
      return createToastStore().add(message, 'error', duration);
    },
    info: (message: string, duration?: number) => {
      return createToastStore().add(message, 'info', duration);
    },
    warning: (message: string, duration?: number) => {
      return createToastStore().add(message, 'warning', duration);
    },
  };
}

export const toast = createToastStore();
