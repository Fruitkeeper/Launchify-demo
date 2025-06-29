import { RoutingData } from "@/types/routing";

// API configuration
const API_BASE_URL = 'http://localhost:8000/api';

// API service functions
export const apiService = {
  async getPrompts() {
    const response = await fetch(`${API_BASE_URL}/prompts`);
    if (!response.ok) throw new Error('Failed to fetch prompts');
    return response.json();
  },

  async getResults() {
    const response = await fetch(`${API_BASE_URL}/results`);
    if (!response.ok) throw new Error('Failed to fetch results');
    return response.json();
  },

  async routePrompt(promptId: number, model?: string) {
    const url = `${API_BASE_URL}/route-prompt/${promptId}${model ? `?model=${model}` : ''}`;
    const response = await fetch(url, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to route prompt');
    return response.json();
  },

  async updateWeights() {
    const response = await fetch(`${API_BASE_URL}/update-weights`, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to update weights');
    return response.json();
  }
};

// Keep mock data as fallback for development
export const mockRoutingData = {
  prompts: [
    {
      id: 1,
      text: "What are the key elements of a successful go-to-market strategy for B2B SaaS products?",
      reference_answer: "A successful B2B SaaS go-to-market strategy includes: 1) Clear value proposition and positioning 2) Deep understanding of target customer segments 3) Product-market fit validation 4) Scalable customer acquisition channels 5) Strong onboarding and success processes 6) Pricing strategy aligned with value delivery 7) Sales and marketing alignment 8) Customer feedback loops for continuous improvement"
    },
    {
      id: 2,
      text: "How do you identify and prioritize the right customer segments for a new product launch?",
      reference_answer: "To identify and prioritize customer segments: 1) Conduct market research and customer interviews 2) Analyze market size and growth potential 3) Assess competitive landscape 4) Evaluate segment accessibility and reachability 5) Consider alignment with company strengths 6) Analyze willingness to pay and budget availability 7) Test messaging resonance 8) Prioritize based on revenue potential, strategic fit, and execution feasibility"
    }
  ],
  results: [
    {
      prompt_id: 1,
      chosen_model: "claude",
      model_scores: [
        {
          model: "gpt-4o",
          latency: 1.2,
          cost: 0.005,
          avg_score: 8.1,
          final_score: 7.8,
          answer: "A successful B2B SaaS go-to-market strategy requires several critical components working in harmony. First, you need a clear value proposition that differentiates your product in the market. This should be supported by deep customer research to understand your target segments' pain points and buying behaviors. Product-market fit is essential before scaling, followed by identifying the most effective customer acquisition channels for your specific market."
        },
        {
          model: "claude",
          latency: 0.8,
          cost: 0.003,
          avg_score: 8.5,
          final_score: 8.2,
          answer: "An effective B2B SaaS go-to-market strategy encompasses eight key elements: 1) Value proposition clarity - articulating unique benefits and competitive differentiation 2) Target market definition - identifying ideal customer profiles and buyer personas 3) Product-market fit validation through customer feedback and usage metrics 4) Multi-channel acquisition strategy including content marketing, partnerships, and direct sales 5) Comprehensive onboarding and customer success programs 6) Value-based pricing aligned with customer ROI 7) Sales and marketing orchestration with shared metrics and goals 8) Continuous optimization through data analysis and customer feedback loops."
        },
        {
          model: "mistral",
          latency: 0.6,
          cost: 0.002,
          avg_score: 7.1,
          final_score: 6.9,
          answer: "Key elements of B2B SaaS go-to-market strategy include understanding your target market, creating compelling messaging, establishing sales processes, and building customer success programs. You need to identify the right channels for reaching customers and ensure your pricing model aligns with market expectations."
        }
      ],
      critic_output: {
        score: 8.5,
        rationale: "The Claude response provides the most comprehensive and structured answer, covering all essential elements of a B2B SaaS go-to-market strategy with clear enumeration and practical details."
      }
    },
    {
      prompt_id: 2,
      chosen_model: "gpt-4o",
      model_scores: [
        {
          model: "gpt-4o",
          latency: 1.1,
          cost: 0.0048,
          avg_score: 8.3,
          final_score: 8.1,
          answer: "Customer segment identification and prioritization requires a systematic approach combining quantitative analysis with qualitative insights. Start with comprehensive market research including surveys, interviews, and competitive analysis. Evaluate each segment across multiple dimensions: market size and growth trajectory, competitive intensity, accessibility through your current channels, alignment with your product capabilities, and willingness to pay. Use frameworks like TAM/SAM/SOM analysis and create detailed buyer personas. Prioritize segments that offer the best combination of revenue opportunity, strategic fit, and execution feasibility."
        },
        {
          model: "claude",
          latency: 0.9,
          cost: 0.0031,
          avg_score: 7.9,
          final_score: 7.7,
          answer: "To identify and prioritize customer segments effectively: Begin with broad market research and customer discovery interviews to understand different user types and their needs. Analyze market characteristics including size, growth rate, and competitive dynamics. Evaluate your ability to reach and serve each segment given your current resources and capabilities. Test messaging and value propositions with different segments to measure resonance. Prioritize based on factors like revenue potential, strategic importance, competitive advantage, and speed to market."
        },
        {
          model: "mistral",
          latency: 0.7,
          cost: 0.0019,
          avg_score: 6.8,
          final_score: 6.5,
          answer: "Customer segment prioritization involves market research, competitive analysis, and understanding customer needs. Focus on segments with high growth potential and where you can deliver unique value. Consider factors like market size, competition level, and your ability to reach customers effectively."
        }
      ],
      critic_output: {
        score: 8.3,
        rationale: "The GPT-4o response provides excellent structure and mentions specific frameworks like TAM/SAM/SOM analysis, offering both strategic and tactical guidance for customer segmentation."
      }
    }
  ]
};
