#!/usr/bin/env python3

import sys
import os
import argparse
import uuid
from datetime import datetime
from tqdm import tqdm

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from router.router import LLMRouter
from critic.critic import Critic
from db.db import DatabaseManager

# Import summary using absolute path to avoid circular import
summary_module_path = os.path.join(project_root, 'run', 'summary.py')
import importlib.util
spec = importlib.util.spec_from_file_location("summary", summary_module_path)
summary_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary_module)
SummaryGenerator = summary_module.SummaryGenerator

def main():
    parser = argparse.ArgumentParser(description='Meta-Agent LLM Router with Self-Learning Feedback Loop')
    parser.add_argument('--rerun', action='store_true', 
                       help='Rerun the system and apply learning from previous runs')
    parser.add_argument('--model', type=str, choices=['gpt-4o', 'claude', 'mistral'],
                       help='Force use of specific model instead of routing')
    parser.add_argument('--prompts', type=int, nargs='+',
                       help='Run specific prompt IDs only (e.g., --prompts 1 2 3)')
    parser.add_argument('--skip-critic', action='store_true',
                       help='Skip critic evaluation to save time/cost')
    
    args = parser.parse_args()
    
    # Initialize components
    print("🚀 Initializing Meta-Agent LLM Router...")
    router = LLMRouter()
    critic = Critic()
    db = DatabaseManager()
    
    # Generate unique run ID
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    print(f"📊 Run ID: {run_id}")
    
    # Apply learning if this is a rerun
    if args.rerun:
        print("🧠 Applying learning from previous runs...")
        router.update_learning_weights()
        print(f"Current weights: {router.scorer.get_weights()}")
    
    # Get prompts to process
    all_prompts = db.get_prompts()
    if args.prompts:
        prompts_to_run = [p for p in all_prompts if p['id'] in args.prompts]
        print(f"🎯 Running {len(prompts_to_run)} selected prompts: {args.prompts}")
    else:
        prompts_to_run = all_prompts
        print(f"📝 Running all {len(prompts_to_run)} prompts")
    
    if not prompts_to_run:
        print("❌ No prompts to process!")
        return
    
    # Process each prompt
    results = []
    print(f"\n🔄 Processing prompts...")
    
    for prompt_data in tqdm(prompts_to_run, desc="Processing prompts"):
        prompt_id = prompt_data['id']
        prompt_text = prompt_data['prompt']
        reference_answer = prompt_data['reference']
        
        print(f"\n📋 Prompt {prompt_id}: {prompt_text[:100]}...")
        
        try:
            # Route to best model or use forced model
            model_name = args.model if args.model else None
            
            # Generate response
            print(f"🤖 Generating response...")
            response = router.generate_response(prompt_text, model_name)
            
            print(f"✅ Response generated using {response['model']} "
                  f"(latency: {response['latency_ms']:.0f}ms, "
                  f"cost: ${response['estimated_cost']:.4f}, "
                  f"tokens: {response['tokens']})")
            
            # Evaluate response with critic (unless skipped)
            critic_score = None
            critic_rationale = None
            
            if not args.skip_critic:
                print("🎯 Evaluating response with critic...")
                evaluation = critic.evaluate_response(
                    response['answer_text'],
                    reference_answer,
                    prompt_text
                )
                critic_score = evaluation['score']
                critic_rationale = evaluation['rationale']
                print(f"📊 Critic score: {critic_score}/10 - {critic_rationale[:100]}...")
            
            # Store results in database
            db.store_run_result(
                run_id=run_id,
                prompt_id=prompt_id,
                model=response['model'],
                answer=response['answer_text'],
                latency_ms=response['latency_ms'],
                tokens=response['tokens'],
                estimated_cost=response['estimated_cost'],
                critic_score=critic_score,
                critic_rationale=critic_rationale
            )
            
            # Store for summary
            results.append({
                'prompt_id': prompt_id,
                'model': response['model'],
                'latency_ms': response['latency_ms'],
                'cost': response['estimated_cost'],
                'tokens': response['tokens'],
                'critic_score': critic_score,
                'prompt': prompt_text
            })
            
        except Exception as e:
            print(f"❌ Error processing prompt {prompt_id}: {e}")
            continue
    
    # Update model performance stats
    print("\n📈 Updating model performance statistics...")
    db.update_model_performance()
    
    # Generate and display summary
    print("\n📊 Generating summary...")
    summary_gen = SummaryGenerator(db)
    summary_gen.print_run_summary(run_id)
    summary_gen.save_run_summary(run_id, f"summary_{run_id}.csv")
    
    # Print final stats
    total_cost = sum(r['cost'] for r in results)
    scores_with_values = [r['critic_score'] for r in results if r['critic_score'] is not None]
    avg_score = sum(scores_with_values) / len(scores_with_values) if scores_with_values else 0
    
    print(f"\n🎉 Run completed!")
    print(f"💰 Total cost: ${total_cost:.4f}")
    if scores_with_values:
        print(f"📊 Average critic score: {avg_score:.1f}/10")
    else:
        print(f"📊 No critic scores (--skip-critic was used)")
    print(f"🗃️  Results saved with run ID: {run_id}")
    
    # Show learning opportunities
    if not args.rerun and len(db.get_all_runs()) >= 10:
        print("\n💡 Tip: Run with --rerun flag to apply learning from this and previous runs!")

if __name__ == "__main__":
    main() 