<script lang="ts">
  export let title: string = '';
  export let subtitle: string = '';
  export let variant: 'default' | 'danger' | 'warning' | 'success' = 'default';
  export let pulseDanger: boolean = false;
  export let className: string = '';
  
  $: borderStyle = pulseDanger 
    ? 'animate-pulse-glow' 
    : variant === 'danger'
    ? 'hover:border-rose-500/50'
    : variant === 'warning'
    ? 'hover:border-amber-500/50'
    : variant === 'success'
    ? 'hover:border-emerald-500/50'
    : 'hover:border-white/20';
</script>

<div 
  class="
    relative overflow-hidden rounded-2xl 
    backdrop-blur-glass
    transition-all duration-300 ease-out
    hover:shadow-lg hover:shadow-black/20
    {borderStyle}
    {className}
  "
  style="
    background: rgba(255, 255, 255, var(--glass-opacity, 0.03));
    border: 1px solid rgba(255, 255, 255, var(--border-opacity, 0.1));
  "
>
  <!-- Subtle gradient overlay -->
  <div class="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent pointer-events-none"></div>
  
  {#if title}
    <div class="relative px-5 py-4 border-b border-white/[0.05]">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-sm font-semibold text-white/90 tracking-wide font-sans">{title}</h3>
          {#if subtitle}
            <p class="text-xs text-white/40 mt-0.5 font-sans">{subtitle}</p>
          {/if}
        </div>
        <slot name="header-action" />
      </div>
    </div>
  {/if}
  
  <div class="relative p-5">
    <slot />
  </div>
</div>

<style>
  @keyframes pulse-glow {
    0%, 100% { 
      box-shadow: 0 0 5px rgba(244, 63, 94, 0.4), 0 0 10px rgba(244, 63, 94, 0.2);
      border-color: rgba(244, 63, 94, 0.5);
    }
    50% { 
      box-shadow: 0 0 20px rgba(244, 63, 94, 0.6), 0 0 40px rgba(244, 63, 94, 0.3);
      border-color: rgba(244, 63, 94, 0.8);
    }
  }
  
  .animate-pulse-glow {
    animation: pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
</style>
