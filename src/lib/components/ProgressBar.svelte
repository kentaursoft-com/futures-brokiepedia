<script lang="ts">
  export let value: number = 0;
  export let max: number = 100;
  export let variant: 'default' | 'emerald' | 'rose' | 'amber' = 'default';
  export let showValue: boolean = true;
  export let size: 'sm' | 'md' | 'lg' = 'md';
  
  $: percentage = Math.min(100, Math.max(0, (value / max) * 100));
  
  $: gradient = variant === 'emerald' 
    ? 'from-emerald-500 to-emerald-400'
    : variant === 'rose'
    ? 'from-rose-500 to-rose-400'
    : variant === 'amber'
    ? 'from-amber-500 to-amber-400'
    : 'from-blue-500 to-cyan-400';
  
  $: height = size === 'sm' ? 'h-1' : size === 'lg' ? 'h-3' : 'h-1.5';
  $: glowColor = variant === 'emerald' ? 'rgba(16, 185, 129, 0.3)' : variant === 'rose' ? 'rgba(244, 63, 94, 0.3)' : variant === 'amber' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(59, 130, 246, 0.3)';
</script>

<div class="w-full">
  <div class="flex items-center justify-between mb-1.5">
    <slot name="label" />
    {#if showValue}
      <span class="text-xs font-mono font-medium text-white/60">{Math.round(percentage)}%</span>
    {/if}
  </div>
  <div class="w-full {height} rounded-full bg-white/[0.06] overflow-hidden">
    <div 
      class="h-full rounded-full bg-gradient-to-r {gradient} transition-all duration-700 ease-out relative"
      style="width: {percentage}%; box-shadow: 0 0 10px {glowColor};"
    >
      <!-- Shine effect -->
      <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
    </div>
  </div>
</div>
