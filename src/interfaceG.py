import os

import streamlit as st

import src.create_db as create_db
import src.helpers as helpers
import src.llm_interface as llm_interface

RAG_METHODS = create_db.METHODS  # ["Dense", "Hybride", "Rerank"]


def title():
    """Apply the page configuration, title and header."""
    st.set_page_config(page_title="AskMyDocs", layout="centered")
    st.markdown(
        """
        <h1 style="text-align: center; color: #0e5a6b;">AskMyDocs</h1>
        <h3 style="text-align: center; color: #555;">Ask questions, get answers grounded in your documents</h3>
        <p style="text-align: center; font-size: 16px; color: #777;">Upload your CSV or PDF files, then ask away.</p>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state():
    """Initialise session state keys if needed."""
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("rag_method", "Dense")
    st.session_state.setdefault("csv_paths", [])
    st.session_state.setdefault("docs", None)


def _retrieve_documents(user_input: str):
    """Retrieve passages with the selected method, or an empty list."""
    if "rag_index" not in st.session_state:
        st.warning("Create the database first, then ask your question.")
        return []
    method = st.session_state.get("rag_method", "Dense")
    try:
        return create_db.query(method, user_input, n_results=5)
    except Exception as exc:  # keep the UI responsive on model/index errors
        st.error(f"Retrieval failed: {exc}")
        return []


def handle_send_message(mistral_key):
    """Send the user's message to the model and update the history."""
    user_input = st.session_state.user_input
    if not user_input:
        return None

    docs = _retrieve_documents(user_input)
    st.session_state["docs"] = docs

    response = llm_interface.query_mistral(user_input, st.session_state.history, mistral_key, docs)
    formatted_response = helpers.format_response(response)

    st.session_state.history.append(f"You: {user_input}")
    st.session_state.history.append(f"Chatbot: \n\n{formatted_response}")

    st.session_state.user_input = ""
    return docs


def display_messages():
    """Display the conversation history."""
    for message in st.session_state.history:
        st.write(message)


def display_documents():
    """Display the passages retrieved for the latest question, with their source."""
    docs = st.session_state.get("docs")
    if docs:
        st.write("Passages retrieved:")
        labels = [f"{i + 1}. {d['source']} · score {d['score']}" for i, d in enumerate(docs)]
        selected_label = st.selectbox("Select a passage to view:", options=labels)
        selected = docs[labels.index(selected_label)]
        st.write(selected["text"])
    elif st.session_state.history and "Chatbot:" in st.session_state.history[-1]:
        st.write("No passages retrieved for this interaction.")


def _save_uploaded_files(uploaded_files, folder):
    """Save uploaded files under ``folder`` and return their paths.

    File names are reduced to their base name so a crafted name cannot write
    outside the target folder.
    """
    os.makedirs(folder, exist_ok=True)
    paths = []
    for uploaded_file in uploaded_files:
        safe_name = os.path.basename(uploaded_file.name)
        if not safe_name:
            continue
        file_path = os.path.join(folder, safe_name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        paths.append(file_path)
    return paths


def _select_rag_method():
    """Pick the retrieval method. All methods share the same index, so the
    choice can be changed at any time without rebuilding."""
    current = st.session_state.get("rag_method", "Dense")
    choice = st.radio(
        "Retrieval method",
        RAG_METHODS,
        index=RAG_METHODS.index(current) if current in RAG_METHODS else 0,
        horizontal=True,
    )
    st.session_state.rag_method = choice


def handle_file_upload():
    """Handle CSV/PDF uploads and index creation."""
    uploaded_files = st.file_uploader(
        "Upload CSV or PDF files", accept_multiple_files=True, type=["csv", "pdf"]
    )

    _select_rag_method()

    if st.button("Create Database"):
        if not uploaded_files:
            st.warning("Please upload CSV or PDF files.")
            return

        paths = _save_uploaded_files(uploaded_files, "uploaded_dataset")
        st.session_state["csv_paths"] = paths

        passages = create_db.files_to_passages(paths)
        if not passages:
            st.warning("No text could be extracted from the uploaded files.")
            return

        with st.spinner("Indexing your documents..."):
            create_db.build_index(passages)
        st.success(f"Indexed {len(passages)} passages. You can now ask questions.")
