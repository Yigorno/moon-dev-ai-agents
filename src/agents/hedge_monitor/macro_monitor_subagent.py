"""
🌙 Moon Dev's Macro Monitor Subagent
Part of the Hedge Monitor System
Built with love by Moon Dev 🚀

Monitors macroeconomic indicators: M2 money supply, FED decisions, bank reserves.
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

# Try to import fredapi, but make it optional
try:
    from fredapi import Fred
    FRED_AVAILABLE = True
except ImportError:
    FRED_AVAILABLE = False
    print("⚠️ fredapi not installed. Install with: pip install fredapi")

# FRED series IDs for economic indicators
FRED_SERIES = {
    'M2': 'M2SL',  # M2 Money Supply
    'WALCL': 'WALCL',  # Fed Balance Sheet (Total Assets)
    'WRESBAL': 'WRESBAL',  # Reserve Balances with Federal Reserve Banks
    'DFF': 'DFF',  # Federal Funds Effective Rate
}

class MacroMonitorSubagent(BaseAgent):
    """Macro Monitor - Tracks macroeconomic indicators for risk context"""

    def __init__(self):
        """Initialize Macro Monitor Subagent"""
        super().__init__('macro_monitor')

        load_dotenv()

        # Get FRED API key from environment
        self.fred_api_key = os.getenv('FRED_API_KEY')

        # Initialize FRED client if available
        self.fred_client = None
        if FRED_AVAILABLE and self.fred_api_key:
            try:
                self.fred_client = Fred(api_key=self.fred_api_key)
                print("✅ FRED API client initialized")
            except Exception as e:
                print(f"⚠️ Could not initialize FRED API: {str(e)}")
        else:
            if not FRED_AVAILABLE:
                print("⚠️ fredapi not installed - macro monitoring will be limited")
            elif not self.fred_api_key:
                print("⚠️ FRED_API_KEY not found in .env - get free key at https://fred.stlouisfed.org/docs/api/api_key.html")

        # Create data directory for this subagent
        self.data_dir = PROJECT_ROOT / "src" / "data" / "hedge_monitor" / "macro"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # History file
        self.history_file = self.data_dir / "macro_history.csv"
        self.load_history()

        cprint("🌍 Macro Monitor Subagent initialized!", "white", "on_blue")

    def load_history(self):
        """Load or initialize macro data history"""
        try:
            if self.history_file.exists():
                self.history = pd.read_csv(self.history_file)
                print(f"📊 Loaded {len(self.history)} historical macro records")
            else:
                self.history = pd.DataFrame(columns=[
                    'timestamp', 'm2_supply', 'fed_balance_sheet',
                    'bank_reserves', 'fed_funds_rate', 'liquidity_trend'
                ])
                print("📝 Created new macro history file")

        except Exception as e:
            print(f"❌ Error loading history: {str(e)}")
            self.history = pd.DataFrame()

    def get_fred_data(self, series_id, days_back=90):
        """Get data from FRED API"""
        try:
            if not self.fred_client:
                return None

            # Get data from the last N days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            data = self.fred_client.get_series(
                series_id,
                observation_start=start_date.strftime('%Y-%m-%d'),
                observation_end=end_date.strftime('%Y-%m-%d')
            )

            if data is not None and not data.empty:
                # Get the most recent value
                latest_value = data.iloc[-1]
                latest_date = data.index[-1]

                return {
                    'value': latest_value,
                    'date': latest_date,
                    'series': data
                }

            return None

        except Exception as e:
            print(f"⚠️ Error fetching {series_id} from FRED: {str(e)}")
            return None

    def calculate_liquidity_trend(self, m2_data, fed_balance_data, bank_reserves_data):
        """Calculate overall liquidity trend (QE vs QT)"""
        try:
            # Simple heuristic: if M2 + Fed Balance Sheet + Bank Reserves are increasing = QE
            # If decreasing = QT

            trends = []

            # Check M2 trend
            if m2_data and len(m2_data['series']) > 30:
                recent_m2 = m2_data['series'].iloc[-30:].mean()
                older_m2 = m2_data['series'].iloc[-60:-30].mean()
                m2_trend = "INCREASING" if recent_m2 > older_m2 else "DECREASING"
                trends.append(('M2', m2_trend, ((recent_m2 - older_m2) / older_m2 * 100)))

            # Check Fed Balance Sheet trend
            if fed_balance_data and len(fed_balance_data['series']) > 30:
                recent_fed = fed_balance_data['series'].iloc[-30:].mean()
                older_fed = fed_balance_data['series'].iloc[-60:-30].mean()
                fed_trend = "INCREASING" if recent_fed > older_fed else "DECREASING"
                trends.append(('FED_BS', fed_trend, ((recent_fed - older_fed) / older_fed * 100)))

            # Check Bank Reserves trend
            if bank_reserves_data and len(bank_reserves_data['series']) > 30:
                recent_res = bank_reserves_data['series'].iloc[-30:].mean()
                older_res = bank_reserves_data['series'].iloc[-60:-30].mean()
                res_trend = "INCREASING" if recent_res > older_res else "DECREASING"
                trends.append(('RESERVES', res_trend, ((recent_res - older_res) / older_res * 100)))

            # Determine overall trend
            if not trends:
                return "UNKNOWN", []

            increasing_count = sum(1 for _, trend, _ in trends if trend == "INCREASING")
            total_count = len(trends)

            if increasing_count >= total_count * 0.66:
                overall = "QE (Quantitative Easing)"
            elif increasing_count <= total_count * 0.33:
                overall = "QT (Quantitative Tightening)"
            else:
                overall = "MIXED"

            return overall, trends

        except Exception as e:
            print(f"❌ Error calculating liquidity trend: {str(e)}")
            return "UNKNOWN", []

    def analyze_macro_risk(self, macro_data):
        """Analyze macroeconomic risk indicators"""
        try:
            risks = []

            # Check if we're in QT (risk-off environment)
            if macro_data['liquidity_trend'] == "QT (Quantitative Tightening)":
                risks.append({
                    'type': 'QUANTITATIVE_TIGHTENING',
                    'severity': 'HIGH',
                    'message': 'FED is in QT mode - liquidity draining from markets. Risk-off environment for crypto.'
                })

            # Check if Fed Funds Rate is high (>4%)
            if macro_data.get('fed_funds_rate') and macro_data['fed_funds_rate'] > 4.0:
                risks.append({
                    'type': 'HIGH_INTEREST_RATES',
                    'severity': 'MEDIUM',
                    'message': f'Fed Funds Rate at {macro_data["fed_funds_rate"]:.2f}% - high rates typically negative for risk assets.'
                })

            # Check M2 trend
            if macro_data.get('m2_change_pct'):
                if macro_data['m2_change_pct'] < -2:  # M2 declining by more than 2%
                    risks.append({
                        'type': 'M2_CONTRACTION',
                        'severity': 'HIGH',
                        'message': f'M2 money supply declining by {abs(macro_data["m2_change_pct"]):.1f}% - money supply contraction is bearish.'
                    })

            return risks

        except Exception as e:
            print(f"❌ Error analyzing macro risk: {str(e)}")
            return []

    def save_to_history(self, macro_data):
        """Save macro data to history"""
        try:
            if macro_data is None:
                return

            # Create new row
            new_row = pd.DataFrame([{
                'timestamp': datetime.now(),
                'm2_supply': macro_data.get('m2_supply'),
                'fed_balance_sheet': macro_data.get('fed_balance_sheet'),
                'bank_reserves': macro_data.get('bank_reserves'),
                'fed_funds_rate': macro_data.get('fed_funds_rate'),
                'liquidity_trend': macro_data.get('liquidity_trend')
            }])

            # Add to history
            self.history = pd.concat([self.history, new_row], ignore_index=True)

            # Keep only last 90 days
            cutoff_time = datetime.now() - timedelta(days=90)
            self.history = self.history[
                pd.to_datetime(self.history['timestamp']) > cutoff_time
            ]

            # Save to file
            self.history.to_csv(self.history_file, index=False)

        except Exception as e:
            print(f"❌ Error saving to history: {str(e)}")

    def run(self):
        """Run macro monitoring cycle"""
        try:
            if not self.fred_client:
                print("⚠️ FRED API not available - skipping macro monitoring")
                print("💡 To enable: pip install fredapi and add FRED_API_KEY to .env")
                print("   Get free key at: https://fred.stlouisfed.org/docs/api/api_key.html")
                return None

            print("\n🌍 Fetching macroeconomic data from FRED...")

            # Get M2 money supply
            m2_data = self.get_fred_data(FRED_SERIES['M2'])

            # Get Fed balance sheet
            fed_balance_data = self.get_fred_data(FRED_SERIES['WALCL'])

            # Get bank reserves
            bank_reserves_data = self.get_fred_data(FRED_SERIES['WRESBAL'])

            # Get Fed Funds Rate
            fed_funds_data = self.get_fred_data(FRED_SERIES['DFF'], days_back=30)

            # Calculate liquidity trend
            liquidity_trend, trend_details = self.calculate_liquidity_trend(
                m2_data, fed_balance_data, bank_reserves_data
            )

            # Compile macro data
            macro_data = {
                'timestamp': datetime.now(),
                'm2_supply': m2_data['value'] if m2_data else None,
                'fed_balance_sheet': fed_balance_data['value'] if fed_balance_data else None,
                'bank_reserves': bank_reserves_data['value'] if bank_reserves_data else None,
                'fed_funds_rate': fed_funds_data['value'] if fed_funds_data else None,
                'liquidity_trend': liquidity_trend,
                'trend_details': trend_details
            }

            # Calculate change percentages if we have history
            if not self.history.empty and len(self.history) > 1:
                prev_data = self.history.iloc[-1]

                if prev_data['m2_supply'] and macro_data['m2_supply']:
                    macro_data['m2_change_pct'] = (
                        (macro_data['m2_supply'] - prev_data['m2_supply']) /
                        prev_data['m2_supply'] * 100
                    )

            # Analyze risks
            risks = self.analyze_macro_risk(macro_data)

            # Save to history
            self.save_to_history(macro_data)

            # Print summary
            print("\n" + "╔" + "═" * 70 + "╗")
            print("║            🌙 Macro Monitor Summary 🌍                             ║")
            print("╠" + "═" * 70 + "╣")

            if macro_data.get('m2_supply'):
                print(f"║  M2 Money Supply: ${macro_data['m2_supply']:,.0f}B".ljust(72) + "║")

            if macro_data.get('fed_balance_sheet'):
                print(f"║  Fed Balance Sheet: ${macro_data['fed_balance_sheet']:,.0f}B".ljust(72) + "║")

            if macro_data.get('bank_reserves'):
                print(f"║  Bank Reserves: ${macro_data['bank_reserves']:,.0f}B".ljust(72) + "║")

            if macro_data.get('fed_funds_rate'):
                print(f"║  Fed Funds Rate: {macro_data['fed_funds_rate']:.2f}%".ljust(72) + "║")

            print("╠" + "═" * 70 + "╣")
            print(f"║  Liquidity Trend: {liquidity_trend}".ljust(72) + "║")

            if trend_details:
                for name, trend, pct in trend_details:
                    emoji = "📈" if trend == "INCREASING" else "📉"
                    print(f"║    {emoji} {name}: {trend} ({pct:+.2f}%)".ljust(72) + "║")

            if risks:
                print("╠" + "═" * 70 + "╣")
                print(f"║  ⚠️  {len(risks)} Risk(s) Detected".ljust(72) + "║")
                for risk in risks:
                    severity_emoji = "🔴" if risk['severity'] == 'HIGH' else "🟡"
                    print(f"║  {severity_emoji} {risk['type']}".ljust(72) + "║")
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
            else:
                print("╠" + "═" * 70 + "╣")
                print("║  ✅ No significant macro risks detected".ljust(72) + "║")

            print("╚" + "═" * 70 + "╝")

            return {
                'macro_data': macro_data,
                'risks': risks
            }

        except Exception as e:
            cprint(f"❌ Error in macro monitor: {str(e)}", "red")
            traceback.print_exc()
            return None

def main():
    """Main function for standalone testing"""
    cprint("\n🚀 Macro Monitor Subagent Starting...", "white", "on_blue")

    monitor = MacroMonitorSubagent()

    while True:
        try:
            monitor.run()

            # Macro data doesn't change frequently, so check less often
            print(f"\n💤 Sleeping for 1 hour...")
            time.sleep(60 * 60)

        except KeyboardInterrupt:
            print("\n👋 Macro Monitor shutting down gracefully...")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
