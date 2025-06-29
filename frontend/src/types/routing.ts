
export interface Prompt {
    id: number;
    text: string;
    reference_answer: string;
  }
  
  export interface ModelScore {
    model: string;
    latency: number;
    cost: number;
    avg_score: number;
    final_score: number;
    answer: string;
  }
  
  export interface CriticOutput {
    score: number;
    rationale: string;
  }
  
  export interface RoutingResult {
    prompt_id: number;
    chosen_model: string;
    model_scores: ModelScore[];
    critic_output: CriticOutput;
  }
  
  export interface RoutingData {
    prompts: Prompt[];
    results: RoutingResult[];
  }