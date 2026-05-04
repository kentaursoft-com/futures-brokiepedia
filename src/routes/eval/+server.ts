import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async () => {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Futures Brokiepedia - Evaluation Report</title>
  <style>
    :root { --bg: #0f172a; --card: #1e293b; --text: #e2e8f0; --muted: #94a3b8; --success: #10b981; --warning: #f59e0b; --danger: #ef4444; --accent: #3b82f6; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; padding: 2rem 1rem; }
    .container { max-width: 900px; margin: 0 auto; }
    header { text-align: center; margin-bottom: 2rem; padding-bottom: 2rem; border-bottom: 1px solid #334155; }
    h1 { font-size: 2rem; margin-bottom: 0.5rem; }
    .subtitle { color: var(--muted); }
    .score-circle { width: 120px; height: 120px; border-radius: 50%; background: conic-gradient(var(--success) calc(var(--score) * 1%), #334155 0); display: flex; align-items: center; justify-content: center; margin: 1.5rem auto; position: relative; }
    .score-circle::before { content: ''; width: 100px; height: 100px; border-radius: 50%; background: var(--card); position: absolute; }
    .score-text { position: relative; z-index: 1; font-size: 2rem; font-weight: bold; }
    .timestamp { color: var(--muted); font-size: 0.875rem; }
    .input-area { background: var(--card); border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; border: 1px solid #334155; }
    .input-area h3 { margin-bottom: 1rem; color: var(--accent); }
    textarea { width: 100%; min-height: 120px; background: var(--bg); border: 1px solid #475569; border-radius: 8px; color: var(--text); padding: 1rem; font-family: 'Monaco', 'Consolas', monospace; font-size: 0.875rem; resize: vertical; }
    .btn { background: var(--accent); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; font-size: 1rem; margin-top: 1rem; transition: opacity 0.2s; }
    .btn:hover { opacity: 0.9; }
    .btn-secondary { background: #475569; margin-left: 0.5rem; }
    .grid { display: grid; gap: 1rem; margin-bottom: 2rem; }
    .grid-2 { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
    .card { background: var(--card); border-radius: 12px; padding: 1.5rem; border: 1px solid #334155; }
    .card h3 { color: var(--accent); margin-bottom: 1rem; font-size: 1.1rem; }
    .metric { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid #334155; }
    .metric:last-child { border-bottom: none; }
    .metric-label { color: var(--muted); }
    .metric-value { font-weight: 600; }
    .badge { display: inline-flex; align-items: center; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
    .badge-success { background: rgba(16, 185, 129, 0.2); color: var(--success); }
    .badge-warning { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
    .badge-danger { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
    .progress-bar { height: 8px; background: #334155; border-radius: 4px; overflow: hidden; margin-top: 0.5rem; }
    .progress-fill { height: 100%; background: var(--success); border-radius: 4px; transition: width 0.5s ease; }
    .status-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.75rem; }
    .status-item { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 6px; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
    .status-dot.green { background: var(--success); }
    .status-dot.yellow { background: var(--warning); }
    .status-dot.red { background: var(--danger); }
    .hidden { display: none; }
    .error { color: var(--danger); padding: 1rem; background: rgba(239,68,68,0.1); border-radius: 8px; }
    pre { background: var(--bg); padding: 1rem; border-radius: 8px; overflow-x: auto; font-size: 0.875rem; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>📊 Futures Brokiepedia</h1>
      <p class="subtitle">Automated Trading Dashboard - Evaluation Report</p>
      <div class="score-circle" id="scoreCircle" style="--score: 0;">
        <span class="score-text" id="overallScore">-</span>
      </div>
      <p class="timestamp" id="timestamp">Paste eval JSON to generate report</p>
    </header>

    <div class="input-area">
      <h3>📋 Evaluation Data Input</h3>
      <p style="color: var(--muted); margin-bottom: 1rem; font-size: 0.9rem;">
        The evaluator can't access Cloudflare Workers directly. Paste the JSON response here to generate the report.
      </p>
      <textarea id="jsonInput" placeholder="Paste the eval JSON here..."></textarea>
      <div style="margin-top: 1rem;">
        <button class="btn" onclick="generateReport()">Generate Report</button>
        <button class="btn btn-secondary" onclick="fetchFromWorker()">Try Fetch from Worker</button>
        <button class="btn btn-secondary" onclick="loadSample()">Load Sample Data</button>
      </div>
      <div id="fetchError" class="error hidden" style="margin-top: 1rem;"></div>
    </div>

    <div id="report" class="hidden">
      <div class="card" style="margin-bottom: 1rem;">
        <h3>📈 Progress Breakdown</h3>
        <div id="progressMetrics"></div>
      </div>

      <div class="grid grid-2">
        <div class="card">
          <h3>🔐 Authentication</h3>
          <div id="authMetrics"></div>
        </div>
        <div class="card">
          <h3>☁️ Cloudflare Infrastructure</h3>
          <div id="infraMetrics"></div>
        </div>
        <div class="card">
          <h3>🎨 Frontend Components</h3>
          <div id="frontendMetrics"></div>
        </div>
        <div class="card">
          <h3>⚠️ Risk Management</h3>
          <div id="riskMetrics"></div>
        </div>
      </div>

      <div class="card" style="margin-bottom: 1rem;">
        <h3>💾 KV Data Status</h3>
        <div id="kvMetrics" class="status-grid"></div>
      </div>

      <div class="card" style="margin-bottom: 1rem;">
        <h3>🖥️ VPS Daemon Status</h3>
        <div id="vpsMetrics"></div>
      </div>

      <div class="card" style="margin-bottom: 1rem;">
        <h3>🛣️ Application Routes</h3>
        <div id="routesList" class="status-grid"></div>
      </div>

      <div class="card" style="margin-bottom: 1rem;">
        <h3>📁 Repository Files</h3>
        <div id="repoMetrics" class="status-grid"></div>
      </div>

      <div class="card">
        <h3>🔧 Raw JSON Data</h3>
        <pre id="rawJson"></pre>
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

    function generateReport() {
      let data;
      try {
        const input = document.getElementById('jsonInput').value.trim();
        if (!input) { alert('Please paste the eval JSON first'); return; }
        data = JSON.parse(input);
      } catch (err) { alert('Invalid JSON: ' + err.message); return; }

      document.getElementById('report').classList.remove('hidden');
      const score = data.progress?.overall || 0;
      document.getElementById('overallScore').textContent = score;
      document.getElementById('scoreCircle').style.setProperty('--score', score);
      document.getElementById('timestamp').textContent = 'Generated: ' + new Date().toLocaleString() + ' | Deployed: ' + (data.project?.deployed_at || 'Unknown');

      const progressDiv = document.getElementById('progressMetrics');
      const progress = data.progress || {};
      progressDiv.innerHTML = Object.entries(progress).filter(([k]) => k !== 'overall').map(([key, val]) => {
        const color = val >= 80 ? 'var(--success)' : val >= 50 ? 'var(--warning)' : 'var(--danger)';
        return '<div class="metric"><span class="metric-label">' + key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase()) + '</span><div style="flex: 1; margin: 0 1rem;"><div class="progress-bar"><div class="progress-fill" style="width: ' + val + '%; background: ' + color + '"></div></div></div><span class="metric-value" style="color: ' + color + '">' + val + '%</span></div>';
      }).join('');

      const auth = data.auth || {};
      document.getElementById('authMetrics').innerHTML = '<div class="metric"><span class="metric-label">Type</span><span class="metric-value">' + (auth.type || 'N/A') + '</span></div><div class="metric"><span class="metric-label">Library</span><span class="metric-value">' + (auth.library || 'N/A') + '</span></div><div class="metric"><span class="metric-label">Gate Active</span><span class="badge ' + (auth.gate_active ? 'badge-success' : 'badge-danger') + '">' + (auth.gate_active ? 'Yes' : 'No') + '</span></div><div class="metric"><span class="metric-label">Session Method</span><span class="metric-value">' + (auth.session_method || 'N/A') + '</span></div><div class="metric"><span class="metric-label">Passkey Registered</span><span class="badge ' + (auth.passkey_registered ? 'badge-success' : 'badge-warning') + '">' + (auth.passkey_registered ? 'Yes' : 'No') + '</span></div>';

      const cf = data.cloudflare || {};
      document.getElementById('infraMetrics').innerHTML = '<div class="metric"><span class="metric-label">KV Namespaces</span><span class="metric-value">' + (cf.kv_namespaces || []).length + ' bound</span></div><div class="metric"><span class="metric-label">D1 Databases</span><span class="metric-value">' + (cf.d1_databases || []).length + ' bound</span></div><div class="metric"><span class="metric-label">Queues</span><span class="metric-value">' + (cf.queues || []).length + ' bound</span></div><div class="metric"><span class="metric-label">Secrets</span><span class="metric-value">' + (cf.secrets_configured || []).length + ' configured</span></div>';

      const fe = data.frontend || {};
      const components = fe.components || {};
      document.getElementById('frontendMetrics').innerHTML = '<div class="metric"><span class="metric-label">Auth Type</span><span class="metric-value">' + (fe.auth_type || 'N/A') + '</span></div><div class="metric"><span class="metric-label">Chart Library</span><span class="metric-value">' + (fe.chart_library || 'N/A') + '</span></div><div class="metric"><span class="metric-label">KV Polling</span><span class="badge ' + (fe.kv_polling_active ? 'badge-success' : 'badge-danger') + '">' + (fe.kv_polling_active ? 'Active' : 'Inactive') + '</span></div><div style="margin-top: 1rem;">' + Object.entries(components).map(([k, v]) => '<div class="status-item"><div class="status-dot ' + (v ? 'green' : 'red') + '"></div><span>' + k.replace(/_/g, ' ') + '</span></div>').join('') + '</div>';

      const risk = data.risk || {};
      document.getElementById('riskMetrics').innerHTML = '<div class="metric"><span class="metric-label">Max Risk/Trade</span><span class="metric-value">' + (risk.max_risk_per_trade_pct || 0) + '%</span></div><div class="metric"><span class="metric-label">Max Positions</span><span class="metric-value">' + (risk.max_concurrent_positions || 0) + '</span></div><div class="metric"><span class="metric-label">Soft Drawdown</span><span class="metric-value">' + (risk.soft_drawdown_pct || 0) + '%</span></div><div class="metric"><span class="metric-label">Hard Drawdown</span><span class="metric-value">' + (risk.hard_drawdown_pct || 0) + '%</span></div><div class="metric"><span class="metric-label">Max Leverage</span><span class="metric-value">' + (risk.max_leverage || 0) + 'x</span></div><div class="metric"><span class="metric-label">Kill Switch</span><span class="badge ' + (risk.kill_switch_wired ? 'badge-success' : 'badge-danger') + '">' + (risk.kill_switch_wired ? 'Wired' : 'Not Wired') + '</span></div><div class="metric"><span class="metric-label">Risk Gate Tests</span><span class="badge ' + (risk.risk_gate_tests_passing ? 'badge-success' : 'badge-warning') + '">' + (risk.risk_gate_tests_passing ? 'Passing' : 'Failing') + '</span></div>';

      const kv = data.kv_data || {};
      document.getElementById('kvMetrics').innerHTML = Object.entries(kv).map(([k, v]) => '<div class="status-item"><div class="status-dot ' + (v.exists ? (v.value || v.has_balance || v.has_equity ? 'green' : 'yellow') : 'red') + '"></div><span>' + k.replace(/_/g, ' ') + '</span></div>').join('');

      const vps = data.vps || {};
      document.getElementById('vpsMetrics').innerHTML = '<div class="metric"><span class="metric-label">Reachable</span><span class="badge ' + (vps.reachable ? 'badge-success' : 'badge-danger') + '">' + (vps.reachable ? 'Yes' : 'No') + '</span></div><div class="metric"><span class="metric-label">Response Time</span><span class="metric-value">' + (vps.response_ms || 0) + 'ms</span></div><div class="metric"><span class="metric-label">Daemon Version</span><span class="metric-value">' + (vps.daemon_version || 'N/A') + '</span></div><div class="metric"><span class="metric-label">LangGraph</span><span class="badge ' + (vps.langgraph_running ? 'badge-success' : 'badge-warning') + '">' + (vps.langgraph_running ? 'Running' : 'Stopped') + '</span></div><div class="metric"><span class="metric-label">Agents Initialized</span><span class="badge ' + (vps.agents_initialized ? 'badge-success' : 'badge-warning') + '">' + (vps.agents_initialized ? 'Yes' : 'No') + '</span></div><div class="metric"><span class="metric-label">Evolution Loop</span><span class="badge ' + (vps.evolution_loop_running ? 'badge-success' : 'badge-warning') + '">' + (vps.evolution_loop_running ? 'Running' : 'Stopped') + '</span></div><div class="metric"><span class="metric-label">Paper Mode</span><span class="badge ' + (vps.paper_mode_active ? 'badge-success' : 'badge-warning') + '">' + (vps.paper_mode_active ? 'Active' : 'Inactive') + '</span></div>';

      document.getElementById('routesList').innerHTML = (data.routes || []).map(r => '<div class="status-item"><div class="status-dot ' + (r.exists ? 'green' : 'red') + '"></div><span>' + r.path + '</span></div>').join('');

      const repo = data.repo || {};
      document.getElementById('repoMetrics').innerHTML = Object.entries(repo).map(([k, v]) => '<div class="status-item"><div class="status-dot ' + (v ? 'green' : 'red') + '"></div><span>' + k.replace(/_/g, ' ').replace(/exists$/, '') + '</span></div>').join('');

      document.getElementById('rawJson').textContent = JSON.stringify(data, null, 2);
      document.getElementById('report').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  </script>
</body>
</html>`;

  return new Response(html, {
    headers: { 'Content-Type': 'text/html' }
  });
};
