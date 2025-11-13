"""
🌙 Moon Dev's SMC Backtesting Strategy
Built with love by Moon Dev 🚀

This file implements the SMC trading strategy using the backtesting.py library
to match the existing RBI agent backtest format.

The strategy combines:
1. Smart Money Concepts (Order Blocks, FVG, MSB, BoS)
2. Market sentiment (when available)
3. Configurable parameters for optimization
"""

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.smc_analysis import (
    detect_swing_highs_lows,
    detect_order_blocks,
    detect_fair_value_gaps,
    detect_market_structure,
    calculate_smc_score
)


class SMCStrategy(Strategy):
    """
    Smart Money Concepts Trading Strategy for backtesting.py

    Parameters (can be optimized):
    - swing_window: Window for swing detection (3-10)
    - ob_volume_mult: Volume multiplier for order blocks (1.2-2.5)
    - ob_lookback: Lookback for order blocks (10-50)
    - fvg_min_gap: Minimum FVG gap percentage (0.3-1.5)
    - score_buy_threshold: SMC score to trigger buy (20-80)
    - score_sell_threshold: SMC score to trigger sell (-20 to -80)
    - stop_loss_pct: Stop loss percentage (1-10)
    - take_profit_pct: Take profit percentage (2-20)
    """

    # Default parameters (can be optimized)
    swing_window = 5
    ob_volume_mult = 1.5
    ob_lookback = 20
    fvg_min_gap = 0.5
    score_buy_threshold = 30
    score_sell_threshold = -30
    stop_loss_pct = 5.0
    take_profit_pct = 10.0

    def init(self):
        """Initialize indicators and SMC analysis"""
        # Convert data to lowercase columns
        df = pd.DataFrame({
            'open': self.data.Open,
            'high': self.data.High,
            'low': self.data.Low,
            'close': self.data.Close,
            'volume': self.data.Volume
        })

        # Run SMC analysis
        df = detect_swing_highs_lows(df, window=self.swing_window)
        df = detect_order_blocks(df,
                                  volume_multiplier=self.ob_volume_mult,
                                  lookback=self.ob_lookback)
        df = detect_fair_value_gaps(df, min_gap_pct=self.fvg_min_gap)
        df = detect_market_structure(df)

        # Calculate SMC scores for each bar
        scores = []
        for i in range(len(df)):
            if i < 20:  # Need minimum data
                scores.append(0)
                continue

            # Get recent window for scoring
            recent_df = df.iloc[max(0, i-20):i+1]

            # Count signals
            bullish_obs = len(recent_df[recent_df['ob_bullish'] == True])
            bearish_obs = len(recent_df[recent_df['ob_bearish'] == True])
            bullish_fvgs = len(recent_df[recent_df['fvg_bullish'] == True])
            bearish_fvgs = len(recent_df[recent_df['fvg_bearish'] == True])

            # Get recent structure breaks (last 5 bars)
            recent_structure = df.iloc[max(0, i-5):i+1]
            msb_bullish = len(recent_structure[recent_structure['msb_bullish'] == True])
            msb_bearish = len(recent_structure[recent_structure['msb_bearish'] == True])
            bos_bullish = len(recent_structure[recent_structure['bos_bullish'] == True])
            bos_bearish = len(recent_structure[recent_structure['bos_bearish'] == True])

            # Current trend
            current_trend = df.iloc[i]['trend']

            # Create summary dict
            summary = {
                'current_price': df.iloc[i]['close'],
                'current_trend': current_trend,
                'bullish_order_blocks': bullish_obs,
                'bearish_order_blocks': bearish_obs,
                'bullish_fvgs': bullish_fvgs,
                'bearish_fvgs': bearish_fvgs,
                'msb_bullish_recent': msb_bullish,
                'msb_bearish_recent': msb_bearish,
                'bos_bullish_recent': bos_bullish,
                'bos_bearish_recent': bos_bearish,
                'bullish_signals': bullish_obs + bullish_fvgs + bos_bullish,
                'bearish_signals': bearish_obs + bearish_fvgs + bos_bearish,
            }

            # Calculate score
            score_result = calculate_smc_score(summary)
            scores.append(score_result['score'])

        # Create indicator from scores
        self.smc_score = self.I(lambda: pd.Series(scores).values, name='SMC_Score')

        # Store entry price for stop loss / take profit
        self.entry_price = None

    def next(self):
        """Execute on each bar"""
        current_score = self.smc_score[-1]
        current_price = self.data.Close[-1]

        # Check if we have a position
        if self.position:
            # Manage existing position
            if self.entry_price:
                # Calculate P&L percentage
                pnl_pct = ((current_price - self.entry_price) / self.entry_price) * 100

                # Check stop loss
                if pnl_pct <= -self.stop_loss_pct:
                    self.position.close()
                    self.entry_price = None
                    return

                # Check take profit
                if pnl_pct >= self.take_profit_pct:
                    self.position.close()
                    self.entry_price = None
                    return

                # Check for reversal signal
                if current_score < self.score_sell_threshold:
                    self.position.close()
                    self.entry_price = None

        else:
            # Look for entry signals

            # Buy signal
            if current_score >= self.score_buy_threshold:
                self.buy()
                self.entry_price = current_price

            # Sell/short signal (if supported)
            # Note: backtesting.py supports shorts, but we'll keep it simple with long-only
            # Uncomment if you want to test shorts:
            # elif current_score <= self.score_sell_threshold:
            #     self.sell()
            #     self.entry_price = current_price


def load_and_prepare_data(csv_path: str) -> pd.DataFrame:
    """
    Load OHLCV data from CSV and prepare for backtesting.

    Args:
        csv_path: Path to CSV file with OHLCV data

    Returns:
        DataFrame ready for backtesting.py
    """
    # Load data
    df = pd.read_csv(csv_path)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Drop unnamed columns
    df = df.drop(columns=[col for col in df.columns if 'unnamed' in col.lower()], errors='ignore')

    # Ensure we have required columns
    required_cols = ['open', 'high', 'low', 'close', 'volume']

    # Try to map common column name variations
    col_mapping = {
        'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume',
        'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
    }

    for old_col, new_col in col_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})

    # Check if we have all required columns
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Capitalize for backtesting.py
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })

    # Parse timestamp if available
    timestamp_cols = ['timestamp', 'time', 'date', 'datetime']
    timestamp_col = None
    for col in timestamp_cols:
        if col in df.columns:
            timestamp_col = col
            break

    if timestamp_col:
        df['Date'] = pd.to_datetime(df[timestamp_col])
        df = df.set_index('Date')
    else:
        # Create a simple date range
        df['Date'] = pd.date_range(start='2024-01-01', periods=len(df), freq='15T')
        df = df.set_index('Date')

    # Keep only OHLCV columns
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

    # Convert to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop NaN rows
    df = df.dropna()

    # Sort by index
    df = df.sort_index()

    return df


def run_backtest(data: pd.DataFrame,
                 cash: float = 10000,
                 commission: float = 0.002,
                 **strategy_params) -> dict:
    """
    Run backtest with given data and parameters.

    Args:
        data: OHLCV DataFrame
        cash: Starting capital
        commission: Commission percentage (0.002 = 0.2%)
        **strategy_params: Strategy parameters to override defaults

    Returns:
        Dictionary with backtest results
    """

    # Create backtest
    bt = Backtest(
        data,
        SMCStrategy,
        cash=cash,
        commission=commission,
        exclusive_orders=True
    )

    # Run with custom parameters if provided
    if strategy_params:
        stats = bt.run(**strategy_params)
    else:
        stats = bt.run()

    # Convert stats to dict
    results = {
        'Start': str(stats['Start']),
        'End': str(stats['End']),
        'Duration': str(stats['Duration']),
        'Exposure Time [%]': float(stats['Exposure Time [%]']),
        'Equity Final [$]': float(stats['Equity Final [$]']),
        'Equity Peak [$]': float(stats['Equity Peak [$]']),
        'Return [%]': float(stats['Return [%]']),
        'Buy & Hold Return [%]': float(stats['Buy & Hold Return [%]']),
        'Return (Ann.) [%]': float(stats['Return (Ann.) [%]']),
        'Volatility (Ann.) [%]': float(stats['Volatility (Ann.) [%]']),
        'Sharpe Ratio': float(stats['Sharpe Ratio']) if not pd.isna(stats['Sharpe Ratio']) else 0,
        'Sortino Ratio': float(stats['Sortino Ratio']) if not pd.isna(stats['Sortino Ratio']) else 0,
        'Calmar Ratio': float(stats['Calmar Ratio']) if not pd.isna(stats['Calmar Ratio']) else 0,
        'Max. Drawdown [%]': float(stats['Max. Drawdown [%]']),
        'Avg. Drawdown [%]': float(stats['Avg. Drawdown [%]']),
        'Max. Drawdown Duration': str(stats['Max. Drawdown Duration']),
        'Avg. Drawdown Duration': str(stats['Avg. Drawdown Duration']),
        '# Trades': int(stats['# Trades']),
        'Win Rate [%]': float(stats['Win Rate [%]']),
        'Best Trade [%]': float(stats['Best Trade [%]']),
        'Worst Trade [%]': float(stats['Worst Trade [%]']),
        'Avg. Trade [%]': float(stats['Avg. Trade [%]']),
        'Max. Trade Duration': str(stats['Max. Trade Duration']),
        'Avg. Trade Duration': str(stats['Avg. Trade Duration']),
        'Profit Factor': float(stats['Profit Factor']) if not pd.isna(stats['Profit Factor']) else 0,
        'Expectancy [%]': float(stats['Expectancy [%]']),
        'SQN': float(stats['SQN']) if not pd.isna(stats['SQN']) else 0,
    }

    # Add strategy parameters used
    results['parameters'] = strategy_params if strategy_params else {
        'swing_window': 5,
        'ob_volume_mult': 1.5,
        'ob_lookback': 20,
        'fvg_min_gap': 0.5,
        'score_buy_threshold': 30,
        'score_sell_threshold': -30,
        'stop_loss_pct': 5.0,
        'take_profit_pct': 10.0
    }

    return results, bt


def main():
    """Example usage"""
    print("🌙 Moon Dev's SMC Backtesting Strategy")
    print("=" * 70)

    # Example: Load sample data
    # You would replace this with your actual data path
    sample_data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"

    try:
        print(f"\n📊 Loading data from: {sample_data_path}")
        data = load_and_prepare_data(sample_data_path)
        print(f"✅ Loaded {len(data)} bars")
        print(f"📅 Date range: {data.index[0]} to {data.index[-1]}")

        print("\n🚀 Running backtest...")
        results, bt = run_backtest(data, cash=10000, commission=0.002)

        print("\n📈 BACKTEST RESULTS:")
        print("=" * 70)
        for key, value in results.items():
            if key != 'parameters':
                print(f"{key}: {value}")

        print("\n⚙️ PARAMETERS USED:")
        for key, value in results['parameters'].items():
            print(f"  {key}: {value}")

        # Show equity curve plot (optional)
        # bt.plot()

        print("\n✅ Backtest complete!")

    except FileNotFoundError:
        print(f"\n⚠️ Sample data file not found: {sample_data_path}")
        print("💡 Please update the path to your OHLCV data")
        print("\nTo use this strategy:")
        print("1. Prepare OHLCV CSV data with columns: open, high, low, close, volume")
        print("2. Call load_and_prepare_data(your_csv_path)")
        print("3. Call run_backtest(data)")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
