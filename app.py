import streamlit as st

import src.interfaceG as interfaceG
from src.config import get_mistral_api_key


def main():
    mistral_key = get_mistral_api_key()

    interfaceG.initialize_session_state()
    interfaceG.title()

    if not mistral_key:
        st.warning(
            "No Mistral API key configured. Set the MISTRAL_API_KEY environment "
            "variable (or a Streamlit secret) to enable answers."
        )

    st.text_input(
        "Your question",
        key="user_input",
        on_change=lambda: interfaceG.handle_send_message(mistral_key),
        placeholder="Enter your message here...",
        label_visibility="collapsed",
    )

    interfaceG.display_messages()
    interfaceG.display_documents()
    interfaceG.handle_file_upload()


if __name__ == "__main__":
    main()
