#!/usr/bin/env python
"""
Retrain the diabetes prediction model for compatibility with current environment
"""

import numpy as np
import pandas as pd
import pickle
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retrain_model():
    """Retrain the model with current scikit-learn version"""
    try:
        # Check if dataset exists
        if not os.path.exists('kaggle_diabetes.csv'):
            logger.error("Dataset not found: kaggle_diabetes.csv")
            logger.info("Please ensure the diabetes dataset is in the project directory")
            return False
        
        logger.info("Loading dataset...")
        df = pd.read_csv('kaggle_diabetes.csv')
        
        # Renaming DiabetesPedigreeFunction as DPF
        df = df.rename(columns={'DiabetesPedigreeFunction': 'DPF'})
        
        # Replacing 0 values with NaN and then filling with mean/median
        df_copy = df.copy(deep=True)
        df_copy[['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']] = \
            df_copy[['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']].replace(0, np.NaN)
        
        logger.info("Filling missing values...")
        df_copy['Glucose'].fillna(df_copy['Glucose'].mean(), inplace=True)
        df_copy['BloodPressure'].fillna(df_copy['BloodPressure'].mean(), inplace=True)
        df_copy['SkinThickness'].fillna(df_copy['SkinThickness'].median(), inplace=True)
        df_copy['Insulin'].fillna(df_copy['Insulin'].median(), inplace=True)
        df_copy['BMI'].fillna(df_copy['BMI'].median(), inplace=True)
        
        # Prepare features and target
        X = df_copy.drop(columns='Outcome')
        y = df_copy['Outcome']
        
        logger.info("Building Random Forest model...")
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import StratifiedKFold
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        # Create classifier
        classifier = RandomForestClassifier(n_estimators=20, random_state=0)
        
        # Stratified K-Fold Cross Validation
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
        
        logger.info("\nPerforming 5-Fold Cross Validation:")
        for fold, (train_index, test_index) in enumerate(skf.split(X, y)):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            classifier.fit(X_train, y_train)
            y_pred = classifier.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            logger.info(f"Fold {fold+1}: Accuracy={accuracy:.4f}, Precision={precision:.4f}, "
                       f"Recall={recall:.4f}, F1={f1:.4f}")
        
        # Train on full dataset for final model
        logger.info("\nTraining final model on full dataset...")
        classifier.fit(X, y)
        
        # Save the model
        filename = 'diabetes-prediction-rfc-model.pkl'
        logger.info(f"Saving model to {filename}...")
        pickle.dump(classifier, open(filename, 'wb'))
        
        logger.info(f"✅ Model retrained and saved successfully!")
        logger.info(f"Model file size: {os.path.getsize(filename) / 1024:.2f} KB")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error retraining model: {e}")
        return False

if __name__ == '__main__':
    success = retrain_model()
    if success:
        print("\n✨ Model is ready! You can now run the application.")
    else:
        print("\n⚠️  Model training failed. Check the logs above.")
