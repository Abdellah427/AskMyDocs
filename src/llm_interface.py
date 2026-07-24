from mistralai import Mistral


def query_mistral(user_input: str, history: list[str], api_key: str) -> str:
    """Query the Mistral model with the recent conversation as context.

    Args:
        user_input: The question or input text to send to the model.
        history: Previous messages in the conversation.
        api_key: The Mistral API key.

    Returns:
        The model's response, or a short message if the request fails.
    """
    if not api_key:
        return "No Mistral API key is configured. Set MISTRAL_API_KEY to enable answers."

    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)

    # Use the last few messages as context.
    conversation_history = "\n".join(history[-5:])
    prompt = f"{conversation_history}\nYou: {user_input}\nBot:"

    try:
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
            top_p=0.9,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Detailed error: {e}")
        return "Sorry, an error occurred while processing your request."
