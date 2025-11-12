"""
🌙 Moon Dev's Hedge Agent - Main Orchestrator
Built with love by Moon Dev 🚀

Orchestrates portfolio monitoring, derivatives tracking, options analysis,
market maker activity, and macro indicators to make intelligent hedge decisions.
"""

import os
import sys
import pandas as pd
import time
from datetime import datetime, timedelta
from termcolor import colored, cprint
from dotenv import load_dotenv
from pathlib import Path
import traceback
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src import config
from src import nice_funcs as n
from src import nice_funcs_hyperliquid as hl
from src.models.model_factory import ModelFactory
from src.agents.base_agent import BaseAgent

# Import all subagents
from src.agents.hedge_monitor.portfolio_monitor_subagent import PortfolioMonitorSubagent
from src.agents.hedge_monitor.macro_monitor_subagent import MacroMonitorSubagent
from src.agents.hedge_monitor.options_monitor_subagent import OptionsMonitorSubagent
from src.agents.hedge_monitor.whale_tracker_subagent import OnChainWhaleTracker
from src.agents.hedge_monitor.orderblocks_monitor_subagent import OrderBlocksMonitor

# Check if Moon Dev API key is available
USE_MOONDEV_API = os.getenv('MOONDEV_API_KEY') is not None

if USE_MOONDEV_API:
    print("💎 Moon Dev API detected - using premium data sources")
    from src.agents.hedge_monitor.derivatives_monitor_subagent import DerivativesMonitorSubagent
    from src.agents.hedge_monitor.marketmaker_monitor_subagent import MarketMakerMonitorSubagent
else:
    print("🌐 No Moon Dev API - using free public data sources (Binance, Bybit, etc.)")
    from src.agents.hedge_monitor.derivatives_monitor_subagent_public import DerivativesMonitorSubagentPublic as DerivativesMonitorSubagent
    # Market maker monitor is optional if no Moon Dev API
    MarketMakerMonitorSubagent = None

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Hedge Agent Configuration
CHECK_INTERVAL_MINUTES = 30  # How often to run full analysis
AI_MODEL_PROVIDER = 'anthropic'  # anthropic, openai, deepseek, groq, etc.

# Hedge Decision Prompt
HEDGE_DECISION_PROMPT = """You are Moon Dev's Hedge Decision AI 🛡️

Your job is to analyze comprehensive market data and decide if the user needs to open hedge positions.

## Current Data Analysis:

### Portfolio Status:
{portfolio_summary}

### Derivatives Market:
{derivatives_summary}

### Options Market:
{options_summary}

### Market Maker Activity:
{marketmaker_summary}

### Whale Activity:
{whale_summary}

### Order Blocks:
{orderblocks_summary}

### Macroeconomic Context:
{macro_summary}

## Your Task:

Based on ALL the above data, provide a hedging recommendation.

**Respond in this exact format:**

DECISION: [OPEN_HEDGE / NO_HEDGE / CLOSE_HEDGE]
HEDGE_TYPE: [SHORT_PERPETUAL / LONG_PERPETUAL / OPTIONS_PUT / NONE]
HEDGE_SIZE_PCT: [0-100] (percentage of portfolio to hedge)
CONFIDENCE: [0-100]

REASONING:
[Your detailed reasoning considering all risk factors]

KEY_RISKS:
- [List 3-5 most critical risks that justify your decision]

HEDGE_EXECUTION:
[If OPEN_HEDGE, specify: asset to hedge, entry strategy, stop loss, take profit]
"""

class HedgeAgent(BaseAgent):
    """Main Hedge Agent - Orchestrates all monitoring and makes hedge decisions"""

    def __init__(self):
        """Initialize Hedge Agent and all subagents"""
        super().__init__('hedge')

        load_dotenv()

        # Initialize AI model
        self.model = ModelFactory.create_model(AI_MODEL_PROVIDER)
        print(f"🤖 Using AI Model: {AI_MODEL_PROVIDER}")

        # Create data directory
        self.data_dir = PROJECT_ROOT / "src" / "data" / "hedge_monitor"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # History file
        self.decisions_file = self.data_dir / "hedge_decisions.csv"
        self.load_decision_history()

        # Initialize all subagents
        print("\n🚀 Initializing subagents...")
        try:
            self.portfolio_monitor = PortfolioMonitorSubagent()
            self.derivatives_monitor = DerivativesMonitorSubagent()
            self.macro_monitor = MacroMonitorSubagent()
            self.options_monitor = OptionsMonitorSubagent()
            self.whale_tracker = OnChainWhaleTracker()
            self.orderblocks_monitor = OrderBlocksMonitor()

            # Market maker monitor only if Moon Dev API is available
            if MarketMakerMonitorSubagent is not None:
                self.marketmaker_monitor = MarketMakerMonitorSubagent()
            else:
                self.marketmaker_monitor = None
                print("⚠️ Market maker monitor disabled (requires Moon Dev API)")

            print("✅ All available subagents initialized successfully!")
        except Exception as e:
            print(f"⚠️ Warning during subagent initialization: {str(e)}")
            traceback.print_exc()

        cprint("\n🛡️ Hedge Agent Fully Initialized!", "white", "on_green")

    def load_decision_history(self):
        """Load or initialize hedge decision history"""
        try:
            if self.decisions_file.exists():
                self.decision_history = pd.read_csv(self.decisions_file)
                print(f"📊 Loaded {len(self.decision_history)} historical hedge decisions")
            else:
                self.decision_history = pd.DataFrame(columns=[
                    'timestamp', 'decision', 'hedge_type', 'hedge_size_pct',
                    'confidence', 'reasoning'
                ])
                print("📝 Created new hedge decision history file")

        except Exception as e:
            print(f"❌ Error loading decision history: {str(e)}")
            self.decision_history = pd.DataFrame()

    def run_all_monitors(self):
        """Run all monitoring subagents and collect their outputs"""
        print("\n" + "═" * 80)
        cprint("🔍 Running All Monitors...", "cyan")
        print("═" * 80)

        results = {}

        # Run portfolio monitor
        try:
            print("\n[1/7] 💼 Portfolio Monitor")
            results['portfolio'] = self.portfolio_monitor.run()
        except Exception as e:
            print(f"❌ Portfolio monitor error: {str(e)}")
            results['portfolio'] = None

        # Run derivatives monitor
        try:
            print("\n[2/7] 📊 Derivatives Monitor")
            results['derivatives'] = self.derivatives_monitor.run()
        except Exception as e:
            print(f"❌ Derivatives monitor error: {str(e)}")
            results['derivatives'] = None

        # Run options monitor
        try:
            print("\n[3/7] 📈 Options Monitor")
            results['options'] = self.options_monitor.run()
        except Exception as e:
            print(f"❌ Options monitor error: {str(e)}")
            results['options'] = None

        # Run market maker monitor (if available)
        if self.marketmaker_monitor is not None:
            try:
                print("\n[4/7] 🐋 Market Maker Monitor (Moon Dev API)")
                results['marketmaker'] = self.marketmaker_monitor.run()
            except Exception as e:
                print(f"❌ Market maker monitor error: {str(e)}")
                results['marketmaker'] = None
        else:
            print("\n[4/7] 🐋 Market Maker Monitor - SKIPPED (Moon Dev API required)")
            results['marketmaker'] = None

        # Run whale tracker
        try:
            print("\n[5/7] 🐋 Whale Tracker (On-Chain)")
            results['whale'] = self.whale_tracker.run()
        except Exception as e:
            print(f"❌ Whale tracker error: {str(e)}")
            results['whale'] = None

        # Run order blocks monitor
        try:
            print("\n[6/7] 📦 Order Blocks Monitor")
            results['orderblocks'] = self.orderblocks_monitor.run()
        except Exception as e:
            print(f"❌ Order blocks monitor error: {str(e)}")
            results['orderblocks'] = None

        # Run macro monitor
        try:
            print("\n[7/7] 🌍 Macro Monitor")
            results['macro'] = self.macro_monitor.run()
        except Exception as e:
            print(f"❌ Macro monitor error: {str(e)}")
            results['macro'] = None

        print("\n" + "═" * 80)
        print("✅ All monitors completed!")
        print("═" * 80)

        return results

    def format_monitor_data_for_ai(self, monitor_results):
        """Format all monitor results into a summary for AI analysis"""
        summaries = {}

        # Portfolio summary
        if monitor_results.get('portfolio'):
            p = monitor_results['portfolio']
            if p.get('snapshot'):
                snap = p['snapshot']
                summaries['portfolio'] = f"""
Total Value: ${snap['total_value_usd']:,.2f}
USDC Balance: ${snap['usdc_balance']:,.2f}
Active Positions: {snap['num_positions']}
Largest Position: {snap['largest_position_pct']:.1f}%
Concentration Risk: {snap['concentration_risk']:.3f}
Analysis: {p.get('analysis', {}).get('reasoning', ['No analysis'])[0]}
"""
        else:
            summaries['portfolio'] = "Portfolio data unavailable"

        # Derivatives summary
        if monitor_results.get('derivatives'):
            d = monitor_results['derivatives']
            risks = d.get('risks', [])
            if risks:
                risk_msgs = '\n'.join([f"- {r['message']}" for r in risks[:5]])
                summaries['derivatives'] = f"{len(risks)} risk(s) detected:\n{risk_msgs}"
            else:
                summaries['derivatives'] = "No significant derivatives risks detected"
        else:
            summaries['derivatives'] = "Derivatives data unavailable"

        # Options summary
        if monitor_results.get('options'):
            o = monitor_results['options']
            signals = o.get('signals', [])
            if signals:
                signal_msgs = '\n'.join([f"- {s['message']}" for s in signals[:5]])
                summaries['options'] = f"{len(signals)} signal(s) detected:\n{signal_msgs}"
            else:
                summaries['options'] = "No significant max pain divergence"
        else:
            summaries['options'] = "Options data unavailable"

        # Market maker summary
        if monitor_results.get('marketmaker'):
            mm = monitor_results['marketmaker']
            if mm.get('analysis'):
                analysis = mm['analysis']
                summaries['marketmaker'] = f"""
Net Positioning: {analysis['net_positioning']}
Accumulation Score: {analysis['accumulation_score']}
Distribution Score: {analysis['distribution_score']}
Signals: {len(analysis.get('signals', []))}
"""
            else:
                summaries['marketmaker'] = "Market maker data unavailable"
        else:
            summaries['marketmaker'] = "Market maker monitoring unavailable (Moon Dev API)"

        # Whale tracker summary
        if monitor_results.get('whale'):
            w = monitor_results['whale']
            signals = w.get('signals', [])
            if signals:
                signal_msgs = '\n'.join([f"- {s['message']}" for s in signals[:5]])
                summaries['whale'] = f"{len(signals)} whale signal(s) detected:\n{signal_msgs}"
            else:
                whale_data = w.get('whale_data')
                if whale_data is not None and not whale_data.empty:
                    acc = len(whale_data[whale_data['signal'] == 'ACCUMULATION'])
                    dist = len(whale_data[whale_data['signal'] == 'DISTRIBUTION'])
                    summaries['whale'] = f"Tracking {len(whale_data)} whales: {acc} accumulating, {dist} distributing"
                else:
                    summaries['whale'] = "Whale tracking available but no activity detected"
        else:
            summaries['whale'] = "Whale tracking unavailable (needs Etherscan API key)"

        # Order blocks summary
        if monitor_results.get('orderblocks'):
            ob = monitor_results['orderblocks']
            signals = ob.get('signals', [])
            if signals:
                signal_msgs = '\n'.join([f"- {s['message']}" for s in signals[:5]])
                summaries['orderblocks'] = f"{len(signals)} order block signal(s):\n{signal_msgs}"
            else:
                ob_data = ob.get('orderblocks')
                if ob_data is not None and not ob_data.empty:
                    supports = len(ob_data[ob_data['type'] == 'SUPPORT'])
                    resistances = len(ob_data[ob_data['type'] == 'RESISTANCE'])
                    summaries['orderblocks'] = f"Tracking {supports} support and {resistances} resistance order blocks"
                else:
                    summaries['orderblocks'] = "Order blocks available but no significant levels"
        else:
            summaries['orderblocks'] = "Order blocks monitoring unavailable"

        # Macro summary
        if monitor_results.get('macro'):
            m = monitor_results['macro']
            if m.get('macro_data'):
                md = m['macro_data']
                summaries['macro'] = f"""
Liquidity Trend: {md.get('liquidity_trend', 'Unknown')}
M2 Money Supply: ${md.get('m2_supply', 0):,.0f}B
Fed Balance Sheet: ${md.get('fed_balance_sheet', 0):,.0f}B
Fed Funds Rate: {md.get('fed_funds_rate', 0):.2f}%
Risks: {len(m.get('risks', []))}
"""
            else:
                summaries['macro'] = "Macro data unavailable (FRED API not configured)"
        else:
            summaries['macro'] = "Macro monitoring unavailable"

        return summaries

    def get_ai_hedge_decision(self, monitor_results):
        """Get AI-powered hedge decision based on all monitor data"""
        try:
            # Format data for AI
            summaries = self.format_monitor_data_for_ai(monitor_results)

            # Create prompt
            prompt = HEDGE_DECISION_PROMPT.format(
                portfolio_summary=summaries.get('portfolio', 'N/A'),
                derivatives_summary=summaries.get('derivatives', 'N/A'),
                options_summary=summaries.get('options', 'N/A'),
                marketmaker_summary=summaries.get('marketmaker', 'N/A'),
                whale_summary=summaries.get('whale', 'N/A'),
                orderblocks_summary=summaries.get('orderblocks', 'N/A'),
                macro_summary=summaries.get('macro', 'N/A')
            )

            print("\n🤖 Consulting AI for hedge decision...")

            # Get AI response
            response = self.model.generate_response(
                system_prompt="You are an expert risk management AI specializing in crypto portfolio hedging.",
                user_content=prompt,
                temperature=0.3,  # Lower temperature for more consistent decisions
                max_tokens=1000
            )

            # Parse response
            decision = self.parse_ai_decision(response)

            return decision

        except Exception as e:
            cprint(f"❌ Error getting AI decision: {str(e)}", "red")
            traceback.print_exc()
            return None

    def parse_ai_decision(self, ai_response):
        """Parse AI response into structured decision"""
        try:
            lines = ai_response.strip().split('\n')

            decision = {
                'decision': 'NO_HEDGE',
                'hedge_type': 'NONE',
                'hedge_size_pct': 0,
                'confidence': 50,
                'reasoning': ai_response,
                'key_risks': [],
                'execution_plan': ''
            }

            # Parse structured fields
            for line in lines:
                line = line.strip()

                if line.startswith('DECISION:'):
                    decision['decision'] = line.split(':', 1)[1].strip().split()[0]

                elif line.startswith('HEDGE_TYPE:'):
                    decision['hedge_type'] = line.split(':', 1)[1].strip().split()[0]

                elif line.startswith('HEDGE_SIZE_PCT:'):
                    try:
                        decision['hedge_size_pct'] = int(line.split(':', 1)[1].strip().split()[0])
                    except:
                        pass

                elif line.startswith('CONFIDENCE:'):
                    try:
                        decision['confidence'] = int(line.split(':', 1)[1].strip().split()[0])
                    except:
                        pass

            return decision

        except Exception as e:
            print(f"⚠️ Error parsing AI decision: {str(e)}")
            return {
                'decision': 'NO_HEDGE',
                'hedge_type': 'NONE',
                'hedge_size_pct': 0,
                'confidence': 0,
                'reasoning': ai_response,
                'key_risks': [],
                'execution_plan': ''
            }

    def execute_hedge(self, decision, portfolio_value):
        """Execute hedge trade based on AI decision"""
        try:
            if decision['decision'] != 'OPEN_HEDGE':
                return False

            hedge_size_usd = portfolio_value * (decision['hedge_size_pct'] / 100)

            print(f"\n🎯 Executing hedge:")
            print(f"   Type: {decision['hedge_type']}")
            print(f"   Size: ${hedge_size_usd:,.2f} ({decision['hedge_size_pct']}% of portfolio)")
            print(f"   Confidence: {decision['confidence']}%")

            # For now, just log the decision - actual execution would happen here
            print("\n⚠️ DEMO MODE: Not executing actual trades")
            print("💡 To enable: Uncomment execution code in execute_hedge()")

            # Example execution code (commented out for safety):
            # if decision['hedge_type'] == 'SHORT_PERPETUAL':
            #     # Execute short on HyperLiquid
            #     result = hl.market_sell('BTC', hedge_size_usd, leverage=2)
            #     return result
            #
            # elif decision['hedge_type'] == 'LONG_PERPETUAL':
            #     # Execute long on HyperLiquid
            #     result = hl.market_buy('BTC', hedge_size_usd, leverage=2)
            #     return result

            return True

        except Exception as e:
            cprint(f"❌ Error executing hedge: {str(e)}", "red")
            return False

    def save_decision(self, decision):
        """Save hedge decision to history"""
        try:
            new_row = pd.DataFrame([{
                'timestamp': datetime.now(),
                'decision': decision['decision'],
                'hedge_type': decision['hedge_type'],
                'hedge_size_pct': decision['hedge_size_pct'],
                'confidence': decision['confidence'],
                'reasoning': decision['reasoning'][:500]  # Truncate for CSV
            }])

            self.decision_history = pd.concat([self.decision_history, new_row], ignore_index=True)

            # Keep only last 90 days
            cutoff_time = datetime.now() - timedelta(days=90)
            self.decision_history = self.decision_history[
                pd.to_datetime(self.decision_history['timestamp']) > cutoff_time
            ]

            self.decision_history.to_csv(self.decisions_file, index=False)

        except Exception as e:
            print(f"❌ Error saving decision: {str(e)}")

    def run(self):
        """Main hedge agent cycle"""
        try:
            print("\n" + "╔" + "═" * 78 + "╗")
            print("║" + " " * 20 + "🛡️  HEDGE AGENT CYCLE  🛡️" + " " * 22 + "║")
            print("╚" + "═" * 78 + "╝")

            # Run all monitors
            monitor_results = self.run_all_monitors()

            # Get AI decision
            decision = self.get_ai_hedge_decision(monitor_results)

            if decision:
                # Print decision
                print("\n" + "╔" + "═" * 78 + "╗")
                print("║" + " " * 25 + "🤖 AI DECISION 🤖" + " " * 25 + "║")
                print("╠" + "═" * 78 + "╣")
                print(f"║  Decision: {decision['decision']:<64} ║")
                print(f"║  Hedge Type: {decision['hedge_type']:<62} ║")
                print(f"║  Size: {decision['hedge_size_pct']}% of portfolio{' ' * (53 - len(str(decision['hedge_size_pct'])))}║")
                print(f"║  Confidence: {decision['confidence']}%{' ' * (59 - len(str(decision['confidence'])))}║")
                print("╠" + "═" * 78 + "╣")
                print("║  Reasoning:" + " " * 66 + "║")

                # Print reasoning (wrapped)
                reasoning = decision['reasoning']
                words = reasoning.split()
                line = "║  "
                for word in words:
                    if len(line) + len(word) + 1 > 76:
                        print(line.ljust(78) + "║")
                        line = "║  " + word
                    else:
                        line += " " + word if line != "║  " else word
                if line != "║  ":
                    print(line.ljust(78) + "║")

                print("╚" + "═" * 78 + "╝")

                # Save decision
                self.save_decision(decision)

                # Execute if needed
                if decision['decision'] == 'OPEN_HEDGE':
                    portfolio_value = monitor_results.get('portfolio', {}).get('snapshot', {}).get('total_value_usd', 0)
                    if portfolio_value > 0:
                        self.execute_hedge(decision, portfolio_value)

            return {
                'monitor_results': monitor_results,
                'decision': decision
            }

        except Exception as e:
            cprint(f"❌ Error in hedge agent cycle: {str(e)}", "red")
            traceback.print_exc()
            return None

def main():
    """Main function for running hedge agent"""
    cprint("\n🚀 Moon Dev's Hedge Agent Starting...", "white", "on_green")

    agent = HedgeAgent()

    while True:
        try:
            agent.run()

            print(f"\n💤 Sleeping for {CHECK_INTERVAL_MINUTES} minutes...")
            print(f"⏰ Next check at: {(datetime.now() + timedelta(minutes=CHECK_INTERVAL_MINUTES)).strftime('%H:%M:%S')}")
            time.sleep(CHECK_INTERVAL_MINUTES * 60)

        except KeyboardInterrupt:
            print("\n👋 Hedge Agent shutting down gracefully...")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {str(e)}")
            traceback.print_exc()
            time.sleep(60)

if __name__ == "__main__":
    main()
