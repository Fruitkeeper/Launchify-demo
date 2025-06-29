import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Loader2, Clock, DollarSign, BarChart3, Play, Square, Terminal, RefreshCw } from 'lucide-react';
import { apiService, mockRoutingData } from '@/data/mockData';
import { RoutingResult, Prompt } from '@/types/routing';
import { ModelDistributionChart } from './ModelDistributionChart';
import { PromptSummary } from './PromptSummary';

interface RunSummary {
  run_id: string;
  timestamp: string;
  prompts_count: number;
  models_used: string[];
  avg_score: number | null;
  total_cost: number;
}

interface SystemProcess {
  run_id: string;
  command: string;
  status: 'running' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  return_code?: number;
}

const RoutingDashboard = () => {
  const [selectedPromptId, setSelectedPromptId] = useState<number>(1);
  const [isRouting, setIsRouting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [results, setResults] = useState<RoutingResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [runHistory, setRunHistory] = useState<RunSummary[]>([]);
  const [selectedView, setSelectedView] = useState<'dashboard' | 'history' | 'control'>('dashboard');
  const [systemProcesses, setSystemProcesses] = useState<SystemProcess[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentOutput, setCurrentOutput] = useState<string[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);

  // Load data from API on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Try to fetch from API
      const [data, runsData] = await Promise.all([
        apiService.getResults(),
        fetch('http://localhost:8000/api/runs').then(r => r.json())
      ]);
      
      setPrompts(data.prompts.map((p: any) => ({
        id: p.id,
        text: p.text,
        reference_answer: p.reference_answer
      })));
      setResults(data.results);
      setRunHistory(runsData.runs);
      
      // Set the first prompt as selected if available
      if (data.prompts.length > 0 && selectedPromptId === 1) {
        setSelectedPromptId(data.prompts[0].id);
      }
    } catch (err) {
      console.warn('Failed to fetch from API, using mock data:', err);
      setError('Using demo data - API not available');
      // Fallback to mock data
      setPrompts(mockRoutingData.prompts);
      setResults(mockRoutingData.results);
      setSelectedPromptId(mockRoutingData.prompts[0]?.id || 1);
    } finally {
      setIsLoading(false);
    }
  };

  const runSystemCommand = async (command: string) => {
    try {
      setIsRunning(true);
      setCurrentOutput([]);
      
      // Start the system run
      const response = await fetch('http://localhost:8000/api/run-system', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
      });
      
      if (!response.ok) throw new Error('Failed to start run');
      
      const result = await response.json();
      setActiveRunId(result.run_id);
      
      // Start streaming the output
      streamOutput(result.run_id);
      
    } catch (err) {
      console.error('Failed to run system command:', err);
      setError(`Failed to run ${command}: ${err}`);
      setIsRunning(false);
    }
  };

  const streamOutput = (runId: string) => {
    const eventSource = new EventSource(`http://localhost:8000/api/run-output/${runId}`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'output') {
        setCurrentOutput(prev => [...prev, data.data]);
      } else if (data.type === 'status') {
        setIsRunning(false);
        setCurrentOutput(prev => [...prev, `\n✅ Process ${data.status} with code: ${data.return_code}`]);
        eventSource.close();
        
        // Refresh data after completion
        if (data.status === 'completed') {
          setCurrentOutput(prev => [...prev, '🔄 Refreshing dashboard data...']);
          setTimeout(async () => {
            await loadData();
            setCurrentOutput(prev => [...prev, '✅ Dashboard data refreshed!']);
          }, 1000);
        }
      } else if (data.type === 'error') {
        setCurrentOutput(prev => [...prev, `❌ Error: ${data.message}`]);
        setIsRunning(false);
        eventSource.close();
      }
    };
    
    eventSource.onerror = () => {
      setIsRunning(false);
      setCurrentOutput(prev => [...prev, '❌ Connection lost']);
      eventSource.close();
    };
  };

  const getCurrentPrompt = (): Prompt | undefined => {
    return prompts.find(p => p.id === selectedPromptId);
  };

  const getCurrentResult = (): RoutingResult | undefined => {
    return results.find(r => r.prompt_id === selectedPromptId);
  };

  const handleRouteAgain = async () => {
    setIsRouting(true);
    try {
      // Call the API to route the prompt again
      const response = await apiService.routePrompt(selectedPromptId);
      console.log('Re-routing result:', response);
      
      // Update the results with the new data
      // For now, we'll just simulate an update
      setTimeout(() => {
        console.log(`Re-routing completed for prompt ${selectedPromptId}`);
      }, 1000);
    } catch (err) {
      console.error('Failed to re-route prompt:', err);
    } finally {
      setTimeout(() => {
        setIsRouting(false);
      }, 1500);
    }
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
          <div className="text-lg font-semibold text-gray-800">Loading LLM Routing Dashboard...</div>
          <div className="text-gray-500">Fetching prompts and routing results</div>
        </div>
      </div>
    );
  }

  const currentPrompt = getCurrentPrompt();
  const currentResult = getCurrentResult();

  if (!currentPrompt || !currentResult) {
    return (
      <div className="p-6">
        <div className="text-center text-gray-500">
          No data available for selected prompt
          {error && (
            <div className="mt-2 text-orange-600 text-sm">
              {error}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Error notification */}
      {error && (
        <div className="bg-orange-100 border-l-4 border-orange-500 text-orange-700 p-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm">{error}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 p-6 overflow-y-auto">
        <h2 className="text-lg font-semibold mb-6 text-gray-800">LLM Routing Dashboard</h2>
        
        {/* View Toggle */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              className={`flex-1 py-2 px-2 rounded-md text-xs font-medium transition-colors ${
                selectedView === 'dashboard'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              onClick={() => setSelectedView('dashboard')}
            >
              Dashboard
            </button>
            <button
              className={`flex-1 py-2 px-2 rounded-md text-xs font-medium transition-colors ${
                selectedView === 'control'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              onClick={() => setSelectedView('control')}
            >
              System Control
            </button>
            <button
              className={`flex-1 py-2 px-2 rounded-md text-xs font-medium transition-colors ${
                selectedView === 'history'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              onClick={() => setSelectedView('history')}
            >
              History
            </button>
          </div>
          
          {/* Refresh Button */}
          <Button 
            onClick={loadData}
            disabled={isLoading}
            variant="outline"
            size="sm"
            className="w-full mt-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-3 h-3 mr-2 animate-spin" />
                Refreshing...
              </>
            ) : (
              <>
                <RefreshCw className="w-3 h-3 mr-2" />
                Refresh Data
              </>
            )}
          </Button>
        </div>

        {selectedView === 'dashboard' && (
          <>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Prompt ID
                </label>
                <Select
                  value={selectedPromptId.toString()}
                  onValueChange={(value) => setSelectedPromptId(parseInt(value))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {prompts.map((prompt) => (
                      <SelectItem key={prompt.id} value={prompt.id.toString()}>
                        Prompt {prompt.id}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button 
                onClick={handleRouteAgain}
                disabled={isRouting}
                className="w-full"
              >
                {isRouting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Routing...
                  </>
                ) : (
                  'Route this prompt again'
                )}
              </Button>
            </div>

            {/* Summary Section */}
            <div className="mt-8">
              <PromptSummary results={results} />
            </div>

            {/* Model Distribution Chart */}
            <div className="mt-6">
              <ModelDistributionChart results={results} />
            </div>
          </>
        )}

        {selectedView === 'control' && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">System Commands</h3>
            
            <div className="space-y-2">
              <Button 
                onClick={() => runSystemCommand('run')}
                disabled={isRunning}
                className="w-full text-sm"
                variant="default"
              >
                {isRunning ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                Full Run (All Prompts)
              </Button>
              
              <Button 
                onClick={() => runSystemCommand('rerun')}
                disabled={isRunning}
                className="w-full text-sm"
                variant="secondary"
              >
                {isRunning ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                Rerun (with Learning)
              </Button>
              
              <Button 
                onClick={() => runSystemCommand('test')}
                disabled={isRunning}
                className="w-full text-sm"
                variant="outline"
              >
                {isRunning ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                Quick Test (3 Prompts)
              </Button>
            </div>
            
            <div className="border-t pt-4 mt-4">
              <h4 className="text-xs font-semibold text-gray-600 mb-2">Force Model:</h4>
              <div className="space-y-1">
                <Button 
                  onClick={() => runSystemCommand('run-gpt')}
                  disabled={isRunning}
                  className="w-full text-xs"
                  variant="outline"
                  size="sm"
                >
                  GPT-4o Only
                </Button>
                <Button 
                  onClick={() => runSystemCommand('run-claude')}
                  disabled={isRunning}
                  className="w-full text-xs"
                  variant="outline"
                  size="sm"
                >
                  Claude Only
                </Button>
                <Button 
                  onClick={() => runSystemCommand('run-mistral')}
                  disabled={isRunning}
                  className="w-full text-xs"
                  variant="outline"
                  size="sm"
                >
                  Mistral Only
                </Button>
              </div>
            </div>
          </div>
        )}

        {selectedView === 'history' && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Recent Runs ({runHistory.length})</h3>
            {runHistory.map((run) => (
              <div key={run.run_id} className="bg-gray-50 rounded-lg p-3 border">
                <div className="text-xs font-mono text-gray-600 mb-1">
                  {run.run_id}
                </div>
                <div className="text-sm text-gray-800 mb-2">
                  {formatDate(run.timestamp)}
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-600">
                  <div className="flex items-center gap-1">
                    <BarChart3 className="w-3 h-3" />
                    {run.prompts_count} prompts
                  </div>
                  <div className="flex items-center gap-1">
                    <DollarSign className="w-3 h-3" />
                    ${run.total_cost.toFixed(4)}
                  </div>
                  {run.avg_score && (
                    <div className="flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      {run.avg_score}/10
                    </div>
                  )}
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {run.models_used.map((model) => (
                    <Badge key={model} variant="secondary" className="text-xs">
                      {model}
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="ml-64 p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          {selectedView === 'control' && (
            <Card>
              <CardHeader>
                <CardTitle className="text-xl flex items-center gap-2">
                  <Terminal className="w-5 h-5" />
                  Live System Output
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-black text-green-400 p-4 rounded font-mono text-sm h-96 overflow-y-auto">
                  {currentOutput.length === 0 ? (
                    <div className="text-gray-500">
                      {isRunning ? "Starting system run..." : "Click a command above to see live output here"}
                    </div>
                  ) : (
                    currentOutput.map((line, idx) => (
                      <div key={idx}>{line}</div>
                    ))
                  )}
                  {isRunning && (
                    <div className="flex items-center gap-2 mt-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Running...</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {selectedView === 'dashboard' && (
            <>
              {/* Prompt Display */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Prompt #{selectedPromptId}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-gray-700 mb-2">Prompt Text:</h4>
                      <p className="text-gray-600 bg-gray-50 p-3 rounded font-mono text-sm">
                        {currentPrompt.text}
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-700 mb-2">Reference Answer:</h4>
                      <p className="text-gray-600 bg-blue-50 p-3 rounded font-mono text-sm">
                        {currentPrompt.reference_answer}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Scoring Table */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Model Scoring Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                      <thead>
                        <tr className="border-b-2 border-gray-200">
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Model</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Latency</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Cost</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Avg Score</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Final Score</th>
                        </tr>
                      </thead>
                      <tbody className="font-mono">
                        {currentResult.model_scores.map((score) => (
                          <tr 
                            key={score.model}
                            className={`border-b border-gray-100 ${
                              score.model === currentResult.chosen_model ? 'bg-green-50' : ''
                            }`}
                          >
                            <td className="py-3 px-4 flex items-center gap-2">
                              {score.model}
                              {score.model === currentResult.chosen_model && (
                                <CheckCircle className="w-4 h-4 text-green-600" />
                              )}
                            </td>
                            <td className="text-right py-3 px-4">{score.latency}s</td>
                            <td className="text-right py-3 px-4">${score.cost.toFixed(3)}</td>
                            <td className="text-right py-3 px-4">{score.avg_score.toFixed(1)}</td>
                            <td className="text-right py-3 px-4 font-semibold">{score.final_score.toFixed(1)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  
                  <div className="mt-4 p-3 bg-green-50 rounded border-l-4 border-green-400">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="font-semibold">Chosen Model: {currentResult.chosen_model}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Model Answers */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Model Responses</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {currentResult.model_scores.map((score) => (
                      <div key={score.model} className="border rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant={score.model === currentResult.chosen_model ? "default" : "secondary"}>
                            {score.model}
                          </Badge>
                          {score.model === currentResult.chosen_model && (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          )}
                        </div>
                        <p className="text-gray-700 font-mono text-sm bg-gray-50 p-3 rounded">
                          {score.answer}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Critic Output */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Critic Evaluation</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold text-yellow-800">
                        Score: {currentResult.critic_output.score}/10
                      </span>
                    </div>
                    <p className="text-yellow-800 font-mono text-sm">
                      <strong>Rationale:</strong> {currentResult.critic_output.rationale}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </>
          )}

          {selectedView === 'history' && (
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Run History & Terminal Output</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {runHistory.map((run) => (
                    <div key={run.run_id} className="border rounded-lg p-6 bg-gray-50">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-800">
                            Run: {run.run_id}
                          </h3>
                          <p className="text-sm text-gray-600">{formatDate(run.timestamp)}</p>
                        </div>
                        <div className="flex gap-4 text-sm">
                          <div className="flex items-center gap-1">
                            <BarChart3 className="w-4 h-4" />
                            <span>{run.prompts_count} prompts</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <DollarSign className="w-4 h-4" />
                            <span>${run.total_cost.toFixed(4)}</span>
                          </div>
                          {run.avg_score && (
                            <div className="flex items-center gap-1">
                              <CheckCircle className="w-4 h-4" />
                              <span>{run.avg_score}/10 avg</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <span className="text-sm font-medium text-gray-700">Models used: </span>
                        {run.models_used.map((model) => (
                          <Badge key={model} variant="outline" className="ml-1">
                            {model}
                          </Badge>
                        ))}
                      </div>

                      <div className="bg-black text-green-400 p-4 rounded font-mono text-sm">
                        <div>🚀 Run ID: {run.run_id}</div>
                        <div>📊 Processing {run.prompts_count} prompts...</div>
                        <div>💰 Total cost: ${run.total_cost.toFixed(4)}</div>
                        {run.avg_score && <div>📈 Average critic score: {run.avg_score}/10</div>}
                        <div>✅ Run completed successfully</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default RoutingDashboard;