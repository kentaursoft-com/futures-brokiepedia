<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let scrolled = false;

  onMount(() => {
    const onScroll = () => scrolled = window.scrollY > 20;
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  });
</script>

<svelte:head>
  <title>Futures Brokiepedia — AI-Powered Crypto Trading</title>
</svelte:head>

<!-- ===== HEADER ===== -->
<header class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 {scrolled ? 'bg-zinc-950/90 backdrop-blur-xl border-b border-zinc-800/50' : 'bg-transparent'}">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
    <!-- Logo -->
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl flex items-center justify-center shadow-lg bg-gradient-to-br from-emerald-500 to-emerald-600">
        <span class="text-white font-bold text-sm font-mono">FB</span>
      </div>
      <span class="font-bold text-lg text-white/90 hidden sm:block">Futures Brokiepedia</span>
    </div>

    <!-- Navigation -->
    <nav class="hidden md:flex items-center gap-8">
      <a href="#features" class="text-sm text-zinc-400 hover:text-white transition-colors">Features</a>
      <a href="#how-it-works" class="text-sm text-zinc-400 hover:text-white transition-colors">How It Works</a>
      <a href="#security" class="text-sm text-zinc-400 hover:text-white transition-colors">Security</a>
    </nav>

    <!-- Sign In -->
    <button
      class="px-5 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 transition-all shadow-lg shadow-emerald-900/30 active:scale-[0.98]"
      on:click={() => goto('/auth')}
    >
      Sign In
    </button>
  </div>
</header>

<!-- ===== HERO ===== -->
<section class="min-h-screen flex items-center relative overflow-hidden bg-zinc-950">
  <!-- Background gradient -->
  <div class="absolute inset-0 bg-gradient-to-b from-emerald-950/20 via-zinc-950 to-zinc-950"></div>
  <div class="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-emerald-500/5 rounded-full blur-3xl"></div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6 pt-24 pb-16 relative z-10">
    <div class="max-w-3xl mx-auto text-center">
      <!-- Badge -->
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium mb-6">
        <div class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div>
        AI Trading Platform — Now Live
      </div>

      <!-- Headline -->
      <h1 class="text-4xl sm:text-5xl md:text-6xl font-bold text-white leading-tight tracking-tight">
        Trade Crypto Futures
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-emerald-300">with AI Precision</span>
      </h1>

      <p class="text-lg sm:text-xl text-zinc-400 mt-6 max-w-2xl mx-auto leading-relaxed">
        Autonomous multi-agent system that analyzes markets, generates signals, and executes trades across 8 exchanges. Powered by LangGraph and DeepSeek AI.
      </p>

      <!-- CTA Buttons -->
      <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mt-10">
        <button
          class="w-full sm:w-auto px-8 py-3.5 rounded-xl text-base font-semibold text-white bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 transition-all shadow-xl shadow-emerald-900/40 active:scale-[0.98]"
          on:click={() => goto('/auth')}
        >
          Launch Dashboard
        </button>
        <a href="#features"
          class="w-full sm:w-auto px-8 py-3.5 rounded-xl text-base font-medium text-zinc-300 bg-zinc-800/50 border border-zinc-700/50 hover:bg-zinc-800 transition-all text-center"
        >
          Learn More
        </a>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-6 mt-16 pt-12 border-t border-zinc-800/50">
        {#each [
          { value: '8', label: 'Exchanges' },
          { value: '6', label: 'AI Agents' },
          { value: '100%', label: 'Automated' },
          { value: '24/7', label: 'Trading' },
        ] as stat}
          <div class="text-center">
            <div class="text-2xl sm:text-3xl font-bold font-mono text-white">{stat.value}</div>
            <div class="text-sm text-zinc-500 mt-1">{stat.label}</div>
          </div>
        {/each}
      </div>
    </div>
  </div>
</section>

<!-- ===== FEATURES ===== -->
<section id="features" class="py-20 sm:py-28 bg-zinc-950">
  <div class="max-w-7xl mx-auto px-4 sm:px-6">
    <div class="text-center mb-16">
      <h2 class="text-3xl sm:text-4xl font-bold text-white">Powered by 6 AI Department Agents</h2>
      <p class="text-zinc-400 mt-4 max-w-xl mx-auto">Each department specializes in a different market analysis approach, voting together to produce a single aggregated signal.</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
      {#each [
        { icon: '🧮', title: 'Quantitative', desc: 'Probability models, Kelly criterion position sizing, and Monte Carlo simulations for statistical edge.', color: 'from-blue-500/20 to-blue-600/10', border: 'border-blue-500/20' },
        { icon: '📈', title: 'Technical', desc: 'Multi-timeframe price action analysis with RSI, MACD, EMA, ATR, and volume profile.', color: 'from-cyan-500/20 to-cyan-600/10', border: 'border-cyan-500/20' },
        { icon: '💬', title: 'Sentiment', desc: 'Funding rates, social media pulse, options flow, and Fear & Greed analysis.', color: 'from-pink-500/20 to-pink-600/10', border: 'border-pink-500/20' },
        { icon: '🏛️', title: 'Fundamental', desc: 'Macro context, on-chain metrics, adoption trends, and regulatory landscape.', color: 'from-purple-500/20 to-purple-600/10', border: 'border-purple-500/20' },
        { icon: '📊', title: 'Statistical', desc: 'VaR calculations, correlation blocking, volatility regime classification, and mean reversion.', color: 'from-emerald-500/20 to-emerald-600/10', border: 'border-emerald-500/20' },
        { icon: '🎯', title: 'Qualitative', desc: 'CIO-level synthesis with veto power. Blocks conflicting signals and applies judgment.', color: 'from-amber-500/20 to-amber-600/10', border: 'border-amber-500/20' },
      ] as feature}
        <div class="rounded-xl p-6 border {feature.border} {feature.color} bg-zinc-900/50 hover:bg-zinc-900/80 transition-all group">
          <div class="text-3xl mb-4">{feature.icon}</div>
          <h3 class="text-lg font-semibold text-white mb-2">{feature.title}</h3>
          <p class="text-sm text-zinc-400 leading-relaxed">{feature.desc}</p>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- ===== HOW IT WORKS ===== -->
<section id="how-it-works" class="py-20 sm:py-28 bg-zinc-900/50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6">
    <div class="text-center mb-16">
      <h2 class="text-3xl sm:text-4xl font-bold text-white">How It Works</h2>
      <p class="text-zinc-400 mt-4 max-w-xl mx-auto">From data ingestion to trade execution — fully autonomous pipeline.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      {#each [
        { step: '01', title: 'Ingest', desc: 'Real-time market data from 8 exchanges via ccxt and Binance WebSocket feeds.' },
        { step: '02', title: 'Analyze', desc: '6 AI department agents analyze in parallel via LangGraph state machine.' },
        { step: '03', title: 'Aggregate', desc: 'Weighted voting system produces a single signal with confidence score.' },
        { step: '04', title: 'Execute', desc: 'Risk gate validates, positions sized via Kelly, order placed on exchange.' },
      ] as step}
        <div class="text-center relative">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-4">
            <span class="text-2xl font-bold font-mono text-emerald-400">{step.step}</span>
          </div>
          <h3 class="text-lg font-semibold text-white mb-2">{step.title}</h3>
          <p class="text-sm text-zinc-400 leading-relaxed">{step.desc}</p>
          {#if step.step !== '04'}
            <div class="hidden md:block absolute top-8 left-[60%] w-[calc(80%)] h-px bg-gradient-to-r from-emerald-500/30 to-transparent"></div>
          {/if}
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- ===== EXCHANGES ===== -->
<section class="py-16 sm:py-20 bg-zinc-950">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 text-center">
    <h2 class="text-xl sm:text-2xl font-bold text-white mb-8">Connected to 8 Major Exchanges</h2>
    <div class="flex flex-wrap items-center justify-center gap-6 sm:gap-10">
      {#each [
        { name: 'Binance', color: '#F0B90B' },
        { name: 'Bybit', color: '#F7A600' },
        { name: 'OKX', color: '#fff' },
        { name: 'Bitget', color: '#00F0FF' },
        { name: 'MEXC', color: '#00D084' },
        { name: 'KuCoin', color: '#01C480' },
        { name: 'BingX', color: '#FFC107' },
        { name: 'Gate.io', color: '#1E6FFF' },
      ] as ex}
        <div class="flex items-center gap-2 px-4 py-2 rounded-lg bg-zinc-800/30 border border-zinc-700/30">
          <div class="w-6 h-6 rounded flex items-center justify-center font-bold text-xs" style="background: {ex.color}20; color: {ex.color}">
            {ex.name[0]}
          </div>
          <span class="text-sm font-medium text-zinc-300">{ex.name}</span>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- ===== SECURITY ===== -->
<section id="security" class="py-20 sm:py-28 bg-zinc-900/50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6">
    <div class="max-w-3xl mx-auto">
      <h2 class="text-3xl sm:text-4xl font-bold text-white text-center mb-12">Enterprise-Grade Security</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
        {#each [
          { icon: '🔑', title: 'Passkey Auth', desc: 'WebAuthn passkey authentication for secure, passwordless login.' },
          { icon: '🛡️', title: 'Kill Switch', desc: 'Emergency stop button halts all trading instantly.' },
          { icon: '📋', title: 'Audit Trail', desc: 'Every trade and decision logged with full agent reasoning.' },
          { icon: '🔒', title: 'Risk Gates', desc: 'Multi-layer risk: drawdown limits, position caps, correlation blocking.' },
        ] as sec}
          <div class="flex items-start gap-4 p-5 rounded-xl bg-zinc-800/30 border border-zinc-700/20">
            <span class="text-2xl flex-shrink-0">{sec.icon}</span>
            <div>
              <h3 class="text-base font-semibold text-white mb-1">{sec.title}</h3>
              <p class="text-sm text-zinc-400">{sec.desc}</p>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>
</section>

<!-- ===== CTA ===== -->
<section class="py-20 bg-zinc-950">
  <div class="max-w-3xl mx-auto px-4 sm:px-6 text-center">
    <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">Ready to Trade with AI?</h2>
    <p class="text-zinc-400 text-lg mb-8">Start with paper trading to test the system, then switch to live when you're ready.</p>
    <button
      class="px-10 py-4 rounded-xl text-lg font-semibold text-white bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 transition-all shadow-xl shadow-emerald-900/40 active:scale-[0.98]"
      on:click={() => goto('/auth')}
    >
      Get Started Free
    </button>
  </div>
</section>

<!-- ===== FOOTER ===== -->
<footer class="py-8 border-t border-zinc-800/50 bg-zinc-950">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
    <div class="flex items-center gap-2">
      <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
        <span class="text-white font-bold text-[10px]">FB</span>
      </div>
      <span class="text-sm text-zinc-500">© 2026 Kentaur Soft Inc.</span>
    </div>
    <div class="flex items-center gap-6 text-sm text-zinc-500">
      <a href="https://brokiepedia.com" target="_blank" class="hover:text-zinc-300 transition-colors">Brokiepedia</a>
      <span class="text-zinc-700">|</span>
      <span>Built with LangGraph + DeepSeek</span>
    </div>
  </div>
</footer>
