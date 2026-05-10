import { writable } from 'svelte/store';

export type TradingMode = 'paper' | 'live';

function getInitialMode(): TradingMode {
  if (typeof localStorage === 'undefined') return 'paper';
  const stored = localStorage.getItem('futures_trading_mode');
  if (stored === 'live' || stored === 'paper') return stored;
  return 'paper';
}

export const tradingMode = writable<TradingMode>(getInitialMode());

tradingMode.subscribe((mode) => {
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('futures_trading_mode', mode);
  }
});
