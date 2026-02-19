"""Synthetic transaction generator with realistic fraud patterns."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

def generate_transactions(n_transactions=100000, fraud_rate=0.02):
    n_users = n_transactions // 50
    n_merchants = n_transactions // 100
    n_devices = n_users * 2
    user_ids = ["user_{:05d}".format(i) for i in range(n_users)]
    merchant_ids = ["merchant_{:04d}".format(i) for i in range(n_merchants)]
    device_ids = ["device_{:06d}".format(i) for i in range(n_devices)]
    user_profiles = {}
    for uid in user_ids:
        user_profiles[uid] = {
            "avg_amount": np.random.lognormal(3, 1),
            "primary_device": np.random.choice(device_ids[:n_users]),
            "typical_hour_start": np.random.randint(8, 12),
            "typical_hour_end": np.random.randint(18, 23),
        }
    transactions = []
    start_date = datetime(2024, 1, 1)
    for i in range(n_transactions):
        user_id = np.random.choice(user_ids)
        profile = user_profiles[user_id]
        is_fraud = np.random.random() < fraud_rate
        if is_fraud:
            fraud_type = np.random.choice(["velocity", "new_device", "high_amount", "odd_hours"])
            if fraud_type == "velocity":
                amount = profile["avg_amount"] * np.random.uniform(0.5, 2)
                device_id = profile["primary_device"]
                hour = np.random.randint(profile["typical_hour_start"], profile["typical_hour_end"])
                velocity_1h = np.random.randint(5, 20)
            elif fraud_type == "new_device":
                amount = profile["avg_amount"] * np.random.uniform(1, 3)
                device_id = "device_{:06d}".format(np.random.randint(n_devices, n_devices + 10000))
                hour = np.random.randint(0, 24)
                velocity_1h = np.random.randint(1, 3)
            elif fraud_type == "high_amount":
                amount = profile["avg_amount"] * np.random.uniform(10, 50)
                device_id = profile["primary_device"]
                hour = np.random.randint(0, 24)
                velocity_1h = np.random.randint(1, 5)
            else:
                amount = profile["avg_amount"] * np.random.uniform(1, 5)
                device_id = profile["primary_device"]
                hour = np.random.choice([0, 1, 2, 3, 4, 5])
                velocity_1h = np.random.randint(1, 5)
        else:
            amount = max(1, np.random.lognormal(np.log(profile["avg_amount"]), 0.5))
            device_id = profile["primary_device"] if np.random.random() > 0.1 else np.random.choice(device_ids)
            hour = np.random.randint(profile["typical_hour_start"], profile["typical_hour_end"])
            velocity_1h = np.random.randint(0, 3)
        timestamp = start_date + timedelta(days=int(np.random.randint(0, 365)), hours=int(hour), minutes=int(np.random.randint(0, 60)))
        transactions.append({
            "transaction_id": "txn_{:08d}".format(i),
            "user_id": user_id,
            "merchant_id": np.random.choice(merchant_ids),
            "device_id": device_id,
            "amount": round(amount, 2),
            "timestamp": timestamp,
            "hour": hour,
            "day_of_week": timestamp.weekday(),
            "velocity_1h": velocity_1h,
            "is_new_device": device_id != profile["primary_device"],
            "is_fraud": int(is_fraud),
        })
    return pd.DataFrame(transactions)

def main():
    print("Generating synthetic transactions...")
    df = generate_transactions(n_transactions=100000, fraud_rate=0.02)
    os.makedirs("data", exist_ok=True)
    train_size = int(len(df) * 0.8)
    train_df = df.iloc[:train_size]
    test_df = df.iloc[train_size:]
    train_df.to_csv("data/transactions_train.csv", index=False)
    test_df.to_csv("data/transactions_test.csv", index=False)
    print("Generated {} transactions".format(len(df)))
    print("  Train: {} ({:.2f}% fraud)".format(len(train_df), train_df["is_fraud"].mean()*100))
    print("  Test: {} ({:.2f}% fraud)".format(len(test_df), test_df["is_fraud"].mean()*100))

if __name__ == "__main__":
    main()
