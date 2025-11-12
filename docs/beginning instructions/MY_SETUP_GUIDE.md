# 🎯 Your Personalized Setup Guide

## Your System Configuration

- **Computer**: 16GB VRAM
- **Python Environment**: algotrader (Python 3.10.9)
- **Local AI**: Ollama with Qwen3 14B model ✅
- **Docker Infrastructure**: 27 containers running ✅
- **Paid APIs**: Limited Claude credits (save for important tasks!)

---

## 🚀 Quick Start Checklist

### ✅ Already Done
- [x] Repository cloned
- [x] .env file configured with API keys
- [x] Ollama tested and working
- [x] Python 3.10.9 environment (algotrader)
- [x] Packages installing

### ⏳ To Do After Installation
- [ ] Test Claude API (minimal cost test)
- [ ] Configure RBI agent for Ollama
- [ ] Run first backtest
- [ ] Explore other agents

---

## 💰 Cost-Saving Configuration Strategy

### Your AI Model Priority (Cheapest to Most Expensive)

1. **Ollama Qwen3 14B** (LOCAL) - **$0.00**
   - Use for: ALL backtesting, experimentation, learning
   - Location: http://localhost:11434
   - Model: `qwen3:14b-q4_k_m`
   - Speed: ~5-6 seconds per response
   - Quality: Excellent for most tasks

2. **DeepSeek API** - **$0.14-0.28 per 1M tokens** (Very cheap!)
   - Use for: Backup when Ollama busy
   - You have key: ✅
   - Model: `deepseek-chat` or `deepseek-r1`

3. **Claude API** - **$3-15 per 1M tokens** (Your limited credits!)
   - Use for: Final validation ONLY
   - Save credits: Use sparingly!

---

## 📝 Agent-by-Agent Configuration

### 1. RBI Agent (PRIORITY - Start Here!)

**File**: `src/agents/rbi_agent_pp_multi.py`

**What it does**: Converts trading ideas into backtested strategies

**Your Configuration Changes**:

```python
# Line ~60-70: Change AI model to use Ollama
MODEL = "ollama/qwen3:14b-q4_k_m"
# OR keep DeepSeek for now (very cheap)
# MODEL = "deepseek/deepseek-r1"

# Line 130-132: Adjust targets
TARGET_RETURN = 20.0  # Good starting point
SAVE_IF_OVER_RETURN = 1.0  # Save if > 1% return

# Line ~102-103: Start with classic mode
STRATEGIES_FROM_FILES = False
# (Later switch to True for web search integration)

# Line ~154: Reduce threads if needed
MAX_PARALLEL_THREADS = 2  # Start with 2, increase if system handles it
```

**File paths to update** (search for these and change to your paths):
```python
# Around line 169
DATA_DIR = "G:\\Drive'ım\\Moondev_AI_agents\\moon-dev-ai-agents\\src\\data\\rbi"

# Around line 171
IDEAS_FILE = "G:\\Drive'ım\\Moondev_AI_agents\\moon-dev-ai-agents\\src\\data\\rbi_pp_multi\\ideas.txt"
```

**First Test**:
```bash
# 1. Create ideas file
cd "G:\Drive'ım\Moondev_AI_agents\moon-dev-ai-agents\src\data\rbi_pp_multi"
echo "RSI strategy: Buy when RSI < 30, sell when RSI > 70" > ideas.txt

# 2. Run agent
cd "G:\Drive'ım\Moondev_AI_agents\moon-dev-ai-agents"
python src\agents\rbi_agent_pp_multi.py
```

---

### 2. Research Agent

**File**: `src/agents/research_agent.py`

**What it does**: Finds trading strategy ideas automatically

**Configuration**: Check if it uses configurable AI model, switch to Ollama/DeepSeek

---

### 3. Chart Analysis Agent

**File**: `src/agents/chartanalysis_agent.py`

**What it does**: Analyzes chart screenshots using AI

**Your setup**: Can use Ollama for this too!

---

### 4. Web Search Agent

**File**: `src/agents/websearch_agent.py`

**What it does**: Auto-finds strategies, feeds into RBI agent

**Advanced use**: Run this + RBI agent 24/7 for fully automated discovery

---

## 🔧 How to Configure Each Agent for Ollama

### Standard Pattern in Most Agents

Look for these lines in agent files:

```python
# OLD (uses paid API)
MODEL = "claude-3-5-sonnet-20241022"
# or
MODEL = "gpt-4"
# or
MODEL = "deepseek-chat"

# CHANGE TO (uses FREE Ollama)
MODEL = "ollama/qwen3:14b-q4_k_m"
```

### Using LiteLLM (the library these agents use)

Add to your .env file:
```bash
# Ollama as primary
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:14b-q4_k_m

# Fallbacks
DEEPSEEK_KEY=sk-8d8e112d20fd4fbdb9e388f49aca484c
OPENAI_KEY=your_key_here
ANTHROPIC_KEY=sk-ant-api03-...
```

Then in agent code:
```python
import litellm
import os

# Try Ollama first, fall back to DeepSeek
try:
    response = litellm.completion(
        model="ollama/qwen3:14b-q4_k_m",
        messages=messages,
        api_base="http://localhost:11434"
    )
except:
    # Fallback to DeepSeek if Ollama fails
    response = litellm.completion(
        model="deepseek/deepseek-chat",
        messages=messages,
        api_key=os.getenv("DEEPSEEK_KEY")
    )
```

---

## 📊 Recommended Testing Order

### Week 1: Backtesting & Learning
1. **Day 1-2**: RBI Agent with Ollama
   - Test 10-20 simple strategies
   - Learn how to read backtest results
   - Cost: $0.00

2. **Day 3-4**: Research Agent
   - Find strategy ideas automatically
   - Feed into RBI agent
   - Cost: ~$1-2 if using DeepSeek

3. **Day 5-7**: Chart Analysis
   - Practice with chart screenshots
   - Understand AI analysis
   - Cost: $0.00 with Ollama

### Week 2: Advanced Features
1. Web Search + RBI integration
2. Explore other analysis agents
3. Set up n8n workflows (optional)

### Week 3+: Production (If Desired)
1. Review best backtests
2. Paper trading first
3. Only then consider live (small amounts!)

---

## 🎯 Agent Categories & Your Use

### ✅ SAFE - Use Freely (No Real Money)

**Backtesting & Research**:
- `rbi_agent_pp_multi.py` - Automated backtesting ⭐ START HERE
- `research_agent.py` - Find strategy ideas
- `websearch_agent.py` - Auto-find strategies online

**Analysis**:
- `chartanalysis_agent.py` - Analyze charts
- `whale_agent.py` - Monitor whale activity
- `sentiment_agent.py` - Twitter sentiment
- `funding_agent.py` - Funding rates
- `liquidation_agent.py` - Track liquidations

**Content Creation**:
- `prompt_agent.py` - Improve prompts
- `tweet_agent.py` - Generate tweets
- `video_agent.py` - Create videos

### ⚠️ CAUTION - Read Docs First

- `swarm_agent.py` - Queries 6 AI models (uses your API credits!)
- `million_agent.py` - Uses Gemini's 1M context window

### ❌ DANGER - DO NOT RUN YET!

**These trade REAL MONEY**:
- `trading_agent.py` ❌
- `strategy_agent.py` ❌
- `sniper_agent.py` ❌
- `copy_agent.py` ❌
- `solana_agent.py` ❌

**Only after**:
1. Extensive backtesting
2. Paper trading
3. Understanding all risks
4. Setting up trading accounts
5. Small test amounts

---

## 🔍 Finding Configuration in Agents

### Quick Method to Find What Needs Changing

1. **Open agent file**:
   ```bash
   notepad src\agents\rbi_agent_pp_multi.py
   ```

2. **Search for these patterns** (Ctrl+F):
   - `MODEL =` - AI model selection
   - `API_KEY` - API key usage
   - `_DIR =` - Directory paths
   - `FILE =` - File paths
   - `FOLDER =` - Folder paths

3. **Common things to update**:
   - File paths (change to your Windows paths)
   - AI models (switch to Ollama/DeepSeek)
   - Thread counts (adjust for your system)
   - Timeframes/symbols (customize testing)

---

## 🛠️ System-Specific Configurations

### For Your 16GB VRAM

**Ollama Settings**:
```bash
# Check current Ollama config
curl http://localhost:11434/api/tags

# If needed, adjust num_ctx (context window)
# Lower = less VRAM usage
```

**Agent Thread Counts**:
```python
# RBI Agent - start conservative
MAX_PARALLEL_THREADS = 2  # Can increase to 4 if system handles it

# Research Agent - check docs
# Reduce concurrent operations if needed
```

### For Your Limited Claude Credits

**Add this to .env**:
```bash
# Track usage
USE_CLAUDE=false  # Default to false, manually enable when needed
CLAUDE_MAX_REQUESTS=10  # Daily limit you set
```

**Create usage tracker** (optional):
```python
# claude_tracker.py
import os
from datetime import date

def can_use_claude():
    """Check if we haven't exceeded daily limit"""
    today = str(date.today())
    count_file = "claude_usage.txt"

    if not os.path.exists(count_file):
        with open(count_file, 'w') as f:
            f.write(f"{today},0")
        return True

    with open(count_file, 'r') as f:
        last_date, count = f.read().strip().split(',')

    if last_date != today:
        # New day, reset
        count = 0

    max_requests = int(os.getenv('CLAUDE_MAX_REQUESTS', 10))
    return int(count) < max_requests
```

---

## 📚 Documentation Quick Reference

| Agent | Doc File | Priority for You |
|-------|----------|------------------|
| RBI Agent | [docs/rbi_agent.md](docs/rbi_agent.md) | ⭐⭐⭐ START HERE |
| Research | [docs/research_agent.md](docs/research_agent.md) | ⭐⭐ |
| Chart Analysis | [docs/chartanalysis_agent.md](docs/chartanalysis_agent.md) | ⭐⭐ |
| Web Search | [docs/websearch_agent.md](docs/websearch_agent.md) | ⭐ |
| Prompt | [docs/prompt_agent.md](docs/prompt_agent.md) | ⭐ |
| Trading | [docs/trading_agent.md](docs/trading_agent.md) | ❌ NOT YET |
| Swarm | [docs/swarm_agent.md](docs/swarm_agent.md) | ⚠️ COSTS MONEY |

---

## 🎁 Bonus: Your Docker Infrastructure Uses

### n8n Workflow Ideas
- Schedule RBI agent runs
- Alert when good backtest found
- Auto-save results to database

### Langfuse Integration
- Track all AI calls
- Monitor token usage
- Compare Ollama vs. paid APIs

### Supabase Backend
- Store backtest results
- Create web dashboard
- Share with team

### Qdrant Vector DB
- Store strategy embeddings
- Find similar strategies
- Semantic search

**I can help you set these up later if interested!**

---

## 📋 Next Actions

1. **Wait for pip install to complete**
2. **Test Claude API**: `python test_claude_api.py`
3. **Test Ollama**: `python test_ollama.py`
4. **Configure RBI agent for Ollama**
5. **Run first backtest**
6. **Review results**
7. **Ask me for help with specific agents!**

---

## 🆘 Getting Help

**For specific agents**:
1. Check `docs/[agent_name].md` first
2. Look at configuration section in agent file
3. Ask me - I've read all the docs! 😊

**Common questions I can help with**:
- "How do I configure [agent] for Ollama?"
- "What does this agent do?"
- "How much will running [agent] cost?"
- "What are the file paths I need to change?"
- "How do I integrate with my Docker setup?"

---

**Ready to start when you are!** Let me know when the installation completes and we'll test everything! 🚀
