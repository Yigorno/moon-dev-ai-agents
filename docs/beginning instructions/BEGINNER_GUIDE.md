# Beginner's Guide to Moon Dev AI Agents

## Welcome!

This guide will help you get started with AI agents as a beginner.

## What You Have Installed

You now have **50+ AI agents** that can help with:
- Trading strategy backtesting (testing ideas on historical data)
- Market research and analysis
- Content creation (videos, tweets, clips)
- Live trading (⚠️ ADVANCED - NOT for beginners!)

## Your Current Setup

### ✅ Configured API Keys
Your .env file has these AI services ready:
- OpenAI (GPT models)
- DeepSeek (cheap AI)
- Groq (fast inference)
- Gemini (Google AI)
- Grok (xAI)
- OpenRouter (200+ models)
- BirdEye (Solana data)

### ❌ Missing (Optional)
- Anthropic Claude - Better AI responses
- ElevenLabs - Voice features

## Recommended Starting Path

### 1. Start with Backtesting (SAFEST)

**RBI Agent** - Automated backtesting tool

**Location**: `src/agents/rbi_agent_pp_multi.py`

**What it does**:
- Takes a trading strategy idea (in plain English)
- Automatically codes it into a backtest
- Tests it across 20+ cryptocurrencies
- Shows you which strategies might work

**How to use**:
1. Create `src/data/rbi_pp_multi/ideas.txt`
2. Write your strategy idea:
   ```
   Buy when RSI < 30 and sell when RSI > 70
   ```
3. Run:
   ```bash
   cd "G:\Drive'ım\Moondev_AI_agents\moon-dev-ai-agents"
   python src/agents/rbi_agent_pp_multi.py
   ```
4. Check results in `src/data/rbi_pp_multi/backtest_stats.csv`

### 2. Research Agent

**Location**: `src/agents/research_agent.py`

**What it does**: Searches for trading strategy ideas automatically

### 3. Chart Analysis

**Location**: `src/agents/chartanalysis_agent.py`

**What it does**: Analyzes crypto chart screenshots using AI

## DANGER ZONE ⚠️

### DO NOT RUN THESE (Yet!):
- `trading_agent.py` - REAL MONEY TRADING
- `strategy_agent.py` - LIVE STRATEGY EXECUTION
- `sniper_agent.py` - AUTO-TRADING NEW TOKENS
- `copybot_agent.py` - COPIES OTHER TRADERS' MOVES

These agents require:
- Real money in trading accounts
- Exchange API keys with trading permissions
- Thorough understanding of trading risks
- Extensive testing and validation

## Safety Rules

1. **ALWAYS backtest first** - Never trade real money without testing
2. **Start small** - If you eventually trade, use tiny amounts
3. **Understand the code** - Read what the agent does before running
4. **API keys are secrets** - NEVER share your .env file
5. **No guarantees** - AI agents can lose money in trading

## Learning Path

### Week 1: Understanding
- Read the README.md
- Watch the YouTube videos in the README
- Explore the codebase

### Week 2: Backtesting
- Use RBI agent with simple strategies
- Understand the backtest results
- Learn what metrics mean (Sharpe ratio, drawdown, etc.)

### Week 3: Research
- Use research agent to find ideas
- Combine with RBI agent for automated testing
- Build a library of tested strategies

### Month 2+: Consider Advanced
- Only after thorough backtesting
- Only with money you can afford to lose
- Start with testnet/paper trading

## Common Issues

### Issue: "Module not found"
**Solution**: Make sure you ran `pip install -r requirements.txt`

### Issue: "API key error"
**Solution**: Check your .env file has the required API key for that agent

### Issue: "Permission denied"
**Solution**: Make sure you're running from the correct directory

## File Structure

```
moon-dev-ai-agents/
├── src/
│   ├── agents/          # All agent Python files
│   ├── data/            # Data storage
│   │   └── rbi_pp_multi/  # Backtesting results
│   └── utils/           # Utility functions
├── .env                 # Your API keys (DO NOT SHARE!)
├── requirements.txt     # Python packages
└── README.md           # Full documentation
```

## Getting Help

- **Discord**: https://discord.gg/8UPuVZ53bh
- **YouTube Playlist**: https://www.youtube.com/playlist?list=PLXrNVMjRZUJg4M4uz52iGd1LhXXGVbIFz
- **Documentation**: README.md in the main folder

## Key Concepts

### What is Backtesting?
Testing a trading strategy on historical data to see how it would have performed.

### What is an AI Agent?
An autonomous program that uses AI to make decisions and perform tasks.

### What is an API Key?
A password that lets the agent use external services (like OpenAI's GPT).

### What is .env file?
A file storing sensitive information (API keys, passwords) that shouldn't be shared.

## Next Steps

1. ✅ Installation complete
2. ⏳ Test with RBI agent
3. ⏳ Explore other research agents
4. ⏳ Learn about trading strategies
5. ⏳ Build your own strategies

Remember: The goal is LEARNING, not quick profits. Take your time!
