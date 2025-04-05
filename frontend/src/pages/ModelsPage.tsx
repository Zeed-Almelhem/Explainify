import ModelUpload from '../components/ModelUpload';
import ModelList from '../components/ModelList';
import ExplanationView from '../components/ExplanationView';

export default function ModelsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-8">
          <section>
            <h2 className="text-2xl font-bold mb-4">Upload Model</h2>
            <ModelUpload />
          </section>
          
          <section>
            <h2 className="text-2xl font-bold mb-4">Your Models</h2>
            <ModelList />
          </section>
        </div>

        <section>
          <h2 className="text-2xl font-bold mb-4">Model Explanations</h2>
          <ExplanationView />
        </section>
      </div>
    </div>
  );
}
