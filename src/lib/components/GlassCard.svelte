<script lang="ts">
  export let title: string = '';
  export let subtitle: string = '';
  export let variant: 'default' | 'danger' | 'warning' | 'success' = 'default';
  export let pulseDanger: boolean = false;
  export let className: string = '';
  
  $: borderGlow = pulseDanger 
    ? 'animate-pulse-glow border-rose-500/60 shadow-[0_0_20px_rgba(244,63,94,0.3)]' 
    : variant === 'danger'
    ? 'border-rose-500/30 hover:border-rose-500/50'
    : variant === 'warning'
    ? 'border-amber-500/30 hover:border-amber-500/50'
    : variant === 'success'
    ? 'border-emerald-500/30 hover:border-emerald-500/50'
    : 'border-white/10 hover:border-white/20';
</script>

<div class="
  relative overflow-hidden rounded-2xl 
  bg-white/[0.03] backdrop-blur-glass
  border {borderGlow}
  transition-all duration-300 ease-out
  hover:bg-white/[0.05] hover:shadow-lg hover:shadow-black/20
  {className}
">
  <!-- Subtle gradient overlay -->
  <div class="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent pointer-events-none"></div>
  
  {#if title}
    <div class="relative px-5 py-4 border-b border-white/5">
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
