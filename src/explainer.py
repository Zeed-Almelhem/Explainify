import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.inspection import permutation_importance

class XAIExplainer:
    def __init__(self, model_handler, dataset_path):
        self.model_handler = model_handler
        try:
            self.data = pd.read_csv(dataset_path)
            if len(self.data.columns) < 2:
                raise ValueError("Dataset must have at least 2 columns (features and target)")
            
            # Assume last column is target
            self.X = self.data.iloc[:, :-1]
            self.y = self.data.iloc[:, -1]
            self.feature_names = self.X.columns.tolist()
            
            # Validate data types
            if not all(self.X.dtypes.apply(lambda x: np.issubdtype(x, np.number))):
                raise ValueError("All features must be numeric")
                
            # Try a prediction to validate model compatibility
            try:
                if hasattr(self.model_handler.model, 'predict'):
                    self.model_handler.model.predict(self.X.iloc[:1])
            except Exception as e:
                raise ValueError(f"Model is not compatible with the provided dataset: {str(e)}")
                
        except Exception as e:
            raise ValueError(f"Error loading dataset: {str(e)}")

    def get_feature_importance(self):
        """Generate feature importance visualization"""
        try:
            if hasattr(self.model_handler.model, 'feature_importances_'):
                importances = self.model_handler.model.feature_importances_
                importance_df = pd.DataFrame({
                    'feature': self.feature_names,
                    'importance': importances
                })
            else:
                # Use permutation importance for models without feature_importances_
                result = permutation_importance(
                    self.model_handler.model, self.X, self.y,
                    n_repeats=5, random_state=42
                )
                importance_df = pd.DataFrame({
                    'feature': self.feature_names,
                    'importance': result.importances_mean
                })

            fig = px.bar(
                importance_df,
                x='importance',
                y='feature',
                orientation='h',
                title='Feature Importance'
            )
            
            return fig.to_json()
        except Exception as e:
            raise ValueError(f"Error generating feature importance: {str(e)}")

    def get_global_explanations(self):
        """Generate global model explanations"""
        try:
            if self.model_handler.model_type == "clustering":
                # For clustering, show cluster centers
                centers = self.model_handler.model.cluster_centers_
                center_df = pd.DataFrame(
                    centers,
                    columns=self.feature_names[:2] if len(self.feature_names) > 2 else self.feature_names
                )
                
                fig = px.scatter(
                    center_df,
                    x=center_df.columns[0],
                    y=center_df.columns[1],
                    title='Cluster Centers',
                    labels={'x': 'Feature 1', 'y': 'Feature 2'}
                )
            else:
                # For classification/regression, show feature distributions
                melted_df = pd.melt(self.X)
                fig = px.box(
                    melted_df,
                    x='variable',
                    y='value',
                    title='Feature Distributions',
                    labels={'variable': 'Features', 'value': 'Value'}
                )
            
            return fig.to_json()
        except Exception as e:
            raise ValueError(f"Error generating global explanations: {str(e)}")

    def get_local_explanations(self):
        """Generate local explanations for specific predictions"""
        try:
            figs = []
            
            # Get sample predictions to explain (up to 5 samples)
            sample_indices = np.random.choice(len(self.X), min(5, len(self.X)), replace=False)
            
            for idx in sample_indices:
                sample = self.X.iloc[idx:idx+1]
                
                if self.model_handler.model_type == "classification":
                    # For classification, show prediction probabilities
                    pred_proba = self.model_handler.model.predict_proba(sample)[0]
                    class_names = getattr(self.model_handler.model, 'classes_', 
                                       [f'Class {i}' for i in range(len(pred_proba))])
                    
                    prob_df = pd.DataFrame({
                        'class': class_names,
                        'probability': pred_proba
                    })
                    
                    fig = px.bar(
                        prob_df,
                        x='class',
                        y='probability',
                        title=f'Prediction Probabilities for Instance {idx}'
                    )
                else:
                    # For regression/clustering, show feature values vs mean
                    feature_df = pd.DataFrame({
                        'feature': self.feature_names,
                        'value': sample.values[0],
                        'mean': self.X.mean().values
                    }).melt(id_vars=['feature'], var_name='type', value_name='value')
                    
                    fig = px.bar(
                        feature_df,
                        x='feature',
                        y='value',
                        color='type',
                        title=f'Feature Values vs Mean for Instance {idx}',
                        barmode='group'
                    )
                
                figs.append(fig.to_json())
            
            return figs
        except Exception as e:
            raise ValueError(f"Error generating local explanations: {str(e)}")

    def get_influential_samples(self):
        """Identify most influential training samples"""
        try:
            if self.model_handler.model_type == "clustering":
                # For clustering, show all points colored by cluster
                predictions = self.model_handler.model.predict(self.X)
                
                # Use first two features for visualization
                plot_df = pd.DataFrame({
                    'x': self.X.iloc[:, 0],
                    'y': self.X.iloc[:, 1] if len(self.feature_names) > 1 else np.zeros(len(self.X)),
                    'cluster': predictions
                })
                
                fig = px.scatter(
                    plot_df,
                    x='x',
                    y='y',
                    color='cluster',
                    title='Clustering Results',
                    labels={
                        'x': self.feature_names[0],
                        'y': self.feature_names[1] if len(self.feature_names) > 1 else ''
                    }
                )
            else:
                # For classification/regression, show data distribution
                if len(self.feature_names) >= 2:
                    plot_df = pd.DataFrame({
                        'x': self.X.iloc[:, 0],
                        'y': self.X.iloc[:, 1],
                        'target': self.y
                    })
                    
                    fig = px.scatter(
                        plot_df,
                        x='x',
                        y='y',
                        color='target',
                        title='Data Distribution',
                        labels={
                            'x': self.feature_names[0],
                            'y': self.feature_names[1],
                            'target': 'Target'
                        }
                    )
                else:
                    plot_df = pd.DataFrame({
                        'x': self.X.iloc[:, 0],
                        'target': self.y
                    })
                    
                    fig = px.scatter(
                        plot_df,
                        x='x',
                        y='target',
                        title='Data Distribution',
                        labels={
                            'x': self.feature_names[0],
                            'target': 'Target'
                        }
                    )
            
            return fig.to_json()
        except Exception as e:
            raise ValueError(f"Error generating influential samples: {str(e)}")
