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