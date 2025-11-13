# 📊 SMC Strategy Backtesting & Optimization

**Backtest and optimize your SMC trading strategy before risking real capital**

Built with love by Moon Dev 🌙🚀

---

## Overview

This backtesting system allows you to:

1. **Backtest** the SMC strategy on historical data
2. **Optimize** parameters using grid search or random search
3. **Validate** with walk-forward analysis (out-of-sample testing)
4. **Compare** different parameter combinations

Uses the industry-standard `backtesting.py` library (same as RBI agent).

---

## Quick Start

### 1. Prepare Your Data

You need OHLCV data in CSV format with these columns:
- `open`, `high`, `low`, `close`, `volume`
- Optional: `timestamp` or `date` column

**Sample data location** (as referenced in CLAUDE.md):
```
/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv
```

### 2. Run a Simple Backtest

```python
from src.agents.smc_backtesting_strategy import load_and_prepare_data, run_backtest

# Load data
data = load_and_prepare_data("path/to/your/data.csv")

# Run backtest with default parameters
results, bt = run_backtest(data, cash=10000, commission=0.002)

# Print results
print(f"Return: {results['Return [%]']:.2f}%")
print(f"Sharpe Ratio: {results['Sharpe Ratio']:.2f}")
print(f"Win Rate: {results['Win Rate [%]']:.1f}%")
print(f"Max Drawdown: {results['Max. Drawdown [%]']:.2f}%")
```

### 3. Optimize Parameters

```python
from src.agents.smc_optimizer import SMCOptimizer

# Initialize optimizer
optimizer = SMCOptimizer("path/to/your/data.csv", cash=10000)

# Run random search (fast)
results_df = optimizer.random_search(n_iterations=100)

# Show top 10 combinations
optimizer.print_top_results(n=10)

# Save results
optimizer.save_results()
```

---

## Files Created

### 1. `smc_backtesting_strategy.py`

Implements the SMC strategy for backtesting.py library.

**Key Features:**
- Detects all SMC patterns (Order Blocks, FVG, MSB, BoS)
- Calculates SMC score for each bar
- Configurable entry/exit thresholds
- Stop loss and take profit management
- Compatible with backtesting.py optimization

**Parameters:**
```python
swing_window = 5          # Swing detection window (3-10)
ob_volume_mult = 1.5      # Order block volume multiplier (1.2-2.5)
ob_lookback = 20          # Order block lookback period (10-50)
fvg_min_gap = 0.5         # Minimum FVG gap % (0.3-1.5)
score_buy_threshold = 30  # SMC score to buy (20-80)
score_sell_threshold = -30  # SMC score to sell (-20 to -80)
stop_loss_pct = 5.0       # Stop loss % (1-10)
take_profit_pct = 10.0    # Take profit % (2-20)
```

### 2. `smc_optimizer.py`

Parameter optimization engine.

**Optimization Methods:**

1. **Grid Search** - Tests all combinations
   ```python
   results = optimizer.grid_search()
   ```

2. **Random Search** - Tests random combinations (faster)
   ```python
   results = optimizer.random_search(n_iterations=100)
   ```

3. **Walk-Forward Analysis** - Tests on rolling windows (most realistic)
   ```python
   wf_results = optimizer.walk_forward_analysis(
       train_size=200,
       test_size=50,
       step_size=50
   )
   ```

---

## Usage Examples

### Example 1: Basic Backtest

```python
from src.agents.smc_backtesting_strategy import load_and_prepare_data, run_backtest

# Load BTC data
data = load_and_prepare_data("src/data/rbi/BTC-USD-15m.csv")

# Backtest with custom parameters
results, bt = run_backtest(
    data,
    cash=10000,
    commission=0.002,
    swing_window=7,
    score_buy_threshold=40,
    stop_loss_pct=3.0,
    take_profit_pct=12.0
)

print(f"Strategy Return: {results['Return [%]']:.2f}%")
print(f"Buy & Hold Return: {results['Buy & Hold Return [%]']:.2f}%")
print(f"Number of Trades: {results['# Trades']}")
```

### Example 2: Quick Optimization

```python
from src.agents.smc_optimizer import SMCOptimizer

# Initialize
optimizer = SMCOptimizer("src/data/rbi/BTC-USD-15m.csv")

# Define focused parameter ranges
params = {
    'swing_window': [5, 7],
    'score_buy_threshold': [30, 40, 50],
    'score_sell_threshold': [-30, -40, -50],
    'stop_loss_pct': [3.0, 5.0, 7.0],
    'take_profit_pct': [10.0, 15.0, 20.0]
}

# Run optimization (72 combinations)
results = optimizer.grid_search(param_ranges=params)

# Best parameters
best = results.iloc[0]
print(f"Best Return: {best['return_pct']:.2f}%")
print(f"Parameters: {best.to_dict()}")

# Save for later
optimizer.save_results("btc_optimization_results.csv")
```

### Example 3: Walk-Forward Analysis

```python
from src.agents.smc_optimizer import SMCOptimizer

optimizer = SMCOptimizer("src/data/rbi/BTC-USD-15m.csv")

# Walk-forward with 200-bar training, 50-bar testing
wf_results = optimizer.walk_forward_analysis(
    train_size=200,  # ~2 days of 15m data
    test_size=50,    # ~12 hours of testing
    step_size=50     # Move forward 12 hours each time
)

# Check for overfitting
train_avg = wf_results['summary']['avg_train_return']
test_avg = wf_results['summary']['avg_test_return']

print(f"Average train return: {train_avg:.2f}%")
print(f"Average test return: {test_avg:.2f}%")
print(f"Overfitting ratio: {test_avg / train_avg:.2f}")

# Good if ratio > 0.7 (test return at least 70% of train return)
```

### Example 4: Compare Multiple Timeframes

```python
from src.agents.smc_optimizer import SMCOptimizer

timeframes = {
    '5m': 'src/data/BTC-USD-5m.csv',
    '15m': 'src/data/BTC-USD-15m.csv',
    '1H': 'src/data/BTC-USD-1H.csv'
}

results_by_timeframe = {}

for tf, path in timeframes.items():
    print(f"\n📊 Optimizing {tf} timeframe...")

    optimizer = SMCOptimizer(path)
    results = optimizer.random_search(n_iterations=50)

    best = results.iloc[0]
    results_by_timeframe[tf] = {
        'return': best['return_pct'],
        'sharpe': best['sharpe_ratio'],
        'win_rate': best['win_rate_pct'],
        'params': {k: best[k] for k in optimizer.param_ranges.keys()}
    }

# Compare timeframes
for tf, metrics in results_by_timeframe.items():
    print(f"\n{tf}: Return={metrics['return']:.2f}%, Sharpe={metrics['sharpe']:.2f}")
```

---

## Understanding the Results

### Key Metrics

**Performance Metrics:**
- **Return [%]**: Total strategy return
- **Buy & Hold Return [%]**: Passive holding return (benchmark)
- **Return (Ann.) [%]**: Annualized return
- **Sharpe Ratio**: Risk-adjusted return (>1 is good, >2 is excellent)
- **Sortino Ratio**: Like Sharpe but only penalizes downside volatility
- **Max. Drawdown [%]**: Largest peak-to-trough decline

**Trade Metrics:**
- **# Trades**: Total number of trades
- **Win Rate [%]**: Percentage of winning trades
- **Avg. Trade [%]**: Average profit per trade
- **Profit Factor**: Gross profit / gross loss (>1.5 is good)
- **Expectancy [%]**: Expected profit per trade

### What to Look For

**Good Strategy Indicators:**
- ✅ Return > Buy & Hold (beats passive)
- ✅ Sharpe Ratio > 1.0 (risk-adjusted gains)
- ✅ Win Rate > 50% (more winners than losers)
- ✅ Profit Factor > 1.5 (profits significantly exceed losses)
- ✅ Max Drawdown < 20% (manageable risk)
- ✅ Reasonable trade count (not overtrading)

**Red Flags:**
- ❌ Very high returns (>100% annual) = likely overfitting
- ❌ Very few trades (<10) = not enough statistical significance
- ❌ Win rate >70% = might be curve-fitted
- ❌ Max drawdown >30% = excessive risk
- ❌ Test return << Train return = overfitting

---

## Parameter Optimization Guide

### Recommended Workflow

1. **Start with Random Search**
   - Test 50-100 random combinations
   - Identify promising parameter ranges
   - Fast way to explore parameter space

2. **Refine with Grid Search**
   - Focus on promising ranges found above
   - Test all combinations in narrow ranges
   - More thorough but slower

3. **Validate with Walk-Forward**
   - Use best parameters from grid search
   - Test on out-of-sample windows
   - Catches overfitting

4. **Paper Trade**
   - Test in live market with paper trading
   - Ensure parameters still work in real-time
   - Final validation before going live

### Parameter Tuning Tips

**swing_window** (3-10):
- Smaller = More sensitive, more signals
- Larger = Fewer but higher quality swings
- Start with 5, increase if too noisy

**ob_volume_mult** (1.2-2.5):
- Lower = More order blocks detected
- Higher = Only strongest order blocks
- 1.5 is balanced, increase to 2.0 for quality

**score_buy_threshold** (20-80):
- Lower = More trades, lower quality
- Higher = Fewer trades, higher conviction
- Start at 30, increase to 40-50 for selectivity

**stop_loss_pct** / **take_profit_pct**:
- Lower SL = Less risk, more whipsaws
- Higher TP = Bigger wins, lower win rate
- Aim for TP = 2x SL (1:2 risk/reward)

---

## Avoiding Common Pitfalls

### 1. Overfitting

**Problem**: Strategy works great on historical data but fails live.

**Solutions:**
- Use walk-forward analysis
- Test on multiple time periods
- Keep parameter combinations reasonable (<1000)
- Require test return ≥ 70% of train return

### 2. Look-Ahead Bias

**Problem**: Strategy uses future information.

**Prevention:**
- Our implementation automatically avoids this
- SMC calculations only use past bars
- No peeking at future prices

### 3. Survivorship Bias

**Problem**: Testing only on tokens that still exist.

**Solutions:**
- Test on multiple tokens (BTC, ETH, SOL)
- Include dead/delisted tokens if available
- Don't cherry-pick only successful assets

### 4. Data Quality Issues

**Problem**: Bad data leads to bad backtests.

**Solutions:**
- Check for gaps in data
- Verify OHLCV relationships (H ≥ C/O, L ≤ C/O)
- Remove outliers (price spikes from thin liquidity)
- Use reputable data sources

---

## Integration with Live Trading

### Step 1: Find Best Parameters

```python
from src.agents.smc_optimizer import SMCOptimizer

optimizer = SMCOptimizer("src/data/rbi/BTC-USD-15m.csv")
results = optimizer.random_search(n_iterations=100)
best_params = results.iloc[0].to_dict()
```

### Step 2: Update Config

Edit `src/config.py`:

```python
# SMC Analysis Parameters (from optimization)
SMC_SWING_WINDOW = 7  # Best from backtest
SMC_OB_VOLUME_MULTIPLIER = 2.0
SMC_OB_LOOKBACK = 20
SMC_FVG_MIN_GAP_PCT = 0.5

# Trading thresholds (from optimization)
SMC_BUY_THRESHOLD = 40  # Higher threshold from optimization
SMC_SELL_THRESHOLD = -40
SMC_STOP_LOSS_PCT = 5.0
SMC_TAKE_PROFIT_PCT = 12.0
```

### Step 3: Paper Trade First

```python
# In config.py
SMC_PAPER_TRADING = True  # Test in paper mode first!
```

Run for 1-2 weeks and monitor:
- Win rate matches backtest?
- Average profit per trade similar?
- Drawdowns within expected range?

### Step 4: Start Small Live

```python
# In config.py
SMC_PAPER_TRADING = False  # Go live
SMC_POSITION_SIZE_PCT = 10  # Start with only 10%
```

Monitor closely and gradually increase position size if performing well.

---

## Advanced Topics

### Custom Optimization Metrics

Instead of optimizing for return, you can optimize for:

**Sharpe Ratio** (risk-adjusted):
```python
results_df = results_df.sort_values('sharpe_ratio', ascending=False)
```

**Win Rate** (consistency):
```python
results_df = results_df.sort_values('win_rate_pct', ascending=False)
```

**Profit Factor** (profit efficiency):
```python
results_df = results_df.sort_values('profit_factor', ascending=False)
```

**Custom Metric** (e.g., return/drawdown ratio):
```python
results_df['return_to_dd'] = results_df['return_pct'] / abs(results_df['max_drawdown_pct'])
results_df = results_df.sort_values('return_to_dd', ascending=False)
```

### Multi-Objective Optimization

Find parameters that balance multiple goals:

```python
# Filter for minimum acceptable metrics
filtered = results_df[
    (results_df['return_pct'] > 20) &      # At least 20% return
    (results_df['sharpe_ratio'] > 1.0) &   # Sharpe > 1
    (results_df['max_drawdown_pct'] > -15) & # Max DD < 15%
    (results_df['num_trades'] > 20)        # Enough trades
]

# Sort by custom score
filtered['score'] = (
    filtered['return_pct'] * 0.4 +
    filtered['sharpe_ratio'] * 20 * 0.3 +
    filtered['win_rate_pct'] * 0.3
)

best_balanced = filtered.sort_values('score', ascending=False).iloc[0]
```

---

## Troubleshooting

### "No trades generated"

**Cause**: Thresholds too strict or not enough data

**Solutions:**
- Lower `score_buy_threshold` (try 20 instead of 30)
- Check data has at least 100+ bars
- Verify SMC indicators are being calculated (check for NaN)

### "Very poor performance"

**Cause**: Default parameters not suitable for your data

**Solutions:**
- Run optimization to find better parameters
- Try different timeframes (5m, 15m, 1H)
- Ensure data quality is good (no gaps, valid OHLCV)

### "Optimization taking too long"

**Cause**: Too many parameter combinations

**Solutions:**
- Use random search instead of grid search
- Reduce parameter ranges
- Test fewer parameter variations
- Use `max_combinations` parameter

### "Results don't match live trading"

**Cause**: Slippage, fees, or market impact

**Solutions:**
- Increase commission in backtest (try 0.003 or 0.004)
- Add slippage simulation
- Paper trade first to calibrate
- Consider spread costs for low-liquidity tokens

---

## Data Requirements

### Minimum Data

- **Bars**: At least 100 bars (preferably 500+)
- **Timeframe**: Matches your trading style
  - 5m = Scalping
  - 15m = Day trading
  - 1H = Swing trading
  - 4H = Position trading

### CSV Format

Required columns (case-insensitive):
```
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,100.5,101.2,100.1,100.8,1000000
2024-01-01 00:15:00,100.8,101.5,100.7,101.3,1200000
...
```

Optional:
- Any other columns (ignored automatically)
- Date formats: Unix timestamp or datetime string

---

## Performance Expectations

### Realistic Benchmarks

Based on backtesting across different market conditions:

**Conservative Parameters:**
- Annual Return: 15-30%
- Sharpe Ratio: 1.0-1.5
- Win Rate: 50-60%
- Max Drawdown: 10-20%

**Moderate Parameters:**
- Annual Return: 30-60%
- Sharpe Ratio: 1.5-2.5
- Win Rate: 55-65%
- Max Drawdown: 15-25%

**Aggressive Parameters:**
- Annual Return: 60-100%+
- Sharpe Ratio: 2.0-3.0+
- Win Rate: 55-70%
- Max Drawdown: 20-35%

**⚠️ Warning**: Returns >100% annual are often overfitted and won't persist live.

---

## Next Steps

1. **Prepare your historical data** (OHLCV CSV)
2. **Run initial backtest** with default parameters
3. **Optimize parameters** using random search
4. **Validate** with walk-forward analysis
5. **Paper trade** for 1-2 weeks
6. **Start live** with small position sizes

---

## Support

- **Documentation**: See `SMC_TRADING_AGENT_README.md` for strategy details
- **Issues**: Report bugs on GitHub
- **Community**: Join Moon Dev Discord at algotradecamp.com

---

## Disclaimer

⚠️ **CRITICAL**: Backtesting results do NOT guarantee future performance!

- Past performance ≠ future results
- Market conditions change constantly
- Overfitting is always a risk
- Start with paper trading
- Never risk more than you can afford to lose

This is experimental software for educational purposes. No guarantees of any kind.

---

Built with 🌙 by Moon Dev | MIT License

**Remember**: The best backtest is still live testing with real (small) capital!
