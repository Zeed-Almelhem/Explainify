import { Explanation } from '../services/api';

interface ExplanationVisualizerProps {
  explanation: Explanation;
}

export default function ExplanationVisualizer({ explanation }: ExplanationVisualizerProps) {
  const featureImportances = explanation.result.feature_importance as Record<string, number>;
  const maxImportance = Math.max(...Object.values(featureImportances));

  return (
    <div className="bg-white p-4 rounded-lg border">
      <div className="text-sm text-gray-500 mb-2">
        Generated on {new Date(explanation.created_at).toLocaleString()}
      </div>
      
      <div className="space-y-3">
        {Object.entries(featureImportances).map(([feature, importance]) => (
          <div key={feature}>
            <div className="flex justify-between text-sm mb-1">
              <span>{feature}</span>
              <span>{(importance * 100).toFixed(1)}%</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full">
              <div
                className="h-full bg-indigo-600 rounded-full"
                style={{
                  width: `${(importance / maxImportance) * 100}%`
                }}
              />
            </div>
          </div>
        ))}
      </div>

      {explanation.result.prediction !== undefined && (
        <div className="mt-4 pt-4 border-t">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Prediction</h4>
          <div className="text-lg font-semibold text-indigo-600">
            Class {explanation.result.prediction}
          </div>
          {explanation.result.prediction_probabilities && (
            <div className="text-sm text-gray-500 mt-1">
              Confidence: {(Math.max(...explanation.result.prediction_probabilities) * 100).toFixed(1)}%
            </div>
          )}
        </div>
      )}

      <div className="mt-4 pt-4 border-t">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Input Data</h4>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(explanation.result.input_data as Record<string, number>).map(([key, value]) => (
            <div key={key} className="text-sm">
              <span className="font-medium">{key}:</span> {value.toFixed(2)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
