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
    prices: Record<string, number>;
  }>({
    connected: false,
    candles: [],
    ticker: null,
    lastPrice: 0,
    prices: {},
  });

  let ws: WebSocket | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout>;
  const symbol = "btcusdt";

  function connect() {
    if (typeof WebSocket === 'undefined') return;
    if (ws?.readyState === WebSocket.OPEN) return;

    // Subscribe to both kline and ticker streams
    const streams = `${symbol}@kline_1m/${symbol}@ticker`;
    ws = new WebSocket(`wss://fstream.binance.com/stream?streams=${streams}`);

    ws.onopen = () => {
      update((s) => ({ ...s, connected: true }));
      console.log("[Binance WS] Connected");
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      const data = message.data;
      
      if (!data) return;

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
            prices: { ...s.prices, BTCUSDT: candle.close },
          };
        });
      } else if (data.e === "24hrTicker") {
        const price = parseFloat(data.c);
        const change24h = parseFloat(data.p);
        const change24hPct = parseFloat(data.P);
        const volume24h = parseFloat(data.v);

        update((s) => ({
          ...s,
          lastPrice: price,
          prices: { ...s.prices, BTCUSDT: price },
          ticker: {
            symbol: "BTC-PERP",
            price,
            change24h,
            change24hPct,
            volume24h,
          },
        }));
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
