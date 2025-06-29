#!/usr/bin/env python3
"""
Process LLM routing run results and create organized response files
"""

import csv
import json
import os
from pathlib import Path

def clean_filename(text):
    """Clean text to create valid filename"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '_')
    # Truncate if too long
    return text[:50].strip()

def process_run_results(csv_file):
    """Process CSV file and create organized response files"""
    
    base_dir = Path(csv_file).parent
    responses_dir = base_dir / "responses"
    by_topic_dir = responses_dir / "by_topic"
    by_model_dir = responses_dir / "by_model"
    
    # Read CSV file
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Processing {len(rows)} responses...")
    
    for row in rows:
        prompt_id = row['prompt_id']
        model = row['model']
        prompt = row['prompt']
        answer = row['answer']
        critic_score = row['critic_score']
        critic_rationale = row['critic_rationale']
        latency_ms = row['latency_ms']
        tokens = row['tokens']
        estimated_cost = row['estimated_cost']
        timestamp = row['timestamp']
        
        # Create clean filename from prompt
        prompt_short = clean_filename(prompt)
        
        # Create response data
        response_data = {
            "metadata": {
                "prompt_id": int(prompt_id),
                "model": model,
                "timestamp": timestamp,
                "performance": {
                    "latency_ms": float(latency_ms),
                    "tokens": int(tokens),
                    "estimated_cost": float(estimated_cost)
                },
                "quality": {
                    "critic_score": float(critic_score),
                    "critic_rationale": critic_rationale
                }
            },
            "prompt": prompt,
            "response": answer
        }
        
        # Save by topic
        topic_filename = f"{prompt_id:02d}_{prompt_short}.json"
        topic_file = by_topic_dir / topic_filename
        
        with open(topic_file, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        
        # Save by model
        model_dir = by_model_dir / model
        model_filename = f"{prompt_id:02d}_{prompt_short}.json"
        model_file = model_dir / model_filename
        
        with open(model_file, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Processed prompt {prompt_id}: {prompt[:50]}...")
    
    print(f"\n✅ Successfully processed {len(rows)} responses")
    print(f"📁 Files saved to:")
    print(f"   - By topic: {by_topic_dir}")
    print(f"   - By model: {by_model_dir}")

if __name__ == "__main__":
    csv_file = "raw_data.csv"
    if os.path.exists(csv_file):
        process_responses(csv_file)
    else:
        print(f"❌ CSV file not found: {csv_file}") 