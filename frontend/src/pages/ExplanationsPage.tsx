import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';

interface Explanation {
  id: string;
  model_id: string;
  type: 'feature_importance' | 'instance_explanation';
  result: any;
  created_at: string;
}

interface Model {
  id: string;
  name: string;
}

export default function ExplanationsPage() {
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [explanationType, setExplanationType] = useState<'feature_importance' | 'instance_explanation'>('feature_importance');
  const [inputData, setInputData] = useState<string>('');

  const { data: models } = useQuery<Model[]>({
    queryKey: ['models'],
    queryFn: async () => {
      const response = await axios.get('http://localhost:8000/api/v1/models');
      return response.data;
    },
  });

  const { data: explanations, isLoading: isLoadingExplanations } = useQuery<Explanation[]>({
    queryKey: ['explanations', selectedModel],
    queryFn: async () => {
      const response = await axios.get(`http://localhost:8000/api/v1/explanations?model_id=${selectedModel}`);
      return response.data;
    },
    enabled: !!selectedModel,
  });

  const generateExplanation = useMutation({
    mutationFn: async () => {
      const payload = {
        model_id: selectedModel,
        type: explanationType,
        input_data: JSON.parse(inputData),
      };
      const response = await axios.post('http://localhost:8000/api/v1/explanations/generate', payload);
      return response.data;
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await generateExplanation.mutateAsync();
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium leading-6 text-gray-900">Generate Explanation</h3>
          <form onSubmit={handleSubmit} className="mt-5 space-y-4">
            <div>
              <label htmlFor="model" className="block text-sm font-medium text-gray-700">
                Select Model
              </label>
              <select
                id="model"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="">Select a model</option>
                {models?.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="type" className="block text-sm font-medium text-gray-700">
                Explanation Type
              </label>
              <select
                id="type"
                value={explanationType}
                onChange={(e) => setExplanationType(e.target.value as 'feature_importance' | 'instance_explanation')}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="feature_importance">Feature Importance</option>
                <option value="instance_explanation">Instance Explanation</option>
              </select>
            </div>

            <div>
              <label htmlFor="input-data" className="block text-sm font-medium text-gray-700">
                Input Data (JSON format)
              </label>
              <textarea
                id="input-data"
                rows={4}
                value={inputData}
                onChange={(e) => setInputData(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder='{"feature1": 1.0, "feature2": 2.0}'
              />
            </div>

            <div>
              <button
                type="submit"
                disabled={!selectedModel || !inputData || generateExplanation.isPending}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {generateExplanation.isPending ? 'Generating...' : 'Generate Explanation'}
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium leading-6 text-gray-900">Explanation Results</h3>
          <div className="mt-4">
            {isLoadingExplanations ? (
              <div>Loading...</div>
            ) : (
              <ul role="list" className="divide-y divide-gray-200">
                {explanations?.map((explanation) => (
                  <li key={explanation.id} className="py-4">
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-900">
                        Type: {explanation.type}
                      </p>
                      <p className="text-sm text-gray-500">
                        Created: {new Date(explanation.created_at).toLocaleDateString()}
                      </p>
                      <pre className="mt-2 text-sm text-gray-700 bg-gray-50 p-4 rounded-md overflow-auto">
                        {JSON.stringify(explanation.result, null, 2)}
                      </pre>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
