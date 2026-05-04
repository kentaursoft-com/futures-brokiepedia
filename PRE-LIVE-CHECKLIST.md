# Pre-Live Checklist for futures.brokiepedia.com

## 🔴 CRITICAL - Must Fix Before Live

### 1. Security
- [ ] **SSH Key Authentication** — Add your SSH key, disable password auth
- [ ] **Firewall** — UFW/iptables configured (only ports 22, 80, 443, 8080, 9000 open)
- [ ] **Secrets Management** — All API keys in `.env` (never committed)
- [ ] **Cloudflare Secrets** — Worker secrets set via `wrangler secret put`
- [ ] **HTTPS Only** — Cloudflare SSL/TLS set to "Full (strict)"
- [ ] **Kill-Switch Tested** — Verify it halts trading immediately

### 2. Exchange Configuration
- [ ] **Binance Testnet First** — Test with paper trading for 1-2 weeks
- [ ] **API Key Permissions** — Only "Futures" + "Read" permissions (no withdraw!)
- [ ] **IP Whitelist** — Restrict Binance API to your VPS IP
- [ ] **Test Order Flow** — Place/cancel small test orders

### 3. Risk Limits
- [ ] **Max Position Size** — Start with 1-2% risk per trade
- [ ] **Daily Loss Limit** — Max 3 losing trades or 3% daily drawdown
- [ ] **Hard Stop** — 6% portfolio drawdown = automatic halt
- [ ] **Leverage** — Start with 1-2x, max 5x (configured)

### 4. Monitoring
- [ ] **Telegram Alerts** — Verified working (bot token + chat ID)
- [ ] **Health Checks** — All services green (`./scripts/health-check.sh`)
- [ ] **Log Rotation** — Docker logs don't fill disk (`logrotate` or max-size)
- [ ] **Disk Space** — Monitor with 80% alert threshold

## 🟡 IMPORTANT - Should Fix Before Live

### 5. Database
- [ ] **Turso Connected** — Verify writes are persisting
- [ ] **QuestDB Backups** — Automated backup strategy
- [ ] **Database Indexes** — Verify query performance

### 6. Error Handling
- [ ] **Exchange Downtime** — Graceful handling of API failures
- [ ] **Network Issues** — Reconnection logic working
- [ ] **Rate Limiting** — Not hitting exchange limits

### 7. Testing
- [ ] **Integration Tests** — `./scripts/test-integration.sh` passes
- [ ] **Paper Trading** — Run for minimum 1 week with profit
- [ ] **Kill-Switch** — Test emergency stop 3+ times
- [ ] **Position Sizing** — Verify Kelly calculation accuracy

## 🟢 NICE TO HAVE - Can Add Later

### 8. UX Improvements
- [ ] Loading states for all async operations
- [ ] Better error messages (not just "API error")
- [ ] Mobile responsiveness polish
- [ ] Dark/light mode toggle

### 9. Analytics
- [ ] Grafana dashboard for VPS metrics
- [ ] Custom alerts (Slack, Discord, Email)
- [ ] Trade performance attribution

### 10. Documentation
- [ ] Runbook for common issues
- [ ] Recovery procedures
- [ ] On-call rotation (if team)

---

## 🚨 Live Trading Activation Steps

1. **Week 1-2: Paper Trading**
   ```bash
   TRADING_MODE=paper
   ```
   - Verify signals are generated
   - Check P&L tracking accuracy
   - Test all alerts

2. **Week 3: Small Live Test**
   ```bash
   TRADING_MODE=live
   # But with tiny sizes: MAX_RISK_PER_TRADE_PCT=0.5
   ```
   - $10-50 per trade maximum
   - Verify order execution
   - Confirm fees are calculated

3. **Week 4+: Scale Up**
   - Increase to 1% risk per trade
   - Add second symbol (ETH)
   - Monitor Sharpe ratio > 1.0

---

## ⚠️ Red Flags - STOP if you see these

- Drawdown exceeds 6% in a single day
- More than 5 consecutive losing trades
- Sharpe ratio drops below 0.5
- API errors > 10% of requests
- Position sizes exceed calculated risk

**When in doubt, switch to paper mode!**
