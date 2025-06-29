
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RoutingResult } from '@/types/routing';

interface ModelDistributionChartProps {
  results: RoutingResult[];
}

export const ModelDistributionChart: React.FC<ModelDistributionChartProps> = ({ results }) => {
  // Calculate model distribution
  const modelCounts = results.reduce((acc, result) => {
    acc[result.chosen_model] = (acc[result.chosen_model] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const total = results.length;
  const modelStats = Object.entries(modelCounts).map(([model, count]) => ({
    model,
    count,
    percentage: (count / total) * 100
  }));

  const colors = {
    'GPT-4o': 'bg-blue-500',
    'Claude': 'bg-purple-500',
    'Mistral': 'bg-orange-500'
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-sm">Model Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {modelStats.map(({ model, count, percentage }) => (
            <div key={model} className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="font-medium">{model}</span>
                <span>{count} ({percentage.toFixed(1)}%)</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${colors[model as keyof typeof colors] || 'bg-gray-400'}`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
        
        {/* Summary stats */}
        <div className="mt-4 pt-3 border-t border-gray-200">
          <div className="text-xs text-gray-600">
            <div>Total prompts: {total}</div>
            <div>Most used: {modelStats.sort((a, b) => b.count - a.count)[0]?.model}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
