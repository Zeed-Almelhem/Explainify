import { useRef, useState } from 'react';
import { useModels } from '../hooks/useModels';
import LoadingSpinner from './LoadingSpinner';

export default function ModelUpload() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const { uploadModel, isUploading, uploadError } = useModels();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      await handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.pkl') && !file.name.endsWith('.h5')) {
      alert('Please upload a .pkl or .h5 file');
      return;
    }
    await uploadModel(file);
  };

  return (
    <div className="w-full max-w-xl mx-auto p-4">
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center ${
          dragActive
            ? 'border-indigo-600 bg-indigo-50'
            : 'border-gray-300 hover:border-indigo-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pkl,.h5"
          onChange={handleChange}
        />

        {isUploading ? (
          <div className="py-4">
            <LoadingSpinner />
            <p className="mt-2 text-sm text-gray-600">Uploading model...</p>
          </div>
        ) : (
          <>
            <div className="text-sm text-gray-600">
              <p className="font-medium">Drop your model file here or</p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-indigo-600 hover:text-indigo-800 font-medium"
              >
                click to upload
              </button>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              Supported formats: .pkl, .h5
            </p>
          </>
        )}
      </div>

      {uploadError && (
        <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
          {uploadError instanceof Error ? uploadError.message : 'Upload failed'}
        </div>
      )}
    </div>
  );
}
