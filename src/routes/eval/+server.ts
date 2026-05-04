import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async () => {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Futures Brokiepedia - Evaluation Report</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            navy: { DEFAULT: '#0F172A', light: '#1E293B', lighter: '#334155' },
            emerald: { DEFAULT: '#10B981', glow: 'rgba(16, 185, 129, 0.4)' },
            rose: { DEFAULT: '#F43F5E', glow: 'rgba(244, 63, 94, 0.4)' },
            amber: { DEFAULT: '#F59E0B', glow: 'rgba(245, 158, 11, 0.4)' },
          },
          fontFamily: {
            sans: ['Inter', 'system-ui', 'sans-serif'],
            mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
          },
          animation: {
            'glow-emerald': 'glow-emerald 2s ease-in-out infinite alternate',
            'glow-rose': 'glow-rose 2s ease-in-out infinite alternate',
            'glow-amber': 'glow-amber 2s ease-in-out infinite alternate',
            'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
          },
          keyframes: {
            'glow-emerald': {
              '0%': { boxShadow: '0 0 2px #10B981' },
              '100%': { boxShadow: '0 0 8px #10B981, 0 0 16px rgba(16, 185, 129, 0.3)' },
            },
            'glow-rose': {
              '0%': { boxShadow: '0 0 2px #F43F5E' },
              '100%': { boxShadow: '0 0 8px #F43F5E, 0 0 16px rgba(244, 63, 94, 0.3)' },
            },
            'glow-amber': {
              '0%': { boxShadow: '0 0 2px #F59E0B' },
              '100%': { boxShadow: '0 0 8px #F59E0B, 0 0 16px rgba(245, 158, 11, 0.3)' },
            },
            'pulse-glow': {
              '0%, 100%': { boxShadow: '0 0 5px rgba(244, 63, 94, 0.4), 0 0 10px rgba(244, 63, 94, 0.2)' },
              '50%': { boxShadow: '0 0 20px rgba(244, 63, 94, 0.6), 0 0 40px rgba(244, 63, 94, 0.3)' },
            },
          },
        },
      },
    };
  </script>
  <style>
    body { font-family: 'Inter', system-ui, sans-serif; background: #0F172A; color: #e2e8f0; }
    .font-mono { font-family: 'JetBrains Mono', 'Fira Code', monospace; }
    .glass-card {
      background: rgba(255, 255, 255, 0.03);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      transition: all 0.3s ease;
    }
    .glass-card:hover {
      background: rgba(255, 255, 255, 0.05);
      border-color: rgba(255, 255, 255, 0.15);
    }
    .score-ring {
      width: 140px;
      height: 140px;
      border-radius: 50%;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .score-ring::before {
      content: '';
      position: absolute;
      inset: 4px;
      border-radius: 50%;
      background: #0F172A;
    }
    .score-text {
      position: relative;
      z-index: 1;
      font-size: 2.5rem;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
    }
    .progress-track {
      height: 6px;
      background: rgba(255,255,255,0.06);
      border-radius: 3px;
      overflow: hidden;
    }
    .progress-fill {
      height: 100%;
      border-radius: 3px;
      transition: width 0.7s ease;
      position: relative;
    }
    .progress-fill::after {
      content: '';
      position: absolute;
      inset: 0;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
      animation: shimmer 2s infinite;
    }
    @keyframes shimmer {
      0% { transform: translateX(-100%); }
      100% { transform: translateX(100%); }
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }
    .status-dot.online {
      background: #10B981;
      box-shadow: 0 0 6px #10B981, 0 0 12px rgba(16,185,129,0.4);
      animation: glow-emerald 2s ease-in-out infinite alternate;
    }
    .status-dot.warning {
      background: #F59E0B;
      box-shadow: 0 0 6px #F59E0B, 0 0 12px rgba(245,158,11,0.4);
      animation: glow-amber 2s ease-in-out infinite alternate;
    }
    .status-dot.error {
      background: #F43F5E;
      box-shadow: 0 0 6px #F43F5E, 0 0 12px rgba(244,63,94,0.4);
      animation: glow-rose 2s ease-in-out infinite alternate;
    }
    .status-dot.offline {
      background: #64748B;
    }
    .risk-card-pulse {
      animation: pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
      border-color: rgba(244, 63, 94, 0.6) !important;
    }
    .metric-value {
      font-family: 'JetBrains Mono', monospace;
    }
    textarea:focus {
      outline: none;
      border-color: rgba(59, 130, 246, 0.5);
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    .scrollbar-hide::-webkit-scrollbar { display: none; }
    .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
  </style>
</head>
<body class="min-h-screen">
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- Header -->
    <header class="text-center mb-10">
      <h1 class="text-3xl sm:text-4xl font-bold text-white/90 mb-2">📊 Futures Brokiepedia</h1>
      <p class="text-white/40 text-sm sm:text-base">Automated Trading Dashboard - Evaluation Report</p>
      
      <!-- Score Circle -->
      <div class="mt-8 flex justify-center">
        <div class="score-ring" id="scoreRing" style="background: conic-gradient(#10B981 calc(0 * 1%), rgba(255,255,255,0.1) 0);">
          <span class="score-text text-emerald-400" id="overallScore">-</span>
        </div>
      </div>
      <p class="text-white/40 text-sm mt-4 font-mono" id="timestamp">Paste eval JSON to generate report</p>
    </header>

    <!-- Input Area -->
    <div class="glass-card p-5 sm:p-6 mb-8">
      <h3 class="text-blue-400 font-semibold mb-3 flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
        Evaluation Data Input
      </h3>
      <p class="text-white/40 text-sm mb-4">
        Cloudflare Workers are restricted for some AI evaluators. Paste the JSON response below to generate a visual report.
      </p>
      <textarea id="jsonInput" class="w-full min-h-[120px] bg-navy/50 border border-white/10 rounded-xl p-4 text-sm font-mono text-white/80 resize-y" placeholder="Paste the eval JSON here..."></textarea>
      <div class="flex flex-wrap gap-2 mt-4">
        <button class="bg-blue-500 hover:bg-blue-400 text-white px-5 py-2.5 rounded-xl font-medium transition-colors flex items-center gap-2" onclick="generateReport()">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
          Generate Report
        </button>
        <button class="bg-white/5 hover:bg-white/10 text-white/70 px-5 py-2.5 rounded-xl font-medium transition-colors border border-white/10" onclick="fetchFromWorker()">
          Try Fetch from Worker
        </button>
        <button class="bg-white/5 hover:bg-white/10 text-white/70 px-5 py-2.5 rounded-xl font-medium transition-colors border border-white/10" onclick="loadSample()">
          Load Sample Data
        </button>
      </div>
      <div id="fetchError" class="hidden mt-4 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-sm"></div>
    </div>

    <!-- Report Content -->
    <div id="report" class="hidden space-y-6">
      <!-- Overall Progress -->
      <div class="glass-card p-5 sm:p-6">
        <h3 class="text-blue-400 font-semibold mb-5 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
          Progress Breakdown
        </h3>
        <div id="progressMetrics" class="space-y-4"></div>
      </div>

      <!-- Two Column Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Risk Management - Prominent Card -->
        <div id="riskCard" class="glass-card p-5 sm:p-6 lg:col-span-2">
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-rose-400 font-semibold flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
              Risk Management
            </h3>
            <div id="riskStatusBadge"></div>
          </div>
          <div id="riskMetrics" class="grid grid-cols-2 sm:grid-cols-3 gap-4"></div>
        </div>

        <!-- Auth -->
        <div class="glass-card p-5 sm:p-6">
          <h3 class="text-blue-400 font-semibold mb-4 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
            Authentication
          </h3>
          <div id="authMetrics" class="space-y-3"></div>
        </div>

        <!-- Cloudflare Infra -->
        <div class="glass-card p-5 sm:p-6">
          <h3 class="text-blue-400 font-semibold mb-4 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"></path></svg>
            Cloudflare Infrastructure
          </h3>
          <div id="infraMetrics" class="space-y-3"></div>
        </div>

        <!-- Frontend -->
        <div class="glass-card p-5 sm:p-6">
          <h3 class="text-blue-400 font-semibold mb-4 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"></path></svg>
            Frontend Components
          </h3>
          <div id="frontendMetrics"></div>
        </div>

        <!-- VPS -->
        <div class="glass-card p-5 sm:p-6">
          <h3 class="text-blue-400 font-semibold mb-4 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"></path></svg>
            VPS Daemon Status
          </h3>
          <div id="vpsMetrics" class="space-y-3"></div>
        </div>
      </div>

      <!-- KV Data -->
      <div class="glass-card p-5 sm:p-6">
        <h3 class="text-blue-400 font-semibold mb-4 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>
          KV Data Status
        </h3>
        <div id="kvMetrics" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3"></div>
      </div>

      <!-- Routes -->
      <div class="glass-card p-5 sm:p-6">
        <h3 class="text-blue-400 font-semibold mb-4 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 7m0 13V7"></path></svg>
          Application Routes
        </h3>
        <div id="routesList" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3"></div>
      </div>

      <!-- Repo -->
      <div class="glass-card p-5 sm:p-6">
        <h3 class="text-blue-400 font-semibold mb-4 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
          Repository Files
        </h3>
        <div id="repoMetrics" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3"></div>
      </div>

      <!-- Raw JSON -->
      <div class="glass-card p-5 sm:p-6">
        <h3 class="text-blue-400 font-semibold mb-4 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
          Raw JSON Data
        </h3>
        <pre id="rawJson" class="bg-navy/50 border border-white/10 rounded-xl p-4 text-xs font-mono text-white/60 overflow-x-auto"></pre>
      </div>
    </div>
  </div>

  <script>
    const SAMPLE_DATA = {"project":{"name":"Futures Brokiepedia","version":"1.0.0","deployed_at":"2026-05-04T09:50:37.942Z","environment":"production"},"routes":[{"path":"/","file":"src/routes/(app)/+page.svelte","exists":true},{"path":"/auth","file":"src/routes/auth/+page.svelte","exists":true},{"path":"/trade","file":"src/routes/(app)/trade/+page.svelte","exists":true},{"path":"/positions","file":"src/routes/(app)/positions/+page.svelte","exists":true},{"path":"/signals","file":"src/routes/(app)/signals/+page.svelte","exists":true},{"path":"/analytics","file":"src/routes/(app)/analytics/+page.svelte","exists":true},{"path":"/settings","file":"src/routes/(app)/settings/+page.svelte","exists":true}],"auth":{"type":"username_password","library":"custom","gate_active":true,"session_method":"cookie","passkey_registered":false},"cloudflare":{"kv_namespaces":[{"name":"LIVE_STATE","bound":true},{"name":"AGENT_SIGNALS","bound":true}],"d1_databases":[{"name":"BROKIEPEDIA_DB","bound":true}],"queues":[{"name":"AGENT_TASKS","bound":true}],"secrets_configured":["DEEPSEEK_API_KEY","TELEGRAM_BOT_TOKEN","BINANCE_API_KEY","BINANCE_SECRET_KEY","TURSO_DB_URL","TURSO_DB_TOKEN","EVAL_API_KEY"]},"kv_data":{"portfolio_state":{"exists":true,"last_updated":"2026-05-04T09:50:37.389Z","has_balance":false,"has_equity":false},"daily_pnl":{"exists":true,"last_updated":"2026-05-04T09:50:37.389Z","value_is_zero":false},"open_positions":{"exists":true,"count":0,"is_stub_data":true},"agent_signals":{"exists":true,"departments_reporting":0,"last_updated":"2026-05-04T09:50:37.389Z"},"active_strategy_metrics":{"exists":true,"strategy_name":null,"win_rate":0,"last_updated":"2026-05-04T09:50:37.389Z"},"binance_ws_alive":{"exists":true,"value":true,"last_updated":"2026-05-04T09:50:37.389Z"},"questdb_alive":{"exists":true,"value":false},"chromadb_alive":{"exists":true,"value":false},"execution_enabled":{"exists":true,"value":false}},"turso":{"connected":false,"tables":{}},"vps":{"reachable":false,"response_ms":1,"daemon_version":null,"langgraph_running":false,"agents_initialized":false,"evolution_loop_running":false,"paper_mode_active":false,"market_data_feed":{"binance_ws_connected":false,"last_candle_ts":null,"symbols_tracked":[]},"services":{"questdb":false,"chromadb":false,"langsmith_tracing":false},"strategy_research_md":{"exists":false,"last_modified":null,"active_strategy_name":null}},"frontend":{"auth_type":"password","chart_library":"TradingView","kv_polling_active":true,"polling_interval_ms":5000,"components":{"trading_chart":true,"agent_department_panel":true,"strategy_evolution_panel":true,"kill_switch_button":true,"health_status_bar":true,"health_checks_are_real":true,"positions_table":true,"positions_use_real_data":true,"recent_activity_real":true,"drawdown_bar_with_limits":true,"leverage_warning_badge":true}},"repo":{"env_example_exists":true,"docker_compose_exists":true,"systemd_service_exists":true,"install_script_exists":true,"risk_gate_tests_exist":true,"strategy_research_md_in_repo":true},"risk":{"max_risk_per_trade_pct":2,"max_concurrent_positions":4,"soft_drawdown_pct":3,"hard_drawdown_pct":6,"max_leverage":5,"kill_switch_wired":true,"risk_gate_tests_passing":false},"progress":{"auth_gate":80,"real_health_checks":100,"vps_connected":0,"real_kv_data":50,"trading_chart":100,"agent_panel":100,"strategy_panel":100,"kill_switch":100,"infra_files":100,"risk_gate_tested":100,"overall":83}};

    function loadSample() {
      document.getElementById('jsonInput').value = JSON.stringify(SAMPLE_DATA, null, 2);
      generateReport();
    }

    async function fetchFromWorker() {
      const errorDiv = document.getElementById('fetchError');
      errorDiv.classList.add('hidden');
      try {
        const res = await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/eval?key=brokiepedia-eval-2026-ken');
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        document.getElementById('jsonInput').value = JSON.stringify(data, null, 2);
        generateReport();
      } catch (err) {
        errorDiv.textContent = '❌ Could not fetch from worker: ' + err.message + '. Paste JSON manually.';
        errorDiv.classList.remove('hidden');
      }
    }

    function getStatusDot(status) {
      const colors = {
        online: 'online', warning: 'warning', error: 'error', offline: 'offline'
      };
      return '<span class="status-dot ' + (colors[status] || 'offline') + '"></span>';
    }

    function getBadge(text, type) {
      const colors = {
        success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20',
        warning: 'bg-amber-500/15 text-amber-400 border-amber-500/20',
        danger: 'bg-rose-500/15 text-rose-400 border-rose-500/20',
        info: 'bg-blue-500/15 text-blue-400 border-blue-500/20',
        neutral: 'bg-white/5 text-white/50 border-white/10'
      };
      return '<span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-mono font-semibold border ' + (colors[type] || colors.neutral) + '">' + text + '</span>';
    }

    function generateReport() {
      let data;
      try {
        const input = document.getElementById('jsonInput').value.trim();
        if (!input) { alert('Please paste the eval JSON first'); return; }
        data = JSON.parse(input);
      } catch (err) { alert('Invalid JSON: ' + err.message); return; }

      document.getElementById('report').classList.remove('hidden');
      
      const score = data.progress?.overall || 0;
      const scoreColor = score >= 80 ? '#10B981' : score >= 50 ? '#F59E0B' : '#F43F5E';
      document.getElementById('overallScore').textContent = score;
      document.getElementById('overallScore').style.color = scoreColor;
      document.getElementById('scoreRing').style.background = 'conic-gradient(' + scoreColor + ' ' + (score * 3.6) + 'deg, rgba(255,255,255,0.1) 0)';
      document.getElementById('timestamp').textContent = 'Generated: ' + new Date().toLocaleString() + ' | Environment: ' + (data.project?.environment || 'Unknown');

      // Progress
      const progressDiv = document.getElementById('progressMetrics');
      const progress = data.progress || {};
      progressDiv.innerHTML = Object.entries(progress).filter(([k]) => k !== 'overall').map(([key, val]) => {
        const color = val >= 80 ? '#10B981' : val >= 50 ? '#F59E0B' : '#F43F5E';
        return '<div class="flex items-center gap-4"><span class="text-sm text-white/50 w-40 flex-shrink-0">' + key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase()) + '</span><div class="flex-1 progress-track"><div class="progress-fill" style="width: ' + val + '%; background: linear-gradient(90deg, ' + color + '88, ' + color + ');"></div></div><span class="text-sm font-mono font-semibold w-12 text-right" style="color: ' + color + '">' + val + '%</span></div>';
      }).join('');

      // Risk - Prominent
      const risk = data.risk || {};
      const riskBreach = !risk.risk_gate_tests_passing;
      const riskCard = document.getElementById('riskCard');
      if (riskBreach) {
        riskCard.classList.add('risk-card-pulse');
      } else {
        riskCard.classList.remove('risk-card-pulse');
      }
      
      document.getElementById('riskStatusBadge').innerHTML = getBadge(riskBreach ? 'THRESHOLD BREACH' : 'WITHIN LIMITS', riskBreach ? 'danger' : 'success');
      
      document.getElementById('riskMetrics').innerHTML = [
        { label: 'Max Risk/Trade', value: (risk.max_risk_per_trade_pct || 0) + '%', warn: risk.max_risk_per_trade_pct > 2 },
        { label: 'Max Positions', value: (risk.max_concurrent_positions || 0), warn: false },
        { label: 'Soft Drawdown', value: (risk.soft_drawdown_pct || 0) + '%', warn: false },
        { label: 'Hard Drawdown', value: (risk.hard_drawdown_pct || 0) + '%', warn: false },
        { label: 'Max Leverage', value: (risk.max_leverage || 0) + 'x', warn: risk.max_leverage > 5 },
        { label: 'Kill Switch', value: risk.kill_switch_wired ? 'WIRED' : 'NOT WIRED', warn: !risk.kill_switch_wired },
      ].map(item => '<div class="bg-white/[0.03] rounded-xl p-4 border border-white/[0.06]"><p class="text-xs text-white/40 mb-1">' + item.label + '</p><p class="text-lg font-mono font-bold ' + (item.warn ? 'text-rose-400' : 'text-white/90') + '">' + item.value + '</p></div>').join('');

      // Auth
      const auth = data.auth || {};
      document.getElementById('authMetrics').innerHTML = [
        ['Type', auth.type || 'N/A'], ['Library', auth.library || 'N/A'], ['Session', auth.session_method || 'N/A']
      ].map(([k, v]) => '<div class="flex items-center justify-between py-2 border-b border-white/[0.04] last:border-0"><span class="text-sm text-white/40">' + k + '</span><span class="text-sm font-mono text-white/80">' + v + '</span></div>').join('') + '<div class="flex gap-2 mt-3">' + getBadge(auth.gate_active ? 'GATE ACTIVE' : 'GATE INACTIVE', auth.gate_active ? 'success' : 'danger') + getBadge(auth.passkey_registered ? 'PASSKEY OK' : 'NO PASSKEY', auth.passkey_registered ? 'success' : 'warning') + '</div>';

      // Infra
      const cf = data.cloudflare || {};
      document.getElementById('infraMetrics').innerHTML = [
        ['KV Namespaces', (cf.kv_namespaces || []).length + ' bound'],
        ['D1 Databases', (cf.d1_databases || []).length + ' bound'],
        ['Queues', (cf.queues || []).length + ' bound'],
        ['Secrets', (cf.secrets_configured || []).length + ' configured']
      ].map(([k, v]) => '<div class="flex items-center justify-between py-2 border-b border-white/[0.04] last:border-0"><span class="text-sm text-white/40">' + k + '</span><span class="text-sm font-mono text-white/80">' + v + '</span></div>').join('');

      // Frontend
      const fe = data.frontend || {};
      const components = fe.components || {};
      document.getElementById('frontendMetrics').innerHTML = '<div class="space-y-3 mb-4"><div class="flex items-center justify-between"><span class="text-sm text-white/40">Chart Library</span><span class="text-sm font-mono text-white/80">' + (fe.chart_library || 'N/A') + '</span></div><div class="flex items-center justify-between"><span class="text-sm text-white/40">KV Polling</span>' + getBadge(fe.kv_polling_active ? 'ACTIVE' : 'INACTIVE', fe.kv_polling_active ? 'success' : 'danger') + '</div></div><div class="grid grid-cols-2 gap-2">' + Object.entries(components).map(([k, v]) => '<div class="flex items-center gap-2 p-2 rounded-lg ' + (v ? 'bg-emerald-500/10' : 'bg-white/[0.03]') + '">' + getStatusDot(v ? 'online' : 'offline') + '<span class="text-xs text-white/60">' + k.replace(/_/g, ' ') + '</span></div>').join('') + '</div>';

      // VPS
      const vps = data.vps || {};
      document.getElementById('vpsMetrics').innerHTML = [
        ['Reachable', vps.reachable ? 'YES' : 'NO', vps.reachable ? 'success' : 'danger'],
        ['Response', (vps.response_ms || 0) + 'ms', 'info'],
        ['LangGraph', vps.langgraph_running ? 'RUNNING' : 'STOPPED', vps.langgraph_running ? 'success' : 'warning'],
        ['Agents', vps.agents_initialized ? 'INIT' : 'NOT INIT', vps.agents_initialized ? 'success' : 'warning'],
        ['Evolution', vps.evolution_loop_running ? 'RUNNING' : 'STOPPED', vps.evolution_loop_running ? 'success' : 'warning'],
        ['Paper Mode', vps.paper_mode_active ? 'ACTIVE' : 'INACTIVE', vps.paper_mode_active ? 'success' : 'warning']
      ].map(([k, v, t]) => '<div class="flex items-center justify-between py-2 border-b border-white/[0.04] last:border-0"><span class="text-sm text-white/40">' + k + '</span>' + getBadge(v, t) + '</div>').join('');

      // KV
      const kv = data.kv_data || {};
      document.getElementById('kvMetrics').innerHTML = Object.entries(kv).map(([k, v]) => '<div class="flex items-center gap-2 p-3 rounded-xl ' + (v.exists ? (v.value || v.has_balance || v.has_equity ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-amber-500/10 border border-amber-500/20') : 'bg-white/[0.03] border border-white/[0.06]') + '">' + getStatusDot(v.exists ? (v.value || v.has_balance || v.has_equity ? 'online' : 'warning') : 'offline') + '<span class="text-xs text-white/60">' + k.replace(/_/g, ' ') + '</span></div>').join('');

      // Routes
      document.getElementById('routesList').innerHTML = (data.routes || []).map(r => '<div class="flex items-center gap-2 p-3 rounded-xl ' + (r.exists ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-rose-500/10 border border-rose-500/20') + '">' + getStatusDot(r.exists ? 'online' : 'error') + '<span class="text-xs font-mono text-white/70">' + r.path + '</span></div>').join('');

      // Repo
      const repo = data.repo || {};
      document.getElementById('repoMetrics').innerHTML = Object.entries(repo).map(([k, v]) => '<div class="flex items-center gap-2 p-3 rounded-xl ' + (v ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-white/[0.03] border border-white/[0.06]') + '">' + getStatusDot(v ? 'online' : 'offline') + '<span class="text-xs text-white/60">' + k.replace(/_/g, ' ').replace(/exists$/, '') + '</span></div>').join('');

      // Raw JSON
      document.getElementById('rawJson').textContent = JSON.stringify(data, null, 2);

      // Scroll
      document.getElementById('report').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  </script>
</body>
</html>`;

  return new Response(html, {
    headers: { 'Content-Type': 'text/html' }
  });
};
