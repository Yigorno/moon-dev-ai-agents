"""
🌙 Moon Dev's Smart Money Concepts (SMC) Trading Agent
Built with love by Moon Dev 🚀

This agent combines technical SMC analysis with live market data to make
intelligent trading decisions using AI.

DUAL ANALYSIS SYSTEM:
1. Technical SMC Analysis: Order Blocks, FVG, MSB, BoS from OHLCV data
2. Live Market Data: Open Interest, Funding Rates, Liquidations, CVD

DECISION METHODS:
- LLM Analysis: AI analyzes both signals and makes trading decision
- Scoring System: Numerical scoring of SMC + market data
- Hybrid: Both methods for confirmation

Built with love by Moon Dev 🚀
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from termcolor import colored, cprint
from dotenv import load_dotenv
import time
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src import config
from src import nice_funcs as n
from src.agents.base_agent import BaseAgent
from src.models.model_factory import ModelFactory
from src.agents.smc_analysis import analyze_smc_complete, calculate_smc_score
from src.agents.smc_market_data import SMCMarketDataAggregator

# Load environment
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Exchange selection
EXCHANGE = "ASTER"  # Options: "ASTER", "HYPERLIQUID", "SOLANA"

# Trading mode
PAPER_TRADING = True  # Set to False for live trading (USE WITH CAUTION!)

# Position sizing
POSITION_SIZE_PCT = 30  # % of balance to use per position
LEVERAGE = 5  # Leverage for Aster/HyperLiquid (ignored on Solana)

# Risk management
STOP_LOSS_PCT = 5.0  # Stop loss percentage
TAKE_PROFIT_PCT = 10.0  # Take profit percentage

# AI settings
AI_MODEL_PROVIDER = 'anthropic'  # Options: anthropic, openai, deepseek, groq, ollama
AI_TEMPERATURE = 0.7
AI_MAX_TOKENS = 2048

# Data settings
OHLCV_TIMEFRAME = '15m'  # Timeframe for OHLCV data
OHLCV_DAYS_BACK = 3  # Days of historical data
LIQUIDATION_LIMIT = 10000  # Number of liquidation records to analyze

# Decision method
DECISION_METHOD = 'LLM'  # Options: 'LLM', 'SCORING', 'HYBRID'

# Confidence threshold
MIN_CONFIDENCE = 70  # Minimum confidence to execute trade (0-100)

# ============================================================================
# SMC TRADING AGENT
# ============================================================================

class SMCTradingAgent(BaseAgent):
    """Smart Money Concepts Trading Agent"""

    def __init__(self):
        """Initialize SMC Trading Agent"""
        super().__init__('smc_trading')

        # Initialize market data aggregator
        self.market_data_agg = SMCMarketDataAggregator()

        # Initialize AI model
        self.model = ModelFactory.create_model(AI_MODEL_PROVIDER)

        # Create data directory
        self.data_dir = Path(__file__).parent.parent / "data" / "smc_trading"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Trade history
        self.trade_history_file = self.data_dir / "trade_history.csv"
        self.load_trade_history()

        cprint("🌙 SMC Trading Agent initialized!", "white", "on_blue")
        print(f"  Exchange: {EXCHANGE}")
        print(f"  Paper Trading: {PAPER_TRADING}")
        print(f"  Decision Method: {DECISION_METHOD}")
        print(f"  AI Model: {AI_MODEL_PROVIDER}")

    def load_trade_history(self):
        """Load trade history from file"""
        try:
            if self.trade_history_file.exists():
                self.trade_history = pd.read_csv(self.trade_history_file)
                print(f"📊 Loaded {len(self.trade_history)} historical trades")
            else:
                self.trade_history = pd.DataFrame(columns=[
                    'timestamp', 'symbol', 'action', 'price', 'size',
                    'smc_score', 'market_score', 'confidence', 'reasoning'
                ])
                print("📝 Created new trade history")
        except Exception as e:
            print(f"⚠️ Error loading trade history: {str(e)}")
            self.trade_history = pd.DataFrame()

    def save_trade(self, trade_data: dict):
        """Save trade to history"""
        try:
            new_trade = pd.DataFrame([trade_data])
            self.trade_history = pd.concat([self.trade_history, new_trade], ignore_index=True)
            self.trade_history.to_csv(self.trade_history_file, index=False)
            print(f"💾 Trade saved to history")
        except Exception as e:
            print(f"⚠️ Error saving trade: {str(e)}")

    def analyze_token(self, token_address: str, symbol: str = None) -> dict:
        """
        Run complete SMC + Market Data analysis on a token.

        Args:
            token_address: Solana token address
            symbol: Symbol for market data (e.g., 'BTC', 'SOL')

        Returns:
            Dictionary with analysis results
        """
        try:
            print(f"\n{'='*70}")
            print(f"🌙 SMC Analysis for {symbol or token_address[:8]}")
            print(f"{'='*70}")

            # Step 1: Get OHLCV data
            print(f"\n[1/3] 📊 Fetching OHLCV data ({OHLCV_TIMEFRAME}, {OHLCV_DAYS_BACK} days)...")
            ohlcv_df = n.get_ohlcv_data(
                token_address,
                timeframe=OHLCV_TIMEFRAME,
                days_back=OHLCV_DAYS_BACK
            )

            if ohlcv_df is None or ohlcv_df.empty:
                print("❌ Failed to fetch OHLCV data")
                return None

            print(f"✅ Got {len(ohlcv_df)} candles")

            # Step 2: Run SMC analysis
            print(f"\n[2/3] 🎯 Running SMC analysis...")
            smc_result = analyze_smc_complete(ohlcv_df)

            if not smc_result:
                print("❌ SMC analysis failed")
                return None

            smc_summary = smc_result['summary']
            smc_score_result = calculate_smc_score(smc_summary)

            print(f"\n  📈 SMC Summary:")
            print(f"    Trend: {smc_summary['current_trend']}")
            print(f"    Bullish Signals: {smc_summary['bullish_signals']}")
            print(f"    Bearish Signals: {smc_summary['bearish_signals']}")
            print(f"    Score: {smc_score_result['score']}/100")
            print(f"    Signal: {smc_score_result['signal']}")

            # Step 3: Aggregate market data
            print(f"\n[3/3] 📡 Aggregating market data...")
            market_data = self.market_data_agg.aggregate_market_data(
                symbol=symbol or 'BTC',
                liquidation_limit=LIQUIDATION_LIMIT
            )

            if not market_data:
                print("⚠️ No market data available (continuing with SMC only)")
                market_data = {
                    'sentiment_score': 0,
                    'overall_signal': 'NEUTRAL',
                    'sentiment_reasons': ['Market data unavailable']
                }

            print(f"\n  💰 Market Data Summary:")
            print(f"    Signal: {market_data['overall_signal']}")
            print(f"    Sentiment Score: {market_data['sentiment_score']}")

            # Combine results
            return {
                'token_address': token_address,
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'ohlcv_df': smc_result['df'],
                'smc_summary': smc_summary,
                'smc_score': smc_score_result,
                'market_data': market_data,
                'current_price': smc_summary['current_price']
            }

        except Exception as e:
            cprint(f"❌ Error analyzing token: {str(e)}", "red")
            import traceback
            traceback.print_exc()
            return None

    def make_decision_llm(self, analysis: dict) -> dict:
        """
        Use LLM to make trading decision based on analysis.

        Args:
            analysis: Complete analysis results

        Returns:
            Dictionary with decision and reasoning
        """
        try:
            print(f"\n🤖 Consulting AI for trading decision...")

            # Prepare data for LLM
            smc_summary = analysis['smc_summary']
            smc_score = analysis['smc_score']
            market_data = analysis['market_data']
            current_price = analysis['current_price']

            # Build prompt
            system_prompt = """You are an expert cryptocurrency trader specializing in Smart Money Concepts (SMC) and market microstructure analysis.

Your job is to analyze both technical SMC signals and live market data to make trading decisions.

You must respond in EXACTLY this format:
Line 1: DECISION: BUY, SELL, or HOLD
Line 2: CONFIDENCE: <number between 0-100>
Line 3: REASONING: <one concise paragraph explaining your decision>
Line 4: KEY_FACTORS: <comma-separated list of 3-5 key factors>

Be decisive but cautious. Only recommend BUY/SELL with high confidence when multiple factors align."""

            user_prompt = f"""Analyze this cryptocurrency and provide a trading decision:

TECHNICAL SMC ANALYSIS:
- Current Price: ${current_price:.8f}
- Trend: {smc_summary['current_trend']}
- Bullish Order Blocks: {smc_summary['bullish_order_blocks']}
- Bearish Order Blocks: {smc_summary['bearish_order_blocks']}
- Bullish FVGs: {smc_summary['bullish_fvgs']}
- Bearish FVGs: {smc_summary['bearish_fvgs']}
- Recent MSB Bullish: {smc_summary['msb_bullish_recent']}
- Recent MSB Bearish: {smc_summary['msb_bearish_recent']}
- Recent BoS Bullish: {smc_summary['bos_bullish_recent']}
- Recent BoS Bearish: {smc_summary['bos_bearish_recent']}
- SMC Score: {smc_score['score']}/100 ({smc_score['signal']})
- Interpretation: {smc_score['interpretation']}

LIVE MARKET DATA:
- Overall Signal: {market_data['overall_signal']}
- Sentiment Score: {market_data['sentiment_score']}
- Key Factors:
"""

            # Add market data factors
            for reason in market_data.get('sentiment_reasons', []):
                user_prompt += f"  • {reason}\n"

            # Add CVD details if available
            if market_data.get('liquidation_cvd'):
                cvd = market_data['liquidation_cvd']
                user_prompt += f"\nLIQUIDATION CVD:\n"
                user_prompt += f"  • Trend: {cvd['cvd_trend']}\n"
                user_prompt += f"  • Recent CVD: ${cvd['cvd_recent']:,.0f}\n"
                user_prompt += f"  • Cascade Detected: {cvd['liquidation_cascade']}\n"

            # Add funding rate details if available
            if market_data.get('funding_rates'):
                funding = market_data['funding_rates']
                user_prompt += f"\nFUNDING RATES:\n"
                user_prompt += f"  • Sentiment: {funding['sentiment']}\n"
                user_prompt += f"  • Annual Rate: {funding['avg_funding_annual_pct']:.2f}%\n"
                user_prompt += f"  • Interpretation: {funding['interpretation']}\n"

            # Add OI details if available
            if market_data.get('open_interest'):
                oi = market_data['open_interest']
                user_prompt += f"\nOPEN INTEREST:\n"
                user_prompt += f"  • Trend: {oi['oi_trend']}\n"
                user_prompt += f"  • Change: {oi['oi_change_pct']:.2f}%\n"

            user_prompt += f"\nProvide your trading decision now:"

            # Get LLM response
            response = self.model.generate_response(
                system_prompt=system_prompt,
                user_message=user_prompt,
                temperature=AI_TEMPERATURE,
                max_tokens=AI_MAX_TOKENS
            )

            # Parse response
            lines = response.strip().split('\n')
            decision = None
            confidence = 0
            reasoning = ""
            key_factors = []

            for line in lines:
                line = line.strip()
                if line.startswith('DECISION:'):
                    decision_text = line.split(':', 1)[1].strip().upper()
                    if 'BUY' in decision_text:
                        decision = 'BUY'
                    elif 'SELL' in decision_text:
                        decision = 'SELL'
                    else:
                        decision = 'HOLD'
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = int(''.join(filter(str.isdigit, line.split(':', 1)[1])))
                    except:
                        confidence = 50
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
                elif line.startswith('KEY_FACTORS:'):
                    key_factors = [f.strip() for f in line.split(':', 1)[1].split(',')]

            return {
                'decision': decision or 'HOLD',
                'confidence': confidence,
                'reasoning': reasoning,
                'key_factors': key_factors,
                'raw_response': response
            }

        except Exception as e:
            cprint(f"❌ Error getting LLM decision: {str(e)}", "red")
            import traceback
            traceback.print_exc()
            return {
                'decision': 'HOLD',
                'confidence': 0,
                'reasoning': f'Error in AI analysis: {str(e)}',
                'key_factors': []
            }

    def make_decision_scoring(self, analysis: dict) -> dict:
        """
        Use scoring system to make trading decision.

        Combined score = SMC score + Market Data sentiment score
        Range: -200 to +200

        Args:
            analysis: Complete analysis results

        Returns:
            Dictionary with decision and reasoning
        """
        try:
            smc_score = analysis['smc_score']['score']
            market_score = analysis['market_data']['sentiment_score']

            combined_score = smc_score + market_score

            # Determine decision
            if combined_score >= 60:
                decision = 'BUY'
                confidence = min(95, 50 + combined_score // 2)
                reasoning = f"Strong bullish confluence (SMC: {smc_score}, Market: {market_score})"
            elif combined_score >= 30:
                decision = 'BUY'
                confidence = min(80, 50 + combined_score // 3)
                reasoning = f"Moderate bullish signals (SMC: {smc_score}, Market: {market_score})"
            elif combined_score <= -60:
                decision = 'SELL'
                confidence = min(95, 50 + abs(combined_score) // 2)
                reasoning = f"Strong bearish confluence (SMC: {smc_score}, Market: {market_score})"
            elif combined_score <= -30:
                decision = 'SELL'
                confidence = min(80, 50 + abs(combined_score) // 3)
                reasoning = f"Moderate bearish signals (SMC: {smc_score}, Market: {market_score})"
            else:
                decision = 'HOLD'
                confidence = 40
                reasoning = f"Mixed signals, no clear direction (SMC: {smc_score}, Market: {market_score})"

            key_factors = [
                f"SMC Score: {smc_score}",
                f"Market Sentiment: {market_score}",
                f"Combined Score: {combined_score}",
                analysis['smc_score']['interpretation'],
                analysis['market_data']['overall_signal']
            ]

            return {
                'decision': decision,
                'confidence': confidence,
                'reasoning': reasoning,
                'key_factors': key_factors,
                'combined_score': combined_score
            }

        except Exception as e:
            cprint(f"❌ Error in scoring decision: {str(e)}", "red")
            return {
                'decision': 'HOLD',
                'confidence': 0,
                'reasoning': f'Error in scoring: {str(e)}',
                'key_factors': []
            }

    def make_decision_hybrid(self, analysis: dict) -> dict:
        """
        Use hybrid approach: both LLM and scoring must agree.

        Args:
            analysis: Complete analysis results

        Returns:
            Dictionary with decision and reasoning
        """
        try:
            # Get both decisions
            llm_decision = self.make_decision_llm(analysis)
            scoring_decision = self.make_decision_scoring(analysis)

            # Check if they agree
            if llm_decision['decision'] == scoring_decision['decision']:
                # Both agree - higher confidence
                avg_confidence = (llm_decision['confidence'] + scoring_decision['confidence']) // 2
                return {
                    'decision': llm_decision['decision'],
                    'confidence': min(95, avg_confidence + 10),  # Bonus for agreement
                    'reasoning': f"LLM & Scoring agree: {llm_decision['reasoning']}",
                    'key_factors': llm_decision['key_factors'] + [f"Scoring: {scoring_decision['combined_score']}"],
                    'agreement': True
                }
            else:
                # Disagree - reduce to HOLD or take LLM with reduced confidence
                return {
                    'decision': 'HOLD',
                    'confidence': 30,
                    'reasoning': f"Mixed signals - LLM says {llm_decision['decision']}, Scoring says {scoring_decision['decision']}",
                    'key_factors': ['Conflicting signals between methods'],
                    'agreement': False
                }

        except Exception as e:
            cprint(f"❌ Error in hybrid decision: {str(e)}", "red")
            return {
                'decision': 'HOLD',
                'confidence': 0,
                'reasoning': f'Error in hybrid analysis: {str(e)}',
                'key_factors': []
            }

    def execute_trade(self, token_address: str, decision: dict, analysis: dict):
        """
        Execute trade based on decision (or paper trade).

        Args:
            token_address: Token address to trade
            decision: Trading decision
            analysis: Complete analysis
        """
        try:
            if decision['decision'] == 'HOLD':
                cprint("\n✋ Decision: HOLD - No action taken", "yellow")
                return

            if decision['confidence'] < MIN_CONFIDENCE:
                cprint(f"\n⚠️ Confidence {decision['confidence']}% below threshold {MIN_CONFIDENCE}% - No action taken", "yellow")
                return

            action = decision['decision']
            current_price = analysis['current_price']

            print(f"\n{'='*70}")
            if PAPER_TRADING:
                cprint(f"📄 PAPER TRADE - {action}", "cyan")
            else:
                cprint(f"💰 LIVE TRADE - {action}", "green")
            print(f"{'='*70}")

            print(f"  Token: {token_address}")
            print(f"  Price: ${current_price:.8f}")
            print(f"  Confidence: {decision['confidence']}%")
            print(f"  Reasoning: {decision['reasoning']}")

            # Save to trade history
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': analysis.get('symbol', 'UNKNOWN'),
                'action': action,
                'price': current_price,
                'size': POSITION_SIZE_PCT,
                'smc_score': analysis['smc_score']['score'],
                'market_score': analysis['market_data']['sentiment_score'],
                'confidence': decision['confidence'],
                'reasoning': decision['reasoning']
            }

            self.save_trade(trade_data)

            if not PAPER_TRADING:
                # TODO: Implement actual trading logic here
                # Use nice_funcs or nice_funcs_aster depending on exchange
                print("\n⚠️ Live trading not implemented yet!")
                print("  Set PAPER_TRADING = True for now")
            else:
                cprint("\n✅ Paper trade recorded", "green")

        except Exception as e:
            cprint(f"❌ Error executing trade: {str(e)}", "red")
            import traceback
            traceback.print_exc()

    def run(self, token_address: str, symbol: str = None):
        """
        Run complete SMC trading analysis and execution.

        Args:
            token_address: Solana token address to analyze
            symbol: Symbol for market data (e.g., 'BTC', 'SOL')
        """
        try:
            # Step 1: Analyze token
            analysis = self.analyze_token(token_address, symbol)

            if not analysis:
                cprint("\n❌ Analysis failed - aborting", "red")
                return

            # Step 2: Make decision
            print(f"\n{'='*70}")
            print(f"🎯 Making Trading Decision ({DECISION_METHOD})")
            print(f"{'='*70}")

            if DECISION_METHOD == 'LLM':
                decision = self.make_decision_llm(analysis)
            elif DECISION_METHOD == 'SCORING':
                decision = self.make_decision_scoring(analysis)
            elif DECISION_METHOD == 'HYBRID':
                decision = self.make_decision_hybrid(analysis)
            else:
                cprint(f"❌ Unknown decision method: {DECISION_METHOD}", "red")
                return

            print(f"\n  Decision: {decision['decision']}")
            print(f"  Confidence: {decision['confidence']}%")
            print(f"  Reasoning: {decision['reasoning']}")

            # Step 3: Execute trade
            self.execute_trade(token_address, decision, analysis)

            print(f"\n{'='*70}")
            cprint("✅ SMC Trading Agent cycle complete!", "green")
            print(f"{'='*70}\n")

        except Exception as e:
            cprint(f"❌ Error in SMC Trading Agent: {str(e)}", "red")
            import traceback
            traceback.print_exc()


def main():
    """Main function for standalone execution"""
    cprint("\n🚀 Moon Dev's SMC Trading Agent Starting...", "white", "on_blue")

    agent = SMCTradingAgent()

    # Example: Analyze SOL token
    # Replace with actual token address
    SOL_ADDRESS = "So11111111111111111111111111111111111111112"

    try:
        agent.run(token_address=SOL_ADDRESS, symbol='SOL')

    except KeyboardInterrupt:
        print("\n\n👋 SMC Trading Agent shutting down gracefully...")
    except Exception as e:
        cprint(f"\n❌ Fatal error: {str(e)}", "red")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
