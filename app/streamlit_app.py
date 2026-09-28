"""Small Streamlit interface for the provenance-first research API."""

from __future__ import annotations

import requests
import streamlit as st

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Sri Lankan Legal NLP", layout="wide")
st.title("Sri Lankan Legal NLP Research Prototype")
st.warning("Research-based legal information only—not legal advice. Verify official sources.")

language = st.selectbox("Language", ["en", "si"])
text = st.text_area("Enter legal text", height=220)

if st.button("Identify entities") and text.strip():
    response = requests.post(
        f"{API}/ner", json={"text": text, "language": language}, timeout=30
    )
    response.raise_for_status()
    st.json(response.json())

if st.button("Prepare simplification review") and text.strip():
    response = requests.post(
        f"{API}/simplification/prepare",
        json={"text": text, "language": language},
        timeout=30,
    )
    response.raise_for_status()
    st.json(response.json())

st.subheader("Amendment candidates")
provision = st.text_input("Provision number (optional)")
if st.button("Find amendments"):
    response = requests.get(
        f"{API}/amendments", params={"provision": provision or None}, timeout=30
    )
    response.raise_for_status()
    st.json(response.json())
