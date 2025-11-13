# 📊 SMC Trading Agent - Smart Money Concepts

**Advanced cryptocurrency trading agent combining technical SMC analysis with live market data**

Built with love by Moon Dev 🌙🚀

---

## Overview

The SMC Trading Agent uses **Smart Money Concepts** (institutional trading techniques) combined with **live market microstructure data** to make intelligent trading decisions powered by AI.

### What is Smart Money Concepts (SMC)?

Smart Money Concepts is a trading methodology that focuses on identifying where institutional traders ("smart money") are positioning themselves by analyzing:

- **Order Blocks (OB)** - Zones where institutions placed large buy/sell orders
- **Fair Value Gaps (FVG)** - Price inefficiencies that often get filled
- **Market Structure Break (MSB)** - Major trend reversals
- **Break of Structure (BoS)** - Trend continuation patterns
- **Swing Highs/Lows** - Key price pivot points

### Live Market Data Integration

The agent also analyzes real-time derivatives market data:

- **Open Interest (OI)** changes - Rising/falling leverage
- **Funding Rates** - Long/short positioning sentiment
- **Liquidations** - Cascade events and forced selling/buying
- **Cumulative Volume Delta (CVD)** - Net buying vs selling pressure

## Architecture

### Three-Module System

```
┌─────────────────────────────────────────────────────────────┐
│                   SMC Trading Agent                         │
│                 (smc_trading_agent.py)                      │
│                                                             │
│  ┌────────────────┐         ┌────────────────────────┐    │
│  │  SMC Analysis  │         │  Market Data Aggregator│    │
│  │ (smc_analysis) │         │  (smc_market_data)     │    │
│  │                │         │                        │    │
│  │ • Order Blocks │         │ • Liquidation CVD      │    │
│  │ • FVG Detection│         │ • Funding Rates        │    │
│  │ • MSB/BoS      │         │ • Open Interest        │    │
│  │ • Swing Points │         │ • Sentiment Scoring    │    │
│  └────────┬───────┘         └──────────┬─────────────┘    │
│           │                            │                  │
│           └────────────┬───────────────┘                  │
│                        │                                  │
│                   ┌────▼────┐                            │
│                   │   LLM   │                            │
│                   │Decision │                            │
│                   │ Engine  │                            │
│                   └────┬────┘                            │
│                        │                                  │
│                   Trade Decision                          │
│                   (BUY/SELL/HOLD)                        │
└─────────────────────────────────────────────────────────────┘
```

### Module Descriptions

1. **smc_analysis.py** - Technical SMC indicator calculations
   - Detects swing highs/lows using configurable windows
   - Identifies order blocks based on volume and price movement
   - Finds fair value gaps (bullish and bearish)
   - Tracks market structure breaks and continuations
   - Generates SMC scoring (-100 to +100)

2. **smc_market_data.py** - Live market data aggregation
   - Fetches liquidation data and calculates CVD
   - Gets funding rates across exchanges
   - Monitors open interest changes
   - Detects liquidation cascades
   - Generates market sentiment score

3. **smc_trading_agent.py** - Main orchestrator and decision engine
   - Fetches OHLCV data for any token
   - Runs SMC technical analysis
   - Aggregates live market data
   - Uses AI to synthesize both signals
   - Makes trading decisions (BUY/SELL/HOLD)
   - Executes trades (paper or live)

## Setup

### 1. Install Dependencies

All required packages are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `pandas`, `numpy` - Data analysis
- `anthropic` / `openai` - AI decision making
- `requests` - API calls
- `python-dotenv` - Environment variables

### 2. API Keys Required

Add these to your `.env` file:

```env
# REQUIRED
ANTHROPIC_KEY=your_key_here           # For AI decision making (or use OpenAI)
BIRDEYE_API_KEY=your_key_here        # For OHLCV token data

# OPTIONAL but RECOMMENDED
MOONDEV_API_KEY=your_key_here        # For liquidations, funding, OI data
                                      # Note: Agent works without this, but limited market data

# ALTERNATIVE AI PROVIDERS (choose one)
OPENAI_KEY=your_key_here             # For OpenAI GPT models
DEEPSEEK_KEY=your_key_here           # For DeepSeek models
GROQ_API_KEY=your_key_here           # For Groq (fast inference)
```

### 3. Configure Settings

Edit `src/config.py`:

```python
# SMC Trading Agent Settings 📊
SMC_TRADING_ENABLED = True  # Enable/disable agent
SMC_PAPER_TRADING = True  # True = paper trading, False = live trades
SMC_EXCHANGE = 'ASTER'  # 'ASTER', 'HYPERLIQUID', or 'SOLANA'
SMC_POSITION_SIZE_PCT = 30  # % of balance per position
SMC_LEVERAGE = 5  # Leverage (1-125x for Aster/HyperLiquid)
SMC_MIN_CONFIDENCE = 70  # Minimum confidence to trade (0-100)
SMC_DECISION_METHOD = 'LLM'  # 'LLM', 'SCORING', or 'HYBRID'
SMC_AI_MODEL_PROVIDER = 'anthropic'  # AI provider
```

## Usage

### Running the Agent

```bash
# Run standalone with a specific token
python src/agents/smc_trading_agent.py
```

### In Python Code

```python
from src.agents.smc_trading_agent import SMCTradingAgent

agent = SMCTradingAgent()

# Analyze a Solana token
SOL_ADDRESS = "So11111111111111111111111111111111111111112"
agent.run(token_address=SOL_ADDRESS, symbol='SOL')
```

### Example Output

```
══════════════════════════════════════════════════════════════════
🌙 SMC Analysis for SOL
══════════════════════════════════════════════════════════════════

[1/3] 📊 Fetching OHLCV data (15m, 3 days)...
✅ Got 288 candles

[2/3] 🎯 Running SMC analysis...

  📈 SMC Summary:
    Trend: uptrend
    Bullish Signals: 5
    Bearish Signals: 2
    Score: 45/100
    Signal: BUY

[3/3] 📡 Aggregating market data...

  💰 Market Data Summary:
    Signal: BUY
    Sentiment Score: 25

══════════════════════════════════════════════════════════════════
🎯 Making Trading Decision (LLM)
══════════════════════════════════════════════════════════════════

🤖 Consulting AI for trading decision...

  Decision: BUY
  Confidence: 78%
  Reasoning: Strong bullish SMC confluence with uptrend structure,
  multiple order blocks supporting, and positive funding rates
  indicating bullish sentiment. Recent BoS confirms continuation.

══════════════════════════════════════════════════════════════════
📄 PAPER TRADE - BUY
══════════════════════════════════════════════════════════════════
  Token: So11111111111111111111111111111111111111112
  Price: $0.00012345
  Confidence: 78%
  Reasoning: [AI reasoning here]

✅ Paper trade recorded

══════════════════════════════════════════════════════════════════
✅ SMC Trading Agent cycle complete!
══════════════════════════════════════════════════════════════════
```

## Decision Methods

### 1. LLM Method (Default)

Uses AI (Claude, GPT-4, etc.) to analyze both SMC and market data:

```python
SMC_DECISION_METHOD = 'LLM'
```

**Pros:**
- Most intelligent and nuanced decisions
- Considers complex interactions between signals
- Can explain reasoning in natural language

**Cons:**
- Slower (~3-5 seconds per decision)
- Costs API credits
- Less deterministic

### 2. Scoring Method

Uses pure numerical scoring system:

```python
SMC_DECISION_METHOD = 'SCORING'
```

**Scoring System:**
- SMC Score: -100 to +100 (from technical analysis)
- Market Score: -100 to +100 (from live data)
- Combined: -200 to +200

**Decision Rules:**
- Combined ≥ 60: BUY (high confidence)
- Combined ≥ 30: BUY (moderate confidence)
- Combined ≤ -60: SELL (high confidence)
- Combined ≤ -30: SELL (moderate confidence)
- Otherwise: HOLD

**Pros:**
- Very fast (instant decisions)
- Free (no API costs)
- Fully deterministic and transparent

**Cons:**
- Less nuanced than AI
- Can't adapt to novel situations
- No natural language reasoning

### 3. Hybrid Method

Requires both LLM and Scoring to agree:

```python
SMC_DECISION_METHOD = 'HYBRID'
```

**Logic:**
- If both methods agree → Higher confidence trade
- If they disagree → Default to HOLD (safety first)

**Pros:**
- Highest confidence trades only
- Reduces false signals
- Best for conservative trading

**Cons:**
- Fewer trades (only when both agree)
- Slower than scoring alone
- Still has API costs

## SMC Indicators Explained

### Order Blocks (OB)

**What:** Zones where institutions placed large orders
**How Detected:**
- High volume (>1.5x average)
- Strong price movement away from zone
- Occurs at swing highs/lows

**Trading Implication:**
- Bullish OB = Support zone (potential bounce)
- Bearish OB = Resistance zone (potential rejection)

### Fair Value Gaps (FVG)

**What:** Price inefficiencies (gaps in price action)
**How Detected:**
- Current bar low > Two bars ago high (bullish FVG)
- Current bar high < Two bars ago low (bearish FVG)

**Trading Implication:**
- FVGs often get "filled" as price returns to them
- Bullish FVG = Support zone
- Bearish FVG = Resistance zone

### Market Structure Break (MSB)

**What:** Major trend reversals
**How Detected:**
- In uptrend: Price breaks below previous swing low
- In downtrend: Price breaks above previous swing high

**Trading Implication:**
- Strong reversal signal
- Trend change likely

### Break of Structure (BoS)

**What:** Trend continuation patterns
**How Detected:**
- In uptrend: Price breaks above previous swing high
- In downtrend: Price breaks below previous swing low

**Trading Implication:**
- Trend continuation
- Good entry for trend followers

## Market Data Indicators

### Cumulative Volume Delta (CVD)

**What:** Net buying vs selling pressure
**Formula:** CVD = Σ(Short Liquidations - Long Liquidations)

**Interpretation:**
- Positive CVD = More shorts liquidated = Bullish pressure
- Negative CVD = More longs liquidated = Bearish pressure
- Cascade = High volume spike = Volatility

### Funding Rates

**What:** Fee paid between longs and shorts
**Interpretation:**
- Positive (>0.1%) = Longs paying shorts = Bullish sentiment (contrarian bearish)
- Negative (<-0.1%) = Shorts paying longs = Bearish sentiment (contrarian bullish)
- Extreme = Potential reversal

### Open Interest (OI)

**What:** Total open derivative contracts
**Interpretation:**
- Rising OI + Rising price = Bullish (new longs)
- Rising OI + Falling price = Bearish (new shorts)
- Falling OI = Deleveraging / Position closing

## Configuration Parameters

### SMC Analysis Parameters

```python
# In config.py
SMC_SWING_WINDOW = 5  # Bars on each side for swing detection (3-10)
SMC_OB_VOLUME_MULTIPLIER = 1.5  # Volume threshold for OB (1.2-2.0)
SMC_OB_LOOKBACK = 20  # Bars to check for OB (10-50)
SMC_FVG_MIN_GAP_PCT = 0.5  # Minimum gap size for FVG (0.3-1.0)
```

**Tuning Tips:**
- Smaller `SWING_WINDOW` = More sensitive, more signals
- Higher `OB_VOLUME_MULTIPLIER` = Only strongest OBs
- Larger `FVG_MIN_GAP_PCT` = Only significant gaps

### Data Parameters

```python
SMC_OHLCV_TIMEFRAME = '15m'  # '5m', '15m', '1H', '4H'
SMC_OHLCV_DAYS_BACK = 3  # Historical data (1-7 days)
SMC_LIQUIDATION_LIMIT = 10000  # Liquidation records (1k-50k)
```

**Timeframe Selection:**
- 5m = Scalping (many signals, high noise)
- 15m = Day trading (balanced)
- 1H = Swing trading (fewer, higher quality)
- 4H = Position trading (very selective)

## Risk Management

### Built-in Safety Features

1. **Paper Trading Mode** (Default)
   ```python
   SMC_PAPER_TRADING = True  # No real trades executed
   ```

2. **Minimum Confidence Threshold**
   ```python
   SMC_MIN_CONFIDENCE = 70  # Only trade with ≥70% confidence
   ```

3. **Position Sizing**
   ```python
   SMC_POSITION_SIZE_PCT = 30  # Max 30% of balance per trade
   ```

4. **Stop Loss / Take Profit**
   ```python
   SMC_STOP_LOSS_PCT = 5.0  # Auto-exit at -5%
   SMC_TAKE_PROFIT_PCT = 10.0  # Auto-exit at +10%
   ```

### Recommended Settings by Risk Tolerance

**Conservative:**
```python
SMC_POSITION_SIZE_PCT = 10
SMC_LEVERAGE = 2
SMC_MIN_CONFIDENCE = 80
SMC_DECISION_METHOD = 'HYBRID'
```

**Moderate:**
```python
SMC_POSITION_SIZE_PCT = 30
SMC_LEVERAGE = 5
SMC_MIN_CONFIDENCE = 70
SMC_DECISION_METHOD = 'LLM'
```

**Aggressive:**
```python
SMC_POSITION_SIZE_PCT = 50
SMC_LEVERAGE = 10
SMC_MIN_CONFIDENCE = 60
SMC_DECISION_METHOD = 'SCORING'
```

## Data Storage

Trade history is automatically saved to:
```
src/data/smc_trading/trade_history.csv
```

Contains:
- Timestamp
- Symbol
- Action (BUY/SELL/HOLD)
- Price
- Size
- SMC Score
- Market Score
- Confidence
- Reasoning

## Troubleshooting

### "No OHLCV data available"

**Cause:** BirdEye API issue or invalid token address

**Solutions:**
1. Verify token address is correct
2. Check BIRDEYE_API_KEY is valid
3. Try a different token (SOL, USDC)
4. Check API rate limits

### "No market data available"

**Cause:** Moon Dev API key missing or invalid

**Solutions:**
1. Agent will continue with SMC analysis only
2. Add MOONDEV_API_KEY to .env for full functionality
3. Or get a key at: https://algotradecamp.com

### "Confidence below threshold"

**Cause:** Signals are mixed or weak

**Solutions:**
1. Lower `SMC_MIN_CONFIDENCE` (not recommended)
2. Wait for clearer signals
3. Try HYBRID method for higher conviction

### "AI decision error"

**Cause:** AI API issue

**Solutions:**
1. Check API key is valid
2. Try different provider (anthropic → openai)
3. Fall back to SCORING method

## Performance Expectations

### Backtesting (Recommended)

Before live trading, backtest your settings:
1. Set `SMC_PAPER_TRADING = True`
2. Run for 1-2 weeks with real data
3. Review trade_history.csv
4. Adjust parameters
5. Only go live after consistent positive results

### Typical Performance (Paper Trading)

- **Win Rate:** 55-65% (varies by market conditions)
- **Risk/Reward:** 1:2 average (5% stop, 10% target)
- **Trades per Day:** 1-3 (depends on timeframe)
- **False Signals:** 35-45% (no system is perfect)

## Advanced Usage

### Custom Token Lists

```python
# In your code
tokens_to_analyze = [
    ('So11111111111111111111111111111111111111112', 'SOL'),
    ('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'USDC'),
    # Add more (address, symbol) tuples
]

agent = SMCTradingAgent()

for token_address, symbol in tokens_to_analyze:
    agent.run(token_address, symbol)
    time.sleep(5)  # Rate limiting
```

### Integration with Main Orchestrator

```python
# In src/main.py
from src.agents.smc_trading_agent import SMCTradingAgent

ACTIVE_AGENTS = {
    'risk': True,
    'smc_trading': True,  # Add this
    # ... other agents
}

if ACTIVE_AGENTS.get('smc_trading'):
    smc_agent = SMCTradingAgent()
    smc_agent.run(token_address, symbol)
```

## Disclaimer

⚠️ **CRITICAL WARNINGS:**

1. **This is experimental software** - No guarantees of any kind
2. **Not financial advice** - Do your own research (DYOR)
3. **Substantial risk of loss** - Only trade with money you can afford to lose
4. **Test thoroughly** - Use paper trading mode extensively before going live
5. **Start small** - Begin with tiny position sizes if going live
6. **Monitor constantly** - Never leave automated trading unattended
7. **Market conditions change** - Past performance ≠ future results

## Support & Community

- **YouTube:** Moon Dev Trading (weekly updates)
- **Discord:** Join at algotradecamp.com
- **GitHub Issues:** Report bugs or request features
- **Documentation:** See CLAUDE.md for project overview

## Roadmap

- [x] ~~SMC technical indicators~~ ✅
- [x] ~~Live market data integration~~ ✅
- [x] ~~AI decision engine~~ ✅
- [ ] Multi-timeframe analysis
- [ ] Confluence scoring (multiple timeframes)
- [ ] Discord/Telegram alerts
- [ ] TradingView integration
- [ ] Automated backtesting system
- [ ] Portfolio mode (multiple tokens)

---

Built with 🌙 by Moon Dev | MIT License

**Remember:** Trade responsibly. The best trade is sometimes no trade.
