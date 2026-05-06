<script lang="ts">
  import { onMount } from 'svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import { theme, accentColors, applyTheme, type ThemeConfig } from '$lib/stores/theme';
  import { currency, cryptoCurrencies, fiatCurrencies, formatCryptoFiat } from '$lib/stores/currency';
  
  $: preview = formatCryptoFiat(100, $currency.cryptoCurrency, $currency.fiatCurrency, $currency.exchangeRates);
  $: previewPnl = formatCryptoFiat(2.5, $currency.cryptoCurrency, $currency.fiatCurrency, $currency.exchangeRates);

  let previewAccent = $theme.accentColor;
  let previewGlass = $theme.glassOpacity;
  let previewBorder = $theme.borderOpacity;
  let previewDimmer = $theme.backgroundDimmer;
  let previewFontScale = $theme.fontScale;
  let bgImageUrl = $theme.backgroundImage;
  let bgType = $theme.backgroundType;

  // Update preview in real-time
  $: {
    const preview: ThemeConfig = {
      ...$theme,
      accentColor: previewAccent,
      accentRgb: accentColors.find(c => c.value === previewAccent)?.rgb || '59, 130, 246',
      glassOpacity: previewGlass,
      borderOpacity: previewBorder,
      backgroundDimmer: previewDimmer,
      fontScale: previewFontScale,
      backgroundImage: bgImageUrl,
      backgroundType: bgType,
    };
    applyTheme(preview);
  }

  function saveTheme() {
    const selected = accentColors.find(c => c.value === previewAccent);
    theme.set({
      ...$theme,
      accentColor: previewAccent,
      accentRgb: selected?.rgb || '59, 130, 246',
      glassOpacity: previewGlass,
      borderOpacity: previewBorder,
      backgroundDimmer: previewDimmer,
      fontScale: previewFontScale,
      backgroundImage: bgImageUrl,
      backgroundType: bgType,
    });
  }

  function resetTheme() {
    theme.reset();
    previewAccent = '#3B82F6';
    previewGlass = 0.03;
    previewBorder = 0.1;
    previewDimmer = 0.7;
    previewFontScale = 1;
    bgImageUrl = '';
    bgType = 'solid';
  }

  function handleImageUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        bgImageUrl = e.target?.result as string;
        bgType = 'image';
      };
      reader.readAsDataURL(file);
    }
  }

  const themeOptions = [
    { id: 'dark', label: 'Dark', icon: '🌙' },
    { id: 'light', label: 'Light', icon: '☀️' },
    { id: 'system', label: 'System', icon: '💻' },
  ] as const;
</script>

<div class="space-y-5 max-w-5xl mx-auto pb-20 sm:pb-0">
  <!-- Header -->
  <div>
    <h1 class="text-2xl font-bold text-white/90 font-sans">Appearance Settings</h1>
    <p class="text-white/40 text-sm mt-1">Customize your trading dashboard</p>
  </div>

  <!-- Theme Preview (Mini Dashboard) -->
  <GlassCard title="Live Preview" subtitle="See your changes in real-time">
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
      <div class="glass-card p-3 rounded-xl">
        <div class="flex items-center justify-between mb-2">
          <span class="text-[10px] text-white/40 uppercase tracking-wider">Equity</span>
          <div class="w-1.5 h-1.5 rounded-full" style="background: var(--accent-primary); box-shadow: 0 0 6px var(--accent-primary);"></div>
        </div>
        <p class="text-lg font-mono font-bold text-white/90">$10,420.50</p>
      </div>
      <div class="glass-card p-3 rounded-xl">
        <div class="flex items-center justify-between mb-2">
          <span class="text-[10px] text-white/40 uppercase tracking-wider">P&L</span>
          <div class="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_#10B981]"></div>
        </div>
        <p class="text-lg font-mono font-bold text-emerald-400">+$420.50</p>
      </div>
      <div class="glass-card p-3 rounded-xl">
        <div class="flex items-center justify-between mb-2">
          <span class="text-[10px] text-white/40 uppercase tracking-wider">Positions</span>
          <div class="w-1.5 h-1.5 rounded-full bg-amber-400 shadow-[0_0_6px_#F59E0B]"></div>
        </div>
        <p class="text-lg font-mono font-bold text-white/90">3</p>
      </div>
      <div class="glass-card p-3 rounded-xl" style="border-color: rgba(244, 63, 94, 0.6); animation: pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;">
        <div class="flex items-center justify-between mb-2">
          <span class="text-[10px] text-white/40 uppercase tracking-wider">Drawdown</span>
          <div class="w-1.5 h-1.5 rounded-full bg-rose-400 shadow-[0_0_6px_#F43F5E]"></div>
        </div>
        <p class="text-lg font-mono font-bold text-rose-400">4.2%</p>
      </div>
    </div>

    <!-- Mini Progress Bar -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-xs text-white/40">System Health</span>
        <span class="text-xs font-mono text-white/70">87%</span>
      </div>
      <div class="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
        <div class="h-full rounded-full transition-all" style="width: 87%; background: linear-gradient(90deg, var(--accent-primary)88, var(--accent-primary)); box-shadow: 0 0 8px var(--accent-primary)40;"></div>
      </div>
    </div>
  </GlassCard>

  <!-- Color Theme -->
  <GlassCard title="Color Theme" subtitle="Choose your accent color">
    <div class="grid grid-cols-4 sm:grid-cols-8 gap-3">
      {#each accentColors as color}
        <button
          class="group relative w-full aspect-square rounded-xl border-2 transition-all duration-200 {previewAccent === color.value ? 'border-white scale-110' : 'border-transparent hover:scale-105'}"
          style="background: {color.value}; box-shadow: {previewAccent === color.value ? `0 0 20px ${color.value}60` : 'none'};"
          on:click={() => previewAccent = color.value}
        >
          {#if previewAccent === color.value}
            <div class="absolute inset-0 flex items-center justify-center">
              <svg class="w-5 h-5 text-white drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
          {/if}
          <span class="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] text-white/50 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
            {color.name}
          </span>
        </button>
      {/each}
    </div>
  </GlassCard>

  <!-- Currency Settings -->
  <GlassCard title="Currency Settings" subtitle="Choose your display currencies">
    <div class="space-y-5">
      <!-- Crypto Currency -->
      <div>
        <span class="text-sm text-white/60 mb-2 block">Platform Crypto Currency</span>
        <div class="flex gap-2 p-1 bg-white/[0.03] rounded-xl border border-white/[0.06] w-fit">
          {#each cryptoCurrencies as crypto}
            <button
              class="px-4 py-2 rounded-lg text-sm font-medium transition-all {$currency.cryptoCurrency === crypto.value ? 'bg-white/[0.08] text-white/90' : 'text-white/40 hover:text-white/70'}"
              on:click={() => currency.update(c => ({ ...c, cryptoCurrency: crypto.value }))}
            >
              <span class="mr-1">{crypto.icon}</span>
              {crypto.label}
            </button>
          {/each}
        </div>
      </div>

      <!-- Fiat Currency -->
      <div>
        <span class="text-sm text-white/60 mb-2 block">Fiat Currency</span>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {#each fiatCurrencies as fiat}
            <button
              class="px-4 py-2.5 rounded-xl text-sm font-medium transition-all border {$currency.fiatCurrency === fiat.value ? 'bg-white/[0.08] text-white/90 border-white/20' : 'text-white/40 hover:text-white/70 border-white/[0.06]'}"
              on:click={() => currency.update(c => ({ ...c, fiatCurrency: fiat.value }))}
            >
              <span class="mr-1">{fiat.symbol}</span>
              {fiat.label}
            </button>
          {/each}
        </div>
      </div>

      <!-- Preview -->
      <div class="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06]">
        <span class="text-xs text-white/30 uppercase tracking-wider block mb-3">Preview</span>
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm text-white/50">Total Balance</span>
            <div class="text-right">
              <span class="text-sm font-mono font-semibold text-white/80">{preview.crypto}</span>
              <span class="text-xs text-white/40 block">{preview.fiat}</span>
            </div>
          </div>
          <div class="h-px bg-white/[0.06]"></div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-white/50">Today's P&L</span>
            <div class="text-right">
              <span class="text-sm font-mono font-semibold text-emerald-400">+{previewPnl.crypto}</span>
              <span class="text-xs text-emerald-400/60 block">+{previewPnl.fiat.replace('≈ ', '')}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </GlassCard>

  <!-- Dark/Light Mode -->
  <GlassCard title="Appearance Mode" subtitle="Choose your preferred theme">
    <div class="flex gap-2 p-1 bg-white/[0.03] rounded-xl border border-white/[0.06]">
      {#each themeOptions as option}
        <button
          class="flex-1 py-2.5 px-3 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 {$theme.theme === option.id ? 'bg-white/[0.08] text-white/90' : 'text-white/40 hover:text-white/70'}"
          on:click={() => {
            $theme.theme = option.id;
            applyTheme($theme);
          }}
        >
          <span>{option.icon}</span>
          <span class="hidden sm:inline">{option.label}</span>
        </button>
      {/each}
    </div>
  </GlassCard>

  <!-- Background Settings -->
  <GlassCard title="Background" subtitle="Customize your dashboard background">
    <div class="space-y-5">
      <!-- Background Type Toggle -->
      <div class="flex gap-2 p-1 bg-white/[0.03] rounded-xl border border-white/[0.06] w-fit">
        <button
          class="px-4 py-2 rounded-lg text-sm font-medium transition-all {bgType === 'solid' ? 'bg-white/[0.08] text-white/90' : 'text-white/40 hover:text-white/70'}"
          on:click={() => bgType = 'solid'}
        >
          Solid Color
        </button>
        <button
          class="px-4 py-2 rounded-lg text-sm font-medium transition-all {bgType === 'image' ? 'bg-white/[0.08] text-white/90' : 'text-white/40 hover:text-white/70'}"
          on:click={() => bgType = 'image'}
        >
          Image
        </button>
      </div>

      {#if bgType === 'image'}
        <div class="space-y-3">
          <label class="block">
            <span class="text-sm text-white/60 mb-2 block">Upload Background Image</span>
            <input
              type="file"
              accept="image/*"
              class="block w-full text-sm text-white/40 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-white/[0.08] file:text-white/70 hover:file:bg-white/[0.12] cursor-pointer"
              on:change={handleImageUpload}
            />
          </label>

          {#if bgImageUrl}
            <div class="relative rounded-xl overflow-hidden h-32 border border-white/[0.1]">
              <img src={bgImageUrl} alt="Background preview" class="w-full h-full object-cover" />
              <div class="absolute inset-0" style="background: rgba(15, 23, 42, {previewDimmer});"></div>
            </div>
          {/if}

          <!-- Dimmer Slider -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-white/60">Background Dimmer</span>
              <span class="text-sm font-mono text-white/40">{Math.round(previewDimmer * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              bind:value={previewDimmer}
              class="w-full h-2 bg-white/[0.1] rounded-full appearance-none cursor-pointer accent-[var(--accent-primary)]"
            />
          </div>
        </div>
      {/if}
    </div>
  </GlassCard>

  <!-- Glass Effect Settings -->
  <GlassCard title="Glass Effects" subtitle="Adjust transparency and borders">
    <div class="space-y-5">
      <!-- Glass Opacity -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-white/60">Card Opacity</span>
          <span class="text-sm font-mono text-white/40">{Math.round(previewGlass * 1000) / 10}%</span>
        </div>
        <input
          type="range"
          min="0"
          max="0.15"
          step="0.005"
          bind:value={previewGlass}
          class="w-full h-2 bg-white/[0.1] rounded-full appearance-none cursor-pointer"
          style="accent-color: var(--accent-primary);"
        />
      </div>

      <!-- Border Opacity -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-white/60">Border Opacity</span>
          <span class="text-sm font-mono text-white/40">{Math.round(previewBorder * 100)}%</span>
        </div>
        <input
          type="range"
          min="0"
          max="0.3"
          step="0.01"
          bind:value={previewBorder}
          class="w-full h-2 bg-white/[0.1] rounded-full appearance-none cursor-pointer"
          style="accent-color: var(--accent-primary);"
        />
      </div>
    </div>
  </GlassCard>

  <!-- Font Scale -->
  <GlassCard title="Font Scale" subtitle="Adjust text size">
    <div class="flex items-center gap-4">
      <span class="text-sm text-white/40">A</span>
      <input
        type="range"
        min="0.85"
        max="1.25"
        step="0.05"
        bind:value={previewFontScale}
        class="flex-1 h-2 bg-white/[0.1] rounded-full appearance-none cursor-pointer"
        style="accent-color: var(--accent-primary);"
      />
      <span class="text-lg text-white/40">A</span>
      <span class="text-sm font-mono text-white/40 w-12 text-right">{Math.round(previewFontScale * 100)}%</span>
    </div>
  </GlassCard>

  <!-- Action Buttons -->
  <div class="flex gap-3">
    <button
      class="flex-1 py-3 px-6 rounded-xl font-medium text-white transition-all hover:opacity-90 active:scale-[0.98]"
      style="background: linear-gradient(135deg, var(--accent-primary), var(--accent-primary)dd); box-shadow: 0 0 20px var(--accent-primary)40;"
      on:click={saveTheme}
    >
      Save Changes
    </button>
    <button
      class="px-6 py-3 rounded-xl font-medium text-white/60 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.08] transition-all"
      on:click={resetTheme}
    >
      Reset to Default
    </button>
  </div>
</div>

<style>
  /* Range input styling */
  input[type="range"] {
    -webkit-appearance: none;
    appearance: none;
    height: 8px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.1);
    outline: none;
  }
  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--accent-primary, #3B82F6);
    cursor: pointer;
    box-shadow: 0 0 10px var(--accent-primary, #3B82F6)60;
    border: 2px solid white;
  }
  input[type="range"]::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--accent-primary, #3B82F6);
    cursor: pointer;
    box-shadow: 0 0 10px var(--accent-primary, #3B82F6)60;
    border: 2px solid white;
  }

  @keyframes pulse-glow {
    0%, 100% {
      box-shadow: 0 0 5px rgba(244, 63, 94, 0.4), 0 0 10px rgba(244, 63, 94, 0.2);
    }
    50% {
      box-shadow: 0 0 20px rgba(244, 63, 94, 0.6), 0 0 40px rgba(244, 63, 94, 0.3);
    }
  }
</style>
