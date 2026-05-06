import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface CurrencyConfig {
  cryptoCurrency: string;
  fiatCurrency: string;
  exchangeRates: Record<string, number>;
}

const defaultConfig: CurrencyConfig = {
  cryptoCurrency: 'USDT',
  fiatCurrency: 'PHP',
  exchangeRates: {
    'USDT/PHP': 56.5,
    'USDT/USD': 1.0,
    'BTC/USD': 65000,
    'ETH/USD': 3500,
  }
};

function createCurrencyStore() {
  const stored = browser ? localStorage.getItem('currency_config') : null;
  const initial = stored ? JSON.parse(stored) : defaultConfig;
  
  const { subscribe, set, update } = writable<CurrencyConfig>(initial);
  
  return {
    subscribe,
    set: (config: CurrencyConfig) => {
      if (browser) {
        localStorage.setItem('currency_config', JSON.stringify(config));
      }
      set(config);
    },
    update: (updater: (config: CurrencyConfig) => CurrencyConfig) => {
      update(config => {
        const newConfig = updater(config);
        if (browser) {
          localStorage.setItem('currency_config', JSON.stringify(newConfig));
        }
        return newConfig;
      });
    }
  };
}

export const currency = createCurrencyStore();

export function formatCryptoFiat(
  value: number,
  cryptoCurrency: string,
  fiatCurrency: string,
  exchangeRates: Record<string, number>
): { crypto: string; fiat: string } {
  const rate = exchangeRates[`${cryptoCurrency}/${fiatCurrency}`] || 1;
  const fiatValue = value * rate;
  
  return {
    crypto: `${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })} ${cryptoCurrency}`,
    fiat: `≈ ${fiatValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${fiatCurrency}`
  };
}

export const cryptoCurrencies = [
  { value: 'USDT', label: 'USDT', icon: '₮' },
  { value: 'BTC', label: 'BTC', icon: '₿' },
  { value: 'ETH', label: 'ETH', icon: 'Ξ' },
  { value: 'USDC', label: 'USDC', icon: '₮' },
];

export const fiatCurrencies = [
  { value: 'PHP', label: 'PHP - Philippine Peso', symbol: '₱' },
  { value: 'USD', label: 'USD - US Dollar', symbol: '$' },
  { value: 'EUR', label: 'EUR - Euro', symbol: '€' },
  { value: 'GBP', label: 'GBP - British Pound', symbol: '£' },
  { value: 'JPY', label: 'JPY - Japanese Yen', symbol: '¥' },
  { value: 'KRW', label: 'KRW - Korean Won', symbol: '₩' },
];
