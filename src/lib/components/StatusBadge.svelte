<script lang="ts">
  export let status: 'online' | 'offline' | 'warning' | 'error' | 'processing' = 'offline';
  export let label: string = '';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  
  const config = {
    online: { 
      color: '#10B981', 
      bg: 'rgba(16, 185, 129, 0.15)',
      glow: 'animate-glow-emerald',
      label: 'ONLINE'
    },
    offline: { 
      color: '#64748B', 
      bg: 'rgba(100, 116, 139, 0.15)',
      glow: '',
      label: 'OFFLINE'
    },
    warning: { 
      color: '#F59E0B', 
      bg: 'rgba(245, 158, 11, 0.15)',
      glow: 'animate-glow-amber',
      label: 'WARNING'
    },
    error: { 
      color: '#F43F5E', 
      bg: 'rgba(244, 63, 94, 0.15)',
      glow: 'animate-glow-rose',
      label: 'ERROR'
    },
    processing: { 
      color: '#3B82F6', 
      bg: 'rgba(59, 130, 246, 0.15)',
      glow: 'animate-pulse',
      label: 'PROCESSING'
    },
  };
  
  $: c = config[status];
  $: sizeClasses = size === 'sm' ? 'text-[10px] px-2 py-0.5 gap-1.5' : size === 'lg' ? 'text-sm px-4 py-1.5 gap-2.5' : 'text-xs px-3 py-1 gap-2';
  $: dotSize = size === 'sm' ? 'w-1.5 h-1.5' : size === 'lg' ? 'w-2.5 h-2.5' : 'w-2 h-2';
</script>

<div 
  class="inline-flex items-center rounded-full font-mono font-semibold tracking-wider {sizeClasses} {c.glow}"
  style="background: {c.bg}; color: {c.color};"
>
  <span 
    class="rounded-full {dotSize} flex-shrink-0"
    style="background: {c.color}; box-shadow: 0 0 6px {c.color}, 0 0 12px {c.color}80;"
  ></span>
  <span>{label || c.label}</span>
</div>
