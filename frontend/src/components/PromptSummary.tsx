
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RoutingResult } from '@/types/routing';

interface PromptSummaryProps {
  results: RoutingResult[];
}

export const PromptSummary: React.FC<PromptSummaryProps> = ({ results }) => {
  // Calculate summary statistics
  const totalPrompts = results.length;
  
  // Model distribution
  const modelCounts = results.reduce((acc, result) => {
    acc[result.chosen_model] = (acc[result.chosen_model] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Average critic scores
  const avgCriticScore = results.reduce((sum, result) => sum + result.critic_output.score, 0) / totalPrompts;

  // Average metrics per model
  const modelMetrics = results.reduce((acc, result) => {
    result.model_scores.forEach(score => {
      if (!acc[score.model]) {
        acc[score.model] = { latency: [], cost: [], finalScore: [] };
      }
      acc[score.model].latency.push(score.latency);
      acc[score.model].cost.push(score.cost);
      acc[score.model].finalScore.push(score.final_score);
    });
    return acc;
  }, {} as Record<string, { latency: number[], cost: number[], finalScore: number[] }>);

  const avgModelStats = Object.entries(modelMetrics).map(([model, metrics]) => ({
    model,
    avgLatency: metrics.latency.reduce((a, b) => a + b, 0) / metrics.latency.length,
    avgCost: metrics.cost.reduce((a, b) => a + b, 0) / metrics.cost.length,
    avgFinalScore: metrics.finalScore.reduce((a, b) => a + b, 0) / metrics.finalScore.length,
    timesChosen: modelCounts[model] || 0
  }));

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg">All Prompts Summary</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Overall Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="text-2xl font-bold text-blue-700">{totalPrompts}</div>
              <div className="text-sm text-blue-600">Total Prompts</div>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <div className="text-2xl font-bold text-green-700">{avgCriticScore.toFixed(1)}</div>
              <div className="text-sm text-green-600">Avg Critic Score</div>
            </div>
          </div>

          {/* Model Performance Table */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-3">Model Performance Overview</h4>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 font-medium text-gray-700">Model</th>
                    <th className="text-right py-2 font-medium text-gray-700">Chosen</th>
                    <th className="text-right py-2 font-medium text-gray-700">Avg Latency</th>
                    <th className="text-right py-2 font-medium text-gray-700">Avg Cost</th>
                    <th className="text-right py-2 font-medium text-gray-700">Avg Score</th>
                  </tr>
                </thead>
                <tbody className="font-mono text-xs">
                  {avgModelStats.map((stat) => (
                    <tr key={stat.model} className="border-b border-gray-100">
                      <td className="py-2 font-medium">{stat.model}</td>
                      <td className="text-right py-2">{stat.timesChosen}x</td>
                      <td className="text-right py-2">{stat.avgLatency.toFixed(1)}s</td>
                      <td className="text-right py-2">${stat.avgCost.toFixed(3)}</td>
                      <td className="text-right py-2">{stat.avgFinalScore.toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Quick Insights */}
          <div className="bg-gray-50 p-3 rounded-lg">
            <h4 className="font-semibold text-gray-700 mb-2">Quick Insights</h4>
            <div className="text-sm text-gray-600 space-y-1">
              <div>• Most chosen: {Object.entries(modelCounts).sort(([,a], [,b]) => b - a)[0]?.[0]} ({Math.max(...Object.values(modelCounts))} times)</div>
              <div>• Best avg score: {avgModelStats.sort((a, b) => b.avgFinalScore - a.avgFinalScore)[0]?.model} ({avgModelStats.sort((a, b) => b.avgFinalScore - a.avgFinalScore)[0]?.avgFinalScore.toFixed(1)})</div>
              <div>• Fastest avg: {avgModelStats.sort((a, b) => a.avgLatency - b.avgLatency)[0]?.model} ({avgModelStats.sort((a, b) => a.avgLatency - b.avgLatency)[0]?.avgLatency.toFixed(1)}s)</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};