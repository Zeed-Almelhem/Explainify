import { useState } from 'react';
import { useModels } from '../hooks/useModels';
import { useExplanations } from '../hooks/useExplanations';
import LoadingSpinner from './LoadingSpinner';
import { Model } from '../types';
import DataInputForm from './DataInputForm';
import ExplanationVisualizer from './ExplanationVisualizer';

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
  const { generateExplanation, isGenerating, explanations } = useExplanations();
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [activeTab, setActiveTab] = useState<'features' | 'predictions' | 'stats'>('features');

  const handleExplain = async (model: Model) => {
    setSelectedModel(model);
    setShowForm(true);
  };

  const handleSubmitData = async (inputData: Record<string, number>) => {
    if (!selectedModel) return;
    
    await generateExplanation({
      model_id: selectedModel.id,
      type: 'feature_importance',
      input_data: inputData
    });
    
    setShowForm(false);
  };

  const getModelStats = (model: Model) => {
    const modelExplanations = explanations?.filter(e => e.model_id === model.id) || [];
    return {
      explanationsCount: modelExplanations.length,
      lastUsed: modelExplanations.length > 0 
        ? new Date(modelExplanations[modelExplanations.length - 1].created_at).toLocaleDateString()
        : 'Never'
    };
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
    <div className="space-y-6">
      {showForm && selectedModel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium mb-4">Enter Input Data</h3>
            <DataInputForm 
              features={selectedModel.features || []} 
              onSubmit={handleSubmitData}
              onCancel={() => setShowForm(false)}
            />
          </div>
        </div>
      )}

      {allModels.map((model) => (
        <div
          key={model.id}
          className="border rounded-lg p-6 hover:shadow-md transition-shadow bg-white"
        >
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="font-medium text-xl text-gray-900">{model.name}</h3>
              <p className="text-sm text-gray-500">{model.type}</p>
              {model.description && (
                <p className="text-sm text-gray-600 mt-1">{model.description}</p>
              )}
            </div>
            <button
              onClick={() => handleExplain(model)}
              disabled={isGenerating}
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {isGenerating ? 'Generating...' : 'Explain'}
            </button>
          </div>

          <div className="border-t pt-4">
            <div className="flex space-x-4 mb-4">
              <button
                onClick={() => setActiveTab('features')}
                className={`px-3 py-1 rounded-md ${
                  activeTab === 'features' ? 'bg-gray-100 text-gray-900' : 'text-gray-500'
                }`}
              >
                Features
              </button>
              <button
                onClick={() => setActiveTab('predictions')}
                className={`px-3 py-1 rounded-md ${
                  activeTab === 'predictions' ? 'bg-gray-100 text-gray-900' : 'text-gray-500'
                }`}
              >
                Predictions
              </button>
              <button
                onClick={() => setActiveTab('stats')}
                className={`px-3 py-1 rounded-md ${
                  activeTab === 'stats' ? 'bg-gray-100 text-gray-900' : 'text-gray-500'
                }`}
              >
                Stats
              </button>
            </div>

            <div className="mt-4">
              {activeTab === 'features' && (
                <div className="grid grid-cols-2 gap-4">
                  {model.features?.map(feature => (
                    <div key={feature} className="bg-gray-50 p-2 rounded">
                      {feature}
                    </div>
                  ))}
                </div>
              )}
              
              {activeTab === 'predictions' && (
                <div className="space-y-4">
                  {explanations
                    ?.filter(e => e.model_id === model.id)
                    .slice(-3)
                    .map(explanation => (
                      <ExplanationVisualizer key={explanation.id} explanation={explanation} />
                    ))}
                </div>
              )}
              
              {activeTab === 'stats' && (
                <div className="space-y-2">
                  <p>Total Explanations: {getModelStats(model).explanationsCount}</p>
                  <p>Last Used: {getModelStats(model).lastUsed}</p>
                  <p>Created: {new Date(model.created_at).toLocaleDateString()}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
