export interface Model {
  id: string;
  name: string;
  type: string;
  created_at: string;
  description?: string;
  features?: string[];
}

export interface Explanation {
  id: string;
  model_id: string;
  type: string;
  created_at: string;
  result: {
    feature_importance: Record<string, number>;
  };
}
