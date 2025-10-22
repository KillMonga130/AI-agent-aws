import os
import uuid
import json
import requests
import streamlit as st

st.set_page_config(page_title="Ocean Agent UI", page_icon="🌊", layout="centered")

st.title("🌊 Ocean Forecasting Agent")

# Config
default_api = os.getenv("OCEAN_API", "")
api_base = st.text_input("API base URL (no trailing slash)", value=default_api, placeholder="https://xxxxx.execute-api.<region>.amazonaws.com/Prod")
session_id = st.text_input("Session ID", value=f"demo-{uuid.uuid4().hex[:6]}")

sample_question = "Is it safe to sail from Cape Town to Mossel Bay tomorrow?"
query = st.text_area("Question", value=sample_question, height=120)

col1, col2, col3 = st.columns(3)
with col1:
    run_btn = st.button("Ask Agent", type="primary")
with col2:
    health_btn = st.button("/health (local FastAPI)")
with col3:
    info_btn = st.button("/info (local FastAPI)")

if run_btn:
    if not api_base:
        st.error("Please enter the API base URL.")
    else:
        url = f"{api_base.rstrip('/')}/query"
        try:
            with st.spinner("Calling agent..."):
                resp = requests.post(url, json={"query": query, "session_id": session_id}, timeout=120)
            st.write(f"Status: {resp.status_code}")
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            st.json(data)
            if isinstance(data, dict) and data.get("response"):
                st.markdown("### Agent Response")
                st.write(data["response"]) 
        except Exception as e:
            st.exception(e)

# Optional helpers for local FastAPI dev only
if health_btn:
    try:
        r = requests.get("http://127.0.0.1:8080/health", timeout=10)
        st.write(r.status_code, r.text)
    except Exception as e:
        st.warning(str(e))

if info_btn:
    try:
        r = requests.get("http://127.0.0.1:8080/info", timeout=10)
        st.write(r.status_code)
        st.json(r.json())
    except Exception as e:
        st.warning(str(e))
