import { useExplanations } from '../hooks/useExplanations';
import LoadingSpinner from './LoadingSpinner';

export default function ExplanationView() {
  const { explanations, isLoading, error } = useExplanations();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-700 rounded-md">
        {error instanceof Error ? error.message : 'Failed to load explanations'}
      </div>
    );
  }

  if (!explanations.length) {
    return (
      <div className="text-center text-gray-500 py-8">
        No explanations generated yet
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {explanations.map((explanation) => (
        <div key={explanation.id} className="border rounded-lg p-6">
          <h3 className="font-medium text-lg mb-4">
            {explanation.type === 'feature_importance' 
              ? 'Feature Importance Analysis'
              : 'Instance Explanation'
            }
          </h3>
          
          {explanation.type === 'feature_importance' && (
            <div className="space-y-3">
              {Object.entries(explanation.result.feature_importance)
                .sort(([, a], [, b]) => (b as number) - (a as number))
                .map(([feature, importance]) => (
                  <div key={feature} className="relative pt-1">
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">
                        {feature}
                      </span>
                      <span className="text-sm text-gray-600">
                        {(Number(importance) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="overflow-hidden h-2 bg-gray-200 rounded">
                      <div
                        className="bg-indigo-600 h-2 rounded"
                        style={{ width: `${Number(importance) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
            </div>
          )}

          <div className="mt-4 text-xs text-gray-500">
            Generated on {new Date(explanation.created_at).toLocaleString()}
          </div>
        </div>
      ))}
    </div>
  );
}
