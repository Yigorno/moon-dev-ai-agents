"""
🌙 Moon Dev's Order Blocks Monitor
Part of the Hedge Monitor System
Built with love by Moon Dev 🚀

Tracks institutional order blocks from TradingLite to identify key support/resistance.
Uses web scraping since TradingLite doesn't provide public API.
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
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src import config
from src.agents.base_agent import BaseAgent

# Try to import selenium (optional)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not installed. Install with: pip install selenium")

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# TradingLite configuration
TRADINGLITE_BASE = "https://tradinglite.com"

# Symbols to track
TRACKED_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

# Order block significance threshold
SIGNIFICANT_VOLUME_MULTIPLIER = 2.0  # Order blocks 2x avg volume

class OrderBlocksMonitor(BaseAgent):
    """Order Blocks Monitor - Tracks institutional order blocks from TradingLite"""

    def __init__(self):
        """Initialize order blocks monitor"""
        super().__init__('orderblocks_monitor')

        load_dotenv()

        # Check if Selenium is available
        if not SELENIUM_AVAILABLE:
            cprint("⚠️ Order Blocks Monitor requires Selenium!", "yellow")
            print("Install with: pip install selenium webdriver-manager")
            self.driver = None
        else:
            # Initialize Selenium WebDriver
            try:
                chrome_options = Options()
                chrome_options.add_argument('--headless')  # Run in background
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')

                # Try to use chromedriver
                self.driver = webdriver.Chrome(options=chrome_options)
                cprint("✅ Selenium WebDriver initialized", "green")
            except Exception as e:
                print(f"⚠️ Could not initialize WebDriver: {str(e)}")
                print("💡 Install chromedriver or use: pip install webdriver-manager")
                self.driver = None

        # Create data directory
        self.data_dir = PROJECT_ROOT / "src" / "data" / "hedge_monitor" / "order_blocks"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # History file
        self.history_file = self.data_dir / "orderblocks_history.csv"
        self.load_history()

        # TradingLite credentials (if you have account)
        self.tradinglite_email = os.getenv('TRADINGLITE_EMAIL')
        self.tradinglite_password = os.getenv('TRADINGLITE_PASSWORD')

        cprint("📦 Order Blocks Monitor initialized!", "white", "on_blue")

    def load_history(self):
        """Load order blocks history"""
        try:
            if self.history_file.exists():
                self.history = pd.read_csv(self.history_file)
                print(f"📊 Loaded {len(self.history)} order block records")
            else:
                self.history = pd.DataFrame(columns=[
                    'timestamp', 'symbol', 'price_level', 'type',
                    'volume', 'strength', 'status'
                ])
                print("📝 Created new order blocks history")

        except Exception as e:
            print(f"❌ Error loading history: {str(e)}")
            self.history = pd.DataFrame()

    def login_tradinglite(self):
        """Login to TradingLite (if credentials provided)"""
        try:
            if not self.driver:
                return False

            if not self.tradinglite_email or not self.tradinglite_password:
                print("💡 No TradingLite credentials - using public view")
                return False

            print("\n🔐 Logging into TradingLite...")

            # Navigate to login page
            self.driver.get(f"{TRADINGLITE_BASE}/login")
            time.sleep(2)

            # Find and fill email field
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_input.send_keys(self.tradinglite_email)

            # Find and fill password field
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(self.tradinglite_password)

            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()

            time.sleep(3)

            print("✅ Logged into TradingLite")
            return True

        except Exception as e:
            print(f"⚠️ Could not login to TradingLite: {str(e)}")
            return False

    def scrape_orderblocks_selenium(self, symbol='BTCUSDT'):
        """Scrape order blocks using Selenium"""
        try:
            if not self.driver:
                print("❌ Selenium not available")
                return None

            print(f"\n🔍 Scraping order blocks for {symbol}...")

            # Navigate to TradingLite chart
            url = f"{TRADINGLITE_BASE}/chart/{symbol}"
            self.driver.get(url)
            time.sleep(5)  # Wait for page to load

            # Look for order block elements (this depends on TradingLite's HTML structure)
            # You may need to inspect the page and adjust selectors
            try:
                # Try to find order block data in the page
                # This is a placeholder - actual implementation depends on TradingLite's structure
                page_source = self.driver.page_source

                # Look for order block data patterns
                # TradingLite may expose data in JavaScript variables or data attributes

                # Example: look for data in script tags
                scripts = self.driver.find_elements(By.TAG_NAME, 'script')
                for script in scripts:
                    content = script.get_attribute('innerHTML')
                    if 'orderblock' in content.lower() or 'order_block' in content.lower():
                        # Parse order block data
                        # This is highly dependent on TradingLite's implementation
                        pass

                print("✅ Page loaded, but order block parsing not yet implemented")
                print("💡 Need to inspect TradingLite's HTML structure to extract data")

                return None

            except Exception as e:
                print(f"⚠️ Error extracting order blocks: {str(e)}")
                return None

        except Exception as e:
            print(f"❌ Error scraping with Selenium: {str(e)}")
            traceback.print_exc()
            return None

    def scrape_orderblocks_api_attempt(self, symbol='BTCUSDT'):
        """
        Attempt to find TradingLite API endpoints
        (TradingLite may have internal APIs we can use)
        """
        try:
            print(f"\n🔍 Attempting API fetch for {symbol} order blocks...")

            # TradingLite might have internal API endpoints
            # Common patterns to try:
            api_endpoints = [
                f"{TRADINGLITE_BASE}/api/orderblocks/{symbol}",
                f"{TRADINGLITE_BASE}/api/v1/orderblocks/{symbol}",
                f"{TRADINGLITE_BASE}/api/charts/{symbol}/orderblocks",
            ]

            for endpoint in api_endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        print(f"✅ Found working endpoint: {endpoint}")
                        data = response.json()
                        return data
                except:
                    continue

            print("⚠️ No public API endpoints found")
            return None

        except Exception as e:
            print(f"❌ Error attempting API fetch: {str(e)}")
            return None

    def generate_mock_orderblocks(self, symbol='BTCUSDT', current_price=None):
        """
        Generate mock order blocks for demonstration
        (Replace with actual TradingLite data once scraping works)
        """
        try:
            print(f"\n🎲 Generating mock order blocks for {symbol}...")

            # Get current price (you'd get this from your data source)
            if current_price is None:
                # Default prices for demo
                prices = {
                    'BTCUSDT': 95000,
                    'ETHUSDT': 3500,
                    'SOLUSDT': 190
                }
                current_price = prices.get(symbol, 100)

            # Generate mock order blocks (support and resistance levels)
            order_blocks = []

            # Support levels (below current price)
            support_levels = [
                current_price * 0.95,  # 5% below
                current_price * 0.90,  # 10% below
                current_price * 0.85,  # 15% below
            ]

            for level in support_levels:
                order_blocks.append({
                    'symbol': symbol,
                    'price_level': level,
                    'type': 'SUPPORT',
                    'volume': 1000000,  # Mock volume
                    'strength': 'STRONG' if level == support_levels[0] else 'MEDIUM',
                    'status': 'ACTIVE',
                    'timestamp': datetime.now()
                })

            # Resistance levels (above current price)
            resistance_levels = [
                current_price * 1.05,  # 5% above
                current_price * 1.10,  # 10% above
                current_price * 1.15,  # 15% above
            ]

            for level in resistance_levels:
                order_blocks.append({
                    'symbol': symbol,
                    'price_level': level,
                    'type': 'RESISTANCE',
                    'volume': 1000000,  # Mock volume
                    'strength': 'STRONG' if level == resistance_levels[0] else 'MEDIUM',
                    'status': 'ACTIVE',
                    'timestamp': datetime.now()
                })

            return pd.DataFrame(order_blocks)

        except Exception as e:
            print(f"❌ Error generating mock data: {str(e)}")
            return None

    def analyze_orderblocks(self, orderblocks_df, current_price):
        """Analyze order blocks for trading signals"""
        try:
            if orderblocks_df is None or orderblocks_df.empty:
                return []

            signals = []

            # Find nearest support and resistance
            supports = orderblocks_df[orderblocks_df['type'] == 'SUPPORT'].sort_values('price_level', ascending=False)
            resistances = orderblocks_df[orderblocks_df['type'] == 'RESISTANCE'].sort_values('price_level')

            if not supports.empty:
                nearest_support = supports.iloc[0]
                distance_to_support = ((current_price - nearest_support['price_level']) / current_price) * 100

                if distance_to_support < 2:  # Within 2% of support
                    signals.append({
                        'type': 'NEAR_SUPPORT',
                        'severity': 'HIGH' if nearest_support['strength'] == 'STRONG' else 'MEDIUM',
                        'message': f"Price near {nearest_support['strength']} support at ${nearest_support['price_level']:.2f} ({distance_to_support:.1f}% below) - potential bounce"
                    })

            if not resistances.empty:
                nearest_resistance = resistances.iloc[0]
                distance_to_resistance = ((nearest_resistance['price_level'] - current_price) / current_price) * 100

                if distance_to_resistance < 2:  # Within 2% of resistance
                    signals.append({
                        'type': 'NEAR_RESISTANCE',
                        'severity': 'HIGH' if nearest_resistance['strength'] == 'STRONG' else 'MEDIUM',
                        'message': f"Price near {nearest_resistance['strength']} resistance at ${nearest_resistance['price_level']:.2f} ({distance_to_resistance:.1f}% above) - potential rejection"
                    })

            return signals

        except Exception as e:
            print(f"❌ Error analyzing order blocks: {str(e)}")
            return []

    def save_to_history(self, orderblocks_df):
        """Save order blocks to history"""
        try:
            if orderblocks_df is None or orderblocks_df.empty:
                return

            # Append to history
            self.history = pd.concat([self.history, orderblocks_df], ignore_index=True)

            # Keep only last 7 days
            cutoff = datetime.now() - timedelta(days=7)
            self.history = self.history[
                pd.to_datetime(self.history['timestamp']) > cutoff
            ]

            # Save to file
            self.history.to_csv(self.history_file, index=False)

        except Exception as e:
            print(f"❌ Error saving to history: {str(e)}")

    def run(self):
        """Run order blocks monitoring cycle"""
        try:
            all_orderblocks = []
            all_signals = []

            for symbol in TRACKED_SYMBOLS:
                # Try actual scraping first (if implemented)
                orderblocks = self.scrape_orderblocks_selenium(symbol)

                # Fall back to mock data for demonstration
                if orderblocks is None:
                    orderblocks = self.generate_mock_orderblocks(symbol)

                if orderblocks is not None:
                    all_orderblocks.append(orderblocks)

                    # Analyze for signals (would need current price from your data source)
                    # For now, using mock current price
                    current_price = orderblocks['price_level'].mean()  # Placeholder
                    signals = self.analyze_orderblocks(orderblocks, current_price)
                    all_signals.extend(signals)

                    # Save to history
                    self.save_to_history(orderblocks)

            # Combine all order blocks
            if all_orderblocks:
                combined_df = pd.concat(all_orderblocks, ignore_index=True)
            else:
                combined_df = None

            # Print summary
            print("\n" + "╔" + "═" * 70 + "╗")
            print("║            🌙 Order Blocks Monitor Summary 📦                      ║")
            print("╠" + "═" * 70 + "╣")

            if combined_df is not None and not combined_df.empty:
                print(f"║  Tracking {len(combined_df)} order blocks across {len(TRACKED_SYMBOLS)} symbols".ljust(72) + "║")
                print("╠" + "═" * 70 + "╣")

                # Show breakdown by type
                supports = len(combined_df[combined_df['type'] == 'SUPPORT'])
                resistances = len(combined_df[combined_df['type'] == 'RESISTANCE'])

                print(f"║  📊 Support Levels: {supports}".ljust(72) + "║")
                print(f"║  📊 Resistance Levels: {resistances}".ljust(72) + "║")

                if all_signals:
                    print("╠" + "═" * 70 + "╣")
                    print(f"║  ⚠️  {len(all_signals)} Signal(s) Detected".ljust(72) + "║")

                    for signal in all_signals:
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
                    print("║  ✅ No significant order block proximity detected".ljust(72) + "║")

                print("╠" + "═" * 70 + "╣")
                print("║  💡 NOTE: Currently using mock data for demonstration".ljust(72) + "║")
                print("║     Actual TradingLite scraping requires further setup".ljust(72) + "║")
            else:
                print("║  ⚠️ No order block data available".ljust(72) + "║")

            print("╚" + "═" * 70 + "╝")

            return {
                'orderblocks': combined_df,
                'signals': all_signals
            }

        except Exception as e:
            cprint(f"❌ Error in order blocks monitor: {str(e)}", "red")
            traceback.print_exc()
            return None

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function for standalone testing"""
    cprint("\n🚀 Order Blocks Monitor Starting...", "white", "on_blue")

    monitor = OrderBlocksMonitor()

    try:
        while True:
            try:
                monitor.run()

                print(f"\n💤 Sleeping for 30 minutes...")
                time.sleep(30 * 60)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error in main loop: {str(e)}")
                time.sleep(60)

    finally:
        print("\n🧹 Cleaning up...")
        monitor.cleanup()
        print("👋 Order Blocks Monitor shutting down gracefully...")

if __name__ == "__main__":
    main()
