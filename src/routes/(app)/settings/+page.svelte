<script lang="ts">
  import { onMount } from 'svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { api } from '$lib/api';
  import { theme, accentColors, applyTheme } from '$lib/stores/theme';
  import { currency, cryptoCurrencies, fiatCurrencies, formatCryptoFiat } from '$lib/stores/currency';

  // ============================================================
  // Trading Preferences
  // ============================================================
  let defaultLeverage = 10;
  let maxPositionSize = 1000;
  let riskPerTrade = 2;
  let defaultTimeframe = '1h';
  let autoTrade = false;

  // ============================================================
  // Notifications
  // ============================================================
  let notifyTrades = true;
  let notifySignals = true;
  let notifyAlerts = true;
  let telegramConnected = false;

  // ============================================================
  // Appearance (simplified)
  // ============================================================
  let previewAccent = $theme.accentColor;
  let saving = false;
  let saveMsg = '';

  const themeOptions = [
    { id: 'dark', label: 'Dark', icon: '🌙' },
    { id: 'light', label: 'Light', icon: '☀️' },
  ] as const;

  const timeframeOptions = ['1m', '5m', '15m', '1h', '4h', '1d'];
  $: systemServices = [
    { name: 'Daemon', status: 'online' },
    { name: 'Turso DB', status: 'online' },
    { name: 'Binance WS', status: 'offline' },
    { name: 'DeepSeek AI', status: 'online' },
    { name: 'Cloudflare', status: 'online' },
    { name: 'GitHub', status: 'online' },
    { name: 'Telegram', status: 'online' },
    { name: 'Execution', status: autoTrade ? 'online' : 'offline' },
  ];

  // ============================================================
  // Load / Save
  // ============================================================
  onMount(async () => {
    try {
      const saved = await api.getSettings();
      if (saved) {
        defaultLeverage = saved.trading?.defaultLeverage ?? 10;
        maxPositionSize = saved.trading?.maxPositionSize ?? 1000;
        riskPerTrade = saved.trading?.riskPerTrade ?? 2;
        defaultTimeframe = saved.trading?.defaultTimeframe ?? '1h';
        autoTrade = saved.trading?.autoTrade ?? false;
        notifyTrades = saved.notifications?.trades ?? true;
        notifySignals = saved.notifications?.signals ?? true;
        notifyAlerts = saved.notifications?.alerts ?? true;
        telegramConnected = saved.notifications?.telegram ?? false;
        previewAccent = saved.appearance?.accent || $theme.accentColor;
      }
    } catch (e) {
      console.log('No saved settings, using defaults');
    }
  });

  async function saveSettings() {
    saving = true;
    saveMsg = '';
    try {
      await api.saveSettings({
        trading: { defaultLeverage, maxPositionSize, riskPerTrade, defaultTimeframe, autoTrade },
        notifications: { trades: notifyTrades, signals: notifySignals, alerts: notifyAlerts, telegram: telegramConnected },
        appearance: { accent: previewAccent },
      });
      saveMsg = '✅ Settings saved';
      setTimeout(() => saveMsg = '', 3000);
    } catch (e: any) {
      saveMsg = '❌ Failed to save: ' + (e.message || 'unknown error');
    } finally {
      saving = false;
    }
  }

  async function triggerKillSwitch() {
    if (!confirm('⚠️ TRIGGER KILL SWITCH?\n\nThis will halt ALL trading immediately.')) return;
    try {
      await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/killswitch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ passkey_verified: true }),
        credentials: 'include',
      });
      saveMsg = '🛑 Kill switch activated!';
    } catch (e: any) {
      saveMsg = '❌ Kill switch failed: ' + (e.message || 'daemon unreachable');
    }
  }
</script>

<div class="space-y-5 max-w-5xl mx-auto pb-20 sm:pb-0">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
    <div>
      <h1 class="text-2xl font-bold text-white/90 font-sans">Settings</h1>
      <p class="text-white/40 text-sm mt-1">Trading preferences and system configuration</p>
    </div>
    <StatusBadge status={autoTrade ? 'online' : 'offline'} label={autoTrade ? 'AUTO-TRADE ON' : 'AUTO-TRADE OFF'} size="sm" />
  </div>

  {#if saveMsg}
    <div class="px-4 py-3 rounded-lg text-sm font-sans {saveMsg.startsWith('✅') ? 'bg-emerald-900/40 text-emerald-300 border border-emerald-700/40' : saveMsg.startsWith('❌') ? 'bg-rose-900/40 text-rose-300 border border-rose-700/40' : 'bg-amber-900/40 text-amber-300 border border-amber-700/40'}">
      {saveMsg}
    </div>
  {/if}

  <!-- ============================================================ -->
  <!-- TRADING PREFERENCES -->
  <!-- ============================================================ -->
  <GlassCard title="Trading Preferences" subtitle="Default trade parameters">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
      <div>
        <label for="lev-select" class="text-sm text-zinc-400 font-sans block mb-1.5">Default Leverage</label>
        <select id="lev-select"
          class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-white text-sm font-mono focus:outline-none focus:border-emerald-500"
          bind:value={defaultLeverage}
        >
          {#each [1, 2, 3, 5, 10, 20, 25, 50, 75, 100] as lev}
            <option value={lev}>{lev}x</option>
          {/each}
        </select>
      </div>

      <div>
        <label for="tf-select" class="text-sm text-zinc-400 font-sans block mb-1.5">Default Timeframe</label>
        <select id="tf-select"
          class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-white text-sm font-mono focus:outline-none focus:border-emerald-500"
          bind:value={defaultTimeframe}
        >
          {#each timeframeOptions as tf}
            <option value={tf}>{tf}</option>
          {/each}
        </select>
      </div>

      <div>
        <label for="pos-size" class="text-sm text-zinc-400 font-sans block mb-1.5">Max Position Size (USDT)</label>
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 font-mono text-sm">$</span>
          <input id="pos-size"
            type="number"
            class="w-full bg-zinc-800 border border-zinc-700 rounded-lg pl-8 pr-3 py-2 text-white text-sm font-mono focus:outline-none focus:border-emerald-500"
            bind:value={maxPositionSize}
            min="0"
            step="100"
          />
        </div>
      </div>

      <div>
        <label for="risk-range" class="text-sm text-zinc-400 font-sans block mb-1.5">Risk Per Trade (%)</label>
        <div class="flex items-center gap-3">
          <input id="risk-range"
            type="range"
            min="0.5"
            max="5"
            step="0.1"
            bind:value={riskPerTrade}
            class="flex-1 h-2 bg-zinc-700 rounded-full appearance-none cursor-pointer accent-emerald-500"
          />
          <span class="text-sm font-mono text-zinc-300 w-10 text-right">{riskPerTrade}%</span>
        </div>
      </div>
    </div>

    <!-- Auto-Trade Toggle -->
    <div class="flex items-center justify-between mt-5 pt-4 border-t border-zinc-800/50">
      <div>
        <span class="text-sm text-zinc-300 font-sans">Automated Trading</span>
        <p class="text-xs text-zinc-500 font-sans mt-0.5">Allow the AI engine to execute trades automatically</p>
      </div>
      <button
        class="relative w-12 h-6 rounded-full transition-colors {autoTrade ? 'bg-emerald-500' : 'bg-zinc-700'}"
        on:click={() => autoTrade = !autoTrade}
      >
        <div class="absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform {autoTrade ? 'translate-x-6' : ''}"></div>
      </button>
    </div>
  </GlassCard>

  <!-- ============================================================ -->
  <!-- NOTIFICATIONS -->
  <!-- ============================================================ -->
  <GlassCard title="Notifications" subtitle="Telegram and in-app alerts">
    <div class="space-y-4">
      <div class="flex items-center justify-between py-2">
        <div class="flex items-center gap-3">
          <div class="w-2 h-2 rounded-full {telegramConnected ? 'bg-emerald-400' : 'bg-rose-400'}"></div>
          <div>
            <span class="text-sm text-zinc-300 font-sans">Telegram Bot</span>
            <p class="text-xs text-zinc-500 font-sans">Connected to @FuturesBrokiepediaBot</p>
          </div>
        </div>
        <StatusBadge status={telegramConnected ? 'online' : 'offline'} size="sm" />
      </div>

      <div class="space-y-3 ml-5 pl-4 border-l border-zinc-800/50">
        {#each [
          { key: 'notifyTrades', label: 'Trade Execution', desc: 'When a trade is opened or closed', bind: notifyTrades },
          { key: 'notifySignals', label: 'New Signal', desc: 'When a department generates a signal', bind: notifySignals },
          { key: 'notifyAlerts', label: 'Risk Alerts', desc: 'Drawdown warnings and system alerts', bind: notifyAlerts },
        ] as item}
          <div class="flex items-center justify-between">
            <div>
              <span class="text-sm text-zinc-300 font-sans">{item.label}</span>
              <p class="text-xs text-zinc-500 font-sans">{item.desc}</p>
            </div>
            <button
              class="relative w-10 h-5 rounded-full transition-colors flex-shrink-0 {item.bind ? 'bg-emerald-500' : 'bg-zinc-700'}"
              on:click={() => {
                if (item.key === 'notifyTrades') notifyTrades = !notifyTrades;
                if (item.key === 'notifySignals') notifySignals = !notifySignals;
                if (item.key === 'notifyAlerts') notifyAlerts = !notifyAlerts;
              }}
            >
              <div class="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform {item.bind ? 'translate-x-5' : ''}"></div>
            </button>
          </div>
        {/each}
      </div>
    </div>
  </GlassCard>

  <!-- ============================================================ -->
  <!-- SYSTEM STATUS -->
  <!-- ============================================================ -->
  <GlassCard title="System Status" subtitle="Infrastructure health">
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {#each systemServices as service}
        <div class="bg-zinc-800/30 rounded-xl p-3 border border-zinc-700/30">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs text-zinc-400 font-sans">{service.name}</span>
            <div class="w-2 h-2 rounded-full {service.status === 'online' ? 'bg-emerald-400' : 'bg-rose-400'}"></div>
          </div>
        </div>
      {/each}
    </div>
  </GlassCard>

  <!-- ============================================================ -->
  <!-- QUICK LINKS -->
  <!-- ============================================================ -->
  <GlassCard title="Quick Links">
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <a href="/api-keys" class="flex items-center gap-3 p-3 rounded-xl bg-zinc-800/30 border border-zinc-700/30 hover:border-emerald-500/30 transition-all group">
        <span class="text-lg">🔑</span>
        <span class="text-sm text-zinc-300 group-hover:text-white transition-colors">API Keys</span>
      </a>
      <a href="/trade" class="flex items-center gap-3 p-3 rounded-xl bg-zinc-800/30 border border-zinc-700/30 hover:border-blue-500/30 transition-all group">
        <span class="text-lg">📊</span>
        <span class="text-sm text-zinc-300 group-hover:text-white transition-colors">Open Trade</span>
      </a>
      <a href="/signals" class="flex items-center gap-3 p-3 rounded-xl bg-zinc-800/30 border border-zinc-700/30 hover:border-purple-500/30 transition-all group">
        <span class="text-lg">📶</span>
        <span class="text-sm text-zinc-300 group-hover:text-white transition-colors">View Signals</span>
      </a>
    </div>
  </GlassCard>

  <!-- ============================================================ -->
  <!-- APPEARANCE (SIMPLIFIED) -->
  <!-- ============================================================ -->
  <GlassCard title="Appearance" subtitle="Theme and display preferences">
    <div class="space-y-5">
      <!-- Dark/Light + Accent in one row -->
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <span class="text-sm text-zinc-400 font-sans block mb-2">Theme Mode</span>
          <div class="flex gap-2 p-1 bg-zinc-800/50 rounded-xl border border-zinc-700/30">
            {#each themeOptions as option}
              <button
                class="flex-1 py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-1.5 {$theme.theme === option.id ? 'bg-zinc-700/80 text-white/90' : 'text-zinc-400 hover:text-white/70'}"
                on:click={() => { $theme.theme = option.id; applyTheme($theme); }}
              >
                <span>{option.icon}</span>
                <span>{option.label}</span>
              </button>
            {/each}
          </div>
        </div>
        <div>
          <span class="text-sm text-zinc-400 font-sans block mb-2">Accent Color</span>
          <div class="flex gap-2">
            {#each accentColors.filter((_, i) => i % 2 === 0 || i === 1 || i === 5 || i === 9 || i === 13) as color}
              <button
                class="w-8 h-8 rounded-full border-2 transition-all {previewAccent === color.value ? 'border-white scale-110' : 'border-transparent hover:scale-105'}"
                style="background: {color.value}; box-shadow: {previewAccent === color.value ? `0 0 12px ${color.value}60` : 'none'};"
                on:click={() => {
                  previewAccent = color.value;
                  const c = accentColors.find(a => a.value === color.value);
                  theme.update(t => ({ ...t, accentColor: color.value, accentRgb: c?.rgb || '59,130,246' }));
                  applyTheme({ ...$theme, accentColor: color.value, accentRgb: c?.rgb || '59,130,246' });
                }}
              >
                {#if previewAccent === color.value}
                  <div class="flex items-center justify-center">
                    <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                {/if}
              </button>
            {/each}
          </div>
        </div>
      </div>

      <!-- Currency (compact) -->
      <div class="flex flex-col sm:flex-row gap-4 pt-4 border-t border-zinc-800/50">
        <div class="flex-1">
          <span class="text-sm text-zinc-400 font-sans block mb-2">Crypto Display</span>
          <div class="flex gap-2">
            {#each cryptoCurrencies as crypto}
              <button
                class="px-3 py-1.5 rounded-lg text-sm transition-all {$currency.cryptoCurrency === crypto.value ? 'bg-zinc-700/80 text-white/90' : 'text-zinc-400 hover:text-white/70'}"
                on:click={() => currency.update(c => ({ ...c, cryptoCurrency: crypto.value }))}
              >
                {crypto.icon} {crypto.label}
              </button>
            {/each}
          </div>
        </div>
        <div>
          <span class="text-sm text-zinc-400 font-sans block mb-2">Fiat Display</span>
          <div class="flex gap-2">
            {#each fiatCurrencies as fiat}
              <button
                class="px-3 py-1.5 rounded-lg text-sm transition-all {$currency.fiatCurrency === fiat.value ? 'bg-zinc-700/80 text-white/90' : 'text-zinc-400 hover:text-white/70'}"
                on:click={() => currency.update(c => ({ ...c, fiatCurrency: fiat.value }))}
              >
                {fiat.symbol} {fiat.label}
              </button>
            {/each}
          </div>
        </div>
      </div>
    </div>
  </GlassCard>

  <!-- ============================================================ -->
  <!-- KILL SWITCH + SAVE -->
  <!-- ============================================================ -->
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
    <button
      class="flex items-center justify-center gap-3 py-4 px-6 rounded-xl font-semibold text-white bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 active:scale-[0.98] transition-all shadow-lg shadow-rose-900/40"
      on:click={triggerKillSwitch}
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
      EMERGENCY KILL SWITCH
    </button>

    <button
      class="flex items-center justify-center gap-2 py-4 px-6 rounded-xl font-semibold text-white transition-all {saving ? 'bg-emerald-700' : 'bg-emerald-600 hover:bg-emerald-500'} active:scale-[0.98]"
      on:click={saveSettings}
      disabled={saving}
    >
      {saving ? '⏳ Saving...' : '💾 Save Settings'}
    </button>
  </div>
</div>
