<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  
  export let items: Array<{ path: string; label: string; icon: string }> = [];
  
  const icons: Record<string, string> = {
    dashboard: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    chart: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z',
    portfolio: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z',
    signal: 'M13 10V3L4 14h7v7l9-11h-7z',
    analytics: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    settings: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
    risk: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
    logs: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    system: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
  };
  
  function navigate(path: string) {
    goto(path);
  }
  
  $: currentPath = $page.url.pathname;
</script>

<!-- Bottom Navigation - Mobile Only -->
<nav class="fixed bottom-0 left-0 right-0 z-50 sm:hidden">
  <!-- Frosted glass backdrop -->
  <div 
    class="absolute inset-0 border-t"
    style="
      background: rgba(15, 23, 42, 0.95);
      backdrop-filter: blur(12px) saturate(180%);
      -webkit-backdrop-filter: blur(12px) saturate(180%);
      border-color: rgba(255, 255, 255, var(--border-opacity, 0.1));
    "
  ></div>
  
  <div class="relative flex items-center justify-around px-2 py-2">
    {#each items.slice(0, 4) as item}
      {@const isActive = currentPath === item.path}
      <button
        class="flex flex-col items-center gap-1 py-2 px-4 rounded-xl transition-all duration-200 {isActive ? 'text-white' : 'text-white/40 hover:text-white/70'}"
        on:click={() => navigate(item.path)}
        style={isActive ? `color: var(--accent-primary);` : ''}
      >
        <div class="relative">
          <svg 
            class="w-6 h-6 transition-transform duration-200 {isActive ? 'scale-110' : ''}" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            stroke-width={isActive ? 2.5 : 1.5}
          >
            <path stroke-linecap="round" stroke-linejoin="round" d={icons[item.icon] || icons.dashboard}></path>
          </svg>
          {#if isActive}
            <div 
              class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full"
              style="background: var(--accent-primary); box-shadow: 0 0 6px var(--accent-primary);"
            ></div>
          {/if}
        </div>
        <span class="text-xs font-medium tracking-wide">{item.label}</span>
      </button>
    {/each}
  </div>
  
  <!-- Safe area padding for iOS -->
  <div class="h-[env(safe-area-inset-bottom)]"></div>
</nav>
