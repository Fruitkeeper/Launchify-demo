import os
import time
import anthropic
from dotenv import load_dotenv
from typing import Dict

# Load environment variables
load_dotenv()

class AnthropicModel:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model_name = "claude-3-5-sonnet-20241022"
        # Anthropic pricing per 1K tokens
        self.input_price_per_1k = 0.003  # $0.003 per 1K input tokens
        self.output_price_per_1k = 0.015  # $0.015 per 1K output tokens
        
    def generate_response(self, prompt: str) -> Dict:
        """Generate response from Anthropic Claude"""
        start_time = time.time()
        
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1500,
                temperature=0.7,
                system="You are a helpful assistant specializing in go-to-market strategy and business development. Provide comprehensive, actionable insights.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Extract response data
            answer_text = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            
            # Validate response
            if not answer_text or answer_text.strip() == "":
                return {
                    "answer_text": "Error generating response: Empty response from Claude",
                    "latency_ms": latency_ms,
                    "tokens": 0,
                    "estimated_cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "error_type": "empty_response"
                }
            
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
            error_type = "unknown_error"
            if "rate limit" in str(e).lower():
                error_type = "rate_limit"
            elif "invalid api key" in str(e).lower() or "authentication" in str(e).lower():
                error_type = "auth_error"
            elif "timeout" in str(e).lower():
                error_type = "timeout"
            elif "connection" in str(e).lower():
                error_type = "connection_error"
            
            return {
                "answer_text": f"Error generating response: {str(e)}",
                "latency_ms": (time.time() - start_time) * 1000,
                "tokens": 0,
                "estimated_cost": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "error_type": error_type
            } 