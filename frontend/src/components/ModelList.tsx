import { useModels } from '../hooks/useModels';
import { useExplanations } from '../hooks/useExplanations';
import LoadingSpinner from './LoadingSpinner';
import { Model } from '../types';

// Pre-built models
const PREBUILT_MODELS: Model[] = [
  {
    id: 'iris',
    name: 'Iris Classifier',
    type: 'sklearn',
    description: 'A RandomForest classifier trained on the classic iris dataset.',
    features: ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
    created_at: '2025-04-04T00:00:00Z'
  }
];

export default function ModelList() {
  const { models, isLoading, error } = useModels();
  const { generateExplanation, isGenerating } = useExplanations();

  const handleExplain = async (modelId: string) => {
    // Sample input data for iris dataset
    const sampleInput = {
      sepal_length: 5.1,
      sepal_width: 3.5,
      petal_length: 1.4,
      petal_width: 0.2
    };

    await generateExplanation({
      model_id: modelId,
      type: 'feature_importance',
      input_data: sampleInput
    });
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-700 rounded-md">
        {error instanceof Error ? error.message : 'Failed to load models'}
      </div>
    );
  }

  const allModels = [...PREBUILT_MODELS, ...(models || [])];

  if (!allModels.length) {
    return (
      <div className="text-center text-gray-500 py-8">
        No models available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {allModels.map((model) => (
        <div
          key={model.id}
          className="border rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-medium text-gray-900">{model.name}</h3>
              <p className="text-sm text-gray-500">{model.type}</p>
              {model.description && (
                <p className="text-sm text-gray-600 mt-1">{model.description}</p>
              )}
              <p className="text-xs text-gray-400 mt-2">
                Added {new Date(model.created_at).toLocaleDateString()}
              </p>
            </div>
            <button
              onClick={() => handleExplain(model.id)}
              disabled={isGenerating}
              className="px-3 py-1 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {isGenerating ? 'Generating...' : 'Explain'}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
