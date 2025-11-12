# 🛡️ Hedge Monitor System

**Comprehensive crypto portfolio risk monitoring and intelligent hedge decision system**

Built with love by Moon Dev 🌙🚀

---

## Overview

The Hedge Monitor System is an advanced multi-agent orchestration framework that monitors your crypto portfolio across multiple dimensions and uses AI to make intelligent hedging decisions. It tracks derivatives markets, options activity, market maker positioning, and macroeconomic indicators to protect your portfolio from adverse market conditions.

## Architecture

### Main Agent: `hedge_agent.py`
The orchestrator that runs all subagents, collects their outputs, and makes AI-powered hedge decisions.

### Subagents

1. **Portfolio Monitor** (`portfolio_monitor_subagent.py`)
   - Tracks your current crypto holdings
   - Calculates position concentration risk
   - Monitors portfolio value changes
   - Identifies overexposure to single assets

2. **Derivatives Monitor** (`derivatives_monitor_subagent.py` / `derivatives_monitor_subagent_public.py`)
   - Tracks Open Interest changes (Moon Dev API or free Binance/Bybit APIs)
   - Monitors Funding Rates across markets
   - Detects liquidation cascades
   - Identifies derivatives market stress signals
   - **NEW**: Public API version available (no Moon Dev API required!)

3. **Options Monitor** (`options_monitor_subagent.py`)
   - Tracks options max pain values (Deribit)
   - Monitors BTC & ETH options positioning
   - Identifies price magnets near expiry
   - Detects large options OI imbalances

4. **Market Maker Monitor** (`marketmaker_monitor_subagent.py`)
   - Tracks whale wallet activity
   - Monitors large position changes
   - Detects accumulation vs distribution patterns
   - Uses Moon Dev API whale addresses
   - *(Requires Moon Dev API)*

5. **Whale Tracker** (`whale_tracker_subagent.py`) **NEW! 🐋**
   - On-chain whale wallet monitoring via Etherscan & Solscan APIs
   - Tracks accumulation vs distribution patterns
   - Monitors large wallet transactions
   - Detects net flow changes (buying pressure vs selling pressure)
   - Works with FREE tier APIs (no Moon Dev API required)

6. **Order Blocks Monitor** (`orderblocks_monitor_subagent.py`) **NEW! 📦**
   - Tracks institutional order blocks from TradingLite
   - Identifies key support/resistance levels
   - Monitors price proximity to order blocks
   - Uses Selenium web scraping (no TradingLite API required)
   - Optional TradingLite account login for enhanced data

7. **Macro Monitor** (`macro_monitor_subagent.py`)
   - Tracks M2 money supply (FRED API)
   - Monitors FED balance sheet (QE/QT)
   - Tracks bank reserves
   - Monitors Fed Funds Rate
   - Provides macro context for risk decisions

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The hedge monitor requires `fredapi` for macro economic data monitoring.

### 2. API Keys Required

Add these to your `.env` file:

```env
# Core APIs
ANTHROPIC_KEY=your_key_here           # For AI decision making (REQUIRED)
BIRDEYE_API_KEY=your_key_here        # For portfolio token prices (REQUIRED)

# Trading Data (Choose ONE)
MOONDEV_API_KEY=your_key_here        # Premium: derivatives, liquidations, whale data
                                      # OR use FREE public APIs (Binance, Bybit) - no key needed!

# Optional but Recommended
FRED_API_KEY=your_key_here           # For macro monitoring (FREE)
                                      # Get at: https://fred.stlouisfed.org/docs/api/api_key.html

ETHERSCAN_API_KEY=your_key_here      # For on-chain whale tracking (FREE)
                                      # Get at: https://etherscan.io/apis

SOLSCAN_API_KEY=your_key_here        # For Solana whale tracking (FREE)
                                      # Get at: https://public-api.solscan.io/

# Optional
TRADINGLITE_EMAIL=your_email         # For TradingLite login (optional)
TRADINGLITE_PASSWORD=your_password   # Enables order blocks scraping
```

**Note**: The system now works **without** Moon Dev API! See `SETUP_NO_MOONDEV.md` for details.

### 3. Configure Settings

Edit `src/config.py`:

```python
# Hedge Monitor Agent Settings 🛡️
HEDGE_MONITOR_ENABLED = True  # Enable hedge monitoring
HEDGE_CHECK_INTERVAL_MINUTES = 30  # How often to run analysis
HEDGE_AI_MODEL_PROVIDER = 'anthropic'  # AI provider: anthropic, openai, deepseek, groq
HEDGE_AUTO_EXECUTE = False  # Auto-execute hedges (USE WITH CAUTION!)
HEDGE_MAX_POSITION_PCT = 50  # Max % of portfolio to hedge
```

## Usage

### Running the Full Hedge Agent

```bash
# Run the main hedge agent (orchestrates all subagents)
python src/agents/hedge_agent.py
```

This will:
1. Run all 7 monitoring subagents
2. Collect and analyze their outputs
3. Consult AI for hedge recommendations
4. Display actionable insights
5. (Optional) Execute hedge trades if `HEDGE_AUTO_EXECUTE=True`

### Running Individual Subagents

Each subagent can run independently for testing:

```bash
# Portfolio monitoring
python src/agents/hedge_monitor/portfolio_monitor_subagent.py

# Derivatives monitoring (choose one based on API availability)
python src/agents/hedge_monitor/derivatives_monitor_subagent.py          # Moon Dev API version
python src/agents/hedge_monitor/derivatives_monitor_subagent_public.py   # Free public API version

# Options monitoring
python src/agents/hedge_monitor/options_monitor_subagent.py

# Market maker monitoring (requires Moon Dev API)
python src/agents/hedge_monitor/marketmaker_monitor_subagent.py

# On-chain whale tracking (NEW!)
python src/agents/hedge_monitor/whale_tracker_subagent.py

# Order blocks monitoring (NEW!)
python src/agents/hedge_monitor/orderblocks_monitor_subagent.py

# Macro monitoring
python src/agents/hedge_monitor/macro_monitor_subagent.py
```

## AI Decision Making

The Hedge Agent uses advanced AI (Claude, GPT-4, DeepSeek, etc.) to analyze:

- **Portfolio Risk**: Concentration, drawdowns, position sizes
- **Derivatives Signals**: OI changes, funding rate extremes, liquidations
- **Options Positioning**: Max pain divergence, expiry magnets
- **Market Maker Activity**: Whale wallet positioning (Moon Dev API)
- **On-Chain Whales**: Accumulation/distribution via Etherscan & Solscan
- **Order Blocks**: Institutional support/resistance levels from TradingLite
- **Macro Context**: QE/QT, interest rates, money supply

### Decision Outputs

The AI provides structured recommendations:

```
DECISION: OPEN_HEDGE / NO_HEDGE / CLOSE_HEDGE
HEDGE_TYPE: SHORT_PERPETUAL / LONG_PERPETUAL / OPTIONS_PUT / NONE
HEDGE_SIZE_PCT: 0-100 (percentage of portfolio)
CONFIDENCE: 0-100

REASONING: [Detailed multi-factor analysis]
KEY_RISKS: [3-5 most critical risks]
HEDGE_EXECUTION: [Specific execution strategy]
```

## Data Storage

All subagents store their data in:
```
src/data/hedge_monitor/
├── portfolio/
│   └── portfolio_history.csv
├── derivatives/
│   ├── funding_history.csv
│   ├── funding_history_public.csv      # Public API version
│   ├── oi_history.csv
│   ├── oi_history_public.csv           # Public API version
│   ├── liquidation_history.csv
│   └── liquidation_history_public.csv  # Public API version
├── options/
│   └── options_history.csv
├── marketmaker/
│   ├── whale_activity_history.csv
│   └── whale_addresses.txt
├── whale_tracker/                       # NEW!
│   ├── whale_history.csv
│   └── whale_addresses.json
├── order_blocks/                        # NEW!
│   └── orderblocks_history.csv
└── macro/
    └── macro_history.csv
```

Main hedge decisions are stored in:
```
src/data/hedge_monitor/hedge_decisions.csv
```

## Safety Features

### Demo Mode (Default)
By default, the hedge agent runs in **demo mode** and will NOT execute real trades. It only provides recommendations.

### Production Mode
To enable actual trade execution:

1. Set `HEDGE_AUTO_EXECUTE = True` in `config.py`
2. Uncomment execution code in `hedge_agent.py:execute_hedge()`
3. Verify your exchange API keys are correct
4. **Start with small position sizes for testing!**

⚠️ **WARNING**: Automated hedge execution carries significant risk. Always test thoroughly in demo mode first.

## Example Output

```
╔════════════════════════════════════════════════════════════╗
║                   🛡️  HEDGE AGENT CYCLE  🛡️                ║
╚════════════════════════════════════════════════════════════╝

[1/7] 💼 Portfolio Monitor
╔════════════════════════════════════════════════════════════╗
║            🌙 Portfolio Monitor Summary 💼                 ║
╠════════════════════════════════════════════════════════════╣
║  Total Portfolio Value: $10,250.00                         ║
║  USDC Balance: $2,500.00                                   ║
║  Active Positions: 3                                       ║
║  Largest Position: 45.2%                                   ║
║  Concentration Risk: 0.412                                 ║
║  Risk Level: 🟡 MEDIUM - Moderately concentrated          ║
╚════════════════════════════════════════════════════════════╝

[2/7] 📊 Derivatives Monitor (Public API)
╔════════════════════════════════════════════════════════════╗
║         🌙 Derivatives Monitor Summary 📊                  ║
╠════════════════════════════════════════════════════════════╣
║  🔴 EXTREME_POSITIVE_FUNDING                               ║
║     BTC has extreme positive funding (25.2% annual).       ║
║     Longs paying shorts heavily - potential for squeeze.   ║
╚════════════════════════════════════════════════════════════╝

...

╔════════════════════════════════════════════════════════════╗
║                    🤖 AI DECISION 🤖                       ║
╠════════════════════════════════════════════════════════════╣
║  Decision: OPEN_HEDGE                                      ║
║  Hedge Type: SHORT_PERPETUAL                               ║
║  Size: 25% of portfolio                                    ║
║  Confidence: 78%                                           ║
╠════════════════════════════════════════════════════════════╣
║  Reasoning:                                                ║
║  Multiple risk factors converge: Portfolio is moderately   ║
║  concentrated (41% risk score), BTC funding is extremely   ║
║  positive at 25% annual suggesting overleveraged longs,    ║
║  and macro liquidity is tightening (QT mode). Recommend   ║
║  opening 25% short hedge on BTC perpetuals to protect     ║
║  against potential correction.                             ║
╚════════════════════════════════════════════════════════════╝
```

## Integration with Main Trading System

To integrate with `main.py` orchestrator:

```python
# In src/main.py, add to ACTIVE_AGENTS dict:
ACTIVE_AGENTS = {
    'risk': True,
    'trading': True,
    'hedge': True,  # Add this line
    # ... other agents
}

# Import hedge agent
from src.agents.hedge_agent import HedgeAgent

# Initialize in main()
if ACTIVE_AGENTS.get('hedge'):
    hedge_agent = HedgeAgent()
    hedge_agent.run()
```

## Troubleshooting

### "FRED_API_KEY not found"
- Macro monitoring requires a free FRED API key
- Get one at: https://fred.stlouisfed.org/docs/api/api_key.html
- Add to `.env`: `FRED_API_KEY=your_key_here`
- Or disable macro monitoring (it will skip gracefully)

### "Portfolio data unavailable"
- Ensure your wallet address is correct in `config.py`
- Check BIRDEYE_API_KEY is valid
- Verify you have USDC or tracked tokens in wallet

### "Derivatives data unavailable"
- If using Moon Dev API: Check MOONDEV_API_KEY is valid
- If using public APIs: System auto-falls back to Binance/Bybit (no key needed)
- Check network connectivity
- Verify API rate limits

### "Selenium not installed" (Order Blocks Monitor)
- Install Selenium: `pip install selenium webdriver-manager`
- Or install ChromeDriver manually for your system
- System will use mock data if Selenium unavailable
- TradingLite credentials are optional (enhances data access)

### "Whale tracking unavailable"
- Get free Etherscan API key: https://etherscan.io/apis
- Get free Solscan API key: https://public-api.solscan.io/
- Add to `.env`: `ETHERSCAN_API_KEY=your_key_here`
- System gracefully skips if keys not available

## Advanced Configuration

### Custom Thresholds

Edit subagent files to adjust sensitivity:

```python
# In derivatives_monitor_subagent.py
FUNDING_EXTREME_THRESHOLD = 20  # Annual % for extreme funding
OI_CHANGE_THRESHOLD = 15  # % change in OI considered significant
LIQUIDATION_SPIKE_THRESHOLD = 50  # % increase for liquidation alerts

# In portfolio_monitor_subagent.py
# Concentration risk > 0.5 = HIGH, 0.3-0.5 = MEDIUM, < 0.3 = LOW
```

### AI Model Selection

Switch AI providers in `config.py`:

```python
HEDGE_AI_MODEL_PROVIDER = 'anthropic'  # Reliable, good reasoning
# HEDGE_AI_MODEL_PROVIDER = 'openai'    # Fast, good performance
# HEDGE_AI_MODEL_PROVIDER = 'deepseek'  # Cost-effective, reasoning model
# HEDGE_AI_MODEL_PROVIDER = 'groq'      # Very fast inference
```

## Performance & Cost

- **Runtime**: ~3-5 minutes per full cycle (all 7 subagents)
- **API Costs**:
  - FRED API: Free
  - Deribit API: Free (public endpoints)
  - Binance/Bybit API: Free (no key required)
  - Etherscan API: Free tier available
  - Solscan API: Free tier available
  - Moon Dev API: Paid (optional - can use free alternatives)
  - AI Inference: ~$0.01-0.05 per decision (varies by provider)
- **Data Storage**: ~20-80 MB over 30 days
- **Selenium**: Adds ~10-15 seconds for order blocks scraping

## Roadmap

- [x] ~~On-chain whale tracking~~ **COMPLETED** ✅
- [x] ~~TradingLite order blocks monitoring~~ **COMPLETED** ✅
- [x] ~~Public API support (no Moon Dev API required)~~ **COMPLETED** ✅
- [ ] Add DeFi protocol risk monitoring
- [ ] Integration with TradingView alerts
- [ ] Discord/Telegram notifications
- [ ] Historical backtest of hedge decisions
- [ ] Multi-exchange hedge execution
- [ ] Portfolio rebalancing suggestions
- [ ] Correlation-based hedge optimization

## Disclaimer

⚠️ **IMPORTANT**: This is an experimental educational project.

- Not financial advice
- No guarantees of any kind
- Substantial risk of loss
- Always do your own research (DYOR)
- Test thoroughly before using with real funds
- Never risk more than you can afford to lose

## Support

- **YouTube**: Moon Dev Trading (weekly updates)
- **Discord**: Join algotradecamp.com for community support
- **GitHub Issues**: Report bugs or request features

---

Built with 🌙 by Moon Dev | MIT License
