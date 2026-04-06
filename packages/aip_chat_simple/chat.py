import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import ClientError
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

import aipassport_config as cfg

def is_429(exception):
    return isinstance(exception, ClientError) and "429" in str(exception)

@retry(
    retry=retry_if_exception(is_429),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def generate_with_retry(client, model_id, contents, config):
    return client.models.generate_content(
        model=model_id,
        contents=contents,
        config=config
    )

def render_ai_guide(gemini_api_key: str, context_fn=None):
    """
    Renders a direct Gemini-powered chat interface in the current Streamlit container.
    """
    if not gemini_api_key:
        st.error("Missing GEMINI_API_KEY in secrets.")
        return

    # Initialize client
    client = genai.Client(api_key=gemini_api_key)
    model_id = cfg.DEFAULT_GEMINI_MODEL

    # Initialize chat history in session state if not present
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Quick-action chips — always visible above the input
    cols = st.columns(2)
    if cols[0].button("🖥️ What's on my screen?", use_container_width=True):
        st.session_state["_quick_action"] = "Explain what's on my screen based on the current charts and values."
        st.rerun()
    if cols[1].button("💡 How do I use this activity?", use_container_width=True):
        st.session_state["_quick_action"] = "How do I use this activity and what controls are available?"
        st.rerun()

    prompt = st.chat_input("Ask the AIP Guide anything...")
    
    # Check if a quick action button was clicked in the previous run
    if "_quick_action" in st.session_state:
        prompt = st.session_state.pop("_quick_action")

    # React to user input
    if prompt:
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Prepare context if available
        context_parts = [st.session_state.messages[-1]["content"]]
        
        # 1. Functional Context from context_fn (Page metadata)
        if context_fn:
            try:
                ctx = context_fn()
                context_parts.append(f"\n\n[System Context: {ctx}]")
            except Exception as e:
                context_parts.append(f"\n\n[Context Error: {e}]")

        # 2. Live Page State (Variable values, selections, metrics)
        if live_state := st.session_state.get("_live_state"):
            context_parts.append(f"\n\n[Live Screen State: {live_state}]")

        # 3. Screen Images (Charts, screenshots)
        screen_images = []
        if img_data := st.session_state.get("_screen_image"):
            # Assume it's a base64 string or bytes
            try:
                import base64
                if isinstance(img_data, str):
                    img_bytes = base64.b64decode(img_data)
                else:
                    img_bytes = img_data
                screen_images.append(types.Part.from_bytes(data=img_bytes, mime_type="image/png"))
            except Exception as e:
                context_parts.append(f"\n\n[Image Error: {e}]")

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # System prompt + User prompt + Context
                system_instruction = cfg.AI_GUIDE_SYSTEM_PROMPT
                
                # Fetch response from Gemini with retry logic
                response = generate_with_retry(
                    client=client,
                    model_id=model_id,
                    contents=context_parts + screen_images,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                    )
                )
                
                full_response = response.text
                # Simulate streaming for better UX
                words = full_response.split()
                current_text = ""
                for word in words:
                    current_text += word + " "
                    message_placeholder.markdown(current_text + "▌")
                    time.sleep(0.01)
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                if "429" in str(e):
                    full_response = "⚠️ **Rate Limit Reached**: The Gemini API is currently receiving too many requests. Please wait a few seconds and try again."
                else:
                    full_response = f"Sorry, I encountered an error: {e}"
                message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
