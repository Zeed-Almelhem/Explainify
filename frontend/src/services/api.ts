import axios from 'axios';
import { Model } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Explanation {
  id: string;
  model_id: string;
  type: 'feature_importance' | 'instance_explanation';
  result: any;
  created_at: string;
}

export const modelService = {
  getModels: async (): Promise<Model[]> => {
    const response = await api.get('/models');
    return response.data;
  },

  uploadModel: async (file: File): Promise<Model> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/models/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const explanationService = {
  getExplanations: async (modelId?: string): Promise<Explanation[]> => {
    const url = modelId ? `/explanations?model_id=${modelId}` : '/explanations';
    const response = await api.get(url);
    return response.data;
  },

  generateExplanation: async (params: {
    model_id: string;
    type: string;
    input_data: Record<string, number>;
  }): Promise<Explanation> => {
    const response = await api.post('/explanations', params);
    return response.data;
  },
};
