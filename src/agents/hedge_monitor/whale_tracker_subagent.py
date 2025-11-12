"""
🌙 Moon Dev's On-Chain Whale Tracker
Part of the Hedge Monitor System
Built with love by Moon Dev 🚀

Tracks whale wallets using FREE on-chain APIs:
- Etherscan API (Ethereum)
- Solscan API (Solana)
- Detects large transfers and accumulation patterns
"""

import os
import pandas as pd
import requests
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
from src.agents.base_agent import BaseAgent

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Known whale addresses (you can add more)
KNOWN_WHALES = {
    'ethereum': [
        '0x00000000219ab540356cBB839Cbe05303d7705Fa',  # ETH2 Deposit
        '0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8',  # Binance 7
        '0x28C6c06298d514Db089934071355E5743bf21d60',  # Binance 14
        '0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549',  # Binance 15
    ],
    'bitcoin': [
        '34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo',  # Binance 1
        'bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h',  # Binance 2
    ],
    'solana': [
        '5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9',  # Large holder
        'DRpbCBMxVnDK7maPM5tGv6MvB3v1sRMC86PZ8okm21hy',  # Exchange wallet
    ]
}

# Thresholds for whale activity
LARGE_TRANSFER_ETH = 100  # ETH
LARGE_TRANSFER_BTC = 10   # BTC
LARGE_TRANSFER_SOL = 10000  # SOL

class OnChainWhaleTracker(BaseAgent):
    """On-Chain Whale Tracker - Monitors whale wallets via blockchain APIs"""

    def __init__(self):
        """Initialize whale tracker"""
        super().__init__('whale_tracker')

        load_dotenv()

        # Get API keys (free tier)
        self.etherscan_key = os.getenv('ETHERSCAN_API_KEY')
        self.solscan_key = os.getenv('SOLSCAN_API_KEY')  # Optional, works without it

        # API endpoints
        self.etherscan_base = "https://api.etherscan.io/api"
        self.solscan_base = "https://api.solscan.io"
        self.blockchain_info_base = "https://blockchain.info"

        # Create data directory
        self.data_dir = PROJECT_ROOT / "src" / "data" / "hedge_monitor" / "whale_tracker"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # History file
        self.history_file = self.data_dir / "whale_activity.csv"
        self.load_history()

        if self.etherscan_key:
            cprint("🐋 Whale Tracker initialized with Etherscan API!", "white", "on_blue")
        else:
            cprint("🐋 Whale Tracker initialized (no Etherscan key - limited data)", "white", "on_yellow")
            print("💡 Get free key at: https://etherscan.io/apis")

    def load_history(self):
        """Load whale activity history"""
        try:
            if self.history_file.exists():
                self.history = pd.read_csv(self.history_file)
                print(f"📊 Loaded {len(self.history)} whale activity records")
            else:
                self.history = pd.DataFrame(columns=[
                    'timestamp', 'chain', 'whale_address', 'transfer_count',
                    'total_volume_usd', 'net_flow', 'signal'
                ])
                print("📝 Created new whale activity history")

        except Exception as e:
            print(f"❌ Error loading history: {str(e)}")
            self.history = pd.DataFrame()

    def get_eth_whale_transactions(self, address, limit=10):
        """Get recent transactions for Ethereum whale"""
        try:
            if not self.etherscan_key:
                return None

            url = self.etherscan_base
            params = {
                'module': 'account',
                'action': 'txlist',
                'address': address,
                'startblock': 0,
                'endblock': 99999999,
                'page': 1,
                'offset': limit,
                'sort': 'desc',
                'apikey': self.etherscan_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data['status'] == '1' and data['result']:
                df = pd.DataFrame(data['result'])
                df['value_eth'] = df['value'].astype(float) / 1e18
                df['timestamp'] = pd.to_datetime(df['timeStamp'].astype(int), unit='s')
                return df

            return None

        except Exception as e:
            print(f"⚠️ Error fetching ETH transactions for {address[:10]}: {str(e)}")
            return None

    def get_eth_balance(self, address):
        """Get current ETH balance"""
        try:
            if not self.etherscan_key:
                return 0

            url = self.etherscan_base
            params = {
                'module': 'account',
                'action': 'balance',
                'address': address,
                'tag': 'latest',
                'apikey': self.etherscan_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data['status'] == '1':
                balance_wei = float(data['result'])
                balance_eth = balance_wei / 1e18
                return balance_eth

            return 0

        except Exception as e:
            print(f"⚠️ Error fetching ETH balance: {str(e)}")
            return 0

    def get_sol_whale_transactions(self, address, limit=10):
        """Get recent transactions for Solana whale"""
        try:
            url = f"{self.solscan_base}/account/transaction"
            params = {
                'address': address,
                'limit': limit
            }

            # Solscan may work without API key for limited requests
            headers = {}
            if self.solscan_key:
                headers['token'] = self.solscan_key

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('data'):
                return pd.DataFrame(data['data'])

            return None

        except Exception as e:
            print(f"⚠️ Error fetching SOL transactions for {address[:10]}: {str(e)}")
            return None

    def analyze_whale_activity(self, chain='ethereum'):
        """Analyze whale activity on a specific chain"""
        try:
            whales = KNOWN_WHALES.get(chain, [])
            if not whales:
                return None

            print(f"\n🔍 Analyzing {len(whales)} {chain} whales...")

            activity_data = []

            for whale in whales:
                if chain == 'ethereum':
                    txs = self.get_eth_whale_transactions(whale, limit=20)

                    if txs is not None and not txs.empty:
                        # Analyze recent activity (last 24h)
                        recent = txs[txs['timestamp'] > datetime.now() - timedelta(hours=24)]

                        if not recent.empty:
                            # Calculate net flow (inbound - outbound)
                            inbound = recent[recent['to'].str.lower() == whale.lower()]['value_eth'].sum()
                            outbound = recent[recent['from'].str.lower() == whale.lower()]['value_eth'].sum()
                            net_flow = inbound - outbound

                            # Get current balance
                            balance = self.get_eth_balance(whale)

                            # Determine signal
                            if net_flow > LARGE_TRANSFER_ETH:
                                signal = "ACCUMULATION"
                            elif net_flow < -LARGE_TRANSFER_ETH:
                                signal = "DISTRIBUTION"
                            else:
                                signal = "NEUTRAL"

                            activity_data.append({
                                'chain': chain,
                                'whale_address': whale,
                                'transfer_count': len(recent),
                                'net_flow_eth': net_flow,
                                'balance_eth': balance,
                                'signal': signal,
                                'timestamp': datetime.now()
                            })

                elif chain == 'solana':
                    txs = self.get_sol_whale_transactions(whale, limit=20)
                    # Solana transaction analysis would go here
                    # (simplified for now)

                time.sleep(0.2)  # Rate limiting

            if activity_data:
                return pd.DataFrame(activity_data)

            return None

        except Exception as e:
            print(f"❌ Error analyzing whale activity: {str(e)}")
            traceback.print_exc()
            return None

    def detect_signals(self, whale_data):
        """Detect trading signals from whale activity"""
        try:
            if whale_data is None or whale_data.empty:
                return []

            signals = []

            # Count accumulation vs distribution
            accumulation_count = len(whale_data[whale_data['signal'] == 'ACCUMULATION'])
            distribution_count = len(whale_data[whale_data['signal'] == 'DISTRIBUTION'])

            total_whales = len(whale_data)

            # Strong accumulation signal
            if accumulation_count >= total_whales * 0.6:  # 60% or more accumulating
                signals.append({
                    'type': 'WHALE_ACCUMULATION',
                    'severity': 'HIGH',
                    'message': f'{accumulation_count}/{total_whales} whales are accumulating - potential bullish signal'
                })

            # Strong distribution signal
            elif distribution_count >= total_whales * 0.6:  # 60% or more distributing
                signals.append({
                    'type': 'WHALE_DISTRIBUTION',
                    'severity': 'HIGH',
                    'message': f'{distribution_count}/{total_whales} whales are distributing - potential bearish signal'
                })

            # Check for individual large transfers
            for _, whale in whale_data.iterrows():
                if abs(whale['net_flow_eth']) > LARGE_TRANSFER_ETH * 5:  # Very large transfer
                    direction = "accumulating" if whale['net_flow_eth'] > 0 else "distributing"
                    signals.append({
                        'type': f'LARGE_WHALE_TRANSFER',
                        'severity': 'MEDIUM',
                        'message': f'Whale {whale["whale_address"][:10]}... {direction} {abs(whale["net_flow_eth"]):.1f} ETH'
                    })

            return signals

        except Exception as e:
            print(f"❌ Error detecting signals: {str(e)}")
            return []

    def save_to_history(self, whale_data):
        """Save whale activity to history"""
        try:
            if whale_data is None or whale_data.empty:
                return

            # Append to history
            self.history = pd.concat([self.history, whale_data], ignore_index=True)

            # Keep only last 30 days
            cutoff = datetime.now() - timedelta(days=30)
            self.history = self.history[
                pd.to_datetime(self.history['timestamp']) > cutoff
            ]

            # Save to file
            self.history.to_csv(self.history_file, index=False)

        except Exception as e:
            print(f"❌ Error saving to history: {str(e)}")

    def run(self):
        """Run whale tracking cycle"""
        try:
            # Analyze Ethereum whales
            eth_data = self.analyze_whale_activity('ethereum')

            # Detect signals
            signals = self.detect_signals(eth_data)

            # Save to history
            if eth_data is not None:
                self.save_to_history(eth_data)

            # Print summary
            print("\n" + "╔" + "═" * 70 + "╗")
            print("║            🌙 Whale Tracker Summary 🐋                             ║")
            print("╠" + "═" * 70 + "╣")

            if eth_data is not None and not eth_data.empty:
                print(f"║  Tracked {len(eth_data)} whale addresses".ljust(72) + "║")
                print("╠" + "═" * 70 + "╣")

                # Show whale activity breakdown
                accumulating = len(eth_data[eth_data['signal'] == 'ACCUMULATION'])
                distributing = len(eth_data[eth_data['signal'] == 'DISTRIBUTION'])
                neutral = len(eth_data[eth_data['signal'] == 'NEUTRAL'])

                print(f"║  📈 Accumulating: {accumulating}".ljust(72) + "║")
                print(f"║  📉 Distributing: {distributing}".ljust(72) + "║")
                print(f"║  😴 Neutral: {neutral}".ljust(72) + "║")

                if signals:
                    print("╠" + "═" * 70 + "╣")
                    print(f"║  ⚠️  {len(signals)} Signal(s) Detected".ljust(72) + "║")

                    for signal in signals:
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
                print("║  ⚠️ Unable to fetch whale data".ljust(72) + "║")
                print("║  💡 Add ETHERSCAN_API_KEY to .env for tracking".ljust(72) + "║")

            print("╚" + "═" * 70 + "╝")

            return {
                'whale_data': eth_data,
                'signals': signals
            }

        except Exception as e:
            cprint(f"❌ Error in whale tracker: {str(e)}", "red")
            traceback.print_exc()
            return None

def main():
    """Main function for standalone testing"""
    cprint("\n🚀 On-Chain Whale Tracker Starting...", "white", "on_blue")

    tracker = OnChainWhaleTracker()

    while True:
        try:
            tracker.run()

            print(f"\n💤 Sleeping for 30 minutes...")
            time.sleep(30 * 60)

        except KeyboardInterrupt:
            print("\n👋 Whale Tracker shutting down gracefully...")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
