import os
import time
import requests
from dotenv import load_dotenv
from typing import Dict

# Load environment variables
load_dotenv()

class MistralModel:
    def __init__(self):
        self.api_key = os.getenv('MISTRAL_API_KEY')
        self.model_name = "mistral-large-latest"
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        # Mistral pricing per 1K tokens (approximate)
        self.input_price_per_1k = 0.002  # $0.002 per 1K input tokens
        self.output_price_per_1k = 0.006  # $0.006 per 1K output tokens
        
    def generate_response(self, prompt: str) -> Dict:
        """Generate response from Mistral"""
        start_time = time.time()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant specializing in go-to-market strategy and business development. Provide comprehensive, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            response_data = response.json()
            
            # Extract response data
            answer_text = response_data['choices'][0]['message']['content']
            
            # Estimate token usage (Mistral doesn't always return usage data)
            if 'usage' in response_data:
                input_tokens = response_data['usage']['prompt_tokens']
                output_tokens = response_data['usage']['completion_tokens']
                total_tokens = response_data['usage']['total_tokens']
            else:
                # Rough estimation: ~4 characters per token
                input_tokens = len(prompt) // 4
                output_tokens = len(answer_text) // 4
                total_tokens = input_tokens + output_tokens
            
            # Calculate cost
            input_cost = (input_tokens / 1000) * self.input_price_per_1k
            output_cost = (output_tokens / 1000) * self.output_price_per_1k
            estimated_cost = input_cost + output_cost
            
            return {
                "answer_text": answer_text,
                "latency_ms": latency_ms,
                "tokens": total_tokens,
                "estimated_cost": estimated_cost,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
            
        except Exception as e:
            return {
                "answer_text": f"Error generating response: {str(e)}",
                "latency_ms": (time.time() - start_time) * 1000,
                "tokens": 0,
                "estimated_cost": 0.0,
                "input_tokens": 0,
                "output_tokens": 0
            } 