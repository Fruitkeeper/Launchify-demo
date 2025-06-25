import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict

# Load environment variables
load_dotenv()

class OpenAIModel:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model_name = "gpt-4o"
        # OpenAI pricing per 1K tokens (as of latest pricing)
        self.input_price_per_1k = 0.005  # $0.005 per 1K input tokens
        self.output_price_per_1k = 0.015  # $0.015 per 1K output tokens
        
    def generate_response(self, prompt: str) -> Dict:
        """Generate response from OpenAI GPT-4o"""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specializing in go-to-market strategy and business development. Provide comprehensive, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Extract response data
            answer_text = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
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