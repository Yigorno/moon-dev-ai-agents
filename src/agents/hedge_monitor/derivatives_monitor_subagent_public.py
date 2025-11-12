"""
🌙 Moon Dev's Derivatives Monitor Subagent (Public API Version)
Part of the Hedge Monitor System
Built with love by Moon Dev 🚀

Monitors Open Interest, Funding Rates, and Liquidations using FREE public APIs.
No Moon Dev API required!
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
import numpy as np

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src import config
from src.agents.hedge_monitor.public_data_api import PublicDataAPI
from src.agents.base_agent import BaseAgent

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Thresholds for risk detection
FUNDING_EXTREME_THRESHOLD = 20  # Annual % - extreme positive funding
FUNDING_NEGATIVE_THRESHOLD = -5  # Annual % - extreme negative funding
OI_CHANGE_THRESHOLD = 15  # % change in OI that's considered significant
LIQUIDATION_SPIKE_THRESHOLD = 50  # % increase in liquidations

class DerivativesMonitorSubagentPublic(BaseAgent):
    """Derivatives Monitor - Tracks OI, funding rates, and liquidations using public APIs"""

    def __init__(self):
        """Initialize Derivatives Monitor Subagent (Public API version)"""
        super().__init__('derivatives_monitor_public')

        load_dotenv()

        # Initialize Public Data API (no keys required!)
        self.api = PublicDataAPI()

        # Create data directory for this subagent
        self.data_dir = PROJECT_ROOT / "src" / "data" / "hedge_monitor" / "derivatives"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # History files
        self.funding_history_file = self.data_dir / "funding_history_public.csv"
        self.oi_history_file = self.data_dir / "oi_history_public.csv"
        self.liquidation_history_file = self.data_dir / "liquidation_history_public.csv"

        self.load_history()

        cprint("📊 Derivatives Monitor Subagent (Public API) initialized!", "white", "on_blue")
        print("💡 Using FREE public APIs (Binance, Bybit) - no Moon Dev API required!")

    def load_history(self):
        """Load or initialize historical data"""
        try:
            # Load funding rate history
            if self.funding_history_file.exists():
                self.funding_history = pd.read_csv(self.funding_history_file)
            else:
                self.funding_history = pd.DataFrame(columns=[
                    'timestamp', 'symbol', 'funding_rate', 'annual_rate'
                ])

            # Load OI history
            if self.oi_history_file.exists():
                self.oi_history = pd.read_csv(self.oi_history_file)
            else:
                self.oi_history = pd.DataFrame(columns=[
                    'timestamp', 'total_oi', 'btc_oi', 'eth_oi'
                ])

            # Load liquidation history
            if self.liquidation_history_file.exists():
                self.liquidation_history = pd.read_csv(self.liquidation_history_file)
            else:
                self.liquidation_history = pd.DataFrame(columns=[
                    'timestamp', 'total_liquidations', 'long_liquidations', 'short_liquidations'
                ])

            print("📊 Loaded derivatives history")

        except Exception as e:
            print(f"❌ Error loading history: {str(e)}")
            self.funding_history = pd.DataFrame()
            self.oi_history = pd.DataFrame()
            self.liquidation_history = pd.DataFrame()

    def get_funding_rates(self):
        """Get current funding rates from public API"""
        try:
            print("\n🔍 Fetching funding rates from public sources...")
            df = self.api.get_funding_rates()

            if df is not None and not df.empty:
                print(f"✅ Got funding rates for {len(df)} symbols")
                return df

            return None

        except Exception as e:
            print(f"❌ Error getting funding rates: {str(e)}")
            return None

    def get_open_interest(self):
        """Get current open interest data from public API"""
        try:
            print("\n🔍 Fetching open interest from public sources...")
            oi_data = self.api.get_open_interest()

            if oi_data:
                print(f"✅ Total OI: ${oi_data['total_oi']:,.0f}")
                return oi_data

            return None

        except Exception as e:
            print(f"❌ Error getting open interest: {str(e)}")
            return None

    def get_liquidations(self):
        """Get recent liquidation data from public API"""
        try:
            print("\n🔍 Fetching liquidations from public sources...")
            df = self.api.get_liquidations(limit=100)

            if df is not None and not df.empty:
                # Get recent data (last hour)
                one_hour_ago = datetime.utcnow() - timedelta(hours=1)
                recent = df[df['datetime'] >= one_hour_ago]

                # Separate longs and shorts
                longs = recent[recent['side'] == 'SELL']  # SELL = long liquidation
                shorts = recent[recent['side'] == 'BUY']  # BUY = short liquidation

                liq_data = {
                    'timestamp': datetime.now(),
                    'total_liquidations': recent['usd_value'].sum(),
                    'long_liquidations': longs['usd_value'].sum(),
                    'short_liquidations': shorts['usd_value'].sum()
                }

                print(f"✅ Recent liquidations: ${liq_data['total_liquidations']:,.2f}")
                return liq_data

            return None

        except Exception as e:
            print(f"❌ Error getting liquidations: {str(e)}")
            traceback.print_exc()
            return None

    def analyze_funding_risk(self, funding_data):
        """Analyze funding rate risk"""
        try:
            if funding_data is None or funding_data.empty:
                return None

            risks = []

            # Check for extreme funding rates
            for _, row in funding_data.iterrows():
                symbol = row['symbol']
                annual_rate = row['annual_rate']

                if annual_rate > FUNDING_EXTREME_THRESHOLD:
                    risks.append({
                        'type': 'EXTREME_POSITIVE_FUNDING',
                        'symbol': symbol,
                        'value': annual_rate,
                        'severity': 'HIGH',
                        'message': f"{symbol} has extreme positive funding ({annual_rate:.1f}% annual). Longs paying shorts heavily - potential for long squeeze."
                    })

                elif annual_rate < FUNDING_NEGATIVE_THRESHOLD:
                    risks.append({
                        'type': 'EXTREME_NEGATIVE_FUNDING',
                        'symbol': symbol,
                        'value': annual_rate,
                        'severity': 'HIGH',
                        'message': f"{symbol} has extreme negative funding ({annual_rate:.1f}% annual). Shorts paying longs heavily - potential for short squeeze."
                    })

            return risks

        except Exception as e:
            print(f"❌ Error analyzing funding risk: {str(e)}")
            return None

    def analyze_oi_risk(self, current_oi):
        """Analyze open interest changes"""
        try:
            if current_oi is None:
                return None

            risks = []

            # Compare with previous OI if available
            if not self.oi_history.empty:
                prev_oi = self.oi_history.iloc[-1]

                # Calculate % change
                total_change = ((current_oi['total_oi'] - prev_oi['total_oi']) /
                               prev_oi['total_oi'] * 100)

                if abs(total_change) > OI_CHANGE_THRESHOLD:
                    severity = 'HIGH' if abs(total_change) > 25 else 'MEDIUM'
                    direction = 'increasing' if total_change > 0 else 'decreasing'

                    risks.append({
                        'type': 'OI_CHANGE',
                        'symbol': 'TOTAL',
                        'value': total_change,
                        'severity': severity,
                        'message': f"Total OI {direction} by {abs(total_change):.1f}% - significant market positioning change."
                    })

            return risks

        except Exception as e:
            print(f"❌ Error analyzing OI risk: {str(e)}")
            return None

    def analyze_liquidation_risk(self, current_liq):
        """Analyze liquidation patterns"""
        try:
            if current_liq is None:
                return None

            risks = []

            # Compare with previous liquidations if available
            if not self.liquidation_history.empty:
                prev_liq = self.liquidation_history.iloc[-1]

                # Calculate % change
                if prev_liq['total_liquidations'] > 0:
                    total_change = ((current_liq['total_liquidations'] - prev_liq['total_liquidations']) /
                                   prev_liq['total_liquidations'] * 100)

                    if total_change > LIQUIDATION_SPIKE_THRESHOLD:
                        # Determine if longs or shorts are getting rekt
                        if current_liq['long_liquidations'] > current_liq['short_liquidations']:
                            direction = "LONG"
                            implication = "Price dropping - consider short hedge"
                        else:
                            direction = "SHORT"
                            implication = "Price pumping - longs may be overheated"

                        risks.append({
                            'type': 'LIQUIDATION_SPIKE',
                            'symbol': direction,
                            'value': total_change,
                            'severity': 'HIGH',
                            'message': f"Liquidations up {total_change:.1f}% - {direction}s getting liquidated. {implication}"
                        })

            return risks

        except Exception as e:
            print(f"❌ Error analyzing liquidation risk: {str(e)}")
            return None

    def save_to_history(self, funding_data, oi_data, liq_data):
        """Save current data to history"""
        try:
            # Save funding rates
            if funding_data is not None and not funding_data.empty:
                funding_data['timestamp'] = datetime.now()
                self.funding_history = pd.concat([self.funding_history, funding_data], ignore_index=True)

                # Keep only last 7 days
                cutoff = datetime.now() - timedelta(days=7)
                self.funding_history = self.funding_history[
                    pd.to_datetime(self.funding_history['timestamp']) > cutoff
                ]
                self.funding_history.to_csv(self.funding_history_file, index=False)

            # Save OI
            if oi_data is not None:
                new_oi = pd.DataFrame([oi_data])
                self.oi_history = pd.concat([self.oi_history, new_oi], ignore_index=True)

                # Keep only last 7 days
                cutoff = datetime.now() - timedelta(days=7)
                self.oi_history = self.oi_history[
                    pd.to_datetime(self.oi_history['timestamp']) > cutoff
                ]
                self.oi_history.to_csv(self.oi_history_file, index=False)

            # Save liquidations
            if liq_data is not None:
                new_liq = pd.DataFrame([liq_data])
                self.liquidation_history = pd.concat([self.liquidation_history, new_liq], ignore_index=True)

                # Keep only last 7 days
                cutoff = datetime.now() - timedelta(days=7)
                self.liquidation_history = self.liquidation_history[
                    pd.to_datetime(self.liquidation_history['timestamp']) > cutoff
                ]
                self.liquidation_history.to_csv(self.liquidation_history_file, index=False)

        except Exception as e:
            print(f"❌ Error saving to history: {str(e)}")

    def run(self):
        """Run derivatives monitoring cycle"""
        try:
            # Get all data
            funding_data = self.get_funding_rates()
            oi_data = self.get_open_interest()
            liq_data = self.get_liquidations()

            # Analyze each component
            funding_risks = self.analyze_funding_risk(funding_data)
            oi_risks = self.analyze_oi_risk(oi_data)
            liq_risks = self.analyze_liquidation_risk(liq_data)

            # Combine all risks
            all_risks = []
            if funding_risks:
                all_risks.extend(funding_risks)
            if oi_risks:
                all_risks.extend(oi_risks)
            if liq_risks:
                all_risks.extend(liq_risks)

            # Save to history
            self.save_to_history(funding_data, oi_data, liq_data)

            # Print summary
            print("\n" + "╔" + "═" * 70 + "╗")
            print("║     🌙 Derivatives Monitor Summary (Public API) 📊                ║")
            print("╠" + "═" * 70 + "╣")

            if all_risks:
                print(f"║  ⚠️  {len(all_risks)} Risk(s) Detected".ljust(72) + "║")
                print("╠" + "═" * 70 + "╣")

                for risk in all_risks:
                    severity_emoji = "🔴" if risk['severity'] == 'HIGH' else "🟡"
                    print(f"║  {severity_emoji} {risk['type']}".ljust(72) + "║")
                    # Wrap message if too long
                    msg = risk['message']
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
                print("║  ✅ No significant risks detected".ljust(72) + "║")

            print("╚" + "═" * 70 + "╝")

            return {
                'funding_data': funding_data,
                'oi_data': oi_data,
                'liquidation_data': liq_data,
                'risks': all_risks
            }

        except Exception as e:
            cprint(f"❌ Error in derivatives monitor: {str(e)}", "red")
            traceback.print_exc()
            return None

def main():
    """Main function for standalone testing"""
    cprint("\n🚀 Derivatives Monitor Subagent (Public API) Starting...", "white", "on_blue")

    monitor = DerivativesMonitorSubagentPublic()

    while True:
        try:
            monitor.run()

            print(f"\n💤 Sleeping for 15 minutes...")
            time.sleep(15 * 60)

        except KeyboardInterrupt:
            print("\n👋 Derivatives Monitor shutting down gracefully...")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
