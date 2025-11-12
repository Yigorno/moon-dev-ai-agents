"""
🌙 Moon Dev's Market Maker Monitor Subagent
Part of the Hedge Monitor System
Built with love by Moon Dev 🚀

Monitors market maker positions using whale addresses as proxies.
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
from src.agents.api import MoonDevAPI
from src.agents.base_agent import BaseAgent

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Thresholds for detecting significant activity
WHALE_POSITION_CHANGE_THRESHOLD = 20  # % change in whale position that's significant

class MarketMakerMonitorSubagent(BaseAgent):
    """Market Maker Monitor - Tracks MM positions via whale addresses"""

    def __init__(self):
        """Initialize Market Maker Monitor Subagent"""
        super().__init__('marketmaker_monitor')

        load_dotenv()

        # Initialize Moon Dev API
        self.api = MoonDevAPI()

        # Create data directory for this subagent
        self.data_dir = PROJECT_ROOT / "src" / "data" / "hedge_monitor" / "marketmaker"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # History file
        self.history_file = self.data_dir / "whale_activity_history.csv"
        self.whale_addresses_file = self.data_dir / "whale_addresses.txt"

        self.load_history()
        self.load_whale_addresses()

        cprint("🐋 Market Maker Monitor Subagent initialized!", "white", "on_blue")

    def load_history(self):
        """Load or initialize whale activity history"""
        try:
            if self.history_file.exists():
                self.history = pd.read_csv(self.history_file)
                print(f"📊 Loaded {len(self.history)} historical whale activity records")
            else:
                self.history = pd.DataFrame(columns=[
                    'timestamp', 'num_whale_addresses', 'total_whale_activity',
                    'accumulation_score', 'distribution_score'
                ])
                print("📝 Created new whale activity history file")

        except Exception as e:
            print(f"❌ Error loading history: {str(e)}")
            self.history = pd.DataFrame()

    def load_whale_addresses(self):
        """Load whale addresses from Moon Dev API"""
        try:
            print("\n🔍 Fetching whale addresses from Moon Dev API...")
            whale_addresses = self.api.get_whale_addresses()

            if whale_addresses:
                # Save to local file
                with open(self.whale_addresses_file, 'w') as f:
                    for address in whale_addresses:
                        f.write(f"{address}\n")

                self.whale_addresses = whale_addresses
                print(f"✅ Loaded {len(whale_addresses)} whale addresses")
            else:
                # Try loading from local file
                if self.whale_addresses_file.exists():
                    with open(self.whale_addresses_file, 'r') as f:
                        self.whale_addresses = [line.strip() for line in f.readlines()]
                    print(f"📁 Loaded {len(self.whale_addresses)} whale addresses from cache")
                else:
                    self.whale_addresses = []
                    print("⚠️ No whale addresses available")

        except Exception as e:
            print(f"❌ Error loading whale addresses: {str(e)}")
            self.whale_addresses = []

    def get_whale_positions(self):
        """Get current positions data for whales (using HLP data as proxy)"""
        try:
            print("\n🔍 Fetching whale position data...")

            # Get aggregated positions on HLP
            agg_positions = self.api.get_agg_positions_hlp()

            if agg_positions is not None and not agg_positions.empty:
                # Get detailed positions
                detailed_positions = self.api.get_positions_hlp()

                return {
                    'timestamp': datetime.now(),
                    'aggregated': agg_positions,
                    'detailed': detailed_positions
                }

            return None

        except Exception as e:
            print(f"❌ Error getting whale positions: {str(e)}")
            traceback.print_exc()
            return None

    def analyze_whale_activity(self, current_positions, previous_positions=None):
        """Analyze whale positioning and activity"""
        try:
            if current_positions is None:
                return None

            analysis = {
                'accumulation_score': 0,  # Positive = whales accumulating
                'distribution_score': 0,  # Positive = whales distributing
                'net_positioning': 'NEUTRAL',
                'signals': []
            }

            # Analyze aggregated positions if available
            if current_positions.get('aggregated') is not None:
                agg = current_positions['aggregated']

                # Check if we have previous data to compare
                if previous_positions and previous_positions.get('aggregated') is not None:
                    prev_agg = previous_positions['aggregated']

                    # Compare long vs short positioning
                    if 'total_long_position' in agg.columns and 'total_short_position' in agg.columns:
                        current_longs = agg['total_long_position'].sum()
                        current_shorts = agg['total_short_position'].sum()

                        prev_longs = prev_agg['total_long_position'].sum()
                        prev_shorts = prev_agg['total_short_position'].sum()

                        # Calculate changes
                        long_change_pct = ((current_longs - prev_longs) / prev_longs * 100) if prev_longs > 0 else 0
                        short_change_pct = ((current_shorts - prev_shorts) / prev_shorts * 100) if prev_shorts > 0 else 0

                        # Accumulation signals
                        if long_change_pct > WHALE_POSITION_CHANGE_THRESHOLD:
                            analysis['accumulation_score'] += 1
                            analysis['signals'].append({
                                'type': 'WHALE_LONG_ACCUMULATION',
                                'severity': 'HIGH',
                                'message': f'Whales increasing long positions by {long_change_pct:.1f}% - bullish signal'
                            })

                        # Distribution signals
                        if short_change_pct > WHALE_POSITION_CHANGE_THRESHOLD:
                            analysis['distribution_score'] += 1
                            analysis['signals'].append({
                                'type': 'WHALE_SHORT_ACCUMULATION',
                                'severity': 'HIGH',
                                'message': f'Whales increasing short positions by {short_change_pct:.1f}% - bearish signal'
                            })

                        # Determine net positioning
                        if analysis['accumulation_score'] > analysis['distribution_score']:
                            analysis['net_positioning'] = 'ACCUMULATION (Bullish)'
                        elif analysis['distribution_score'] > analysis['accumulation_score']:
                            analysis['net_positioning'] = 'DISTRIBUTION (Bearish)'
                        else:
                            analysis['net_positioning'] = 'NEUTRAL'

            return analysis

        except Exception as e:
            print(f"❌ Error analyzing whale activity: {str(e)}")
            traceback.print_exc()
            return None

    def save_to_history(self, analysis):
        """Save whale activity analysis to history"""
        try:
            if analysis is None:
                return

            # Create new row
            new_row = pd.DataFrame([{
                'timestamp': datetime.now(),
                'num_whale_addresses': len(self.whale_addresses),
                'total_whale_activity': analysis.get('accumulation_score', 0) + analysis.get('distribution_score', 0),
                'accumulation_score': analysis.get('accumulation_score', 0),
                'distribution_score': analysis.get('distribution_score', 0)
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

    def run(self):
        """Run market maker monitoring cycle"""
        try:
            # Get current whale positions
            current_positions = self.get_whale_positions()

            # Get previous positions from history if available
            previous_positions = None
            if not self.history.empty:
                # For now, we'll just store the timestamp
                # In a real implementation, you'd want to store and load the full position data
                pass

            # Analyze whale activity
            analysis = self.analyze_whale_activity(current_positions, previous_positions)

            # Save to history
            if analysis:
                self.save_to_history(analysis)

            # Print summary
            print("\n" + "╔" + "═" * 70 + "╗")
            print("║            🌙 Market Maker Monitor Summary 🐋                      ║")
            print("╠" + "═" * 70 + "╣")
            print(f"║  Tracking {len(self.whale_addresses)} whale addresses".ljust(72) + "║")

            if analysis:
                print("╠" + "═" * 70 + "╣")
                print(f"║  Net Positioning: {analysis['net_positioning']}".ljust(72) + "║")
                print(f"║  Accumulation Score: {analysis['accumulation_score']}".ljust(72) + "║")
                print(f"║  Distribution Score: {analysis['distribution_score']}".ljust(72) + "║")

                if analysis['signals']:
                    print("╠" + "═" * 70 + "╣")
                    print(f"║  ⚠️  {len(analysis['signals'])} Signal(s) Detected".ljust(72) + "║")

                    for signal in analysis['signals']:
                        severity_emoji = "🔴" if signal['severity'] == 'HIGH' else "🟡"
                        print(f"║  {severity_emoji} {signal['type']}".ljust(72) + "║")
                        msg = signal['message']
                        words = msg.split()
                        line = "║     "
                        for word in words:
                            if len(line) + len(word) + 1 > 68:
                                print(line.ljust(72) + "║")
                                line = "║     " + word
                            else:
                                line += " " + word if line != "║     " else word
                        if line != "║     ":
                            print(line.ljust(72) + "║")
                        print("║".ljust(72) + "║")
                else:
                    print("╠" + "═" * 70 + "╣")
                    print("║  ✅ No significant whale activity detected".ljust(72) + "║")
            else:
                print("╠" + "═" * 70 + "╣")
                print("║  ⚠️ Unable to analyze whale activity".ljust(72) + "║")

            print("╚" + "═" * 70 + "╝")

            return {
                'positions': current_positions,
                'analysis': analysis
            }

        except Exception as e:
            cprint(f"❌ Error in market maker monitor: {str(e)}", "red")
            traceback.print_exc()
            return None

def main():
    """Main function for standalone testing"""
    cprint("\n🚀 Market Maker Monitor Subagent Starting...", "white", "on_blue")

    monitor = MarketMakerMonitorSubagent()

    while True:
        try:
            monitor.run()

            print(f"\n💤 Sleeping for 30 minutes...")
            time.sleep(30 * 60)

        except KeyboardInterrupt:
            print("\n👋 Market Maker Monitor shutting down gracefully...")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
