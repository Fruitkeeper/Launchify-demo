import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Tuple
from models.openai_model import OpenAIModel
from models.anthropic_model import AnthropicModel  
from models.mistral_model import MistralModel
from router.scorer import Scorer
from db.db import DatabaseManager

class LLMRouter:
    def __init__(self):
        self.models = {
            'gpt-4o': OpenAIModel(),
            'claude': AnthropicModel(),
            'mistral': MistralModel()
        }
        self.scorer = Scorer()
        self.db = DatabaseManager()
    
    def get_ranked_models(self, prompt: str) -> List[Tuple[str, float]]:
        """
        Determine the ranked list of models for a given prompt based on historical performance
        Returns a list of (model_name, score) tuples sorted by score (highest first)
        """
        model_scores = {}
        
        for model_name in self.models.keys():
            # Get historical performance
            performance = self.db.get_model_performance(model_name)
            
            # Calculate score using current performance metrics
            score = self.scorer.calculate_score(
                latency_ms=performance['avg_latency'],
                cost=performance['avg_cost'],
                quality_score=performance['avg_score']
            )
            
            model_scores[model_name] = {
                'score': score,
                'performance': performance
            }
        
        # Sort models by score (highest first)
        ranked_models = sorted(model_scores.keys(), key=lambda k: model_scores[k]['score'], reverse=True)
        
        print(f"Model scores for prompt selection:")
        for model in ranked_models:
            data = model_scores[model]
            perf = data['performance']
            print(f"  {model}: score={data['score']:.3f} "
                  f"(quality={perf['avg_score']:.1f}, "
                  f"latency={perf['avg_latency']:.0f}ms, "
                  f"cost=${perf['avg_cost']:.4f}, "
                  f"runs={perf['total_runs']})")
        
        return [(model, model_scores[model]['score']) for model in ranked_models]
    
    def get_best_model(self, prompt: str) -> str:
        """
        Determine the best model for a given prompt based on historical performance
        Returns the model name to use
        """
        ranked_models = self.get_ranked_models(prompt)
        best_model = ranked_models[0][0]
        print(f"Selected model: {best_model}")
        return best_model
    
    def _is_error_response(self, response: Dict) -> bool:
        """Check if a response indicates an error"""
        return (
            response.get('answer_text', '').startswith('Error generating response:') or
            response.get('tokens', 0) == 0 or
            response.get('estimated_cost', 0) == 0.0
        )
    
    def generate_response(self, prompt: str, model_name: str = None) -> Dict:
        """
        Generate response using specified model or best model with fallback to second-best
        """
        if model_name is not None:
            # If a specific model is requested, try only that model
            if model_name not in self.models:
                raise ValueError(f"Unknown model: {model_name}")
            
            model = self.models[model_name]
            response = model.generate_response(prompt)
            response['model'] = model_name
            return response
        
        # Get ranked list of models
        ranked_models = self.get_ranked_models(prompt)
        
        # Try models in order of preference
        for i, (model_name, score) in enumerate(ranked_models):
            print(f"Trying model {i+1}/{len(ranked_models)}: {model_name}")
            
            model = self.models[model_name]
            response = model.generate_response(prompt)
            response['model'] = model_name
            
            # Check if response is valid (not an error)
            if not self._is_error_response(response):
                if i > 0:  # If we used a fallback model
                    print(f"✓ Successfully used fallback model: {model_name}")
                else:
                    print(f"✓ Successfully used primary model: {model_name}")
                return response
            else:
                print(f"✗ Model {model_name} failed: {response.get('answer_text', 'Unknown error')}")
                
                # If this was the last model, return the error response
                if i == len(ranked_models) - 1:
                    print("⚠ All models failed, returning last error response")
                    return response
                else:
                    print(f"→ Falling back to next model...")
        
        # This should never be reached, but just in case
        return response

    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        return list(self.models.keys())
    
    def update_learning_weights(self):
        """
        Update scoring weights based on historical performance
        This implements the "learning" aspect of the system
        """
        all_runs = self.db.get_all_runs()
        
        if len(all_runs) < 10:  # Need sufficient data
            print("Insufficient data for weight learning (need at least 10 runs)")
            return
        
        # Analyze which factors correlate most with high scores
        # This is a simple learning algorithm - could be made more sophisticated
        
        high_score_runs = [run for run in all_runs if run.get('critic_score', 0) >= 8]
        low_score_runs = [run for run in all_runs if run.get('critic_score', 0) <= 4]
        
        if not high_score_runs or not low_score_runs:
            print("Insufficient diversity in scores for learning")
            return
        
        # Calculate average metrics for high vs low scoring runs
        def avg_metric(runs, metric):
            values = [run[metric] for run in runs if run.get(metric) is not None]
            return sum(values) / len(values) if values else 0
        
        high_avg_latency = avg_metric(high_score_runs, 'latency_ms')
        low_avg_latency = avg_metric(low_score_runs, 'latency_ms')
        
        high_avg_cost = avg_metric(high_score_runs, 'estimated_cost')
        low_avg_cost = avg_metric(low_score_runs, 'estimated_cost')
        
        # Adjust weights based on which factors differentiate good vs bad runs
        current_weights = self.scorer.get_weights()
        
        # If high-scoring runs have significantly lower latency, increase latency weight
        if low_avg_latency > 0 and high_avg_latency / low_avg_latency < 0.8:
            current_weights['latency'] *= 1.1
        
        # If high-scoring runs have significantly lower cost, increase cost weight  
        if low_avg_cost > 0 and high_avg_cost / low_avg_cost < 0.8:
            current_weights['cost'] *= 1.1
        
        # Always maintain some focus on quality
        if current_weights['quality'] < 0.3:
            current_weights['quality'] = 0.3
        
        # Update weights
        self.scorer.update_weights(current_weights)
        print(f"Updated weights based on learning: {self.scorer.get_weights()}") 