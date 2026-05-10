<script lang="ts">
  import '../../app.css';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { liveState, startPolling } from '$lib/api';
  import { tradingMode, type TradingMode } from '$lib/stores/tradingMode';
  import { onMount } from 'svelte';
  import BottomNav from '$lib/components/BottomNav.svelte';
  
  let userMenuOpen = false;
  let stopPolling: (() => void) | null = null;
  
  onMount(() => {
    stopPolling = startPolling(5000);
    return () => {
      if (stopPolling) stopPolling();
    };
  });
  
  $: daemonConnected = $liveState ? true : false;
  $: systemStatus = $liveState?.systemStatus || 'paper';
  
  const navItems = [
    { path: '/', label: 'Dash', icon: 'dashboard' },
    { path: '/exchanges', label: 'Exchanges', icon: 'exchange' },
    { path: '/trade', label: 'Trade', icon: 'chart' },
    { path: '/positions', label: 'Risk', icon: 'risk' },
    { path: '/signals', label: 'Signals', icon: 'signal' },
    { path: '/journal', label: 'Journal', icon: 'journal' },
    { path: '/api-keys', label: 'API Keys', icon: 'key' },
    { path: '/analytics', label: 'Logs', icon: 'analytics' },
    { path: '/settings', label: 'System', icon: 'settings' },
  ];
  
  function navigateTo(path: string) {
    goto(path);
  }
  
  function logout() {
    document.cookie = 'session_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
    window.location.href = '/auth';
  }
  
  $: currentPath = $page.url.pathname;
</script>

<div class="min-h-screen bg-navy text-white flex font-sans" style="font-size: calc(1rem * var(--font-scale, 1));">
  <!-- Desktop Sidebar - Icon Only, Expands on Hover -->
  <aside class="hidden sm:flex flex-col fixed left-0 top-0 h-screen z-40 w-[72px] hover:w-56 group transition-all duration-300 ease-out glass border-r-0 border-r border-white/[0.06]" style="border-right: 1px solid rgba(255, 255, 255, var(--border-opacity, 0.1));">
    <!-- Logo -->
    <div class="h-16 flex items-center px-5 border-b border-white/[0.06] overflow-hidden">
      <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg" style="background: linear-gradient(135deg, var(--accent-primary), var(--accent-primary)dd); box-shadow: 0 0 15px var(--accent-primary)40;">
        <span class="text-white font-bold text-sm font-mono">FB</span>
      </div>
      <span class="ml-3 font-bold text-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-white/90">Futures</span>
    </div>
    
    <!-- Navigation -->
    <nav class="flex-1 py-4 px-3 space-y-1 overflow-hidden">
      {#each navItems as item}
        {@const isActive = currentPath === item.path}
        <button
          class="w-full flex items-center px-3 py-3 rounded-xl transition-all duration-200 relative overflow-hidden {isActive ? 'text-white' : 'text-white/40 hover:text-white/80'}"
          style={isActive ? `background: linear-gradient(90deg, rgba(var(--accent-rgb), 0.15), transparent);` : ''}
          on:click={() => navigateTo(item.path)}
        >
          {#if isActive}
            <div class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full shadow-[0_0_8px]" style="background: var(--accent-primary); box-shadow: 0 0 8px var(--accent-primary);"></div>
          {/if}
          <svg class="w-5 h-5 flex-shrink-0 transition-all duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width={isActive ? 2.5 : 1.5} style={isActive ? `filter: drop-shadow(0 0 4px var(--accent-primary));` : ''}>
            {#if item.icon === 'dashboard'}
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
            {:else if item.icon === 'exchange'}
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
            {:else if item.icon === 'chart'}
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path>
            {:else if item.icon === 'risk'}
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            {:else if item.icon === 'signal'}
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            {:else if item.icon === 'analytics'}
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            {:else if item.icon === 'settings'}
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            {:else if item.icon === 'key'}
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
            {:else if item.icon === 'journal'}
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
            {/if}
          </svg>
          <span class="ml-3 text-sm font-medium whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300">{item.label}</span>
        </button>
      {/each}
    </nav>
    
    <!-- Status Footer -->
    <div class="p-4 border-t border-white/[0.06] overflow-hidden">
      <div class="flex items-center gap-3">
        <div 
          class="w-2.5 h-2.5 rounded-full flex-shrink-0 {daemonConnected ? 'animate-pulse' : ''}"
          style="background: {daemonConnected ? '#10B981' : '#64748B'}; box-shadow: 0 0 8px {daemonConnected ? 'rgba(16,185,129,0.6)' : 'transparent'};"
        ></div>
        <div class="whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <span class="text-xs text-white/50">{daemonConnected ? 'Online' : 'Offline'}</span>
          <span class="ml-2 text-[10px] font-mono px-1.5 py-0.5 rounded {systemStatus === 'live' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'}">{systemStatus.toUpperCase()}</span>
        </div>
      </div>
    </div>
  </aside>
  
  <!-- Main Content Area -->
  <div class="flex-1 flex flex-col min-h-screen sm:ml-[72px] w-full">
    <!-- Top Header - Glassmorphic -->
    <header class="h-14 sm:h-16 sticky top-0 z-30 glass border-b-0 flex items-center px-4 sm:px-6" style="border-bottom: 1px solid rgba(255, 255, 255, var(--border-opacity, 0.1));">
      <!-- Mobile Brand -->
      <div class="sm:hidden flex items-center gap-3 mr-4">
        <div class="w-8 h-8 rounded-xl flex items-center justify-center shadow-lg" style="background: linear-gradient(135deg, var(--accent-primary), var(--accent-primary)dd); box-shadow: 0 0 15px var(--accent-primary)40;">
          <span class="text-white font-bold text-sm font-mono">FB</span>
        </div>
      </div>
      
      <!-- Portfolio Mode Toggle -->
      <div class="flex-1 flex items-center px-2">
        <div class="flex p-0.5 bg-zinc-800/60 rounded-lg border border-zinc-700/30">
          <button
            class="px-3 py-1.5 rounded-md text-xs font-semibold font-mono tracking-wider transition-all {$tradingMode === 'paper' ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-900/40' : 'text-zinc-500 hover:text-zinc-300'}"
            on:click={() => tradingMode.set('paper')}
          >
            <span class="mr-1">📄</span> PAPER
          </button>
          <button
            class="px-3 py-1.5 rounded-md text-xs font-semibold font-mono tracking-wider transition-all {$tradingMode === 'live' ? 'bg-rose-600 text-white shadow-sm shadow-rose-900/40' : 'text-zinc-500 hover:text-zinc-300'}"
            on:click={() => tradingMode.set('live')}
          >
            <span class="mr-1">🔥</span> LIVE
          </button>
        </div>
      </div>
      
      <div class="ml-auto flex items-center gap-3">
        <!-- Notification Bell -->
        <button class="p-2 rounded-xl hover:bg-white/[0.06] transition-colors relative">
          <svg class="w-5 h-5 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
          </svg>
          <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full shadow-[0_0_6px_rgba(244,63,94,0.6)]"></span>
        </button>
        
        <!-- User Menu -->
        <div class="relative">
          <button 
            class="w-8 h-8 rounded-xl flex items-center justify-center hover:opacity-90 transition-all border"
            style="background: linear-gradient(135deg, var(--accent-primary)20, var(--accent-primary)10); border-color: var(--accent-primary)30;"
            on:click={() => userMenuOpen = !userMenuOpen}
          >
            <span class="text-xs font-bold font-mono" style="color: var(--accent-primary);">K</span>
          </button>
          {#if userMenuOpen}
            <div class="absolute right-0 mt-2 w-48 glass rounded-2xl shadow-2xl z-50 py-1 overflow-hidden">
              <div class="px-4 py-3 border-b border-white/[0.06]">
                <p class="text-sm font-semibold text-white/90">Kentaur</p>
                <p class="text-xs text-white/40 font-mono">Admin</p>
              </div>
              <button 
                class="w-full text-left px-4 py-2.5 text-sm hover:bg-white/[0.04] transition-colors flex items-center gap-2 text-white/70"
                on:click={() => { userMenuOpen = false; goto('/settings'); }}
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                Settings
              </button>
              <button 
                class="w-full text-left px-4 py-2.5 text-sm hover:bg-white/[0.04] transition-colors flex items-center gap-2 text-rose-400"
                on:click={() => { userMenuOpen = false; logout(); }}
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                Sign Out
              </button>
            </div>
          {/if}
        </div>
      </div>
    </header>
    
    <!-- Page Content -->
    <main class="flex-1 p-4 sm:p-6 pb-24 sm:pb-6 overflow-auto">
      <slot />
    </main>
  </div>
  
  <!-- Mobile Bottom Navigation -->
  <BottomNav items={navItems} />
</div>

<style>
</style>
