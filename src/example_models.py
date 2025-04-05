import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import joblib
import os

def create_example_models():
    # Create models directory if it doesn't exist
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'example_models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    # Classification example (Iris dataset)
    iris_data = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
    X_cls = iris_data.drop('species', axis=1)
    y_cls = iris_data['species']
    
    X_cls_train, X_cls_test, y_cls_train, y_cls_test = train_test_split(
        X_cls, y_cls, test_size=0.2, random_state=42
    )
    
    clf = LogisticRegression(random_state=42)
    clf.fit(X_cls_train, y_cls_train)
    
    # Save classification model and test data
    joblib.dump(clf, os.path.join(models_dir, 'classification_model.pkl'))
    pd.concat([X_cls_test, y_cls_test], axis=1).to_csv(
        os.path.join(models_dir, 'classification_data.csv'), index=False
    )

    # Regression example (Boston Housing dataset)
    from sklearn.datasets import fetch_california_housing
    housing = fetch_california_housing()
    X_reg = pd.DataFrame(housing.data, columns=housing.feature_names)
    y_reg = pd.Series(housing.target, name='price')
    
    X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(
        X_reg, y_reg, test_size=0.2, random_state=42
    )
    
    reg = LinearRegression()
    reg.fit(X_reg_train, y_reg_train)
    
    # Save regression model and test data
    joblib.dump(reg, os.path.join(models_dir, 'regression_model.pkl'))
    pd.concat([X_reg_test, y_reg_test], axis=1).to_csv(
        os.path.join(models_dir, 'regression_data.csv'), index=False
    )

    # Clustering example (generated data)
    np.random.seed(42)
    n_samples = 300
    X_cluster = np.concatenate([
        np.random.normal(0, 1, (n_samples, 2)),
        np.random.normal(4, 1.5, (n_samples, 2)),
        np.random.normal(-4, 1.2, (n_samples, 2))
    ])
    
    clustering = KMeans(n_clusters=3, random_state=42)
    clustering.fit(X_cluster)
    
    # Save clustering model and data
    joblib.dump(clustering, os.path.join(models_dir, 'clustering_model.pkl'))
    pd.DataFrame(X_cluster, columns=['feature1', 'feature2']).to_csv(
        os.path.join(models_dir, 'clustering_data.csv'), index=False
    )

if __name__ == '__main__':
    create_example_models()
