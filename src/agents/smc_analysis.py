"""
🌙 Moon Dev's Smart Money Concepts (SMC) Analysis Module
Built with love by Moon Dev 🚀

This module provides technical analysis functions for Smart Money Concepts including:
- Order Blocks (OB) - Institutional buying/selling zones
- Fair Value Gaps (FVG) - Price inefficiencies (bullish/bearish)
- Market Structure Break (MSB) - Major trend reversals
- Break of Structure (BoS) - Continuation patterns
- Swing High/Low detection

These concepts identify where institutional traders (smart money) are positioning.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# ============================================================================
# SWING POINT DETECTION
# ============================================================================

def detect_swing_highs_lows(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    Detect swing highs and lows in price data.

    A swing high is a high that is higher than 'window' bars on each side.
    A swing low is a low that is lower than 'window' bars on each side.

    Args:
        df: DataFrame with OHLCV data
        window: Number of bars to check on each side

    Returns:
        DataFrame with 'swing_high' and 'swing_low' columns added
    """
    df = df.copy()

    # Initialize columns
    df['swing_high'] = False
    df['swing_low'] = False
    df['swing_high_price'] = np.nan
    df['swing_low_price'] = np.nan

    # Need at least 2*window + 1 bars
    if len(df) < (2 * window + 1):
        return df

    # Check each potential swing point (skip first/last 'window' bars)
    for i in range(window, len(df) - window):
        # Check if it's a swing high
        is_swing_high = True
        current_high = df.iloc[i]['high']

        for j in range(1, window + 1):
            if current_high <= df.iloc[i - j]['high'] or current_high <= df.iloc[i + j]['high']:
                is_swing_high = False
                break

        if is_swing_high:
            df.loc[df.index[i], 'swing_high'] = True
            df.loc[df.index[i], 'swing_high_price'] = current_high

        # Check if it's a swing low
        is_swing_low = True
        current_low = df.iloc[i]['low']

        for j in range(1, window + 1):
            if current_low >= df.iloc[i - j]['low'] or current_low >= df.iloc[i + j]['low']:
                is_swing_low = False
                break

        if is_swing_low:
            df.loc[df.index[i], 'swing_low'] = True
            df.loc[df.index[i], 'swing_low_price'] = current_low

    return df


# ============================================================================
# ORDER BLOCKS DETECTION
# ============================================================================

def detect_order_blocks(df: pd.DataFrame, volume_multiplier: float = 1.5, lookback: int = 20) -> pd.DataFrame:
    """
    Detect order blocks - zones where institutions placed large orders.

    Order blocks are identified by:
    1. High volume (above average)
    2. Strong price movement away from the zone
    3. Occurs at swing highs/lows

    Args:
        df: DataFrame with OHLCV data and swing points
        volume_multiplier: Volume must be this times average volume
        lookback: Number of bars for average volume calculation

    Returns:
        DataFrame with order block information
    """
    df = df.copy()

    # Calculate average volume
    df['avg_volume'] = df['volume'].rolling(window=lookback, min_periods=1).mean()

    # Initialize order block columns
    df['ob_bullish'] = False
    df['ob_bearish'] = False
    df['ob_bullish_high'] = np.nan
    df['ob_bullish_low'] = np.nan
    df['ob_bearish_high'] = np.nan
    df['ob_bearish_low'] = np.nan

    # Detect bullish order blocks (at swing lows with high volume)
    for i in range(1, len(df)):
        if df.iloc[i].get('swing_low', False):
            # Check if volume is high
            if df.iloc[i]['volume'] >= df.iloc[i]['avg_volume'] * volume_multiplier:
                # Check if price moved up after this point (next 3 bars)
                if i + 3 < len(df):
                    future_highs = df.iloc[i+1:i+4]['high'].max()
                    if future_highs > df.iloc[i]['high'] * 1.01:  # At least 1% move up
                        df.loc[df.index[i], 'ob_bullish'] = True
                        df.loc[df.index[i], 'ob_bullish_low'] = df.iloc[i]['low']
                        df.loc[df.index[i], 'ob_bullish_high'] = df.iloc[i]['high']

    # Detect bearish order blocks (at swing highs with high volume)
    for i in range(1, len(df)):
        if df.iloc[i].get('swing_high', False):
            # Check if volume is high
            if df.iloc[i]['volume'] >= df.iloc[i]['avg_volume'] * volume_multiplier:
                # Check if price moved down after this point (next 3 bars)
                if i + 3 < len(df):
                    future_lows = df.iloc[i+1:i+4]['low'].min()
                    if future_lows < df.iloc[i]['low'] * 0.99:  # At least 1% move down
                        df.loc[df.index[i], 'ob_bearish'] = True
                        df.loc[df.index[i], 'ob_bearish_low'] = df.iloc[i]['low']
                        df.loc[df.index[i], 'ob_bearish_high'] = df.iloc[i]['high']

    return df


# ============================================================================
# FAIR VALUE GAPS (FVG) DETECTION
# ============================================================================

def detect_fair_value_gaps(df: pd.DataFrame, min_gap_pct: float = 0.5) -> pd.DataFrame:
    """
    Detect Fair Value Gaps (FVG) - price inefficiencies that often get filled.

    A Bullish FVG occurs when:
    - Current bar's low > Previous bar's high (gap up)
    - Often happens with strong buying pressure

    A Bearish FVG occurs when:
    - Current bar's high < Previous bar's low (gap down)
    - Often happens with strong selling pressure

    Args:
        df: DataFrame with OHLCV data
        min_gap_pct: Minimum gap size as percentage of price

    Returns:
        DataFrame with FVG information
    """
    df = df.copy()

    # Initialize FVG columns
    df['fvg_bullish'] = False
    df['fvg_bearish'] = False
    df['fvg_bullish_bottom'] = np.nan
    df['fvg_bullish_top'] = np.nan
    df['fvg_bearish_bottom'] = np.nan
    df['fvg_bearish_top'] = np.nan

    # Need at least 3 bars for FVG detection
    for i in range(2, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i-1]
        prev2 = df.iloc[i-2]

        # Bullish FVG: Current low > Two bars ago high (gap between bars)
        if current['low'] > prev2['high']:
            gap_size_pct = ((current['low'] - prev2['high']) / prev2['high']) * 100
            if gap_size_pct >= min_gap_pct:
                df.loc[df.index[i], 'fvg_bullish'] = True
                df.loc[df.index[i], 'fvg_bullish_bottom'] = prev2['high']
                df.loc[df.index[i], 'fvg_bullish_top'] = current['low']

        # Bearish FVG: Current high < Two bars ago low (gap between bars)
        if current['high'] < prev2['low']:
            gap_size_pct = ((prev2['low'] - current['high']) / current['high']) * 100
            if gap_size_pct >= min_gap_pct:
                df.loc[df.index[i], 'fvg_bearish'] = True
                df.loc[df.index[i], 'fvg_bearish_bottom'] = current['high']
                df.loc[df.index[i], 'fvg_bearish_top'] = prev2['low']

    return df


# ============================================================================
# MARKET STRUCTURE (MSB & BoS)
# ============================================================================

def detect_market_structure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect Market Structure Breaks (MSB) and Break of Structure (BoS).

    MSB (Market Structure Break):
    - In uptrend: Price breaks below previous swing low (reversal to downtrend)
    - In downtrend: Price breaks above previous swing high (reversal to uptrend)

    BoS (Break of Structure):
    - In uptrend: Price breaks above previous swing high (continuation)
    - In downtrend: Price breaks below previous swing low (continuation)

    Args:
        df: DataFrame with OHLCV data and swing points

    Returns:
        DataFrame with market structure information
    """
    df = df.copy()

    # Initialize columns
    df['msb_bullish'] = False  # Break above in downtrend (reversal to uptrend)
    df['msb_bearish'] = False  # Break below in uptrend (reversal to downtrend)
    df['bos_bullish'] = False  # Break above in uptrend (continuation)
    df['bos_bearish'] = False  # Break below in downtrend (continuation)
    df['trend'] = 'neutral'  # Current trend state

    # Track swing highs and lows
    last_swing_high = None
    last_swing_low = None
    current_trend = 'neutral'

    for i in range(len(df)):
        row = df.iloc[i]

        # Update swing points
        if row.get('swing_high', False):
            last_swing_high = row['swing_high_price']
        if row.get('swing_low', False):
            last_swing_low = row['swing_low_price']

        # Need both swing high and low to determine structure
        if last_swing_high is None or last_swing_low is None:
            df.loc[df.index[i], 'trend'] = current_trend
            continue

        current_high = row['high']
        current_low = row['low']

        # Detect breaks based on current trend
        if current_trend == 'uptrend' or current_trend == 'neutral':
            # Check for BoS (bullish continuation) - break above last swing high
            if current_high > last_swing_high:
                df.loc[df.index[i], 'bos_bullish'] = True
                current_trend = 'uptrend'

            # Check for MSB (bearish reversal) - break below last swing low
            elif current_low < last_swing_low:
                df.loc[df.index[i], 'msb_bearish'] = True
                current_trend = 'downtrend'

        elif current_trend == 'downtrend':
            # Check for MSB (bullish reversal) - break above last swing high
            if current_high > last_swing_high:
                df.loc[df.index[i], 'msb_bullish'] = True
                current_trend = 'uptrend'

            # Check for BoS (bearish continuation) - break below last swing low
            elif current_low < last_swing_low:
                df.loc[df.index[i], 'bos_bearish'] = True
                current_trend = 'downtrend'

        df.loc[df.index[i], 'trend'] = current_trend

    return df


# ============================================================================
# COMPREHENSIVE SMC ANALYSIS
# ============================================================================

def analyze_smc_complete(df: pd.DataFrame,
                         swing_window: int = 5,
                         ob_volume_mult: float = 1.5,
                         ob_lookback: int = 20,
                         fvg_min_gap: float = 0.5) -> Dict:
    """
    Run complete SMC analysis on OHLCV data.

    Args:
        df: DataFrame with OHLCV data (columns: open, high, low, close, volume)
        swing_window: Window for swing detection
        ob_volume_mult: Volume multiplier for order blocks
        ob_lookback: Lookback period for order blocks
        fvg_min_gap: Minimum gap percentage for FVG

    Returns:
        Dictionary with:
        - df: Annotated DataFrame with all SMC indicators
        - summary: Dictionary with current SMC state
    """
    # Ensure lowercase column names
    df = df.copy()
    df.columns = df.columns.str.lower()

    # Step 1: Detect swing points
    df = detect_swing_highs_lows(df, window=swing_window)

    # Step 2: Detect order blocks
    df = detect_order_blocks(df, volume_multiplier=ob_volume_mult, lookback=ob_lookback)

    # Step 3: Detect fair value gaps
    df = detect_fair_value_gaps(df, min_gap_pct=fvg_min_gap)

    # Step 4: Detect market structure
    df = detect_market_structure(df)

    # Step 5: Generate summary
    current_price = df.iloc[-1]['close']

    # Find active order blocks (last 20 bars)
    recent_df = df.tail(20)
    bullish_obs = recent_df[recent_df['ob_bullish'] == True]
    bearish_obs = recent_df[recent_df['ob_bearish'] == True]

    # Find recent FVGs (last 10 bars)
    recent_fvg = df.tail(10)
    bullish_fvgs = recent_fvg[recent_fvg['fvg_bullish'] == True]
    bearish_fvgs = recent_fvg[recent_fvg['fvg_bearish'] == True]

    # Find recent structure breaks (last 5 bars)
    recent_structure = df.tail(5)
    msb_bullish = len(recent_structure[recent_structure['msb_bullish'] == True])
    msb_bearish = len(recent_structure[recent_structure['msb_bearish'] == True])
    bos_bullish = len(recent_structure[recent_structure['bos_bullish'] == True])
    bos_bearish = len(recent_structure[recent_structure['bos_bearish'] == True])

    # Current trend
    current_trend = df.iloc[-1]['trend']

    summary = {
        'current_price': current_price,
        'current_trend': current_trend,
        'bullish_order_blocks': len(bullish_obs),
        'bearish_order_blocks': len(bearish_obs),
        'bullish_fvgs': len(bullish_fvgs),
        'bearish_fvgs': len(bearish_fvgs),
        'msb_bullish_recent': msb_bullish,
        'msb_bearish_recent': msb_bearish,
        'bos_bullish_recent': bos_bullish,
        'bos_bearish_recent': bos_bearish,
        'bullish_signals': len(bullish_obs) + len(bullish_fvgs) + bos_bullish,
        'bearish_signals': len(bearish_obs) + len(bearish_fvgs) + bos_bearish,
    }

    return {
        'df': df,
        'summary': summary
    }


# ============================================================================
# SCORING SYSTEM
# ============================================================================

def calculate_smc_score(summary: Dict) -> Dict:
    """
    Calculate SMC score from -100 (very bearish) to +100 (very bullish).

    Args:
        summary: SMC analysis summary

    Returns:
        Dictionary with score and interpretation
    """
    score = 0

    # Trend (±30 points)
    if summary['current_trend'] == 'uptrend':
        score += 30
    elif summary['current_trend'] == 'downtrend':
        score -= 30

    # Order blocks (±20 points)
    ob_diff = summary['bullish_order_blocks'] - summary['bearish_order_blocks']
    score += min(20, max(-20, ob_diff * 10))

    # Fair value gaps (±20 points)
    fvg_diff = summary['bullish_fvgs'] - summary['bearish_fvgs']
    score += min(20, max(-20, fvg_diff * 10))

    # Market structure breaks (±15 points)
    msb_diff = summary['msb_bullish_recent'] - summary['msb_bearish_recent']
    score += min(15, max(-15, msb_diff * 15))

    # Break of structure (±15 points)
    bos_diff = summary['bos_bullish_recent'] - summary['bos_bearish_recent']
    score += min(15, max(-15, bos_diff * 15))

    # Interpretation
    if score >= 60:
        signal = "STRONG_BUY"
        interpretation = "Strong bullish SMC confluence"
    elif score >= 30:
        signal = "BUY"
        interpretation = "Bullish SMC setup"
    elif score >= -30:
        signal = "NEUTRAL"
        interpretation = "Mixed SMC signals"
    elif score >= -60:
        signal = "SELL"
        interpretation = "Bearish SMC setup"
    else:
        signal = "STRONG_SELL"
        interpretation = "Strong bearish SMC confluence"

    return {
        'score': score,
        'signal': signal,
        'interpretation': interpretation
    }


if __name__ == "__main__":
    # Example usage with sample data
    print("🌙 Moon Dev's SMC Analysis Module")
    print("=" * 60)

    # Create sample OHLCV data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    np.random.seed(42)

    # Generate realistic price movement
    close_prices = 100 + np.cumsum(np.random.randn(100) * 2)

    sample_df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices + np.random.randn(100) * 0.5,
        'high': close_prices + np.abs(np.random.randn(100)) * 2,
        'low': close_prices - np.abs(np.random.randn(100)) * 2,
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 100)
    })

    # Run analysis
    print("\n📊 Running SMC Analysis...")
    result = analyze_smc_complete(sample_df)

    print("\n🎯 SMC Summary:")
    for key, value in result['summary'].items():
        print(f"  {key}: {value}")

    print("\n📈 SMC Score:")
    score_result = calculate_smc_score(result['summary'])
    for key, value in score_result.items():
        print(f"  {key}: {value}")

    print("\n✅ SMC Analysis Module Test Complete!")
