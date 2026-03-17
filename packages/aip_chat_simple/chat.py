import streamlit as st
from google import genai
from google.genai import types
import time

import aipassport_config as cfg

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

    # React to user input
    if prompt := st.chat_input("Ask the AIP Guide anything..."):
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
                
                # Fetch response from Gemini
                response = client.models.generate_content(
                    model=model_id,
                    contents=context_parts + screen_images,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                    )
                )
                
                full_response = response.text
                # Simulate streaming for better UX
                for chunk in full_response.split():
                    message_placeholder.markdown(full_response[:full_response.find(chunk)+len(chunk)] + "▌")
                    time.sleep(0.01)
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"Sorry, I encountered an error: {e}"
                message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
