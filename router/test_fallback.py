#!/usr/bin/env python3
"""
Test script to demonstrate fallback functionality when models fail
"""

import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from router.router import LLMRouter
from models.openai_model import OpenAIModel
from models.anthropic_model import AnthropicModel
from models.mistral_model import MistralModel

class MockFailingModel:
    """Mock model that always fails for testing"""
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    def generate_response(self, prompt: str):
        return {
            "answer_text": f"Error generating response: {self.model_name} is intentionally failing for testing",
            "latency_ms": 100,
            "tokens": 0,
            "estimated_cost": 0.0,
            "input_tokens": 0,
            "output_tokens": 0,
            "error_type": "test_failure"
        }

class MockSuccessModel:
    """Mock model that always succeeds for testing"""
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    def generate_response(self, prompt: str):
        return {
            "answer_text": f"This is a successful response from {self.model_name}! The prompt was: {prompt[:50]}...",
            "latency_ms": 800,
            "tokens": 150,
            "estimated_cost": 0.003,
            "input_tokens": 50,
            "output_tokens": 100
        }

def test_fallback_scenario():
    """Test different fallback scenarios"""
    
    print("🧪 Testing LLM Router Fallback Functionality")
    print("=" * 60)
    
    # Create router instance
    router = LLMRouter()
    
    # Test 1: Replace first model with failing mock
    print("\n📋 Test 1: Primary model fails, should fallback to secondary")
    print("-" * 50)
    
    # Temporarily replace the first ranked model with a failing one
    original_models = router.models.copy()
    
    # Get ranked models to see the order
    test_prompt = "What are the key considerations for customer segmentation?"
    ranked_models = router.get_ranked_models(test_prompt)
    print(f"Model ranking: {[model for model, score in ranked_models]}")
    
    # Replace the top model with a failing mock
    top_model = ranked_models[0][0]
    router.models[top_model] = MockFailingModel(top_model)
    
    print(f"\n🔧 Replaced {top_model} with failing mock")
    
    # Test the fallback
    response = router.generate_response(test_prompt)
    print(f"\n✅ Final response model: {response['model']}")
    print(f"📝 Response preview: {response['answer_text'][:100]}...")
    
    # Test 2: Replace top two models with failing mocks
    print("\n\n📋 Test 2: Top two models fail, should use third model")
    print("-" * 50)
    
    # Replace second model too
    second_model = ranked_models[1][0]
    router.models[second_model] = MockFailingModel(second_model)
    
    print(f"🔧 Also replaced {second_model} with failing mock")
    
    response = router.generate_response(test_prompt)
    print(f"\n✅ Final response model: {response['model']}")
    print(f"📝 Response preview: {response['answer_text'][:100]}...")
    
    # Test 3: All models fail
    print("\n\n📋 Test 3: All models fail, should return error")
    print("-" * 50)
    
    # Replace all models with failing mocks
    for model_name in router.models:
        router.models[model_name] = MockFailingModel(model_name)
    
    print("🔧 Replaced all models with failing mocks")
    
    response = router.generate_response(test_prompt)
    print(f"\n⚠️  Final response model: {response['model']}")
    print(f"❌ Error response: {response['answer_text'][:100]}...")
    
    # Test 4: Restore and test normal operation
    print("\n\n📋 Test 4: Normal operation (all models working)")
    print("-" * 50)
    
    # Restore original models
    router.models = original_models
    
    # Replace all with success mocks for predictable testing
    for model_name in router.models:
        router.models[model_name] = MockSuccessModel(model_name)
    
    response = router.generate_response(test_prompt)
    print(f"\n✅ Final response model: {response['model']}")
    print(f"📝 Response preview: {response['answer_text'][:100]}...")
    
    print("\n" + "=" * 60)
    print("🎉 Fallback testing completed!")

if __name__ == "__main__":
    test_fallback_scenario() 