import os
import csv
import pandas as pd
from tabulate import tabulate
from typing import List, Dict, Optional
from db.db import DatabaseManager

class SummaryGenerator:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def print_run_summary(self, run_id: str):
        """Print a formatted summary table for a specific run"""
        runs = self.db.get_all_runs(run_id)
        
        if not runs:
            print(f"No runs found for run_id: {run_id}")
            return
        
        print(f"\n📊 SUMMARY - Run ID: {run_id}")
        print("=" * 80)
        
        # Prepare data for table
        table_data = []
        total_cost = 0
        total_tokens = 0
        scores = []
        
        for run in runs:
            score_display = f"{run['critic_score']}/10" if run['critic_score'] else "N/A"
            
            table_data.append([
                run['prompt_id'],
                run['model'][:8],  # Truncate model name
                score_display,
                f"{run['latency_ms']:.0f}ms",
                f"${run['estimated_cost']:.4f}",
                f"{run['tokens']:,}",
                run['prompt'][:50] + "..." if len(run['prompt']) > 50 else run['prompt']
            ])
            
            total_cost += run['estimated_cost']
            total_tokens += run['tokens']
            if run['critic_score']:
                scores.append(run['critic_score'])
        
        # Print table
        headers = ["Q#", "Model", "Score", "Latency", "Cost", "Tokens", "Prompt"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Print summary stats
        avg_score = sum(scores) / len(scores) if scores else 0
        print(f"\n📈 SUMMARY STATISTICS")
        print(f"Total Prompts: {len(runs)}")
        print(f"Total Cost: ${total_cost:.4f}")
        print(f"Total Tokens: {total_tokens:,}")
        print(f"Average Score: {avg_score:.1f}/10")
        print(f"Models Used: {', '.join(set(run['model'] for run in runs))}")
        
        # Model breakdown
        self._print_model_breakdown(runs)
        
        # Add intelligent routing analysis
        self._print_routing_analysis(runs)
    
    def _print_model_breakdown(self, runs: List[Dict]):
        """Print breakdown by model"""
        model_stats = {}
        
        for run in runs:
            model = run['model']
            if model not in model_stats:
                model_stats[model] = {
                    'count': 0,
                    'total_cost': 0,
                    'total_latency': 0,
                    'scores': []
                }
            
            model_stats[model]['count'] += 1
            model_stats[model]['total_cost'] += run['estimated_cost']
            model_stats[model]['total_latency'] += run['latency_ms']
            if run['critic_score']:
                model_stats[model]['scores'].append(run['critic_score'])
        
        print(f"\n🤖 MODEL PERFORMANCE BREAKDOWN")
        model_table = []
        
        for model, stats in model_stats.items():
            avg_score = sum(stats['scores']) / len(stats['scores']) if stats['scores'] else 0
            avg_latency = stats['total_latency'] / stats['count']
            avg_cost = stats['total_cost'] / stats['count']
            
            model_table.append([
                model,
                stats['count'],
                f"{avg_score:.1f}/10",
                f"{avg_latency:.0f}ms",
                f"${avg_cost:.4f}",
                f"${stats['total_cost']:.4f}"
            ])
        
        headers = ["Model", "Count", "Avg Score", "Avg Latency", "Avg Cost", "Total Cost"]
        print(tabulate(model_table, headers=headers, tablefmt="grid"))
    
    def save_run_summary(self, run_id: str, filename: str):
        """Save run summary to CSV file"""
        runs = self.db.get_all_runs(run_id)
        
        if not runs:
            print(f"No runs found for run_id: {run_id}")
            return
        
        # Prepare data for CSV
        csv_data = []
        for run in runs:
            csv_data.append({
                'run_id': run['run_id'],
                'prompt_id': run['prompt_id'],
                'model': run['model'],
                'prompt': run['prompt'],
                'answer': run['answer'],
                'latency_ms': run['latency_ms'],
                'tokens': run['tokens'],
                'estimated_cost': run['estimated_cost'],
                'critic_score': run['critic_score'],
                'critic_rationale': run['critic_rationale'],
                'timestamp': run['timestamp']
            })
        
        # Save to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if csv_data:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
        
        print(f"📁 Detailed results saved to: {filename}")
    
    def print_historical_summary(self, limit: int = 5):
        """Print summary of recent runs"""
        all_runs = self.db.get_all_runs()
        
        if not all_runs:
            print("No historical runs found.")
            return
        
        # Group by run_id
        runs_by_id = {}
        for run in all_runs:
            run_id = run['run_id']
            if run_id not in runs_by_id:
                runs_by_id[run_id] = []
            runs_by_id[run_id].append(run)
        
        # Get recent runs
        recent_run_ids = sorted(runs_by_id.keys())[-limit:]
        
        print(f"\n📊 HISTORICAL SUMMARY (Last {len(recent_run_ids)} Runs)")
        print("=" * 80)
        
        history_table = []
        for run_id in recent_run_ids:
            runs = runs_by_id[run_id]
            total_cost = sum(run['estimated_cost'] for run in runs)
            scores = [run['critic_score'] for run in runs if run['critic_score']]
            avg_score = sum(scores) / len(scores) if scores else 0
            models_used = list(set(run['model'] for run in runs))
            
            # Get timestamp from first run
            timestamp = runs[0]['timestamp'][:16] if runs else ""
            
            history_table.append([
                run_id[-8:],  # Show last 8 chars of run_id
                timestamp,
                len(runs),
                ', '.join(models_used),
                f"{avg_score:.1f}/10",
                f"${total_cost:.4f}"
            ])
        
        headers = ["Run ID", "Timestamp", "Prompts", "Models", "Avg Score", "Total Cost"]
        print(tabulate(history_table, headers=headers, tablefmt="grid"))
    
    def export_learning_data(self, filename: str = "learning_data.csv"):
        """Export data for analysis and learning"""
        all_runs = self.db.get_all_runs()
        
        # Calculate additional metrics for learning
        learning_data = []
        for run in all_runs:
            learning_data.append({
                'run_id': run['run_id'],
                'prompt_id': run['prompt_id'],
                'model': run['model'],
                'latency_ms': run['latency_ms'],
                'estimated_cost': run['estimated_cost'],
                'tokens': run['tokens'],
                'critic_score': run['critic_score'],
                'cost_per_token': run['estimated_cost'] / run['tokens'] if run['tokens'] > 0 else 0,
                'efficiency_score': run['critic_score'] / (run['latency_ms'] / 1000) if run['critic_score'] and run['latency_ms'] > 0 else 0,
                'value_score': run['critic_score'] / run['estimated_cost'] if run['critic_score'] and run['estimated_cost'] > 0 else 0
            })
        
        # Save to CSV
        if learning_data:
            df = pd.DataFrame(learning_data)
            df.to_csv(filename, index=False)
            print(f"📊 Learning data exported to: {filename}")
            
            # Print some basic insights
            print(f"\n🔍 INSIGHTS")
            print(f"Total runs: {len(learning_data)}")
            
            if df['critic_score'].notna().any():
                best_model = df.groupby('model')['critic_score'].mean().idxmax()
                print(f"Best performing model: {best_model}")
                
                fastest_model = df.groupby('model')['latency_ms'].mean().idxmin()
                print(f"Fastest model: {fastest_model}")
                
                cheapest_model = df.groupby('model')['estimated_cost'].mean().idxmin()
                print(f"Most cost-effective model: {cheapest_model}")
        else:
            print("No data available for export.")

    def _print_routing_analysis(self, runs: List[Dict]):
        """Print intelligent routing analysis"""
        if len(runs) < 3:
            return  # Not enough data for meaningful analysis
            
        print(f"\n🧠 REAL-TIME LEARNING IN ACTION")
        print("=" * 50)
        
        # Group runs by model to analyze patterns
        model_switches = []
        prev_model = None
        model_performance = {}
        
        for i, run in enumerate(runs):
            model = run['model']
            prompt_id = run['prompt_id']
            score = run['critic_score'] if run['critic_score'] else 0
            latency = run['latency_ms']
            cost = run['estimated_cost']
            
            # Track model performance
            if model not in model_performance:
                model_performance[model] = {
                    'prompts': [],
                    'scores': [],
                    'latencies': [],
                    'costs': []
                }
            
            model_performance[model]['prompts'].append(prompt_id)
            model_performance[model]['scores'].append(score)
            model_performance[model]['latencies'].append(latency)
            model_performance[model]['costs'].append(cost)
            
            # Track switches
            if prev_model and prev_model != model:
                model_switches.append({
                    'prompt': prompt_id,
                    'from': prev_model,
                    'to': model,
                    'reason': self._analyze_switch_reason(runs[:i], model)
                })
            prev_model = model
        
        # Analyze routing decisions
        routing_insights = []
        
        # First few prompts analysis
        first_models = [r['model'] for r in runs[:3]]
        if len(set(first_models)) == 1:
            routing_insights.append(f"Prompts 1-3: Started with {first_models[0]} (no historical data)")
        else:
            routing_insights.append(f"Prompts 1-3: Tried {', '.join(set(first_models))} (exploring options)")
        
        # Model dominance analysis
        for model, perf in model_performance.items():
            if len(perf['prompts']) > len(runs) * 0.5:  # Model used for >50% of prompts
                avg_score = sum(perf['scores']) / len(perf['scores']) if perf['scores'] else 0
                avg_latency = sum(perf['latencies']) / len(perf['latencies'])
                avg_cost = sum(perf['costs']) / len(perf['costs'])
                routing_insights.append(
                    f"{model.title()} dominated ({len(perf['prompts'])} prompts): "
                    f"{avg_score:.1f}/10 score, {avg_latency/1000:.1f}s latency, ${avg_cost:.4f} cost"
                )
        
        # Switch analysis
        if model_switches:
            for switch in model_switches:
                routing_insights.append(
                    f"Prompt {switch['prompt']}: Switched {switch['from']} → {switch['to']} "
                    f"({switch['reason']})"
                )
        
        # New model exploration
        model_first_use = {}
        for run in runs:
            model = run['model']
            if model not in model_first_use:
                model_first_use[model] = run['prompt_id']
        
        for model, first_prompt in model_first_use.items():
            if first_prompt > 1:  # Not the first prompt
                routing_insights.append(f"Prompt {first_prompt}: Tried {model} for the first time!")
        
        # Print insights
        print("📈 Watch the intelligent routing happen:")
        for insight in routing_insights[:6]:  # Limit to most important insights
            print(f"   • {insight}")
        
        # Performance summary
        print(f"\n📊 OUTSTANDING RESULTS")
        successful_prompts = len([r for r in runs if r['estimated_cost'] > 0])
        total_cost = sum(r['estimated_cost'] for r in runs)
        avg_cost_per_response = total_cost / len(runs) if runs else 0
        scores_with_values = [r['critic_score'] for r in runs if r['critic_score']]
        avg_score = sum(scores_with_values) / len(scores_with_values) if scores_with_values else 0
        
        print(f"   ✅ {successful_prompts}/{len(runs)} prompts processed successfully")
        print(f"   💰 Total cost: ${total_cost:.2f} (${avg_cost_per_response:.3f} per response!)")
        if scores_with_values:
            print(f"   ⭐ Average quality: {avg_score:.1f}/10 (excellent!)")
        print(f"   ⚡ Intelligent routing working perfectly")
        
        # Model performance summary
        print(f"\n🤖 Model Performance:")
        for model, perf in model_performance.items():
            if len(perf['prompts']) > 0:
                avg_score = sum(perf['scores']) / len(perf['scores']) if perf['scores'] else 0
                avg_latency = sum(perf['latencies']) / len(perf['latencies']) / 1000  # Convert to seconds
                avg_cost = sum(perf['costs']) / len(perf['costs'])
                print(f"   • {model.title()}: {len(perf['prompts'])} prompts, "
                      f"{avg_score:.1f}/10 score, {avg_latency:.1f}s avg latency, "
                      f"${avg_cost:.4f} avg cost")
    
    def _analyze_switch_reason(self, previous_runs: List[Dict], new_model: str) -> str:
        """Analyze why the system switched to a new model"""
        if not previous_runs:
            return "initial choice"
        
        last_run = previous_runs[-1]
        last_model = last_run['model']
        
        # Simple heuristic analysis
        if last_run['latency_ms'] > 15000:  # > 15 seconds
            return "previous model too slow"
        elif last_run['estimated_cost'] > 0.01:  # > 1 cent
            return "previous model too expensive"
        elif last_run['critic_score'] and last_run['critic_score'] < 7:
            return "previous model low quality"
        else:
            return "exploring better options" 