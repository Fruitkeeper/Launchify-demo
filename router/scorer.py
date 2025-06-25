import os
import yaml
from typing import Dict

class Scorer:
    def __init__(self, weights_path: str = "config/weights.yaml"):
        self.weights_path = weights_path
        self.weights = self.load_weights()
    
    def load_weights(self) -> Dict[str, float]:
        """Load weights from YAML config file"""
        try:
            with open(self.weights_path, 'r') as file:
                weights = yaml.safe_load(file)
                return {
                    'latency': weights.get('latency', 0.4),
                    'cost': weights.get('cost', 0.2), 
                    'quality': weights.get('quality', 0.4)
                }
        except Exception as e:
            print(f"Error loading weights: {e}. Using defaults.")
            return {'latency': 0.4, 'cost': 0.2, 'quality': 0.4}
    
    def calculate_score(self, latency_ms: float, cost: float, quality_score: float) -> float:
        """
        Calculate weighted score for a model based on:
        - latency_ms: response time in milliseconds (lower is better)
        - cost: estimated cost in dollars (lower is better) 
        - quality_score: critic score 1-10 (higher is better)
        
        Returns a score where higher is better
        """
        # Normalize latency (invert so lower latency = higher score)
        # Using log scale to handle wide latency ranges
        latency_score = max(0, 1 / (1 + latency_ms / 1000))  # Convert to 0-1 scale
        
        # Normalize cost (invert so lower cost = higher score)
        cost_score = max(0, 1 / (1 + cost * 100))  # Scale cost and invert
        
        # Normalize quality (scale 1-10 to 0-1)
        quality_normalized = max(0, (quality_score - 1) / 9)
        
        # Calculate weighted score
        total_score = (
            self.weights['latency'] * latency_score +
            self.weights['cost'] * cost_score +
            self.weights['quality'] * quality_normalized
        )
        
        return total_score
    
    def update_weights(self, new_weights: Dict[str, float]):
        """Update weights and save to config file"""
        self.weights.update(new_weights)
        
        # Normalize weights to sum to 1
        total = sum(self.weights.values())
        if total > 0:
            for key in self.weights:
                self.weights[key] /= total
        
        # Save updated weights
        try:
            with open(self.weights_path, 'w') as file:
                yaml.dump(self.weights, file, default_flow_style=False)
        except Exception as e:
            print(f"Error saving weights: {e}")
    
    def get_weights(self) -> Dict[str, float]:
        """Get current weights"""
        return self.weights.copy() 