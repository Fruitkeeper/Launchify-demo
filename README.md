# 🚀 Meta-Agent LLM Router with Self-Learning Feedback Loop

An intelligent system that routes prompts to the best of 3 LLMs (GPT-4o, Claude, Mistral) using a weighted scoring function and learns from critic feedback to improve routing decisions over time.

## 🎯 What It Does

1. **Smart Routing**: Chooses the best LLM for each prompt based on latency, cost, and historical quality scores
2. **Critic Evaluation**: Uses GPT-3.5 to score responses (1-10) against reference answers  
3. **Self-Learning**: Adapts routing weights based on performance patterns from previous runs
4. **Performance Tracking**: Stores all results in SQLite and generates detailed summaries

## 🛠️ Quick Setup

```bash
# 1. Clone and setup
git clone <repo-url>
cd meta-agent-llm-router

# 2. Install dependencies  
make install

# 3. Configure API keys
cp .env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY=your-key
# ANTHROPIC_API_KEY=your-key  
# MISTRAL_API_KEY=your-key

# 4. Run the system
make run
```

## 🚀 Usage

```bash
# Basic commands
make run              # First run (uses default weights)
make rerun            # Rerun with learning from previous results
make test             # Quick test with 3 prompts
make summary          # Show historical performance

# Advanced options
make run-gpt          # Force GPT-4o only
python run/run.py --prompts 1 2 3 --skip-critic  # Custom prompts
python run/run.py --model claude --rerun          # Force model + learning
```

## 🧠 How Learning Works

### Routing Logic
The system scores each model using: `score = w₁×(1/latency) + w₂×(1/cost) + w₃×quality`

**Default weights**: latency=0.4, cost=0.2, quality=0.4

### Learning Algorithm
1. **Data Collection**: Stores latency, cost, tokens, and critic scores for every run
2. **Pattern Analysis**: Identifies high-scoring (≥8) vs low-scoring (≤4) responses  
3. **Weight Adaptation**: Increases weights for factors that correlate with better outcomes
4. **Continuous Improvement**: Each `--rerun` applies learnings from all historical data

### Example Learning Scenarios
- If fast models consistently score higher → increase latency weight
- If cheap models perform well → increase cost weight  
- Always maintains minimum 30% quality weight to ensure focus on answer quality

## 📊 System Architecture

```
prompts/prompts.json     → 25 GTM strategy questions + reference answers
router/router.py         → Model selection logic with learning
router/scorer.py         → Weighted scoring algorithm  
models/*.py              → API wrappers for GPT-4o, Claude, Mistral
critic/critic.py         → GPT-3.5 evaluation against reference answers
db/db.py                 → SQLite storage and historical analysis
run/run.py               → Main orchestration pipeline
run/summary.py           → Performance reporting and CSV export
```

## 🎯 Design Decisions

**Model Selection**: Chose GPT-4o (latest), Claude 3.5 Sonnet (reasoning), Mistral Large (cost-effective)

**Scoring Approach**: Multi-factor optimization balances speed, cost, and quality rather than single metric

**Learning Strategy**: Simple but effective pattern recognition that avoids overfitting with small datasets

**Critic Design**: Uses separate GPT-3.5 for evaluation to avoid bias toward any specific model

**Database**: SQLite for simplicity and portability, with full historical tracking for learning

## 📈 Sample Output

```
Model scores for prompt selection:
  gpt-4o: score=0.751 (quality=8.2, latency=1200ms, cost=$0.0045, runs=15)
  claude: score=0.823 (quality=8.5, latency=800ms, cost=$0.0032, runs=12)  
  mistral: score=0.692 (quality=7.1, latency=600ms, cost=$0.0018, runs=8)
Selected model: claude

🎉 Run completed!
💰 Total cost: $0.0847
📊 Average critic score: 7.8/10
🗃️ Results saved with run ID: run_20241201_143022_a4b8f9d2
```

## 🐳 Docker Support

```bash
make docker-build      # Build container
make docker-run        # Run with volume mounting
```

## 📁 Key Files

- `prompts/prompts.json`: 25 GTM-focused questions with expert reference answers
- `config/weights.yaml`: Configurable scoring weights (auto-updated by learning)
- `data.db`: SQLite database with all historical runs and performance metrics
- `summary_*.csv`: Detailed results export for each run

## 🔧 Customization

- **Add models**: Extend `router/router.py` and create new model wrapper
- **Modify scoring**: Adjust `router/scorer.py` calculation logic
- **Change prompts**: Edit `prompts/prompts.json` with your domain questions  
- **Tune learning**: Modify thresholds and algorithms in `router/router.py`

Built with Python 3.11+, designed for production use with comprehensive error handling and monitoring. 