"Train fraud detection model."
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib
from pathlib import Path


def main():
    base_dir = Path(__file__).parent.parent
    data_path = base_dir / data / transactions.csv
    model_path = base_dir / models / fraud_model.joblib
    
    if not data_path.exists():
        print(Error: Data not found)
        return
    
    print(=*50)
    print(FRAUD DETECTION MODEL TRAINING)
    print(=*50)
    
    df = pd.read_csv(data_path)
    print(Loaded, len(df), transactions)
    
    feature_cols = [amount, hour, day_of_week, velocity_1h]
    if is_new_device in df.columns:
        df[is_new_device_int] = df[is_new_device].astype(int)
        feature_cols.append(is_new_device_int)
    
    X = df[feature_cols].values
    y = df[is_fraud].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(Training set:, len(X_train), samples)
    print(Test set:, len(X_test), samples)
    print(Fraud rate:, round(y_train.mean()*100, 2), %)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=10, class_weight=balanced, random_state=42, n_jobs=-1)
    
    print(nTraining model...)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print(n + =*50)
    print(MODEL EVALUATION)
    print(=*50)
    print(classification_report(y_test, y_pred, target_names=[Legit, Fraud]))
    
    print(ROC-AUC Score:, round(roc_auc_score(y_test, y_prob), 4))
    
    cm = confusion_matrix(y_test, y_pred)
    print(nConfusion Matrix:)
    print( TN:, cm[0,0],  FP:, cm[0,1])
    print( FN:, cm[1,0],  TP:, cm[1,1])
    
    model_path.parent.mkdir(exist_ok=True)
    joblib.dump(model, model_path)
    print(nModel saved to:, model_path)
    
    print(n + =*50)
    print(Training complete!)
    print(=*50)


if __name__ == __main__:
    main()
