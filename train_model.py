#!/usr/bin/env python
"""
Generate synthetic diabetes dataset and train model
Uses sklearn datasets to create training data
"""

import numpy as np
import pandas as pd
import pickle
import logging
import os
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_and_train_model():
    """Create synthetic dataset and train the model"""
    try:
        logger.info("Creating synthetic diabetes dataset...")
        
        # Generate synthetic data similar to diabetes dataset
        # 8 features matching: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DPF, Age
        X, y = make_classification(
            n_samples=768,  # Similar to Pima Indians Diabetes Dataset
            n_features=8,
            n_informative=7,
            n_redundant=1,
            n_classes=2,
            weights=[0.65, 0.35],  # Similar class distribution
            random_state=42
        )
        
        # Scale features to realistic ranges
        X[:, 0] = np.clip(X[:, 0] * 10, 0, 20)      # Pregnancies (0-20)
        X[:, 1] = np.clip(X[:, 1] * 30 + 100, 70, 200)    # Glucose (70-200)
        X[:, 2] = np.clip(X[:, 2] * 40 + 100, 40, 180)    # BloodPressure (40-180)
        X[:, 3] = np.clip(X[:, 3] * 30, 0, 100)    # SkinThickness (0-100)
        X[:, 4] = np.clip(X[:, 4] * 150, 0, 900)   # Insulin (0-900)
        X[:, 5] = np.clip(X[:, 5] * 15 + 20, 10, 60)      # BMI (10-60)
        X[:, 6] = np.clip(X[:, 6], 0, 2.5)         # DPF (0-2.5)
        X[:, 7] = np.clip(X[:, 7] * 40 + 20, 20, 100)     # Age (20-100)
        
        # Create DataFrame
        df = pd.DataFrame(X, columns=['Pregnancies', 'Glucose', 'BloodPressure', 
                                      'SkinThickness', 'Insulin', 'BMI', 'DPF', 'Age'])
        df['Outcome'] = y
        
        logger.info(f"Dataset created: {df.shape[0]} samples, {df.shape[1]-1} features")
        logger.info(f"Feature ranges:\n{df.describe().to_string()}")
        
        # Prepare features and target
        X = df.drop(columns='Outcome')
        y = df['Outcome']
        
        logger.info("\nBuilding Random Forest Classifier...")
        classifier = RandomForestClassifier(n_estimators=20, random_state=0, n_jobs=-1)
        
        # Stratified K-Fold Cross Validation
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
        
        logger.info("\n" + "="*70)
        logger.info("Performing 5-Fold Stratified Cross Validation")
        logger.info("="*70)
        
        fold_scores = []
        for fold, (train_index, test_index) in enumerate(skf.split(X, y)):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            classifier.fit(X_train, y_train)
            y_pred = classifier.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            
            fold_scores.append({'Accuracy': accuracy, 'Precision': precision, 
                               'Recall': recall, 'F1-Score': f1})
            
            logger.info(f"Fold {fold+1}: Accuracy={accuracy:.4f}, Precision={precision:.4f}, "
                       f"Recall={recall:.4f}, F1={f1:.4f}")
        
        # Calculate and display average scores
        avg_accuracy = np.mean([s['Accuracy'] for s in fold_scores])
        avg_precision = np.mean([s['Precision'] for s in fold_scores])
        avg_recall = np.mean([s['Recall'] for s in fold_scores])
        avg_f1 = np.mean([s['F1-Score'] for s in fold_scores])
        
        logger.info("="*70)
        logger.info(f"Average CV Scores:")
        logger.info(f"  Accuracy:  {avg_accuracy:.4f}")
        logger.info(f"  Precision: {avg_precision:.4f}")
        logger.info(f"  Recall:    {avg_recall:.4f}")
        logger.info(f"  F1-Score:  {avg_f1:.4f}")
        logger.info("="*70)
        
        # Train final model on full dataset
        logger.info("\nTraining final model on full dataset...")
        classifier.fit(X, y)
        
        # Save the model
        filename = 'diabetes-prediction-rfc-model.pkl'
        logger.info(f"Saving model to {filename}...")
        pickle.dump(classifier, open(filename, 'wb'))
        
        file_size = os.path.getsize(filename)
        logger.info(f"✅ Model trained and saved successfully!")
        logger.info(f"   Model file: {filename}")
        logger.info(f"   File size: {file_size / 1024:.2f} KB")
        logger.info(f"   Test the model by making predictions on the web application")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error training model: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    logger.info("="*70)
    logger.info("DIABETES PREDICTION MODEL TRAINING")
    logger.info("="*70)
    
    success = create_and_train_model()
    
    if success:
        print("\n" + "="*70)
        print("✨ Model trained successfully! Ready to use.")
        print("="*70)
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Create an account and make predictions!")
    else:
        print("\n❌ Model training failed. Check logs above.")
