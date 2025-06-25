# 🎬 Loom Walkthrough Script - Meta-Agent LLM Router

## Video Structure (8-10 minutes)

### 1. Introduction (1 min)
**Scene**: Show README.md or project overview
- "Hi! I'm excited to show you the Meta-Agent LLM Router - an intelligent system that automatically chooses the best LLM for each prompt and gets smarter over time."
- "This system routes between GPT-4o, Claude, and Mistral based on speed, cost, and quality, then uses a critic to evaluate responses and learn from them."

### 2. Project Structure Tour (2 min)
**Scene**: File explorer showing project structure
- "Let's look at the architecture - we have 25 GTM strategy prompts with reference answers"
- "The router intelligently selects models using weighted scoring"
- "Each model wrapper handles API calls, timing, and cost calculation"
- "A critic evaluates responses, and everything gets stored for learning"

### 3. Configuration & Setup (1 min)
**Scene**: Terminal showing setup commands
```bash
# Show these commands
make help
cp .env.example .env
# Edit .env file showing API key fields
make install
```
- "Setup is simple - copy the environment file, add your API keys, and install dependencies"
- "The Makefile provides easy commands for all operations"

### 4. First Run Demo (2 min)
**Scene**: Terminal running the system
```bash
make test  # Quick demo with 3 prompts
```
- "Let's run a quick test with 3 prompts to see the system in action"
- "Watch how it selects models based on historical performance"
- "Each response gets evaluated by our critic for a 1-10 score"
- "Everything gets stored in the database for future learning"

### 5. Learning in Action (2 min)
**Scene**: Run system twice to show learning
```bash
make run          # First full run
make rerun        # Show learning adaptation
make summary      # Show historical performance
```
- "The magic happens with the learning - on reruns, it analyzes which factors lead to better scores"
- "If faster models consistently perform better, it increases the latency weight"
- "Show the updated weights and how model selection changes"

### 6. Results & Analytics (1 min)
**Scene**: Show summary tables and CSV export
```bash
# Show summary output
ls summary_*.csv
make export
```
- "The system generates beautiful summary tables showing performance by model"
- "Everything exports to CSV for deeper analysis"
- "You can see cost, latency, quality scores, and learning insights"

### 7. Advanced Features (1 min)
**Scene**: Show advanced usage
```bash
python run/run.py --model claude --prompts 1 5 10
make docker-build
```
- "Advanced features include forcing specific models, running custom prompt sets"
- "Full Docker support for production deployment"
- "Easy to extend with new models or scoring algorithms"

## Key Points to Emphasize

### The "Aha" Moments
1. **Smart Routing**: "This isn't just random - it's learning which model works best for each type of question"
2. **Real Learning**: "The weights actually change based on performance - it gets smarter over time"
3. **Practical Value**: "This saves money and time by automatically choosing the optimal model"

### Technical Highlights
- Multi-factor optimization (not just speed or cost)
- Unbiased evaluation using separate critic model
- Comprehensive data tracking for learning
- Production-ready with error handling

### Business Value
- Cost optimization through intelligent routing
- Quality assurance through systematic evaluation
- Continuous improvement without manual tuning
- Scalable architecture for enterprise use

## Demo Script Notes

### Opening Hook
"What if you could automatically route to the best AI model for each task and have the system learn and improve its choices over time? That's exactly what this Meta-Agent LLM Router does."

### Technical Deep-Dive Moments
- Show the scoring algorithm in `router/scorer.py`
- Highlight the learning logic in `router/router.py`  
- Demonstrate the database schema and historical tracking

### Closing
"This system demonstrates how we can build intelligent abstractions over multiple LLMs that get better over time. It's not just about having access to multiple models - it's about intelligently orchestrating them."

## Screen Recording Tips

### Tools Needed
- Terminal with clear font (Monaco/Fira Code, 14pt+)
- Code editor with syntax highlighting
- Browser for README viewing
- Screen recorder with good resolution

### Preparation
1. Clear terminal history
2. Have API keys ready (but don't show them on screen)
3. Reset database to show clean first run
4. Prepare sample .env file
5. Test all commands beforehand

### Visual Flow
1. Start with README.md overview
2. Show file structure in editor
3. Terminal commands and output
4. Back to code to show key algorithms
5. Return to terminal for results
6. End with summary tables/exports

## Alternative Versions

### Short Version (3-4 min)
- Quick intro
- Setup demonstration  
- Single run showing routing and learning
- Results summary

### Technical Deep-Dive (12-15 min)
- Detailed code walkthrough
- Algorithm explanations
- Multiple learning cycles
- Performance analysis
- Extension possibilities

### Business-Focused (5-6 min)
- Problem statement
- Solution overview
- ROI demonstration
- Deployment options
- Use case scenarios 