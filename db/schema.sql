-- Table for storing prompts and their reference answers
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY,
    prompt TEXT NOT NULL,
    reference TEXT NOT NULL
);

-- Table for storing execution runs and results
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT NOT NULL,
    prompt_id INTEGER NOT NULL,
    model TEXT NOT NULL,
    answer TEXT NOT NULL,
    latency_ms REAL NOT NULL,
    tokens INTEGER NOT NULL,
    estimated_cost REAL NOT NULL,
    critic_score INTEGER,
    critic_rationale TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompts (id)
);

-- Table for storing model performance averages
CREATE TABLE IF NOT EXISTS model_performance (
    model TEXT PRIMARY KEY,
    avg_score REAL DEFAULT 0.0,
    avg_latency_ms REAL DEFAULT 0.0,
    avg_cost REAL DEFAULT 0.0,
    total_runs INTEGER DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
); 