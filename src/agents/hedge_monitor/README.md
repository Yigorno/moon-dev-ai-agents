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

2. **Derivatives Monitor** (`derivatives_monitor_subagent.py`)
   - Tracks Open Interest changes (via Moon Dev API)
   - Monitors Funding Rates across markets
   - Detects liquidation cascades
   - Identifies derivatives market stress signals

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

5. **Macro Monitor** (`macro_monitor_subagent.py`)
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
# Required
MOONDEV_API_KEY=your_key_here        # For derivatives, liquidations, whale data
ANTHROPIC_KEY=your_key_here           # For AI decision making
BIRDEYE_API_KEY=your_key_here        # For portfolio token prices

# Optional but Recommended
FRED_API_KEY=your_key_here           # For macro monitoring
                                      # Get free at: https://fred.stlouisfed.org/docs/api/api_key.html
```

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
1. Run all 5 monitoring subagents
2. Collect and analyze their outputs
3. Consult AI for hedge recommendations
4. Display actionable insights
5. (Optional) Execute hedge trades if `HEDGE_AUTO_EXECUTE=True`

### Running Individual Subagents

Each subagent can run independently for testing:

```bash
# Portfolio monitoring
python src/agents/hedge_monitor/portfolio_monitor_subagent.py

# Derivatives monitoring
python src/agents/hedge_monitor/derivatives_monitor_subagent.py

# Options monitoring
python src/agents/hedge_monitor/options_monitor_subagent.py

# Market maker monitoring
python src/agents/hedge_monitor/marketmaker_monitor_subagent.py

# Macro monitoring
python src/agents/hedge_monitor/macro_monitor_subagent.py
```

## AI Decision Making

The Hedge Agent uses advanced AI (Claude, GPT-4, DeepSeek, etc.) to analyze:

- **Portfolio Risk**: Concentration, drawdowns, position sizes
- **Derivatives Signals**: OI changes, funding rate extremes, liquidations
- **Options Positioning**: Max pain divergence, expiry magnets
- **Whale Activity**: Accumulation/distribution patterns
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
│   ├── oi_history.csv
│   └── liquidation_history.csv
├── options/
│   └── options_history.csv
├── marketmaker/
│   ├── whale_activity_history.csv
│   └── whale_addresses.txt
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

[1/5] 💼 Portfolio Monitor
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

[2/5] 📊 Derivatives Monitor
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
- Check MOONDEV_API_KEY is valid
- Verify API key has proper permissions
- Check rate limits (100 requests/minute)

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

- **Runtime**: ~2-3 minutes per full cycle (all 5 subagents)
- **API Costs**:
  - FRED API: Free
  - Deribit API: Free (public endpoints)
  - Moon Dev API: Paid (required)
  - AI Inference: ~$0.01-0.05 per decision (varies by provider)
- **Data Storage**: ~10-50 MB over 30 days

## Roadmap

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
