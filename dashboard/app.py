"""Streamlit dashboard for fraud detection monitoring."""
import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Fraud Detection Dashboard", page_icon="🛡️", layout="wide")
st.title("🛡️ Fraud Detection Dashboard")

@st.cache_data
def load_data():
    train_path = "data/transactions_train.csv"
    test_path = "data/transactions_test.csv"
    train_df = pd.read_csv(train_path) if os.path.exists(train_path) else pd.DataFrame()
    test_df = pd.read_csv(test_path) if os.path.exists(test_path) else pd.DataFrame()
    return train_df, test_df

@st.cache_data
def load_metrics():
    metrics_path = "models/metrics.json"
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            return json.load(f)
    return {}

train_df, test_df = load_data()
model_metrics = load_metrics()

st.sidebar.header("Controls")
data_source = st.sidebar.selectbox("Data Source", ["Train", "Test"])
df = train_df if data_source == "Train" else test_df

if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Transactions", "{:,}".format(len(df)))
    with col2:
        st.metric("Fraud Rate", "{:.2f}%".format(df["is_fraud"].mean() * 100))
    with col3:
        st.metric("Model AUC", "{:.4f}".format(model_metrics.get("auc", 0)) if model_metrics else "N/A")
    with col4:
        st.metric("Avg Amount", "${:.2f}".format(df["amount"].mean()))
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Transaction Amount by Type")
        amount_data = df.groupby("is_fraud")["amount"].mean()
        st.bar_chart(amount_data)
    with col2:
        st.subheader("Fraud by Hour")
        hourly = df.groupby("hour")["is_fraud"].mean() * 100
        st.line_chart(hourly)
    
    st.subheader("Sample Transactions")
    st.dataframe(df.head(100)[["transaction_id", "user_id", "amount", "hour", "velocity_1h", "is_new_device", "is_fraud"]])
else:
    st.warning("No data available. Run `make gen` to generate data.")
