# 🚀 Using Your Local AI Infrastructure with Moon Dev Agents

## 🎯 Your Amazing Docker Setup!

You have a **professional-grade local AI infrastructure** running! Here's what you have:

### 🤖 AI & LLM Services
- **Ollama** (http://localhost:11434) - Local LLM inference
- **Open WebUI** (http://localhost:8080) - ChatGPT-like interface for local models
- **Flowise** (http://localhost:3001) - Visual LLM workflow builder

### 📊 Databases & Storage
- **Qdrant** (http://localhost:6333) - Vector database for embeddings
- **PostgreSQL** (localhost:5433) - Relational database
- **Neo4j** (http://localhost:7474) - Graph database
- **MinIO** (http://localhost:9010) - S3-compatible object storage
- **Redis/Valkey** (localhost:6379) - Cache & message broker
- **ClickHouse** (http://localhost:8123) - Analytics database

### 🛠️ Dev Tools & Platforms
- **n8n** (http://localhost:5678) - Workflow automation (like Zapier)
- **Supabase** - Full backend platform (database, auth, storage)
- **Langfuse** (http://localhost:3000) - LLM observability & analytics
- **SearxNG** (http://localhost:8081) - Privacy-focused search engine

---

## 🤖 Your Ollama Models

You have 4 powerful models installed:

### 1. **Qwen3 30B** (30.5B parameters) - RECOMMENDED for agents
- **Best for**: Complex reasoning, coding, strategy generation
- **Size**: 18.5 GB
- **Use for**: RBI agent, research agent, complex analysis

### 2. **Qwen3 14B** (14.8B parameters) - BALANCED
- **Best for**: General tasks, faster responses
- **Size**: 9.3 GB
- **Use for**: Most agents, good balance of speed/quality

### 3. **GLM-4.6 Cloud** (355B parameters) - CLOUD MODEL
- **Best for**: Highest quality when you need it
- **Note**: This calls external API (not fully local)

### 4. **MiniMax M2 Cloud** (230B parameters) - CLOUD MODEL
- **Best for**: Complex tasks requiring massive models
- **Note**: This calls external API (not fully local)

---

## 💰 Cost Savings Using Local Models

**Estimated costs with cloud APIs**:
- Claude API: ~$3-$15 per 1M tokens
- GPT-4: ~$10-$30 per 1M tokens
- DeepSeek: ~$0.14-$0.28 per 1M tokens

**With local Ollama**: **$0.00** (just electricity!)

For the RBI agent running 100 backtests:
- Cloud APIs: $5-$50
- **Local Ollama**: $0.00 🎉

---

## 🔧 How to Use Ollama with Moon Dev Agents

### Step 1: Test Ollama Connection

```bash
# Test if Ollama is accessible
curl http://localhost:11434/api/tags

# Test a simple generation
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:30b",
  "prompt": "Say hello in one sentence",
  "stream": false
}'
```

### Step 2: Configure Agents to Use Ollama

Most Moon Dev agents use environment variables or configuration. Here's how to modify them:

#### Option A: Using LiteLLM (Recommended)

The agents use `litellm` which supports Ollama. Add to your [.env](.env):

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:30b  # or qwen3:14b for faster responses
```

#### Option B: Modify Agent Files Directly

For agents like RBI, you can modify the model selection:

**File**: [src/agents/rbi_agent_pp_multi.py](src/agents/rbi_agent_pp_multi.py)

Look for lines like:
```python
# Around line 50-60, find the model configuration
MODEL = "deepseek-chat"  # Change this
```

Change to:
```python
MODEL = "ollama/qwen3:30b"  # Use local Ollama
# or
MODEL = "ollama/qwen3:14b"  # Faster, still good quality
```

### Step 3: Create Ollama Helper Script

I'll create a script to easily switch between cloud and local models.

---

## 🎯 Recommended Setup for YOU

### For RBI Backtesting Agent:
1. **Use Qwen3 30B** for best quality (completely free!)
2. Falls back to DeepSeek if Ollama unavailable
3. Only use Claude for final verification

### For Research/Analysis Agents:
1. **Use Qwen3 14B** for speed
2. Good enough for most tasks

### For Critical Work:
1. Use Claude (your paid API)
2. But only after testing with local models first

---

## 🔗 Integration Opportunities

Your Docker setup enables some powerful integrations:

### 1. **n8n Workflows** (http://localhost:5678)
- Automate running agents on schedule
- Chain multiple agents together
- Send notifications to Discord/Telegram

### 2. **Langfuse Tracking** (http://localhost:3000)
- Track all AI agent calls
- Monitor token usage
- Debug agent behavior
- Compare model performance

### 3. **Supabase Backend**
- Store backtest results in PostgreSQL
- Create web dashboards
- Share results with team

### 4. **Qdrant Vector DB**
- Store strategy embeddings
- Find similar trading strategies
- Semantic search through backtests

---

## 📝 Quick Start Commands

### Using Local Qwen3 30B:
```bash
# Add to .env
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
echo "OLLAMA_MODEL=qwen3:30b" >> .env
```

### Test Ollama API:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:30b",
  "prompt": "Explain RSI indicator in one sentence",
  "stream": false
}'
```

### Check Ollama Status:
```bash
docker logs ollama
```

---

## 🎁 Bonus: Model Recommendations by Task

| Task | Model | Reason |
|------|-------|--------|
| **RBI Backtesting** | Qwen3 30B | Best reasoning for strategy generation |
| **Research Agent** | Qwen3 14B | Fast, good quality |
| **Chart Analysis** | Qwen3 30B | Better visual understanding |
| **Tweet Generation** | Qwen3 14B | Fast, creative |
| **Code Generation** | Qwen3 30B | Best for complex code |
| **Quick Tasks** | Qwen3 14B | Speed matters |
| **Critical Decisions** | Claude (API) | Highest quality, use sparingly |

---

## 🚀 Next Steps

1. **Test Claude API** (when installation completes)
2. **Create Ollama integration script**
3. **Configure RBI agent for local models**
4. **Set up Langfuse tracking** (optional)
5. **Create n8n workflow** for automated backtesting (optional)

---

## 💡 Pro Tips

1. **Start with Ollama** for all testing and experimentation
2. **Only use cloud APIs** (Claude, GPT) for final production runs
3. **Use Langfuse** to track which models perform best for which tasks
4. **Set up n8n** to automatically run backtests every night
5. **Use Qdrant** to build a searchable library of strategies

Your setup is **production-grade** and could save you **hundreds of dollars** in API costs! 🎉
