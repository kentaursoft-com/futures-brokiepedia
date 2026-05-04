import { writable } from "svelte/store";

export interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Ticker {
  symbol: string;
  price: number;
  change24h: number;
  change24hPct: number;
  volume24h: number;
}

function createWebSocketStore() {
  const { subscribe, set, update } = writable<{
    connected: boolean;
    candles: Candle[];
    ticker: Ticker | null;
    lastPrice: number;
  }>({
    connected: false,
    candles: [],
    ticker: null,
    lastPrice: 0,
  });

  let ws: WebSocket | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout>;
  const symbol = "btcusdt";

  function connect() {
    if (typeof WebSocket === 'undefined') return;
    if (ws?.readyState === WebSocket.OPEN) return;

    ws = new WebSocket(`wss://fstream.binance.com/ws/${symbol}@kline_1m`);

    ws.onopen = () => {
      update((s) => ({ ...s, connected: true }));
      console.log("[Binance WS] Connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.e === "kline") {
        const k = data.k;
        const candle: Candle = {
          time: Math.floor(k.t / 1000),
          open: parseFloat(k.o),
          high: parseFloat(k.h),
          low: parseFloat(k.l),
          close: parseFloat(k.c),
          volume: parseFloat(k.v),
        };

        update((s) => {
          const candles = [...s.candles];
          const lastIndex = candles.findIndex((c) => c.time === candle.time);

          if (lastIndex >= 0) {
            candles[lastIndex] = candle;
          } else {
            candles.push(candle);
            if (candles.length > 500) candles.shift();
          }

          return {
            ...s,
            candles,
            lastPrice: candle.close,
            ticker: {
              symbol: "BTC-PERP",
              price: candle.close,
              change24h: 0,
              change24hPct: 0,
              volume24h: 0,
            },
          };
        });
      }
    };

    ws.onclose = () => {
      update((s) => ({ ...s, connected: false }));
      console.log("[Binance WS] Disconnected, reconnecting in 3s...");
      reconnectTimer = setTimeout(connect, 3000);
    };

    ws.onerror = (err) => {
      console.error("[Binance WS] Error:", err);
      ws?.close();
    };
  }

  function disconnect() {
    clearTimeout(reconnectTimer);
    ws?.close();
    ws = null;
  }

  return {
    subscribe,
    connect,
    disconnect,
  };
}

export const binanceWS = createWebSocketStore();
