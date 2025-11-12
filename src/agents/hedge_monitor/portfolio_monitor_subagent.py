"""
🌙 Moon Dev's Portfolio Monitor Subagent
Part of the Hedge Monitor System
Built with love by Moon Dev 🚀

Tracks user's crypto portfolio positions and calculates exposure metrics.
"""

import os
import pandas as pd
import time
from datetime import datetime, timedelta
from termcolor import colored, cprint
from dotenv import load_dotenv
from pathlib import Path
import sys
import traceback

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src import config
from src import nice_funcs as n
from src.agents.base_agent import BaseAgent

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class PortfolioMonitorSubagent(BaseAgent):
    """Portfolio Monitor - Tracks user's crypto holdings and exposure"""

    def __init__(self, wallet_address=None):
        """Initialize Portfolio Monitor Subagent"""
        super().__init__('portfolio_monitor')

        load_dotenv()

        # Use provided wallet address or fall back to config
        self.wallet_address = wallet_address or config.address

        # Create data directory for this subagent
        self.data_dir = PROJECT_ROOT / "src" / "data" / "hedge_monitor" / "portfolio"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # History file
        self.history_file = self.data_dir / "portfolio_history.csv"
        self.load_history()

        cprint("💼 Portfolio Monitor Subagent initialized!", "white", "on_blue")
        print(f"📍 Monitoring wallet: {self.wallet_address[:8]}...{self.wallet_address[-8:]}")

    def load_history(self):
        """Load or initialize portfolio history"""
        try:
            if self.history_file.exists():
                self.history = pd.read_csv(self.history_file)
                print(f"📊 Loaded {len(self.history)} historical portfolio records")
            else:
                self.history = pd.DataFrame(columns=[
                    'timestamp', 'total_value_usd', 'num_positions',
                    'largest_position_pct', 'top_asset', 'concentration_risk'
                ])
                print("📝 Created new portfolio history file")

        except Exception as e:
            print(f"❌ Error loading history: {str(e)}")
            self.history = pd.DataFrame()

    def get_portfolio_snapshot(self):
        """Get current portfolio snapshot with exposure metrics"""
        try:
            print("\n🔍 Fetching current portfolio holdings...")

            # Get all holdings using nice_funcs
            holdings = n.fetch_wallet_holdings_og(self.wallet_address)

            if holdings is None or holdings.empty:
                print("⚠️ No holdings found")
                return None

            # Filter out excluded tokens (USDC, SOL if configured)
            if hasattr(config, 'EXCLUDED_TOKENS'):
                holdings = holdings[~holdings['Mint Address'].isin(config.EXCLUDED_TOKENS)]

            # Calculate total portfolio value
            total_value = holdings['USD Value'].sum()

            # Calculate position metrics
            num_positions = len(holdings[holdings['USD Value'] > 0])

            if num_positions > 0:
                # Find largest position
                largest_position = holdings.loc[holdings['USD Value'].idxmax()]
                largest_pct = (largest_position['USD Value'] / total_value) * 100
                top_asset = largest_position['Mint Address']

                # Calculate concentration risk (Herfindahl index)
                # Higher number = more concentrated (0-1 scale, 1 = all in one asset)
                position_pcts = holdings['USD Value'] / total_value
                concentration_risk = (position_pcts ** 2).sum()

            else:
                largest_pct = 0
                top_asset = "None"
                concentration_risk = 0

            # Get USDC balance
            usdc_balance = 0
            try:
                usdc_balance = n.get_token_balance_usd(config.USDC_ADDRESS)
            except:
                pass

            snapshot = {
                'timestamp': datetime.now(),
                'total_value_usd': total_value,
                'usdc_balance': usdc_balance,
                'num_positions': num_positions,
                'largest_position_pct': largest_pct,
                'top_asset': top_asset,
                'concentration_risk': concentration_risk,
                'holdings': holdings  # Full holdings dataframe
            }

            # Print summary
            print("\n" + "╔" + "═" * 60 + "╗")
            print("║            🌙 Portfolio Monitor Summary 💼              ║")
            print("╠" + "═" * 60 + "╣")
            print(f"║  Total Portfolio Value: ${total_value:,.2f}".ljust(62) + "║")
            print(f"║  USDC Balance: ${usdc_balance:,.2f}".ljust(62) + "║")
            print(f"║  Active Positions: {num_positions}".ljust(62) + "║")
            print(f"║  Largest Position: {largest_pct:.1f}%".ljust(62) + "║")
            print(f"║  Concentration Risk: {concentration_risk:.3f}".ljust(62) + "║")

            # Risk assessment
            if concentration_risk > 0.5:
                risk_msg = "🔴 HIGH - Very concentrated"
            elif concentration_risk > 0.3:
                risk_msg = "🟡 MEDIUM - Moderately concentrated"
            else:
                risk_msg = "🟢 LOW - Well diversified"
            print(f"║  Risk Level: {risk_msg}".ljust(62) + "║")
            print("╚" + "═" * 60 + "╝")

            return snapshot

        except Exception as e:
            cprint(f"❌ Error getting portfolio snapshot: {str(e)}", "red")
            traceback.print_exc()
            return None

    def save_to_history(self, snapshot):
        """Save portfolio snapshot to history"""
        try:
            if snapshot is None:
                return

            # Create new row
            new_row = pd.DataFrame([{
                'timestamp': snapshot['timestamp'],
                'total_value_usd': snapshot['total_value_usd'],
                'num_positions': snapshot['num_positions'],
                'largest_position_pct': snapshot['largest_position_pct'],
                'top_asset': snapshot['top_asset'],
                'concentration_risk': snapshot['concentration_risk']
            }])

            # Add to history
            self.history = pd.concat([self.history, new_row], ignore_index=True)

            # Keep only last 30 days
            cutoff_time = datetime.now() - timedelta(days=30)
            self.history = self.history[
                pd.to_datetime(self.history['timestamp']) > cutoff_time
            ]

            # Save to file
            self.history.to_csv(self.history_file, index=False)

        except Exception as e:
            print(f"❌ Error saving to history: {str(e)}")

    def analyze_exposure(self, snapshot):
        """Analyze portfolio exposure and return risk metrics"""
        try:
            if snapshot is None:
                return None

            analysis = {
                'requires_hedge': False,
                'hedge_recommendation': "NONE",
                'risk_level': "LOW",
                'reasoning': []
            }

            # Check concentration risk
            if snapshot['concentration_risk'] > 0.5:
                analysis['requires_hedge'] = True
                analysis['hedge_recommendation'] = "REDUCE_LARGEST_POSITION"
                analysis['risk_level'] = "HIGH"
                analysis['reasoning'].append(
                    f"Very high concentration risk ({snapshot['concentration_risk']:.2f}). "
                    f"Largest position is {snapshot['largest_position_pct']:.1f}% of portfolio."
                )

            # Check if portfolio value has dropped significantly
            if len(self.history) > 0:
                # Get value from 24 hours ago if available
                recent_history = self.history[
                    pd.to_datetime(self.history['timestamp']) >
                    (datetime.now() - timedelta(hours=24))
                ]

                if len(recent_history) > 1:
                    old_value = recent_history.iloc[0]['total_value_usd']
                    current_value = snapshot['total_value_usd']
                    pct_change = ((current_value - old_value) / old_value) * 100

                    if pct_change < -10:  # 10% drop in 24h
                        analysis['requires_hedge'] = True
                        analysis['hedge_recommendation'] = "OPEN_SHORT_HEDGE"
                        analysis['risk_level'] = "HIGH"
                        analysis['reasoning'].append(
                            f"Portfolio down {abs(pct_change):.1f}% in 24h. "
                            "Consider opening short hedge to protect remaining capital."
                        )

            # Check number of positions
            if snapshot['num_positions'] < 3 and snapshot['total_value_usd'] > 100:
                analysis['reasoning'].append(
                    f"Only {snapshot['num_positions']} positions. "
                    "Consider diversifying to reduce single-asset risk."
                )

            if not analysis['reasoning']:
                analysis['reasoning'].append("Portfolio appears well-balanced.")

            return analysis

        except Exception as e:
            print(f"❌ Error analyzing exposure: {str(e)}")
            return None

    def run(self):
        """Run portfolio monitoring cycle"""
        try:
            # Get current portfolio snapshot
            snapshot = self.get_portfolio_snapshot()

            if snapshot:
                # Save to history
                self.save_to_history(snapshot)

                # Analyze exposure
                analysis = self.analyze_exposure(snapshot)

                if analysis:
                    print("\n" + "╔" + "═" * 60 + "╗")
                    print("║            🌙 Exposure Analysis 🎯                      ║")
                    print("╠" + "═" * 60 + "╣")
                    print(f"║  Risk Level: {analysis['risk_level']}".ljust(62) + "║")
                    print(f"║  Hedge Needed: {'YES' if analysis['requires_hedge'] else 'NO'}".ljust(62) + "║")
                    print(f"║  Recommendation: {analysis['hedge_recommendation']}".ljust(62) + "║")
                    print("╠" + "═" * 60 + "╣")
                    print("║  Reasoning:".ljust(62) + "║")
                    for reason in analysis['reasoning']:
                        # Wrap long text
                        words = reason.split()
                        line = "║  "
                        for word in words:
                            if len(line) + len(word) + 1 > 60:
                                print(line.ljust(62) + "║")
                                line = "║  " + word
                            else:
                                line += " " + word if line != "║  " else word
                        if line != "║  ":
                            print(line.ljust(62) + "║")
                    print("╚" + "═" * 60 + "╝")

                return {
                    'snapshot': snapshot,
                    'analysis': analysis
                }

            return None

        except Exception as e:
            cprint(f"❌ Error in portfolio monitor: {str(e)}", "red")
            traceback.print_exc()
            return None

def main():
    """Main function for standalone testing"""
    cprint("\n🚀 Portfolio Monitor Subagent Starting...", "white", "on_blue")

    monitor = PortfolioMonitorSubagent()

    while True:
        try:
            monitor.run()

            print(f"\n💤 Sleeping for 15 minutes...")
            time.sleep(15 * 60)

        except KeyboardInterrupt:
            print("\n👋 Portfolio Monitor shutting down gracefully...")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
