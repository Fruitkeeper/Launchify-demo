import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Tuple
import re

# Load environment variables
load_dotenv()

class Critic:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model_name = "gpt-3.5-turbo"
    
    def evaluate_response(self, model_answer: str, reference_answer: str, prompt: str) -> Dict:
        """
        Evaluate a model's answer against a reference answer
        Returns score (1-10) and rationale
        """
        
        evaluation_prompt = f"""
You are an expert evaluator of go-to-market strategy responses. Your task is to compare a model's answer to a reference answer and provide a score from 1 to 10.

ORIGINAL QUESTION:
{prompt}

REFERENCE ANSWER (Gold Standard):
{reference_answer}

MODEL'S ANSWER:
{model_answer}

Please evaluate the model's answer based on:
1. Accuracy - How well does it align with the reference answer?
2. Completeness - Does it cover the key points from the reference?
3. Clarity - Is it well-structured and easy to understand?
4. Practical Value - Does it provide actionable insights?
5. Business Relevance - Is it relevant to real GTM scenarios?

Provide your evaluation in this exact format:
SCORE: [number from 1-10]
RATIONALE: [2-3 sentence explanation of why you gave this score, highlighting strengths and weaknesses]

Score Guide:
- 9-10: Excellent - Matches or exceeds reference quality, comprehensive and actionable
- 7-8: Good - Covers most key points with good practical value
- 5-6: Average - Basic coverage but missing some important elements
- 3-4: Below Average - Partial coverage with significant gaps
- 1-2: Poor - Major inaccuracies or severely incomplete
"""
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional evaluator who provides consistent, objective assessments of business strategy content."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent evaluation
                max_tokens=500
            )
            
            end_time = time.time()
            evaluation_text = response.choices[0].message.content
            
            # Parse the response to extract score and rationale
            score, rationale = self._parse_evaluation(evaluation_text)
            
            return {
                "score": score,
                "rationale": rationale,
                "evaluation_time_ms": (end_time - start_time) * 1000,
                "raw_evaluation": evaluation_text
            }
            
        except Exception as e:
            print(f"Error in critic evaluation: {e}")
            return {
                "score": 5,  # Default neutral score on error
                "rationale": f"Evaluation failed due to error: {str(e)}",
                "evaluation_time_ms": 0,
                "raw_evaluation": ""
            }
    
    def _parse_evaluation(self, evaluation_text: str) -> Tuple[int, str]:
        """Parse the evaluation text to extract score and rationale"""
        
        try:
            # Look for SCORE: pattern
            score_match = re.search(r'SCORE:\s*(\d+)', evaluation_text, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
                score = max(1, min(10, score))  # Clamp to 1-10 range
            else:
                # Fallback: look for any number between 1-10
                numbers = re.findall(r'\b([1-9]|10)\b', evaluation_text)
                score = int(numbers[0]) if numbers else 5
            
            # Look for RATIONALE: pattern
            rationale_match = re.search(r'RATIONALE:\s*(.+?)(?:\n\n|$)', evaluation_text, re.IGNORECASE | re.DOTALL)
            if rationale_match:
                rationale = rationale_match.group(1).strip()
            else:
                # Fallback: use the entire text after cleaning
                rationale = evaluation_text.replace("SCORE:", "").replace("RATIONALE:", "").strip()
                # Take first few sentences if too long
                sentences = rationale.split('. ')
                if len(sentences) > 3:
                    rationale = '. '.join(sentences[:3]) + '.'
            
            return score, rationale
            
        except Exception as e:
            print(f"Error parsing evaluation: {e}")
            return 5, "Could not parse evaluation properly"
    
    def batch_evaluate(self, evaluations: list) -> list:
        """
        Evaluate multiple responses in batch
        evaluations: list of dicts with 'model_answer', 'reference_answer', 'prompt'
        """
        results = []
        
        for i, eval_data in enumerate(evaluations):
            print(f"Evaluating response {i+1}/{len(evaluations)}...")
            result = self.evaluate_response(
                eval_data['model_answer'],
                eval_data['reference_answer'], 
                eval_data['prompt']
            )
            results.append(result)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        return results 