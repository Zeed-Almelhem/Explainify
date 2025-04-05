import { useState } from 'react';

interface DataInputFormProps {
  features: string[];
  onSubmit: (data: Record<string, number>) => void;
  onCancel: () => void;
}

export default function DataInputForm({ features, onSubmit, onCancel }: DataInputFormProps) {
  const [formData, setFormData] = useState<Record<string, number>>(() => {
    // Initialize form data with default values
    return features.reduce((acc, feature) => ({
      ...acc,
      [feature]: 0
    }), {});
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleInputChange = (feature: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [feature]: parseFloat(value) || 0
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {features.map(feature => (
        <div key={feature}>
          <label htmlFor={feature} className="block text-sm font-medium text-gray-700">
            {feature}
          </label>
          <input
            type="number"
            id={feature}
            name={feature}
            value={formData[feature]}
            onChange={(e) => handleInputChange(feature, e.target.value)}
            step="0.1"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
      ))}
      
      <div className="flex justify-end space-x-3 mt-6">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Generate Explanation
        </button>
      </div>
    </form>
  );
}
