"""
🌙 Moon Dev's Options Monitor Subagent
Part of the Hedge Monitor System
Built with love by Moon Dev 🚀

Monitors options max pain and OI distribution for price magnet detection.
Note: Requires Deribit API access for full functionality.
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
import requests

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src import config
from src.agents.base_agent import BaseAgent

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Deribit API endpoint
DERIBIT_API_URL = "https://www.deribit.com/api/v2/public"

# Symbols to track
TRACKED_SYMBOLS = ['BTC', 'ETH']

class OptionsMonitorSubagent(BaseAgent):
    """Options Monitor - Tracks options max pain and OI distribution"""

    def __init__(self):
        """Initialize Options Monitor Subagent"""
        super().__init__('options_monitor')

        load_dotenv()

        # Create data directory for this subagent
        self.data_dir = PROJECT_ROOT / "src" / "data" / "hedge_monitor" / "options"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # History file
        self.history_file = self.data_dir / "options_history.csv"
        self.load_history()

        cprint("📈 Options Monitor Subagent initialized!", "white", "on_blue")
        print("💡 Using public Deribit API - no authentication required")

    def load_history(self):
        """Load or initialize options history"""
        try:
            if self.history_file.exists():
                self.history = pd.read_csv(self.history_file)
                print(f"📊 Loaded {len(self.history)} historical options records")
            else:
                self.history = pd.DataFrame(columns=[
                    'timestamp', 'symbol', 'expiration', 'max_pain',
                    'current_price', 'distance_to_max_pain_pct'
                ])
                print("📝 Created new options history file")

        except Exception as e:
            print(f"❌ Error loading history: {str(e)}")
            self.history = pd.DataFrame()

    def get_instruments(self, currency):
        """Get available option instruments for a currency"""
        try:
            url = f"{DERIBIT_API_URL}/get_instruments"
            params = {
                'currency': currency,
                'kind': 'option',
                'expired': 'false'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('result'):
                return data['result']

            return []

        except Exception as e:
            print(f"⚠️ Error getting instruments for {currency}: {str(e)}")
            return []

    def get_order_book(self, instrument_name):
        """Get order book for an instrument"""
        try:
            url = f"{DERIBIT_API_URL}/get_order_book"
            params = {'instrument_name': instrument_name}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('result'):
                return data['result']

            return None

        except Exception as e:
            # Don't print errors for individual instruments to reduce noise
            return None

    def calculate_max_pain(self, options_data):
        """Calculate max pain price from options data"""
        try:
            if not options_data:
                return None

            # Group by strike price and sum open interest
            strike_oi = {}

            for option in options_data:
                strike = option.get('strike')
                oi = option.get('open_interest', 0)

                if strike and oi:
                    if strike not in strike_oi:
                        strike_oi[strike] = {'calls': 0, 'puts': 0}

                    if 'C' in option.get('instrument_name', ''):
                        strike_oi[strike]['calls'] += oi
                    else:
                        strike_oi[strike]['puts'] += oi

            if not strike_oi:
                return None

            # Calculate pain at each strike
            pain_by_strike = {}

            for strike in strike_oi.keys():
                total_pain = 0

                for s, oi in strike_oi.items():
                    # Calls lose value if price < strike
                    if strike < s:
                        total_pain += (s - strike) * oi['calls']

                    # Puts lose value if price > strike
                    if strike > s:
                        total_pain += (strike - s) * oi['puts']

                pain_by_strike[strike] = total_pain

            # Max pain is the strike with minimum total pain
            max_pain_strike = min(pain_by_strike, key=pain_by_strike.get)

            return max_pain_strike

        except Exception as e:
            print(f"❌ Error calculating max pain: {str(e)}")
            return None

    def get_current_price(self, currency):
        """Get current spot price for a currency"""
        try:
            url = f"{DERIBIT_API_URL}/get_index_price"
            params = {'index_name': f'{currency.lower()}_usd'}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('result'):
                return data['result'].get('index_price')

            return None

        except Exception as e:
            print(f"⚠️ Error getting price for {currency}: {str(e)}")
            return None

    def analyze_max_pain_signal(self, max_pain, current_price, symbol):
        """Analyze if max pain suggests a price magnet"""
        try:
            if not max_pain or not current_price:
                return None

            distance_pct = ((max_pain - current_price) / current_price) * 100

            signals = []

            # If price is significantly away from max pain, it may act as a magnet
            if abs(distance_pct) > 5:  # More than 5% away
                direction = "above" if distance_pct > 0 else "below"
                severity = "HIGH" if abs(distance_pct) > 10 else "MEDIUM"

                signals.append({
                    'type': 'MAX_PAIN_MAGNET',
                    'severity': severity,
                    'symbol': symbol,
                    'max_pain': max_pain,
                    'current_price': current_price,
                    'distance_pct': distance_pct,
                    'message': f'{symbol} is {abs(distance_pct):.1f}% {direction} max pain (${max_pain:,.0f}). Price may gravitate toward max pain as expiry approaches.'
                })

            return signals

        except Exception as e:
            print(f"❌ Error analyzing max pain signal: {str(e)}")
            return None

    def get_options_data_for_symbol(self, symbol):
        """Get options data for a specific symbol"""
        try:
            print(f"\n🔍 Fetching options data for {symbol}...")

            # Get current price
            current_price = self.get_current_price(symbol)

            if not current_price:
                print(f"⚠️ Could not get current price for {symbol}")
                return None

            # Get available instruments
            instruments = self.get_instruments(symbol)

            if not instruments:
                print(f"⚠️ No options instruments found for {symbol}")
                return None

            # Group by expiration date
            expirations = {}
            for inst in instruments:
                exp_date = inst.get('expiration_timestamp')
                if exp_date:
                    exp_date = datetime.fromtimestamp(exp_date / 1000).strftime('%Y-%m-%d')
                    if exp_date not in expirations:
                        expirations[exp_date] = []
                    expirations[exp_date].append(inst)

            # Focus on nearest expiration
            if expirations:
                nearest_exp = min(expirations.keys())
                nearest_options = expirations[nearest_exp]

                print(f"📅 Analyzing {len(nearest_options)} options expiring on {nearest_exp}")

                # Calculate max pain
                max_pain = self.calculate_max_pain(nearest_options)

                if max_pain:
                    print(f"💰 {symbol} Max Pain: ${max_pain:,.0f} (Current: ${current_price:,.0f})")

                    return {
                        'symbol': symbol,
                        'expiration': nearest_exp,
                        'max_pain': max_pain,
                        'current_price': current_price,
                        'num_options': len(nearest_options)
                    }

            return None

        except Exception as e:
            print(f"❌ Error getting options data for {symbol}: {str(e)}")
            traceback.print_exc()
            return None

    def save_to_history(self, options_data):
        """Save options data to history"""
        try:
            if not options_data:
                return

            # Create new row
            distance_pct = ((options_data['max_pain'] - options_data['current_price']) /
                          options_data['current_price'] * 100)

            new_row = pd.DataFrame([{
                'timestamp': datetime.now(),
                'symbol': options_data['symbol'],
                'expiration': options_data['expiration'],
                'max_pain': options_data['max_pain'],
                'current_price': options_data['current_price'],
                'distance_to_max_pain_pct': distance_pct
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
        """Run options monitoring cycle"""
        try:
            all_options_data = []
            all_signals = []

            # Get data for each tracked symbol
            for symbol in TRACKED_SYMBOLS:
                options_data = self.get_options_data_for_symbol(symbol)

                if options_data:
                    all_options_data.append(options_data)

                    # Save to history
                    self.save_to_history(options_data)

                    # Analyze signals
                    signals = self.analyze_max_pain_signal(
                        options_data['max_pain'],
                        options_data['current_price'],
                        symbol
                    )

                    if signals:
                        all_signals.extend(signals)

            # Print summary
            print("\n" + "╔" + "═" * 70 + "╗")
            print("║            🌙 Options Monitor Summary 📈                           ║")
            print("╠" + "═" * 70 + "╣")

            if all_options_data:
                for data in all_options_data:
                    distance = ((data['max_pain'] - data['current_price']) /
                              data['current_price'] * 100)
                    direction = "↑" if distance > 0 else "↓"

                    print(f"║  {data['symbol']}: Price ${data['current_price']:,.0f} | Max Pain ${data['max_pain']:,.0f} {direction} {abs(distance):.1f}%".ljust(72) + "║")
                    print(f"║       Expiry: {data['expiration']}".ljust(72) + "║")
            else:
                print("║  ⚠️ No options data available".ljust(72) + "║")

            if all_signals:
                print("╠" + "═" * 70 + "╣")
                print(f"║  ⚠️  {len(all_signals)} Signal(s) Detected".ljust(72) + "║")

                for signal in all_signals:
                    severity_emoji = "🔴" if signal['severity'] == 'HIGH' else "🟡"
                    print(f"║  {severity_emoji} {signal['type']} - {signal['symbol']}".ljust(72) + "║")
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
                if all_options_data:
                    print("╠" + "═" * 70 + "╣")
                    print("║  ✅ No significant max pain divergence detected".ljust(72) + "║")

            print("╚" + "═" * 70 + "╝")

            return {
                'options_data': all_options_data,
                'signals': all_signals
            }

        except Exception as e:
            cprint(f"❌ Error in options monitor: {str(e)}", "red")
            traceback.print_exc()
            return None

def main():
    """Main function for standalone testing"""
    cprint("\n🚀 Options Monitor Subagent Starting...", "white", "on_blue")

    monitor = OptionsMonitorSubagent()

    while True:
        try:
            monitor.run()

            print(f"\n💤 Sleeping for 30 minutes...")
            time.sleep(30 * 60)

        except KeyboardInterrupt:
            print("\n👋 Options Monitor shutting down gracefully...")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
