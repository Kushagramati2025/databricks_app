import streamlit as st

st.title("📊 Loan Analytics App")

st.write("Welcome to your first Databricks App 🚀")

# Sample data (temporary)
data = {
    "Loan ID": ["L001", "L002", "L003"],
    "Total Due": [18000, 36000, 18000]
}

st.table(data)