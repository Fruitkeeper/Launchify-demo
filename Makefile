.PHONY: install run rerun clean test docker-build docker-run help

# Default target
help:
	@echo "🚀 Meta-Agent LLM Router - Available Commands:"
	@echo ""
	@echo "  make install     - Install dependencies"
	@echo "  make run         - Run the system (first time)"
	@echo "  make rerun       - Rerun with learning from previous results"
	@echo "  make test        - Run a quick test with sample prompts"
	@echo "  make clean       - Clean up generated files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run in Docker container"
	@echo "  make summary     - Show historical performance summary"
	@echo ""
	@echo "Environment setup:"
	@echo "  1. Copy .env.example to .env"
	@echo "  2. Add your API keys to .env"
	@echo "  3. Run 'make install' to set up dependencies"
	@echo "  4. Run 'make run' to start the system"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"
	@echo ""
	@echo "⚠️  Don't forget to:"
	@echo "   1. Copy .env.example to .env"
	@echo "   2. Add your API keys to .env"

# Run the complete system
run:
	@echo "🚀 Running Meta-Agent LLM Router..."
	python run/run.py

# Rerun with learning enabled
rerun:
	@echo "🧠 Running with learning from previous results..."
	python run/run.py --rerun

# Quick test with first 3 prompts
test:
	@echo "🧪 Running quick test with first 3 prompts..."
	python run/run.py --prompts 1 2 3 --skip-critic

# Show performance summary
summary:
	@echo "📊 Generating historical summary..."
	python -c "from db.db import DatabaseManager; from run.summary import SummaryGenerator; db = DatabaseManager(); sg = SummaryGenerator(db); sg.print_historical_summary()"

# Clean up generated files
clean:
	@echo "🧹 Cleaning up..."
	rm -f data.db
	rm -f summary_*.csv
	rm -f learning_data.csv
	rm -rf __pycache__
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "✅ Cleanup complete!"

# Docker commands
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t meta-agent-llm-router .

docker-run:
	@echo "🐳 Running in Docker container..."
	docker run --env-file .env -v $(PWD)/data:/app/data meta-agent-llm-router

# Advanced options
run-gpt:
	@echo "🤖 Running with GPT-4o only..."
	python run/run.py --model gpt-4o

run-claude:
	@echo "🤖 Running with Claude only..."
	python run/run.py --model claude

run-mistral:
	@echo "🤖 Running with Mistral only..."
	python run/run.py --model mistral

# Export learning data for analysis
export:
	@echo "📊 Exporting learning data..."
	python -c "from db.db import DatabaseManager; from run.summary import SummaryGenerator; db = DatabaseManager(); sg = SummaryGenerator(db); sg.export_learning_data()" 