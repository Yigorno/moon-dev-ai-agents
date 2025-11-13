"""
🌙 Moon Dev's SMC Parameter Optimizer
Built with love by Moon Dev 🚀

This module optimizes SMC strategy parameters using grid search or random search.
Finds the best combination of parameters for your historical data.

Optimization methods:
1. Grid Search - Tests all combinations (thorough but slow)
2. Random Search - Tests random combinations (faster, good coverage)
3. Walk-Forward - Tests on rolling windows (more realistic)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from itertools import product
import sys

sys.path.append(str(Path(__file__).parent.parent))

from src.agents.smc_backtesting_strategy import load_and_prepare_data, run_backtest


class SMCOptimizer:
    """SMC Strategy Parameter Optimizer"""

    def __init__(self, data_path: str, cash: float = 10000, commission: float = 0.002):
        """
        Initialize optimizer with data.

        Args:
            data_path: Path to OHLCV CSV file
            cash: Starting capital
            commission: Commission percentage
        """
        print("🌙 Moon Dev's SMC Optimizer Initializing...")
        print(f"📂 Data: {data_path}")

        self.data = load_and_prepare_data(data_path)
        self.cash = cash
        self.commission = commission

        print(f"✅ Loaded {len(self.data)} bars")
        print(f"📅 Range: {self.data.index[0]} to {self.data.index[-1]}")

        # Results storage
        self.results = []

        # Default parameter ranges for optimization
        self.param_ranges = {
            'swing_window': [3, 5, 7],
            'ob_volume_mult': [1.2, 1.5, 2.0],
            'ob_lookback': [10, 20, 30],
            'fvg_min_gap': [0.3, 0.5, 0.8],
            'score_buy_threshold': [20, 30, 40, 50],
            'score_sell_threshold': [-20, -30, -40, -50],
            'stop_loss_pct': [3.0, 5.0, 7.0],
            'take_profit_pct': [8.0, 10.0, 15.0]
        }

    def grid_search(self, param_ranges: dict = None, max_combinations: int = None) -> pd.DataFrame:
        """
        Perform grid search over parameter combinations.

        Args:
            param_ranges: Dict of parameter ranges to test
                         If None, uses default ranges
            max_combinations: Maximum number of combinations to test
                            If None, tests all combinations

        Returns:
            DataFrame with results sorted by performance
        """
        if param_ranges is None:
            param_ranges = self.param_ranges

        print(f"\n🔍 Starting Grid Search Optimization")
        print("=" * 70)
        print(f"Parameters to optimize:")
        for param, values in param_ranges.items():
            print(f"  {param}: {values}")

        # Calculate total combinations
        total_combinations = np.prod([len(v) for v in param_ranges.values()])
        print(f"\n📊 Total combinations: {total_combinations}")

        if max_combinations and total_combinations > max_combinations:
            print(f"⚠️ Limiting to {max_combinations} random combinations")
            return self.random_search(param_ranges, n_iterations=max_combinations)

        # Generate all combinations
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        combinations = list(product(*param_values))

        print(f"🚀 Testing {len(combinations)} combinations...\n")

        results = []
        for i, combo in enumerate(combinations, 1):
            params = dict(zip(param_names, combo))

            try:
                # Run backtest
                result, _ = run_backtest(
                    self.data,
                    cash=self.cash,
                    commission=self.commission,
                    **params
                )

                # Store results
                result_row = params.copy()
                result_row['return_pct'] = result['Return [%]']
                result_row['sharpe_ratio'] = result['Sharpe Ratio']
                result_row['max_drawdown_pct'] = result['Max. Drawdown [%]']
                result_row['win_rate_pct'] = result['Win Rate [%]']
                result_row['num_trades'] = result['# Trades']
                result_row['profit_factor'] = result['Profit Factor']

                results.append(result_row)

                # Progress update
                if i % 10 == 0 or i == len(combinations):
                    print(f"Progress: {i}/{len(combinations)} ({i/len(combinations)*100:.1f}%) | "
                          f"Best Return: {max([r['return_pct'] for r in results]):.2f}%")

            except Exception as e:
                print(f"⚠️ Error testing combo {i}: {str(e)}")
                continue

        # Convert to DataFrame
        results_df = pd.DataFrame(results)

        # Sort by return (or custom metric)
        results_df = results_df.sort_values('return_pct', ascending=False)

        self.results = results_df

        print(f"\n✅ Grid search complete!")
        print(f"📊 Tested {len(results_df)} combinations successfully")

        return results_df

    def random_search(self, param_ranges: dict = None, n_iterations: int = 100) -> pd.DataFrame:
        """
        Perform random search over parameter space.

        Args:
            param_ranges: Dict of parameter ranges
            n_iterations: Number of random combinations to test

        Returns:
            DataFrame with results
        """
        if param_ranges is None:
            param_ranges = self.param_ranges

        print(f"\n🎲 Starting Random Search Optimization")
        print("=" * 70)
        print(f"Testing {n_iterations} random combinations")

        results = []
        for i in range(n_iterations):
            # Generate random parameters
            params = {}
            for param, values in param_ranges.items():
                params[param] = np.random.choice(values)

            try:
                # Run backtest
                result, _ = run_backtest(
                    self.data,
                    cash=self.cash,
                    commission=self.commission,
                    **params
                )

                # Store results
                result_row = params.copy()
                result_row['return_pct'] = result['Return [%]']
                result_row['sharpe_ratio'] = result['Sharpe Ratio']
                result_row['max_drawdown_pct'] = result['Max. Drawdown [%]']
                result_row['win_rate_pct'] = result['Win Rate [%]']
                result_row['num_trades'] = result['# Trades']
                result_row['profit_factor'] = result['Profit Factor']

                results.append(result_row)

                # Progress update
                if (i + 1) % 10 == 0 or (i + 1) == n_iterations:
                    print(f"Progress: {i+1}/{n_iterations} ({(i+1)/n_iterations*100:.1f}%) | "
                          f"Best Return: {max([r['return_pct'] for r in results]):.2f}%")

            except Exception as e:
                print(f"⚠️ Error testing iteration {i+1}: {str(e)}")
                continue

        # Convert to DataFrame
        results_df = pd.DataFrame(results)

        # Sort by return
        results_df = results_df.sort_values('return_pct', ascending=False)

        self.results = results_df

        print(f"\n✅ Random search complete!")
        print(f"📊 Tested {len(results_df)} combinations successfully")

        return results_df

    def walk_forward_analysis(self,
                               train_size: int = 200,
                               test_size: int = 50,
                               step_size: int = 50,
                               param_ranges: dict = None) -> dict:
        """
        Perform walk-forward analysis (more realistic performance estimation).

        Args:
            train_size: Number of bars for training/optimization
            test_size: Number of bars for testing
            step_size: Number of bars to step forward
            param_ranges: Parameter ranges to optimize

        Returns:
            Dictionary with walk-forward results
        """
        if param_ranges is None:
            param_ranges = self.param_ranges

        print(f"\n🚶 Starting Walk-Forward Analysis")
        print("=" * 70)
        print(f"Train size: {train_size} bars")
        print(f"Test size: {test_size} bars")
        print(f"Step size: {step_size} bars")

        total_bars = len(self.data)
        walk_results = []

        current_pos = 0
        window_num = 1

        while current_pos + train_size + test_size <= total_bars:
            print(f"\n📊 Window {window_num}")
            print(f"Train: {current_pos} to {current_pos + train_size}")
            print(f"Test: {current_pos + train_size} to {current_pos + train_size + test_size}")

            # Split data
            train_data = self.data.iloc[current_pos:current_pos + train_size]
            test_data = self.data.iloc[current_pos + train_size:current_pos + train_size + test_size]

            # Optimize on training data (use small random search)
            print("🔧 Optimizing on training data...")

            best_params = None
            best_train_return = -np.inf

            # Quick optimization (20 random iterations)
            for _ in range(20):
                params = {k: np.random.choice(v) for k, v in param_ranges.items()}

                try:
                    result, _ = run_backtest(train_data, cash=self.cash, commission=self.commission, **params)
                    train_return = result['Return [%]']

                    if train_return > best_train_return:
                        best_train_return = train_return
                        best_params = params
                except:
                    continue

            if best_params is None:
                print("⚠️ Optimization failed for this window")
                current_pos += step_size
                window_num += 1
                continue

            print(f"✅ Best train return: {best_train_return:.2f}%")

            # Test on out-of-sample data
            print("📈 Testing on out-of-sample data...")
            try:
                test_result, _ = run_backtest(test_data, cash=self.cash, commission=self.commission, **best_params)
                test_return = test_result['Return [%]']

                print(f"✅ Test return: {test_return:.2f}%")

                walk_results.append({
                    'window': window_num,
                    'train_return': best_train_return,
                    'test_return': test_return,
                    'params': best_params,
                    'train_start': current_pos,
                    'train_end': current_pos + train_size,
                    'test_start': current_pos + train_size,
                    'test_end': current_pos + train_size + test_size
                })

            except Exception as e:
                print(f"⚠️ Test failed: {str(e)}")

            current_pos += step_size
            window_num += 1

        # Calculate summary statistics
        if walk_results:
            avg_train_return = np.mean([r['train_return'] for r in walk_results])
            avg_test_return = np.mean([r['test_return'] for r in walk_results])

            print(f"\n📊 Walk-Forward Summary:")
            print(f"Windows tested: {len(walk_results)}")
            print(f"Avg train return: {avg_train_return:.2f}%")
            print(f"Avg test return: {avg_test_return:.2f}%")
            print(f"Overfitting ratio: {avg_test_return / avg_train_return:.2f}")

        return {
            'windows': walk_results,
            'summary': {
                'num_windows': len(walk_results),
                'avg_train_return': avg_train_return if walk_results else 0,
                'avg_test_return': avg_test_return if walk_results else 0
            }
        }

    def save_results(self, filename: str = None):
        """Save optimization results to CSV"""
        if self.results is None or len(self.results) == 0:
            print("⚠️ No results to save")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"smc_optimization_{timestamp}.csv"

        # Create results directory
        results_dir = Path(__file__).parent.parent / "data" / "smc_trading" / "optimization"
        results_dir.mkdir(parents=True, exist_ok=True)

        filepath = results_dir / filename

        self.results.to_csv(filepath, index=False)

        print(f"\n💾 Results saved to: {filepath}")

        return filepath

    def print_top_results(self, n: int = 10):
        """Print top N parameter combinations"""
        if self.results is None or len(self.results) == 0:
            print("⚠️ No results available")
            return

        print(f"\n🏆 Top {n} Parameter Combinations:")
        print("=" * 70)

        for i, row in self.results.head(n).iterrows():
            print(f"\n#{list(self.results.index).index(i) + 1}")
            print(f"Return: {row['return_pct']:.2f}% | Sharpe: {row['sharpe_ratio']:.2f} | "
                  f"Win Rate: {row['win_rate_pct']:.1f}%")
            print(f"Max DD: {row['max_drawdown_pct']:.2f}% | Trades: {row['num_trades']}")
            print("Parameters:")
            for param in self.param_ranges.keys():
                print(f"  {param}: {row[param]}")


def main():
    """Example usage"""
    print("🌙 Moon Dev's SMC Optimizer")
    print("=" * 70)

    # Example data path - update this
    data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"

    try:
        # Initialize optimizer
        optimizer = SMCOptimizer(data_path, cash=10000, commission=0.002)

        # Define smaller param ranges for quick testing
        quick_ranges = {
            'swing_window': [5, 7],
            'ob_volume_mult': [1.5, 2.0],
            'ob_lookback': [20],
            'fvg_min_gap': [0.5],
            'score_buy_threshold': [30, 40],
            'score_sell_threshold': [-30, -40],
            'stop_loss_pct': [5.0],
            'take_profit_pct': [10.0]
        }

        # Run random search (faster for demo)
        print("\n🎲 Running Random Search (50 iterations)...")
        results = optimizer.random_search(param_ranges=quick_ranges, n_iterations=50)

        # Show top results
        optimizer.print_top_results(n=5)

        # Save results
        optimizer.save_results()

        print("\n✅ Optimization complete!")
        print("\n💡 Next steps:")
        print("1. Review top parameter combinations")
        print("2. Consider walk-forward analysis for robustness")
        print("3. Test best parameters on out-of-sample data")
        print("4. Update config.py with optimized parameters")

    except FileNotFoundError:
        print(f"\n⚠️ Data file not found: {data_path}")
        print("💡 Update the data_path variable with your OHLCV data")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
