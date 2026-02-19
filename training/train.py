"""Train fraud detection model."""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve
import joblib
import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scorer.features import extract_features, features_to_array, FEATURE_NAMES

def load_data(path):
    return pd.read_csv(path)

def prepare_features(df):
    features_list = []
    for _, row in df.iterrows():
        txn = row.to_dict()
        features = extract_features(txn)
        features_list.append(features_to_array(features))
    return np.array(features_list)

def train_model(X_train, y_train):
    model = RandomForestClassifier(
        n_estimators=100, max_depth=10, min_samples_split=10,
        min_samples_leaf=5, class_weight="balanced", random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legit", "Fraud"]))
    auc = roc_auc_score(y_test, y_proba)
    print("ROC-AUC: {:.4f}".format(auc))
    precision, recall, thresholds = precision_recall_curve(y_test, y_proba)
    f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
    best_idx = np.argmax(f1_scores)
    best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
    print("Best threshold: {:.4f}".format(best_threshold))
    print("\nFeature Importance:")
    for name, importance in sorted(zip(FEATURE_NAMES, model.feature_importances_), key=lambda x: x[1], reverse=True):
        print("  {}: {:.4f}".format(name, importance))
    return {"auc": auc, "best_threshold": best_threshold, "feature_importances": dict(zip(FEATURE_NAMES, model.feature_importances_.tolist()))}

def main():
    print("Loading training data...")
    train_df = load_data("data/transactions_train.csv")
    test_df = load_data("data/transactions_test.csv")
    print("Train: {} samples, {:.2f}% fraud".format(len(train_df), train_df["is_fraud"].mean()*100))
    print("Test: {} samples, {:.2f}% fraud".format(len(test_df), test_df["is_fraud"].mean()*100))
    print("\nExtracting features...")
    X_train = prepare_features(train_df)
    y_train = train_df["is_fraud"].values
    X_test = prepare_features(test_df)
    y_test = test_df["is_fraud"].values
    print("Feature shape: {}".format(X_train.shape))
    print("\nTraining model...")
    model = train_model(X_train, y_train)
    print("\nEvaluating model...")
    metrics = evaluate_model(model, X_test, y_test)
    os.makedirs("models", exist_ok=True)
    model_path = "models/fraud_model.joblib"
    joblib.dump(model, model_path)
    print("\nModel saved to {}".format(model_path))
    with open("models/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print("Metrics saved to models/metrics.json")

if __name__ == "__main__":
    main()
