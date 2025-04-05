import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';

interface Model {
  id: string;
  name: string;
  type: string;
  created_at: string;
}

export default function ModelsPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const { data: models, isLoading } = useQuery<Model[]>({
    queryKey: ['models'],
    queryFn: async () => {
      const response = await axios.get('http://localhost:8000/api/v1/models');
      return response.data;
    },
  });

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('model', file);
      await axios.post('http://localhost:8000/api/v1/models/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files?.[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (selectedFile) {
      await uploadMutation.mutateAsync(selectedFile);
      setSelectedFile(null);
    }
  };

  if (isLoading) {
    return <div className="text-center">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium leading-6 text-gray-900">Upload Model</h3>
          <div className="mt-2 max-w-xl text-sm text-gray-500">
            <p>Upload a trained model file (supported formats: .h5, .pkl)</p>
          </div>
          <div className="mt-5">
            <div className="flex items-center space-x-4">
              <input
                type="file"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-indigo-50 file:text-indigo-700
                  hover:file:bg-indigo-100"
              />
              <button
                onClick={handleUpload}
                disabled={!selectedFile || uploadMutation.isPending}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium leading-6 text-gray-900">Available Models</h3>
          <div className="mt-4">
            <ul role="list" className="divide-y divide-gray-200">
              {models?.map((model) => (
                <li key={model.id} className="py-4">
                  <div className="flex items-center space-x-4">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{model.name}</p>
                      <p className="text-sm text-gray-500">{model.type}</p>
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(model.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
