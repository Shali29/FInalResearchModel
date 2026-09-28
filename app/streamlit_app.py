"""Self-contained Streamlit website for the legal NLP research prototype."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from sri_lankan_legal_nlp.api.service import (
    DISCLAIMER,
    find_amendments,
    find_source_records,
    predict_entities,
    simplification_template,
)

st.set_page_config(
    page_title="Sri Lankan legal NLP",
    page_icon=":material/gavel:",
    layout="wide",
)

st.title("Sri Lankan legal document analysis", icon=":material/gavel:")
st.write("Explore English and Sinhala legal text from the Constitution and Penal Code.")
st.warning(DISCLAIMER, icon=":material/warning:")
st.markdown(
    ":orange-badge[Research prototype] :blue-badge[English + Sinhala] "
    ":red-badge[Not legal advice]"
)

ner_tab, source_tab, simplify_tab, amendment_tab = st.tabs(
    [
        ":material/find_in_page: Entity recognition",
        ":material/library_books: Source search",
        ":material/translate: Simplification",
        ":material/history: Amendments",
    ]
)

with ner_tab:
    st.header("Identify legal entities", icon=":material/find_in_page:")
    st.caption(
        "The current CRF model is provisional (validation micro-F1: 19.85%). "
        "Predictions require human verification."
    )
    with st.form("ner_form"):
        ner_language = st.segmented_control(
            "Language", options=["en", "si"], default="en", key="ner_language"
        )
        ner_text = st.text_area(
            "Legal text",
            height=220,
            placeholder="Paste an English or Sinhala legal passage here.",
            key="ner_text",
        )
        identify = st.form_submit_button(
            "Identify entities", type="primary", icon=":material/search:"
        )

    if identify:
        if not ner_text.strip():
            st.error("Enter legal text before running entity recognition.")
        else:
            with st.spinner("Analyzing the text..."):
                result = predict_entities(ner_text, ner_language or "en")
            entities = result.get("entities", [])
            if result.get("status") == "model_unavailable":
                st.error(
                    "The CRF model file is not available in this deployment. "
                    "Add the deployment artifact and reboot the app."
                )
            elif entities:
                st.success(f"Found {len(entities)} provisional entity span(s).")
                st.dataframe(pd.DataFrame(entities), hide_index=True)
            else:
                st.info("No entity span was detected in this text.")

with source_tab:
    st.header("Search legal sources", icon=":material/library_books:")
    st.caption("Results retain the source filename, page number, language and quality status.")
    with st.form("source_form"):
        source_query = st.text_input(
            "Word, phrase or provision number", placeholder="For example: imprisonment or 12"
        )
        source_language = st.selectbox(
            "Language", options=["All", "English", "Sinhala"], key="source_language"
        )
        search_sources = st.form_submit_button("Search sources", icon=":material/search:")

    if search_sources:
        if not source_query.strip():
            st.error("Enter a word, phrase or provision number.")
        else:
            language_code = {"English": "en", "Sinhala": "si"}.get(source_language)
            matches = find_source_records(source_query, language_code, 20)
            if matches:
                st.success(f"Found {len(matches)} source record(s).")
                for record in matches:
                    title = (
                        f"{record.get('document_title', 'Legal source')} — "
                        f"page {record.get('pdf_page_number', 'unknown')}"
                    )
                    with st.expander(title, icon=":material/article:"):
                        st.write(record.get("text", ""))
                        st.caption(
                            f"Source: {record.get('source_file')} | "
                            f"Language: {record.get('language')} | "
                            f"Quality: {record.get('quality_status')}"
                        )
            else:
                st.info("No result was found, or the deployment source-data file is missing.")

with simplify_tab:
    st.header("Prepare a Sinhala simplification", icon=":material/translate:")
    st.info(
        "This prepares a review record only. It does not invent a translation or claim that "
        "legal meaning has been simplified correctly."
    )
    with st.form("simplification_form"):
        simplify_language = st.segmented_control(
            "Original language",
            options=["en", "si"],
            default="si",
            key="simplify_language",
        )
        simplify_text = st.text_area("Original legal text", height=220, key="simplify_text")
        prepare = st.form_submit_button(
            "Prepare review record", type="primary", icon=":material/edit_document:"
        )

    if prepare:
        if not simplify_text.strip():
            st.error("Enter legal text before preparing the review record.")
        else:
            task = simplification_template(simplify_text, simplify_language or "si")
            st.success("Prepared. Human and legal-expert review is still required.")
            st.json(task, expanded=True)

with amendment_tab:
    st.header("Find amendment candidates", icon=":material/history:")
    st.caption("All candidates remain pending manual review.")
    with st.form("amendment_form"):
        provision = st.text_input("Provision number (optional)", placeholder="For example: 109")
        search_amendments = st.form_submit_button(
            "Find amendments", icon=":material/search:"
        )

    if search_amendments:
        candidates = find_amendments(provision.strip() or None, 50)
        if candidates:
            st.success(f"Found {len(candidates)} unverified candidate(s).")
            for candidate in candidates:
                operation = candidate.get("operation") or "unresolved operation"
                title = (
                    f"Provision {candidate.get('affected_provision')} — {operation} — "
                    f"page {candidate.get('page_number')}"
                )
                with st.expander(title, icon=":material/history_edu:"):
                    st.write(candidate.get("amending_instruction", ""))
                    st.caption(
                        f"Source: {candidate.get('source_file')} | "
                        f"Status: {candidate.get('verification_status')}"
                    )
        else:
            st.info("No candidate was found, or the deployment candidate file is missing.")

st.caption(
    "Undergraduate research prototype • Constitution and Penal Code • English and Sinhala only"
)
