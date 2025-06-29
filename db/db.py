import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "data.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database with schema"""
        with sqlite3.connect(self.db_path) as conn:
            # Read and execute schema
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r') as f:
                schema = f.read()
            conn.executescript(schema)
            
            # Load prompts if they don't exist
            self.load_prompts()
    
    def load_prompts(self):
        """Load prompts from JSON file into database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if prompts already loaded
            cursor.execute("SELECT COUNT(*) FROM prompts")
            if cursor.fetchone()[0] > 0:
                return
                
            # Load prompts from JSON
            prompts_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'prompts.json')
            with open(prompts_path, 'r') as f:
                prompts_data = json.load(f)
            
            # Insert prompts
            for prompt_data in prompts_data:
                cursor.execute(
                    "INSERT INTO prompts (id, prompt, reference) VALUES (?, ?, ?)",
                    (prompt_data['id'], prompt_data['prompt'], prompt_data['reference'])
                )
            conn.commit()
    
    def get_prompts(self) -> List[Dict]:
        """Get all prompts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, prompt, reference FROM prompts ORDER BY id")
            rows = cursor.fetchall()
            return [{"id": row[0], "prompt": row[1], "reference": row[2]} for row in rows]
    
    def store_run_result(self, run_id: str, prompt_id: int, model: str, 
                        answer: str, latency_ms: float, tokens: int, 
                        estimated_cost: float, critic_score: Optional[int] = None, 
                        critic_rationale: Optional[str] = None):
        """Store the result of a model run"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO runs (run_id, prompt_id, model, answer, latency_ms, 
                                tokens, estimated_cost, critic_score, critic_rationale)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (run_id, prompt_id, model, answer, latency_ms, tokens, 
                  estimated_cost, critic_score, critic_rationale))
            conn.commit()
    
    def get_model_performance(self, model: str) -> Dict:
        """Get historical performance metrics for a model"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AVG(critic_score) as avg_score, 
                       AVG(latency_ms) as avg_latency,
                       AVG(estimated_cost) as avg_cost,
                       COUNT(*) as total_runs
                FROM runs 
                WHERE model = ? AND critic_score IS NOT NULL
            """, (model,))
            
            row = cursor.fetchone()
            if row and row[0] is not None:
                return {
                    "avg_score": row[0],
                    "avg_latency": row[1], 
                    "avg_cost": row[2],
                    "total_runs": row[3]
                }
            else:
                return {
                    "avg_score": 5.0,  # Default neutral score
                    "avg_latency": 1000.0,  # Default high latency
                    "avg_cost": 0.01,  # Default moderate cost
                    "total_runs": 0
                }
    
    def get_all_runs(self, run_id: Optional[str] = None) -> List[Dict]:
        """Get all runs, optionally filtered by run_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if run_id:
                cursor.execute("""
                    SELECT r.*, p.prompt FROM runs r 
                    JOIN prompts p ON r.prompt_id = p.id 
                    WHERE r.run_id = ? 
                    ORDER BY r.prompt_id
                """, (run_id,))
            else:
                cursor.execute("""
                    SELECT r.*, p.prompt FROM runs r 
                    JOIN prompts p ON r.prompt_id = p.id 
                    ORDER BY r.timestamp DESC, r.prompt_id
                """)
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def update_model_performance(self):
        """Update the model performance averages"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get unique models
            cursor.execute("SELECT DISTINCT model FROM runs")
            models = [row[0] for row in cursor.fetchall()]
            
            for model in models:
                perf = self.get_model_performance(model)
                cursor.execute("""
                    INSERT OR REPLACE INTO model_performance 
                    (model, avg_score, avg_latency_ms, avg_cost, total_runs, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (model, perf['avg_score'], perf['avg_latency'], 
                      perf['avg_cost'], perf['total_runs'], datetime.now()))
            
            conn.commit() 