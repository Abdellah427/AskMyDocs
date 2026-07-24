import os

import faiss
import streamlit as st

import src.create_db as create_db
import src.helpers as helpers
import src.llm_interface as llm_interface
import src.rerank as rerank

RAG_METHODS = ["Retriever", "ColBERTv2", "Rerank"]

FAISS_INDEX_FILE = "faiss_index_file"
PCA_FILE = "pca_file"


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
    st.session_state.setdefault("rag_method", "")
    st.session_state.setdefault("csv_paths", [])
    st.session_state.setdefault("docs", None)


def _retrieve_documents(user_input: str):
    """Retrieve documents for the current RAG method, or an empty list."""
    method = st.session_state.rag_method

    if method == "Retriever":
        return create_db.query_vector_db_CustomVectorRetriever(user_input, 5)

    if method == "ColBERTv2":
        return create_db.query_vector_db_colbertv2(user_input, 2)

    if method == "Rerank":
        if not (os.path.exists(FAISS_INDEX_FILE) and os.path.exists(PCA_FILE)):
            st.warning("Create the database first to use the Rerank method.")
            return []
        csv_paths = st.session_state.get("csv_paths")
        if not csv_paths:
            return []
        pca = faiss.read_VectorTransform(PCA_FILE)
        index = faiss.read_index(FAISS_INDEX_FILE)
        full_doc = create_db.files_to_list_str(csv_paths)
        return rerank.search_and_rerank(pca, user_input, index, full_doc, top_k=3)

    return []


def handle_send_message(mistral_key):
    """Send the user's message to the chatbot and update the history."""
    user_input = st.session_state.user_input
    if not user_input:
        return None

    docs = _retrieve_documents(user_input)
    st.session_state["docs"] = docs

    prompt = (
        f"Question: \n\n{user_input} \n\n"
        f"Here are some documents to answer the question: \n\n{docs}"
    )
    response = llm_interface.query_mistral(prompt, st.session_state.history, mistral_key)
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
    """Display the documents retrieved for the latest question."""
    if st.session_state.get("docs"):
        st.write("Documents retrieved by the chatbot:")
        doc_labels = [f"Document {i + 1}" for i in range(len(st.session_state["docs"]))]
        selected_label = st.selectbox("Select a document to view:", options=doc_labels)
        selected_index = doc_labels.index(selected_label)
        st.write("Selected Document:")
        st.write(st.session_state["docs"][selected_index])
    elif st.session_state.history and "Chatbot:" in st.session_state.history[-1]:
        st.write("No documents retrieved by the chatbot for this interaction.")


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
    """Render the RAG-method buttons, or the locked state once chosen."""
    st.session_state.setdefault("rag_method_locked", False)

    if st.session_state["rag_method_locked"]:
        st.write(f"RAG Method selected: **{st.session_state.rag_method}** (locked)")
        return

    selected = st.session_state.get("rag_method", "")
    cols = st.columns(len(RAG_METHODS))
    for col, method in zip(cols, RAG_METHODS):
        with col:
            if st.button(method, key=method, use_container_width=True):
                st.session_state.rag_method = method
                st.session_state["rag_method_locked"] = True


def handle_file_upload():
    """Handle CSV/PDF uploads and database creation."""
    uploaded_files = st.file_uploader(
        "Upload CSV or PDF files", accept_multiple_files=True, type=["csv", "pdf"]
    )

    _select_rag_method()

    if st.button("Create Database"):
        if not uploaded_files:
            st.warning("Please upload CSV or PDF files.")
            return

        st.session_state["rag_method_locked"] = True
        csv_paths = _save_uploaded_files(uploaded_files, "uploaded_dataset")
        st.session_state["csv_paths"] = csv_paths

        full_doc = create_db.files_to_list_str(csv_paths)

        method = st.session_state.rag_method
        if method == "Retriever":
            create_db.create_vector_db_all_MiniLM_L6(full_doc)
            st.success("Database created with Retriever successfully!")
        elif method == "ColBERTv2":
            create_db.create_vector_db_colbertv2(full_doc)
            st.success("Database created with ColBERTv2 successfully!")
        elif method == "Rerank":
            rerank.create_vector_db_all_MiniLM_L6_VS(full_doc)
            st.success("Database created with Rerank successfully!")
        else:
            st.warning("Please select a RAG method before creating the database.")

    elif st.session_state.get("rag_method_locked"):
        method = st.session_state.get("rag_method", "Not selected")
        st.info(
            f"Database creation with the '{method}' method is locked. "
            "Please reload the page to change the method."
        )
