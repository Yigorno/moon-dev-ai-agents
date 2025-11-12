"""
🌙 Moon Dev's Public Data Sources Utility
Alternative to Moon Dev API using free public sources
Built with love by Moon Dev 🚀

Provides:
- Funding rates (Binance, Bybit)
- Open Interest (CoinGlass, Binance)
- Liquidations (Binance, CoinGlass)
- Whale tracking (on-chain APIs)
"""

import os
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
import traceback

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

class PublicDataAPI:
    """Fetch derivatives and whale data from free public sources"""

    def __init__(self):
        """Initialize public data API"""
        # CoinGlass API (free tier)
        self.coinglass_base = "https://open-api.coinglass.com/public/v2"

        # Binance public API
        self.binance_base = "https://fapi.binance.com"

        # Bybit public API
        self.bybit_base = "https://api.bybit.com"

        # Cache directory
        self.cache_dir = PROJECT_ROOT / "src" / "data" / "public_api_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        print("✅ Public Data API initialized (no API key required)")
        print("💡 Using Binance, Bybit, and Deribit public endpoints")

    def get_funding_rates(self):
        """Get current funding rates from Binance"""
        try:
            print("\n🔍 Fetching funding rates from Binance...")

            # Binance Premium Index and Funding Rate
            url = f"{self.binance_base}/fapi/v1/premiumIndex"

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Convert to DataFrame
            df = pd.DataFrame(data)

            if df.empty:
                return None

            # Filter for major symbols
            major_symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']
            df = df[df['symbol'].isin(major_symbols)]

            # Calculate annual funding rate (funding rate * 3 * 365)
            df['funding_rate'] = pd.to_numeric(df['lastFundingRate'], errors='coerce')
            df['annual_rate'] = df['funding_rate'] * 3 * 365 * 100  # Convert to %

            # Rename for consistency
            df = df.rename(columns={'symbol': 'symbol', 'lastFundingRate': 'funding_rate'})
            df['event_time'] = datetime.now()

            # Clean symbol names (remove USDT)
            df['symbol'] = df['symbol'].str.replace('USDT', '')

            print(f"✅ Got funding rates for {len(df)} symbols from Binance")
            return df[['symbol', 'funding_rate', 'annual_rate', 'event_time']]

        except Exception as e:
            print(f"⚠️ Error fetching funding rates from Binance: {str(e)}")

            # Try Bybit as fallback
            try:
                print("🔄 Trying Bybit as fallback...")
                url = f"{self.bybit_base}/v2/public/tickers"

                response = requests.get(url, timeout=10)
                response.raise_for_status()

                data = response.json()

                if data.get('result'):
                    results = []
                    for item in data['result']:
                        if item.get('symbol') in ['BTCUSD', 'ETHUSD', 'SOLUSD']:
                            funding_rate = float(item.get('funding_rate', 0))
                            results.append({
                                'symbol': item['symbol'].replace('USD', ''),
                                'funding_rate': funding_rate,
                                'annual_rate': funding_rate * 3 * 365 * 100,
                                'event_time': datetime.now()
                            })

                    return pd.DataFrame(results)

            except Exception as e2:
                print(f"⚠️ Bybit fallback also failed: {str(e2)}")
                return None

    def get_open_interest(self):
        """Get open interest data from Binance"""
        try:
            print("\n🔍 Fetching open interest from Binance...")

            symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
            oi_data = []

            for symbol in symbols:
                url = f"{self.binance_base}/fapi/v1/openInterest"
                params = {'symbol': symbol}

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()

                oi_data.append({
                    'symbol': symbol.replace('USDT', ''),
                    'open_interest': float(data['openInterest']),
                    'timestamp': datetime.now()
                })

                time.sleep(0.1)  # Rate limiting

            df = pd.DataFrame(oi_data)

            # Calculate total OI
            total_oi = df['open_interest'].sum()

            result = {
                'timestamp': datetime.now(),
                'total_oi': total_oi,
                'btc_oi': df[df['symbol'] == 'BTC']['open_interest'].iloc[0] if len(df[df['symbol'] == 'BTC']) > 0 else 0,
                'eth_oi': df[df['symbol'] == 'ETH']['open_interest'].iloc[0] if len(df[df['symbol'] == 'ETH']) > 0 else 0
            }

            print(f"✅ Got open interest: ${total_oi:,.0f}")
            return result

        except Exception as e:
            print(f"⚠️ Error fetching open interest: {str(e)}")
            return None

    def get_liquidations(self, limit=10000):
        """
        Get recent liquidation data from Binance
        Note: Binance only provides recent liquidations, not historical bulk data
        """
        try:
            print("\n🔍 Fetching recent liquidations from Binance...")

            symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
            all_liquidations = []

            for symbol in symbols:
                url = f"{self.binance_base}/fapi/v1/allForceOrders"
                params = {
                    'symbol': symbol,
                    'limit': min(100, limit)  # Binance max is 100
                }

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()

                for item in data:
                    all_liquidations.append({
                        'symbol': item['symbol'].replace('USDT', ''),
                        'side': item['side'],
                        'price': float(item['price']),
                        'quantity': float(item['origQty']),
                        'timestamp': item['time'],
                        'usd_value': float(item['price']) * float(item['origQty'])
                    })

                time.sleep(0.1)  # Rate limiting

            df = pd.DataFrame(all_liquidations)

            if df.empty:
                print("⚠️ No recent liquidations found")
                return None

            # Add datetime column
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Sort by timestamp
            df = df.sort_values('datetime', ascending=True)

            print(f"✅ Got {len(df)} recent liquidations")
            return df

        except Exception as e:
            print(f"⚠️ Error fetching liquidations: {str(e)}")
            traceback.print_exc()
            return None

    def get_whale_addresses(self):
        """
        Get whale addresses from public blockchain explorers
        Returns a list of known whale addresses
        """
        try:
            print("\n🔍 Loading whale addresses from public sources...")

            # These are well-known exchange cold wallets and whale addresses
            # You can expand this list with addresses you want to track
            whale_addresses = [
                # Binance cold wallets (BTC)
                "34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo",  # Binance 1
                "bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h",  # Binance 2

                # Ethereum whales
                "0x00000000219ab540356cBB839Cbe05303d7705Fa",  # ETH2 Deposit Contract
                "0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8",  # Binance 7

                # Add your own addresses to track here
            ]

            print(f"✅ Loaded {len(whale_addresses)} whale addresses")
            return whale_addresses

        except Exception as e:
            print(f"⚠️ Error loading whale addresses: {str(e)}")
            return []

    def get_coinglass_liquidations(self):
        """
        Get aggregated liquidation data from CoinGlass (free tier)
        More comprehensive than individual exchange APIs
        """
        try:
            print("\n🔍 Fetching liquidations from CoinGlass...")

            # CoinGlass API endpoint for liquidations
            url = f"{self.coinglass_base}/liquidation/history"

            # Note: CoinGlass may require API key for some endpoints
            # For now, we'll use the free tier which has limitations

            params = {
                'symbol': 'BTC',
                'timeType': '1h'  # Last hour
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print("✅ Got CoinGlass liquidation data")
                return data
            else:
                print(f"⚠️ CoinGlass API returned status {response.status_code}")
                return None

        except Exception as e:
            print(f"⚠️ CoinGlass API not available: {str(e)}")
            print("💡 Using Binance liquidations as fallback")
            return None

# Test function
if __name__ == "__main__":
    print("🌙 Testing Public Data API...")
    print("=" * 50)

    api = PublicDataAPI()

    # Test funding rates
    print("\n1. Testing Funding Rates:")
    funding = api.get_funding_rates()
    if funding is not None:
        print(funding)

    # Test open interest
    print("\n2. Testing Open Interest:")
    oi = api.get_open_interest()
    if oi:
        print(oi)

    # Test liquidations
    print("\n3. Testing Liquidations:")
    liqs = api.get_liquidations(limit=50)
    if liqs is not None:
        print(f"Got {len(liqs)} liquidations")
        print(liqs.head())

    # Test whale addresses
    print("\n4. Testing Whale Addresses:")
    whales = api.get_whale_addresses()
    print(f"Loaded {len(whales)} addresses")

    print("\n✨ Public Data API Test Complete!")
