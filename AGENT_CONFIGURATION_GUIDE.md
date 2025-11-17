# 🌙 Moon Dev AI Agents - Configuration Guide

**Generated:** 2025-11-17
**Status:** All agents configured with portable paths and graceful error handling

---

## 📋 Configuration Status Summary

### ✅ Completed Fixes
- ✅ Removed all hardcoded Mac-specific paths (`/Users/md/...` and `/Volumes/...`)
- ✅ Implemented dynamic path resolution using `PROJECT_ROOT`
- ✅ Added graceful API error handling across all major agents
- ✅ Fixed hedge agent subagent connections
- ✅ Added helpful error messages for missing API keys
- ✅ Made all paths cross-platform compatible (Linux/Mac/Windows)

### ⚙️ Configuration Required

The following settings need to be configured in your `.env` file and `config.py`:

---

## 🔑 Required API Keys

### Essential for Most Agents
```env
# AI/LLM Providers (at least one required)
ANTHROPIC_KEY=sk-ant-...           # Claude models (recommended for most agents)
OPENAI_KEY=sk-...                  # GPT models (required for RBI agents using GPT-5)
DEEPSEEK_KEY=sk-...                # DeepSeek models (good for reasoning tasks)
GROQ_API_KEY=gsk_...               # Groq (fast inference)
GEMINI_KEY=...                     # Google Gemini

# Market Data
BIRDEYE_API_KEY=...                # Solana token data (required for token trading)
COINGECKO_API_KEY=...              # Token metadata (optional but recommended)

# Blockchain/Trading
SOLANA_PRIVATE_KEY=...             # Solana wallet (required for Solana trading)
RPC_ENDPOINT=https://...           # Solana RPC node
```

### Premium/Optional
```env
# Moon Dev Premium API (optional but unlocks more features)
MOONDEV_API_KEY=...                # Liquidations, funding, OI, whale data, copybot

# Exchange APIs (for specific agents)
HYPER_LIQUID_ETH_PRIVATE_KEY=...   # HyperLiquid perpetuals trading

# Social/Content
TWITTER_USERNAME=...               # Twitter posting (for tweet_agent)
TWITTER_PASSWORD=...
RESTREAM_COOKIES=...               # Restream chat (for chat_agent)

# Macro Data (for hedge_agent)
FRED_API_KEY=...                   # Federal Reserve economic data (optional)
```

---

## 📁 Path Configurations in `config.py`

### CopyBot Agent
```python
# Set this to your copybot portfolio CSV file path
# Leave as None to use default location: src/data/copybot/current_portfolio.csv
COPYBOT_PORTFOLIO_PATH = None  # or "/path/to/your/current_portfolio.csv"
```

**Default location:** `src/data/copybot/current_portfolio.csv`
**If missing:** Agent will show helpful error with setup instructions

### Real-Time Clips Agent
```python
# Set this to your OBS recording folder
# Leave as None to disable the clips agent
REALTIME_CLIPS_OBS_FOLDER = None  # or "/path/to/OBS/recordings"
```

**Examples:**
- Linux: `"/home/user/Videos/OBS"`
- Mac: `"/Users/username/Movies/OBS"`
- Windows: `"C:\\Users\\YourName\\Videos\\OBS"`

**If missing:** Agent will show error on startup with configuration instructions

---

## 🤖 Agent-Specific Configuration

### Main Trading Loop (`main.py`)

Control which agents run in the main orchestration loop:

```python
ACTIVE_AGENTS = {
    'risk':       True,   # Run risk management first (recommended!)
    'trading':    False,  # LLM-based trading agent
    'strategy':   False,  # Strategy-based trading
    'copybot':    False,  # CopyBot portfolio analysis
    'sentiment':  False,  # Twitter sentiment (runs better standalone)
}
```

**⚠️ Safety:** All set to `False` by default. Enable only after testing!

### Risk Agent (`config.py`)
```python
MAX_LOSS_USD = 25              # Stop trading after this loss
MAX_GAIN_USD = 25              # Stop trading after this gain
MINIMUM_BALANCE_USD = 50       # Close positions if balance drops below
USE_AI_CONFIRMATION = True     # Ask AI before closing positions
```

### Trading Agent (`src/agents/trading_agent.py`)
```python
# Exchange Selection (lines 66-80)
EXCHANGE = "SOLANA"            # or "HYPERLIQUID" or "ASTER"
USE_SWARM_MODE = True          # Use 6-model consensus (more robust)
LONG_ONLY = True               # Only buy, no shorting

# Token List (lines 101-104)
MONITORED_TOKENS = [
    # Add your token addresses here
]
```

### Sentiment Agent (`src/agents/sentiment_agent.py`)
```python
TOKENS_TO_TRACK = ["solana", "bitcoin", "ethereum"]
TWEETS_PER_RUN = 30
SENTIMENT_ANNOUNCE_THRESHOLD = 0.4
CHECK_INTERVAL_MINUTES = 15
```

### Hedge Agent (`config.py`)
```python
HEDGE_MONITOR_ENABLED = False     # Set True to enable
HEDGE_CHECK_INTERVAL_MINUTES = 30
HEDGE_AI_MODEL_PROVIDER = 'anthropic'
HEDGE_AUTO_EXECUTE = False        # DANGEROUS! Set True to auto-execute hedges
HEDGE_MAX_POSITION_PCT = 50
```

### RBI Agents (Research-Backtest-Implement)

**Data Location:** `src/data/rbi/BTC-USD-15m.csv` (now uses dynamic paths)

**Model Selection** (in each rbi_agent file):
```python
RESEARCH_CONFIG = {"type": "openai", "name": "gpt-5"}
BACKTEST_CONFIG = {"type": "openai", "name": "gpt-5"}
DEBUG_CONFIG = {"type": "deepseek", "name": "deepseek-chat"}
```

**Ideas File:** `src/data/rbi/ideas.txt` (one strategy per line)

---

## 🔄 Data Directory Structure

All agents now automatically create their data directories:

```
src/data/
├── copybot/              # CopyBot portfolio data
├── hedge_monitor/        # Hedge agent decisions
├── rbi/                  # RBI strategy research
│   ├── MM_DD_YYYY/       # Date-based folders (auto-created)
│   │   ├── research/
│   │   ├── backtests/
│   │   ├── backtests_final/
│   │   ├── backtests_package/
│   │   └── charts/
│   └── BTC-USD-15m.csv   # Sample OHLCV data
├── sentiment/            # Sentiment analysis results
├── realtime_clips/       # Video clips (if configured)
├── execution_results/    # Trade execution logs
├── charts/               # Analysis charts
├── polymarket/           # Prediction market data
├── coingecko_results/    # CoinGecko analysis
└── [agent_name]/         # Each agent creates its own directory
```

---

## 🚀 Running Agents

### Standalone Agents (Run Independently)

These agents have their own check intervals and run continuously:

```bash
# Market monitoring agents
python src/agents/whale_agent.py          # Every 5 minutes
python src/agents/funding_agent.py        # Every 15 minutes
python src/agents/liquidation_agent.py    # Every 10 minutes
python src/agents/sentiment_agent.py      # Every 15 minutes

# Hedge analysis
python src/agents/hedge_agent.py          # Every 30 minutes

# Content creation
python src/agents/realtime_clips_agent.py # Every 2 minutes (if OBS configured)
python src/agents/chat_agent.py           # Restream chat monitoring

# Strategy research
python src/agents/rbi_agent.py            # Process ideas from ideas.txt
python src/agents/rbi_agent_v2.py         # With auto-execution loop
python src/agents/rbi_agent_v3.py         # Enhanced version
```

### Main Orchestrator Loop

```bash
python src/main.py
```

**How it works:**
1. Runs every 15 minutes (configurable in `config.py`)
2. Executes agents in order: risk → trading → strategy → copybot → sentiment
3. Only runs agents enabled in `ACTIVE_AGENTS` dict
4. Risk agent always runs first as safeguard

---

## 🛡️ Error Handling

All agents now include graceful error handling:

### Missing API Keys
```
⚠️ WARNING: ANTHROPIC_KEY not found in environment
   Agent will not be able to analyze positions
   Please add ANTHROPIC_KEY to your .env file
```

### Missing Paths
```
❌ Portfolio file not found: /home/user/moon-dev-ai-agents/src/data/copybot/current_portfolio.csv
   Please either:
   1. Set COPYBOT_PORTFOLIO_PATH in config.py to your portfolio CSV file
   2. Place your portfolio CSV at the default location
   3. Use the copybot API to fetch portfolio data
```

### API Failures
- Agents continue running with reduced functionality
- Clear error messages explain what's missing
- No obscure crashes or stack traces for config issues

---

## 🔍 Testing Agent Initialization

Test individual agents before enabling in main loop:

```bash
# Test with basic initialization (won't trade)
python src/agents/trading_agent.py
python src/agents/risk_agent.py
python src/agents/copybot_agent.py

# Check for error messages about missing:
# - API keys
# - File paths
# - Configuration settings
```

**Expected output:**
- ✅ Green: Successful initialization
- ⚠️ Yellow: Warnings about optional features
- ❌ Red: Critical errors that need fixing

---

## 📊 Agent Dependencies

### By API Key Required

**ANTHROPIC_KEY:**
- trading_agent, risk_agent, copybot_agent, strategy_agent
- hedge_agent, sentiment_agent (optional)

**OPENAI_KEY:**
- rbi_agent (GPT-5), whale_agent, funding_agent, liquidation_agent
- sentiment_agent, clips_agent (TTS)

**DEEPSEEK_KEY:**
- whale_agent, funding_agent, liquidation_agent (preferred for these)
- rbi_agent_v2, rbi_agent_v3 (alternative to OpenAI)

**BIRDEYE_API_KEY:**
- Most trading agents (token data for Solana)
- copybot_agent, solana_agent

**MOONDEV_API_KEY (optional):**
- funding_agent, liquidation_agent, whale_agent
- hedge_agent (derivatives, market maker monitoring)
- copybot_agent (follow list)

### By Exchange

**Solana Trading:**
- SOLANA_PRIVATE_KEY
- BIRDEYE_API_KEY
- RPC_ENDPOINT

**HyperLiquid Trading:**
- HYPER_LIQUID_ETH_PRIVATE_KEY

---

## 🎯 Quick Start Checklist

1. **Environment Setup**
   ```bash
   # Activate conda environment
   conda activate tflow

   # Copy .env_example to .env
   cp .env_example .env

   # Edit .env with your API keys
   nano .env
   ```

2. **Minimum Required Keys** (to get started):
   - [ ] `ANTHROPIC_KEY` (for most agents)
   - [ ] `BIRDEYE_API_KEY` (for token data)
   - [ ] `SOLANA_PRIVATE_KEY` (if trading on Solana)
   - [ ] `RPC_ENDPOINT` (Solana RPC node)

3. **Configure Agents**
   - [ ] Edit `config.py` for trading parameters
   - [ ] Set `MONITORED_TOKENS` in `config.py`
   - [ ] Review risk limits (`MAX_LOSS_USD`, etc.)
   - [ ] Configure agent-specific settings

4. **Test Individual Agents**
   ```bash
   python src/agents/risk_agent.py
   python src/agents/trading_agent.py
   ```

5. **Enable Main Loop** (after testing)
   - [ ] Set `ACTIVE_AGENTS['risk'] = True` in `main.py`
   - [ ] Gradually enable other agents
   - [ ] Monitor first runs carefully

---

## 🆘 Common Issues

### "Module not found" errors
```bash
# Make sure you're in the project root
cd /home/user/moon-dev-ai-agents

# And running with proper imports
python src/agents/agent_name.py
```

### "API key not found" errors
- Check `.env` file exists in project root
- Verify key names match exactly (case-sensitive)
- Ensure no quotes around keys in `.env`

### "Portfolio file not found" (CopyBot)
- Set `COPYBOT_PORTFOLIO_PATH` in `config.py`, or
- Place CSV at `src/data/copybot/current_portfolio.csv`

### "OBS folder not found" (Clips Agent)
- Set `REALTIME_CLIPS_OBS_FOLDER` in `config.py`
- Or set to `None` to disable

### Agent won't trade
- Check `ACTIVE_AGENTS` in `main.py` (must be `True`)
- Verify `MONITORED_TOKENS` list is not empty
- Ensure API keys are valid
- Check risk limits aren't already hit

---

## 📚 Additional Resources

- **Project Instructions:** `CLAUDE.md` - Detailed development guidelines
- **Model Factory:** `src/models/README.md` - LLM provider documentation
- **Agent Base:** `src/agents/base_agent.py` - Base agent implementation
- **Main Loop:** `src/main.py` - Orchestration logic
- **Config:** `src/config.py` - All configuration settings

---

## 🎉 What's Fixed

This configuration update includes:

1. ✅ **Cross-Platform Paths:** All hardcoded Mac paths removed
2. ✅ **Dynamic Path Resolution:** Uses `PROJECT_ROOT` pattern everywhere
3. ✅ **Graceful Error Handling:** Clear messages for missing API keys
4. ✅ **Better Validation:** Checks before using clients/APIs
5. ✅ **Consistent Patterns:** All agents follow same initialization approach
6. ✅ **Helpful Messages:** Color-coded output with remediation steps
7. ✅ **Hedge Agent Fixed:** All subagent connections working
8. ✅ **RBI Agents Fixed:** All 7 RBI agents use dynamic paths

**Files Modified:** 20+ agent files updated with better configuration handling

---

**Happy Trading! 🌙🚀**

*Remember: This is experimental software. Trade at your own risk. Past performance doesn't guarantee future results.*
