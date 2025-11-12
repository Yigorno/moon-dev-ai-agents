# Quick Start Guide - Moon Dev AI Agents

## ✅ Setup Complete!

Your environment is now configured with:
- **Python Version**: 3.10.9 (in `algotrader` environment)
- **API Keys**: Already configured in .env
- **Packages**: Installing (will complete shortly)

## 🚀 How to Run Agents

### Step 1: Activate the Environment

**Option A - Using the Batch File**:
Double-click: `activate_algotrader.bat`

**Option B - Manual Activation**:
Open Command Prompt and run:
```cmd
conda activate algotrader
cd "G:\Drive'ım\Moondev_AI_agents\moon-dev-ai-agents"
```

### Step 2: Run Your First Agent

**Recommended: Start with RBI Backtesting Agent**

1. **Create an ideas file**:
   ```cmd
   cd src\data\rbi_pp_multi
   echo Buy when RSI < 30 and sell when RSI > 70 > ideas.txt
   ```

2. **Run the agent**:
   ```cmd
   cd "G:\Drive'ım\Moondev_AI_agents\moon-dev-ai-agents"
   python src\agents\rbi_agent_pp_multi.py
   ```

3. **View results**:
   - Results: `src\data\rbi_pp_multi\backtest_stats.csv`
   - Charts and code: `src\data\rbi_pp_multi\<timestamp_folder>\`

## 📋 Quick Reference - Safe Agents for Beginners

### Backtesting & Research (NO REAL MONEY)
```cmd
# Automated backtesting from text ideas
python src\agents\rbi_agent_pp_multi.py

# Research trading strategies
python src\agents\research_agent.py

# Analyze chart screenshots
python src\agents\chartanalysis_agent.py
```

### Content Creation
```cmd
# Improve your prompts
python src\agents\prompt_agent.py

# Generate tweet ideas
python src\agents\tweet_agent.py
```

### Market Analysis (Read-Only)
```cmd
# Analyze whale activity
python src\agents\whale_agent.py

# Twitter sentiment analysis
python src\agents\sentiment_agent.py

# Track funding rates
python src\agents\funding_agent.py
```

## ⚠️ DANGER ZONE - Do NOT Run These Yet!

These agents trade REAL MONEY:
- ❌ `trading_agent.py`
- ❌ `strategy_agent.py`
- ❌ `sniper_agent.py`
- ❌ `copy_agent.py`

Only run these after:
1. Extensive backtesting
2. Setting up trading accounts
3. Understanding all risks
4. Testing with small amounts

## 🔧 Configuration

### Edit .env File
```cmd
notepad .env
```

Important settings:
- `ANTHROPIC_KEY` - For Claude AI (optional but recommended)
- `OPENAI_KEY` - For GPT (you have this)
- `DEEPSEEK_KEY` - For DeepSeek (you have this - cheap!)
- `GEMINI_KEY` - For Gemini (you have this)

### RBI Agent Settings

Edit `src\agents\rbi_agent_pp_multi.py` (lines 130-132):
```python
TARGET_RETURN = 50  # AI tries to optimize to this %
SAVE_IF_OVER_RETURN = 1.0  # Save if return > this %
MAX_WORKERS = 18  # Parallel threads (adjust for your CPU)
```

## 📚 Learning Path

### Week 1
- [x] Install and setup ✅
- [ ] Run RBI agent with simple strategies
- [ ] Read BEGINNER_GUIDE.md
- [ ] Watch YouTube videos in README

### Week 2
- [ ] Experiment with different strategy ideas
- [ ] Learn to read backtest results
- [ ] Use research agent to find ideas

### Week 3
- [ ] Study the generated backtest code
- [ ] Modify and improve strategies
- [ ] Build a strategy library

## 🐛 Troubleshooting

### "Module not found" error
**Solution**: Make sure you activated the algotrader environment:
```cmd
conda activate algotrader
```

### "API key error"
**Solution**: Check your .env file has the required key for that agent

### Agent won't run
**Solution**: Check you're in the correct directory:
```cmd
cd "G:\Drive'ım\Moondev_AI_agents\moon-dev-ai-agents"
```

## 📁 Important Files & Folders

```
moon-dev-ai-agents/
├── .env                    # Your API keys (DO NOT SHARE!)
├── activate_algotrader.bat # Quick environment activation
├── BEGINNER_GUIDE.md       # Detailed beginner info
├── QUICK_START.md          # This file
├── README.md               # Full documentation
├── src/
│   ├── agents/             # All agent scripts
│   │   ├── rbi_agent_pp_multi.py  # Main backtesting agent
│   │   ├── research_agent.py       # Strategy research
│   │   └── ...                     # 50+ other agents
│   └── data/
│       └── rbi_pp_multi/   # Backtest results
│           ├── backtest_stats.csv
│           └── user_folders/
└── requirements.txt        # Python packages
```

## 💡 Pro Tips

1. **Start Simple**: Begin with basic strategies like RSI or moving averages
2. **Read the Results**: Understand Sharpe ratio, max drawdown, etc.
3. **Test Multiple Ideas**: The RBI agent can process many strategies
4. **Save Good Strategies**: Build a library of tested strategies
5. **Never Jump to Live Trading**: Backtest extensively first!

## 🆘 Getting Help

- **Discord**: https://discord.gg/8UPuVZ53bh
- **YouTube**: Full playlist in README.md
- **Issues**: Report problems on GitHub

## 🎯 Your Next Steps

1. Wait for package installation to complete
2. Double-click `activate_algotrader.bat`
3. Run: `python src\agents\rbi_agent_pp_multi.py`
4. Check results in `src\data\rbi_pp_multi\backtest_stats.csv`
5. Experiment with different strategy ideas!

---

**Remember**: This is a LEARNING tool, not a get-rich-quick scheme. Take your time, understand the code, and always test before trading real money!
