# 🌐 Hedge Monitor Setup (No Moon Dev API Required)

**Complete guide to using the Hedge Monitor with FREE public data sources!**

Built with love by Moon Dev 🌙🚀

---

## ✅ What Works Without Moon Dev API

The Hedge Monitor system automatically adapts based on available API keys. Here's what you get with **FREE public APIs**:

### ✅ **Fully Functional** (No Premium APIs Needed)
- ✅ **Portfolio Monitoring** - Tracks your holdings via BirdEye API
- ✅ **Derivatives Monitoring** - Funding rates, OI, liquidations via Binance/Bybit
- ✅ **Options Monitoring** - Max pain analysis via Deribit (free public API)
- ✅ **Macro Monitoring** - M2, FED data via FRED API (free with key)
- ✅ **AI Hedge Decisions** - Full AI analysis and recommendations

### ⚠️ **Requires Moon Dev API** (Optional)
- ⚠️ **Market Maker Monitoring** - Whale wallet tracking
- ⚠️ **Historical Liquidations** - Bulk historical data (API provides recent only)

**Bottom line**: 4 out of 5 monitors work perfectly with free APIs! 🎉

---

## 📋 Required API Keys (All FREE!)

Add these to your `.env` file:

```env
# Portfolio Monitoring (REQUIRED)
BIRDEYE_API_KEY=your_key_here
# Get free key at: https://docs.birdeye.so/docs/authentication

# AI Decision Making (REQUIRED - choose one)
ANTHROPIC_KEY=your_key_here
# OR
OPENAI_KEY=your_key_here
# OR
DEEPSEEK_KEY=your_key_here

# Macro Monitoring (RECOMMENDED)
FRED_API_KEY=your_key_here
# Get free key at: https://fred.stlouisfed.org/docs/api/api_key.html

# Optional - Only if you want premium whale tracking
MOONDEV_API_KEY=your_key_here
# Get at: https://algotradecamp.com
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies

```bash
# Activate your conda environment
conda activate tflow

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Keys

Create or edit `.env` in project root:

```bash
# Copy example env
cp .env_example .env

# Edit with your keys
nano .env  # or use your preferred editor
```

Minimum required keys:
- `BIRDEYE_API_KEY` - For portfolio tracking
- `ANTHROPIC_KEY` (or another AI provider) - For hedge decisions

### 3. Test Public Data Sources

```bash
# Test the public API module
python src/agents/hedge_monitor/public_data_api.py
```

You should see:
```
🌙 Testing Public Data API...
✅ Public Data API initialized (no API key required)
1. Testing Funding Rates:
✅ Got funding rates for 4 symbols from Binance
...
```

### 4. Test Individual Monitors

```bash
# Test derivatives monitor (public API version)
python src/agents/hedge_monitor/derivatives_monitor_subagent_public.py

# Test portfolio monitor
python src/agents/hedge_monitor/portfolio_monitor_subagent.py

# Test options monitor
python src/agents/hedge_monitor/options_monitor_subagent.py

# Test macro monitor (requires FRED_API_KEY)
python src/agents/hedge_monitor/macro_monitor_subagent.py
```

### 5. Run Full Hedge Agent

```bash
python src/agents/hedge_agent.py
```

The system will automatically detect that Moon Dev API is not available and use public sources:

```
🌐 No Moon Dev API - using free public data sources (Binance, Bybit, etc.)
🚀 Initializing subagents...
💼 Portfolio Monitor Subagent initialized!
📊 Derivatives Monitor Subagent (Public API) initialized!
💡 Using FREE public APIs (Binance, Bybit) - no Moon Dev API required!
...
⚠️ Market maker monitor disabled (requires Moon Dev API)
✅ All available subagents initialized successfully!
```

---

## 📊 Public Data Sources Used

| Data Type | Source | API Cost | Rate Limits |
|-----------|--------|----------|-------------|
| **Funding Rates** | Binance Public API | FREE | 2400 req/min |
| **Open Interest** | Binance Public API | FREE | 2400 req/min |
| **Liquidations** | Binance Public API | FREE | 2400 req/min |
| **Options Max Pain** | Deribit Public API | FREE | Unlimited |
| **Macro Data** | FRED API | FREE | 1000 req/day |
| **Token Prices** | BirdEye API | FREE tier | 100 req/day |

All sources have generous free tiers that are more than sufficient for hedge monitoring!

---

## 🔧 Configuration

Edit `src/config.py`:

```python
# Hedge Monitor Agent Settings 🛡️
HEDGE_MONITOR_ENABLED = True
HEDGE_CHECK_INTERVAL_MINUTES = 30  # How often to run
HEDGE_AI_MODEL_PROVIDER = 'anthropic'  # or 'openai', 'deepseek', 'groq'
HEDGE_AUTO_EXECUTE = False  # Keep False for safety
HEDGE_MAX_POSITION_PCT = 50  # Max % to hedge
```

---

## 🎯 What Data You Get

### Derivatives Monitor (Public API)
- ✅ **Real-time funding rates** for BTC, ETH, SOL, BNB
- ✅ **Current open interest** across major perpetuals
- ✅ **Recent liquidations** (last 100 events per symbol)
- ✅ **Trend detection** for OI and funding changes

**Note**: Binance only provides recent liquidations (not full historical like Moon Dev API). This is usually sufficient for hedge decisions which focus on recent market stress.

### Portfolio Monitor
- ✅ All your token holdings
- ✅ USD values via BirdEye
- ✅ Concentration risk calculation
- ✅ Position size analysis

### Options Monitor
- ✅ BTC & ETH options max pain (Deribit)
- ✅ Strike price analysis
- ✅ Expiry proximity detection
- ✅ Price magnet identification

### Macro Monitor
- ✅ M2 Money Supply (FRED)
- ✅ FED Balance Sheet (FRED)
- ✅ Bank Reserves (FRED)
- ✅ Fed Funds Rate (FRED)
- ✅ QE/QT trend detection

---

## 💡 TradingView Integration (Optional)

While we use direct exchange APIs, you can also use TradingView for visualization:

### Setting Up TradingView Alerts

1. **Create Alerts in TradingView**:
   - Go to TradingView.com
   - Set up alerts for funding rate extremes
   - Set up alerts for OI changes
   - Set up alerts for liquidation spikes

2. **Use Webhook Integration** (Advanced):
   ```python
   # In your alert, use webhook URL:
   # https://your-server.com/tradingview-webhook

   # The hedge agent can listen for these webhooks
   # (requires setting up a simple Flask server)
   ```

3. **Manual Monitoring**:
   - Use TradingView to visually confirm hedge agent signals
   - Watch funding rate charts alongside agent output
   - Compare OI trends with agent recommendations

### TradingView Charts to Monitor

| Chart | What to Watch |
|-------|--------------|
| `BTCUSDT FUNDING RATE` | High positive = potential long squeeze |
| `BTCUSDT OPEN INTEREST` | Rapid increases = overheated market |
| `BTC OPTIONS MAX PAIN` | Price magnets near expiry |

---

## 🚨 Troubleshooting

### "BIRDEYE_API_KEY not found"
- Get free key at https://docs.birdeye.so
- Add to `.env`: `BIRDEYE_API_KEY=your_key`
- BirdEye free tier: 100 requests/day (plenty for hedge monitoring)

### "No funding rates data"
- Check internet connection
- Binance API is public - no key needed
- Try: `curl https://fapi.binance.com/fapi/v1/premiumIndex`
- If blocked, try VPN (some regions restrict Binance)

### "FRED_API_KEY not found"
- Macro monitoring requires FRED API
- Get free key at https://fred.stlouisfed.org
- Or set `HEDGE_MONITOR_ENABLED = False` in config to skip

### Rate Limits

If you hit rate limits:
- Increase `HEDGE_CHECK_INTERVAL_MINUTES` in config
- Binance: 2400 req/min (very generous)
- BirdEye: 100 req/day (cache portfolio data)
- FRED: 1000 req/day (cache macro data)

---

## 📈 Performance with Public APIs

| Metric | With Moon Dev API | With Public APIs |
|--------|-------------------|------------------|
| **Data Freshness** | Real-time | Real-time |
| **Historical Depth** | 6+ months | Recent only |
| **Whale Tracking** | Full tracking | Not available |
| **Cost** | Paid | FREE |
| **Accuracy** | High | High |
| **Suitable for Hedging** | ✅ Excellent | ✅ Very Good |

**Verdict**: Public APIs are excellent for hedge monitoring! The Hedge Agent's decisions are based primarily on recent market conditions, which public APIs provide perfectly.

---

## 🎉 Next Steps

1. **Run for 24-48 Hours**:
   ```bash
   python src/agents/hedge_agent.py
   ```
   Let it collect data and observe recommendations

2. **Review AI Decisions**:
   ```bash
   # View decision history
   cat src/data/hedge_monitor/hedge_decisions.csv
   ```

3. **Fine-tune Thresholds**:
   Edit thresholds in subagent files:
   - `FUNDING_EXTREME_THRESHOLD` (default: 20%)
   - `OI_CHANGE_THRESHOLD` (default: 15%)
   - `LIQUIDATION_SPIKE_THRESHOLD` (default: 50%)

4. **(Optional) Upgrade to Moon Dev API**:
   - For historical liquidation analysis
   - For whale wallet tracking
   - Get at: https://algotradecamp.com

---

## 💬 Community Support

- **Discord**: Join algotradecamp.com for community help
- **YouTube**: Moon Dev Trading (weekly agent updates)
- **GitHub**: Submit issues or feature requests

---

## 🔐 Security Notes

- All API keys are FREE tier - no credit card required
- Never commit `.env` file to git
- Use demo mode first (`HEDGE_AUTO_EXECUTE = False`)
- Test thoroughly before enabling auto-trading

---

**You're all set! No Moon Dev API needed. The Hedge Monitor works great with free public data! 🚀**

---

Built with 🌙 by Moon Dev | Happy Hedging!
