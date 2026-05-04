# LineIcons Migration Guide

## Why LineIcons?

- **Consistent** — Same style across all platforms
- **Professional** — Clean, modern SVG icons
- **Lightweight** — Tree-shakeable, only load what you use
- **Customizable** — Easy to change size, color, stroke width
- **No Licensing Issues** — Free for commercial use

## Installation

### Option 1: LineIcons Svelte (Recommended)

```bash
npm install @lineicons/svelte
```

### Option 2: LineIcons Web Font

```bash
npm install lineicons
```

Add to `src/app.css`:
```css
@import 'lineicons/dist/lineicons.css';
```

## Emoji → LineIcon Mapping

| Emoji | Current Usage | LineIcon Replacement | Icon Name |
|-------|---------------|---------------------|-----------|
| 💰 | Price alerts | `lni-dollar` | lni-dollar |
| 📊 | RSI alerts, Chart tab | `lni-bar-chart` | lni-bar-chart |
| ⚠️ | Warnings, alerts | `lni-warning` | lni-warning |
| 🔔 | General alerts | `lni-alarm` | lni-alarm |
| 🟢 | Buy button | `lni-arrow-up` | lni-arrow-up (green) |
| 🔴 | Sell button | `lni-arrow-down` | lni-arrow-down (red) |
| ✅ | Success states | `lni-checkmark` | lni-checkmark |
| ❌ | Error states | `lni-cross-circle` | lni-cross-circle |
| 🚀 | Startup message | `lni-rocket` | lni-rocket |
| 📈 | Social feed avatar | `lni-graph` | lni-graph |
| ❤️ | Like button | `lni-heart-fill` | lni-heart-fill |
| 🤍 | Unlike button | `lni-heart` | lni-heart |
| 📝 | Register passkey | `lni-pencil` | lni-pencil |
| 🔒 | Kill switch | `lni-lock` | lni-lock |
| 🔓 | Unlock | `lni-unlock` | lni-unlock |
| 📢 | Announcements | `lni-bullhorn` | lni-bullhorn |
| 🎉 | Celebrations | `lni-party` | lni-party |
| 💀 | Errors (humor) | `lni-bug` | lni-bug |
| 🤔 | Thinking | `lni-question-circle` | lni-question-circle |
| 💡 | Ideas | `lni-bulb` | lni-bulb |
| 👍 | Approval | `lni-thumbs-up` | lni-thumbs-up |
| 🙌 | Celebration | `lni-graduation` | lni-graduation |
| 😂 | Funny | `lni-emoji-smile` | lni-emoji-smile |

## Implementation Examples

### Svelte Component Usage

```svelte
<!-- Before (Emoji) -->
<button>🟢 Buy BTC</button>

<!-- After (LineIcon) -->
<script>
  import { LniArrowUp } from '@lineicons/svelte';
</script>

<button class="buy-btn">
  <LniArrowUp class="icon-green" />
  Buy BTC
</button>

<style>
  .icon-green {
    color: var(--color-long);
    width: 1.25rem;
    height: 1.25rem;
  }
</style>
```

### Alert Types

```svelte
<!-- Before -->
<span>{type === 'price' ? '💰' : type === 'rsi' ? '📊' : '⚠️'}</span>

<!-- After -->
<script>
  import { LniDollar, LniBarChart, LniWarning } from '@lineicons/svelte';
  
  const alertIcons = {
    price: LniDollar,
    rsi: LniBarChart,
    drawdown: LniWarning,
    default: LniAlarm
  };
</script>

<svelte:component this={alertIcons[type] || alertIcons.default} class="alert-icon" />
```

### Status Indicators

```svelte
<!-- Before -->
<span class="status-dot">🟢</span> Live

<!-- After -->
<script>
  import { LniCheckmarkCircle } from '@lineicons/svelte';
</script>

<span class="status-badge">
  <LniCheckmarkCircle class="status-icon online" />
  Live
</span>

<style>
  .status-icon {
    width: 0.75rem;
    height: 0.75rem;
  }
  .status-icon.online {
    color: var(--color-success);
  }
  .status-icon.offline {
    color: var(--color-danger);
  }
</style>
```

## Complete Migration Plan

### Step 1: Install LineIcons
```bash
npm install @lineicons/svelte
```

### Step 2: Create Icon Components
Create `src/lib/components/icons/`:

```svelte
<!-- src/lib/components/icons/StatusIcon.svelte -->
<script lang="ts">
  import { LniCheckmarkCircle, LniCrossCircle, LniWarning } from '@lineicons/svelte';
  
  export let status: 'success' | 'error' | 'warning' = 'success';
  export let size: string = '1rem';
  
  const icons = {
    success: LniCheckmarkCircle,
    error: LniCrossCircle,
    warning: LniWarning
  };
  
  const colors = {
    success: 'text-emerald-500',
    error: 'text-red-500',
    warning: 'text-amber-500'
  };
</script>

<svelte:component 
  this={icons[status]} 
  class="{colors[status]} inline-block"
  style="width: {size}; height: {size};"
/>
```

### Step 3: Replace All Emojis

Run this script to find all emojis:
```bash
#!/bin/bash
echo "Finding all emojis in source files..."
grep -r -n "[🔴🟢🟡✅❌⚠️🚀📊📝🎯💰📈📉🔒🔓📢🎉💀🤔💡👍❤️🙌😂💀🤍]" src/ --include="*.svelte"
```

### Step 4: Update Components

1. **AlertPanel.svelte** — Replace alert type icons
2. **OrderForm.svelte** — Replace buy/sell buttons
3. **SocialFeed.svelte** — Replace like/avatar icons
4. **+page.svelte** — Replace tab icons, status icons
5. **auth/+page.svelte** — Replace form icons
6. **PortfolioAnalytics.svelte** — Replace warning icon

### Step 5: Global Styles

Add to `src/app.css`:
```css
/* Icon Utilities */
.icon {
  display: inline-block;
  vertical-align: middle;
  width: 1.25rem;
  height: 1.25rem;
}

.icon-sm {
  width: 0.875rem;
  height: 0.875rem;
}

.icon-lg {
  width: 1.5rem;
  height: 1.5rem;
}

.icon-green { color: var(--color-long); }
.icon-red { color: var(--color-short); }
.icon-amber { color: var(--color-warning); }
.icon-blue { color: var(--color-info); }
```

## Testing Checklist

- [ ] All emojis replaced with LineIcons
- [ ] Icons render correctly on Chrome, Firefox, Safari
- [ ] Icons are visible in both light and dark modes
- [ ] No console errors about missing icons
- [ ] Mobile: Icons are touch-friendly (min 44px)
- [ ] Accessibility: Icons have aria-labels where needed

## Benefits After Migration

1. **Professional Look** — No more platform-specific emoji variations
2. **Better Performance** — SVG icons vs emoji font loading
3. **Consistent Sizing** — All icons follow same scale
4. **Easy Theming** — Change color with CSS
5. **Accessibility** — Proper ARIA support
