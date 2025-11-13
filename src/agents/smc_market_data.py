"""
🌙 Moon Dev's SMC Market Data Aggregator
Built with love by Moon Dev 🚀

This module aggregates live market data for SMC trading decisions:
- Open Interest (OI) changes
- Funding Rates
- Liquidation volumes and cascades
- Cumulative Volume Delta (CVD) for derivatives and spot
- Order flow analysis

Data sources:
- Moon Dev API (liquidations, funding, OI)
- BirdEye API (spot volume via nice_funcs)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.api import MoonDevAPI
from src import nice_funcs as n

# ============================================================================
# MARKET DATA AGGREGATOR
# ============================================================================

class SMCMarketDataAggregator:
    """Aggregates live market data for SMC trading decisions"""

    def __init__(self):
        """Initialize market data aggregator"""
        self.api = MoonDevAPI()
        print("🌙 SMC Market Data Aggregator initialized")

    # ========================================================================
    # LIQUIDATION DATA & CVD
    # ========================================================================

    def get_liquidation_cvd(self, limit: int = 10000, symbol: str = None) -> Dict:
        """
        Calculate Cumulative Volume Delta (CVD) from liquidation data.

        CVD = Cumulative (Long Liquidations - Short Liquidations)
        - Positive CVD = More longs liquidated = Bearish pressure
        - Negative CVD = More shorts liquidated = Bullish pressure

        Args:
            limit: Number of liquidation records to fetch
            symbol: Filter by symbol (e.g., 'BTC', 'ETH', 'SOL')

        Returns:
            Dictionary with CVD metrics
        """
        try:
            print(f"\n📊 Fetching liquidation data (limit={limit})...")

            # Get liquidation data
            liq_df = self.api.get_liquidation_data(limit=limit)

            if liq_df is None or liq_df.empty:
                print("⚠️ No liquidation data available")
                return None

            # Filter by symbol if provided
            if symbol and 'symbol' in liq_df.columns:
                liq_df = liq_df[liq_df['symbol'].str.contains(symbol, case=False, na=False)]

            if liq_df.empty:
                print(f"⚠️ No liquidation data for {symbol}")
                return None

            # Determine side and calculate CVD
            # Long liquidations = selling pressure (negative for CVD)
            # Short liquidations = buying pressure (positive for CVD)

            # Parse side column
            if 'side' in liq_df.columns:
                liq_df['side_clean'] = liq_df['side'].str.upper()

                # Calculate signed volume (shorts positive, longs negative)
                liq_df['signed_volume'] = np.where(
                    liq_df['side_clean'].str.contains('SHORT', na=False),
                    1,  # Short liquidation = bullish
                    -1  # Long liquidation = bearish
                )

                # Try to get USD size
                if 'usd_size' in liq_df.columns:
                    liq_df['usd_size'] = pd.to_numeric(liq_df['usd_size'], errors='coerce')
                    liq_df['signed_usd'] = liq_df['usd_size'] * liq_df['signed_volume']
                else:
                    # Fallback to price * size
                    if 'price' in liq_df.columns and 'size' in liq_df.columns:
                        liq_df['price'] = pd.to_numeric(liq_df['price'], errors='coerce')
                        liq_df['size'] = pd.to_numeric(liq_df['size'], errors='coerce')
                        liq_df['signed_usd'] = liq_df['price'] * liq_df['size'] * liq_df['signed_volume']
                    else:
                        print("⚠️ Cannot calculate USD volume from liquidations")
                        return None

                # Calculate CVD metrics
                total_longs = abs(liq_df[liq_df['signed_volume'] < 0]['signed_usd'].sum())
                total_shorts = abs(liq_df[liq_df['signed_volume'] > 0]['signed_usd'].sum())
                cvd_total = total_shorts - total_longs

                # Recent CVD (last 20% of data)
                recent_size = max(1, len(liq_df) // 5)
                recent_df = liq_df.tail(recent_size)
                recent_longs = abs(recent_df[recent_df['signed_volume'] < 0]['signed_usd'].sum())
                recent_shorts = abs(recent_df[recent_df['signed_volume'] > 0]['signed_usd'].sum())
                cvd_recent = recent_shorts - recent_longs

                # Calculate CVD trend
                cvd_trend = "BULLISH" if cvd_recent > 0 else "BEARISH" if cvd_recent < 0 else "NEUTRAL"

                # Liquidation cascade detection (high volume in short period)
                if 'datetime' in liq_df.columns or 'order_trade_time' in liq_df.columns:
                    time_col = 'datetime' if 'datetime' in liq_df.columns else 'order_trade_time'
                    liq_df[time_col] = pd.to_datetime(liq_df[time_col], unit='ms' if time_col == 'order_trade_time' else None)

                    # Group by 1-hour windows
                    liq_df.set_index(time_col, inplace=True)
                    hourly_vol = liq_df['signed_usd'].abs().resample('1H').sum()

                    # Detect cascade (volume spike > 3x average)
                    avg_hourly = hourly_vol.mean()
                    max_hourly = hourly_vol.max()
                    cascade_detected = max_hourly > (avg_hourly * 3)
                else:
                    cascade_detected = False

                return {
                    'cvd_total': cvd_total,
                    'cvd_recent': cvd_recent,
                    'cvd_trend': cvd_trend,
                    'total_long_liquidations': total_longs,
                    'total_short_liquidations': total_shorts,
                    'recent_long_liquidations': recent_longs,
                    'recent_short_liquidations': recent_shorts,
                    'liquidation_cascade': cascade_detected,
                    'records_analyzed': len(liq_df)
                }

            else:
                print("⚠️ Liquidation data missing 'side' column")
                return None

        except Exception as e:
            print(f"❌ Error calculating liquidation CVD: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    # ========================================================================
    # FUNDING RATE DATA
    # ========================================================================

    def get_funding_rates(self, symbol: str = None) -> Dict:
        """
        Get current funding rates from Moon Dev API.

        Funding rates indicate market sentiment:
        - Positive funding = Longs pay shorts = Bullish sentiment
        - Negative funding = Shorts pay longs = Bearish sentiment
        - Extreme funding (>0.1% or <-0.1%) = Potential reversal

        Args:
            symbol: Filter by symbol (e.g., 'BTC', 'ETH')

        Returns:
            Dictionary with funding rate metrics
        """
        try:
            print(f"\n💰 Fetching funding rate data...")

            funding_df = self.api.get_funding_data()

            if funding_df is None or funding_df.empty:
                print("⚠️ No funding data available")
                return None

            # Filter by symbol if provided
            if symbol and 'symbol' in funding_df.columns:
                funding_df = funding_df[funding_df['symbol'].str.contains(symbol, case=False, na=False)]

            if funding_df.empty:
                print(f"⚠️ No funding data for {symbol}")
                return None

            # Calculate funding metrics
            if 'funding_rate' in funding_df.columns:
                funding_df['funding_rate'] = pd.to_numeric(funding_df['funding_rate'], errors='coerce')

                avg_funding = funding_df['funding_rate'].mean()
                max_funding = funding_df['funding_rate'].max()
                min_funding = funding_df['funding_rate'].min()

                # Annualize (funding usually every 8 hours)
                avg_funding_annual = avg_funding * 3 * 365

                # Determine sentiment
                if avg_funding > 0.001:  # 0.1% per 8 hours
                    sentiment = "VERY_BULLISH"
                    interpretation = "Longs paying shorts heavily - potential for long squeeze"
                elif avg_funding > 0.0005:
                    sentiment = "BULLISH"
                    interpretation = "Positive funding - longs paying shorts"
                elif avg_funding < -0.001:
                    sentiment = "VERY_BEARISH"
                    interpretation = "Shorts paying longs heavily - potential for short squeeze"
                elif avg_funding < -0.0005:
                    sentiment = "BEARISH"
                    interpretation = "Negative funding - shorts paying longs"
                else:
                    sentiment = "NEUTRAL"
                    interpretation = "Balanced funding - no extreme positioning"

                return {
                    'avg_funding_rate': avg_funding,
                    'avg_funding_annual_pct': avg_funding_annual * 100,
                    'max_funding': max_funding,
                    'min_funding': min_funding,
                    'sentiment': sentiment,
                    'interpretation': interpretation,
                    'exchanges_tracked': len(funding_df)
                }

            else:
                print("⚠️ Funding data missing 'funding_rate' column")
                return None

        except Exception as e:
            print(f"❌ Error getting funding rates: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    # ========================================================================
    # OPEN INTEREST DATA
    # ========================================================================

    def get_open_interest_changes(self, symbol: str = None) -> Dict:
        """
        Get open interest changes from Moon Dev API.

        Open interest represents total open derivative contracts:
        - Rising OI + Rising price = Bullish (new longs)
        - Rising OI + Falling price = Bearish (new shorts)
        - Falling OI + Rising price = Short squeeze
        - Falling OI + Falling price = Long liquidations

        Args:
            symbol: Filter by symbol

        Returns:
            Dictionary with OI metrics
        """
        try:
            print(f"\n📈 Fetching open interest data...")

            oi_df = self.api.get_oi_data()

            if oi_df is None or oi_df.empty:
                print("⚠️ No OI data available")
                return None

            # Filter by symbol if provided
            if symbol and 'symbol' in oi_df.columns:
                oi_df = oi_df[oi_df['symbol'].str.contains(symbol, case=False, na=False)]

            if oi_df.empty:
                print(f"⚠️ No OI data for {symbol}")
                return None

            # Calculate OI metrics
            if 'open_interest' in oi_df.columns:
                oi_df['open_interest'] = pd.to_numeric(oi_df['open_interest'], errors='coerce')

                total_oi = oi_df['open_interest'].sum()

                # Calculate change if timestamp available
                if 'timestamp' in oi_df.columns or 'datetime' in oi_df.columns:
                    time_col = 'timestamp' if 'timestamp' in oi_df.columns else 'datetime'
                    oi_df[time_col] = pd.to_datetime(oi_df[time_col], unit='ms' if time_col == 'timestamp' else None)
                    oi_df = oi_df.sort_values(time_col)

                    # Compare last vs first half
                    mid = len(oi_df) // 2
                    early_oi = oi_df.iloc[:mid]['open_interest'].sum()
                    late_oi = oi_df.iloc[mid:]['open_interest'].sum()

                    if early_oi > 0:
                        oi_change_pct = ((late_oi - early_oi) / early_oi) * 100
                    else:
                        oi_change_pct = 0

                    oi_trend = "RISING" if oi_change_pct > 5 else "FALLING" if oi_change_pct < -5 else "STABLE"
                else:
                    oi_change_pct = 0
                    oi_trend = "UNKNOWN"

                return {
                    'total_open_interest': total_oi,
                    'oi_change_pct': oi_change_pct,
                    'oi_trend': oi_trend,
                    'exchanges_tracked': len(oi_df)
                }

            else:
                print("⚠️ OI data missing 'open_interest' column")
                return None

        except Exception as e:
            print(f"❌ Error getting open interest: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    # ========================================================================
    # COMPREHENSIVE MARKET DATA
    # ========================================================================

    def aggregate_market_data(self, symbol: str = 'BTC', liquidation_limit: int = 10000) -> Dict:
        """
        Aggregate all market data sources into a single report.

        Args:
            symbol: Symbol to analyze (e.g., 'BTC', 'ETH', 'SOL')
            liquidation_limit: Number of liquidation records to analyze

        Returns:
            Dictionary with all market data
        """
        print(f"\n{'='*70}")
        print(f"🌙 Moon Dev's SMC Market Data Aggregation - {symbol}")
        print(f"{'='*70}")

        market_data = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'liquidation_cvd': self.get_liquidation_cvd(limit=liquidation_limit, symbol=symbol),
            'funding_rates': self.get_funding_rates(symbol=symbol),
            'open_interest': self.get_open_interest_changes(symbol=symbol)
        }

        # Generate overall sentiment score
        sentiment_score = 0
        sentiment_reasons = []

        # CVD sentiment (±30 points)
        if market_data['liquidation_cvd']:
            cvd = market_data['liquidation_cvd']
            if cvd['cvd_trend'] == 'BULLISH':
                sentiment_score += 30
                sentiment_reasons.append("Bullish CVD (more shorts liquidated)")
            elif cvd['cvd_trend'] == 'BEARISH':
                sentiment_score -= 30
                sentiment_reasons.append("Bearish CVD (more longs liquidated)")

            if cvd['liquidation_cascade']:
                sentiment_reasons.append("⚠️ Liquidation cascade detected")

        # Funding rate sentiment (±25 points)
        if market_data['funding_rates']:
            funding = market_data['funding_rates']
            if funding['sentiment'] == 'VERY_BULLISH':
                sentiment_score -= 25  # Contrarian: too bullish = reversal risk
                sentiment_reasons.append("Extreme positive funding - long squeeze risk")
            elif funding['sentiment'] == 'BULLISH':
                sentiment_score += 15
                sentiment_reasons.append("Positive funding - bullish sentiment")
            elif funding['sentiment'] == 'VERY_BEARISH':
                sentiment_score += 25  # Contrarian: too bearish = short squeeze
                sentiment_reasons.append("Extreme negative funding - short squeeze potential")
            elif funding['sentiment'] == 'BEARISH':
                sentiment_score -= 15
                sentiment_reasons.append("Negative funding - bearish sentiment")

        # OI sentiment (±20 points)
        if market_data['open_interest']:
            oi = market_data['open_interest']
            if oi['oi_trend'] == 'RISING':
                sentiment_score += 20
                sentiment_reasons.append("Rising open interest - increasing leverage")
            elif oi['oi_trend'] == 'FALLING':
                sentiment_score -= 20
                sentiment_reasons.append("Falling open interest - deleveraging")

        # Overall interpretation
        if sentiment_score >= 40:
            overall_signal = "STRONG_BUY"
        elif sentiment_score >= 20:
            overall_signal = "BUY"
        elif sentiment_score >= -20:
            overall_signal = "NEUTRAL"
        elif sentiment_score >= -40:
            overall_signal = "SELL"
        else:
            overall_signal = "STRONG_SELL"

        market_data['sentiment_score'] = sentiment_score
        market_data['overall_signal'] = overall_signal
        market_data['sentiment_reasons'] = sentiment_reasons

        return market_data


def main():
    """Test the market data aggregator"""
    print("\n🌙 Moon Dev's SMC Market Data Aggregator Test")
    print("=" * 70)

    aggregator = SMCMarketDataAggregator()

    # Test with BTC
    result = aggregator.aggregate_market_data(symbol='BTC', liquidation_limit=5000)

    if result:
        print(f"\n📊 Market Data Summary for {result['symbol']}:")
        print(f"  Overall Signal: {result['overall_signal']}")
        print(f"  Sentiment Score: {result['sentiment_score']}")
        print(f"\n  Reasons:")
        for reason in result['sentiment_reasons']:
            print(f"    - {reason}")

        print("\n✅ Market data aggregation test complete!")
    else:
        print("\n⚠️ Failed to aggregate market data")


if __name__ == "__main__":
    main()
