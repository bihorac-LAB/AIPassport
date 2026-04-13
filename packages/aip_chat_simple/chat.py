import streamlit as st
from openai import OpenAI
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
import base64

import aipassport_config as cfg

def is_rate_limit(exception):
    return "429" in str(exception)

@retry(
    retry=retry_if_exception(is_rate_limit),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def generate_with_retry(client, model_id, messages):
    return client.chat.completions.create(
        model=model_id,
        messages=messages,
        temperature=0.7
    )

def render_ai_guide(navigator_api_key: str, context_fn=None):
    """
    Renders a direct NaviGator-powered chat interface in the current Streamlit container.
    """
    if not navigator_api_key:
        st.error("Missing NAVIGATOR_TOOLKIT_API_KEY in secrets.")
        return

    # Initialize client
    client = OpenAI(
        api_key=navigator_api_key,
        base_url=cfg.NAVIGATOR_TOOLKIT_BASE_URL
    )
    model_id = cfg.DEFAULT_MODEL

    # Initialize chat history and errors in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_error" not in st.session_state:
        st.session_state.chat_error = None

    # Display welcome message if history is empty
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("Hello! I am your AIP Guide. How can I help you today?")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        role = message["role"]
        # Skip system messages for UI display
        if role == "system":
            continue
        with st.chat_message(role):
            content = message["content"]
            if isinstance(content, list):
                for item in content:
                    if item["type"] == "text":
                        st.markdown(item["text"])
                    elif item["type"] == "image_url":
                        st.image(item["image_url"]["url"])
            else:
                st.markdown(content)

    # Prompt user
    prompt = st.chat_input(cfg.AI_GUIDE_PLACEHOLDER)
    
    # Handle Quick Actions
    cols = st.columns(2)
    if cols[0].button("🖥️ What's on my screen?", use_container_width=True):
        st.session_state["_quick_action"] = "Explain what's on my screen based on the current charts and values."
        st.rerun()
    if cols[1].button("💡 How do I use this activity?", use_container_width=True):
        st.session_state["_quick_action"] = "How do I use this activity and what controls are available?"
        st.rerun()

    if "_quick_action" in st.session_state:
        prompt = st.session_state.pop("_quick_action")

    # Error Display
    if st.session_state.chat_error:
        st.error(st.session_state.chat_error)
        if st.button("Dismiss Error"):
            st.session_state.chat_error = None
            st.rerun()

    # React to user input
    if prompt:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Build message history
        messages = [{"role": "system", "content": cfg.AI_GUIDE_SYSTEM_PROMPT}]
        
        # Add context if available
        context_str = ""
        if context_fn:
            try:
                ctx = context_fn()
                context_str += f"\n[Functional Context: {ctx}]"
            except Exception as e:
                context_str += f"\n[Context Error: {e}]"

        if live_state := st.session_state.get("_live_state"):
            context_str += f"\n[Live Screen State: {live_state}]"

        # Construct current user content (Vision support)
        user_content = [{"type": "text", "text": prompt + context_str}]
        
        if img_data := st.session_state.get("_screen_image"):
            try:
                if isinstance(img_data, bytes):
                    b64_img = base64.b64encode(img_data).decode('utf-8')
                else:
                    b64_img = img_data # Assume already b64
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64_img}"}
                })
            except Exception as e:
                user_content[0]["text"] += f"\n[Image Processing Error: {e}]"

        # Append history (limited to avoid token blow-up, e.g., last 10 messages)
        # Convert existing messages to OpenAI format if needed, but here they already are
        messages.extend(st.session_state.messages[-10:])
        messages.append({"role": "user", "content": user_content})

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                response = generate_with_retry(client, model_id, messages)
                full_response = response.choices[0].message.content
                
                # Simple streaming simulation for UX consistency
                words = full_response.split()
                curr = ""
                for w in words:
                    curr += w + " "
                    message_placeholder.markdown(curr + "▌")
                    time.sleep(0.01)
                message_placeholder.markdown(full_response)
                
                # Save to history
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.chat_error = None
                
            except Exception as e:
                st.session_state.chat_error = f"Sorry, I encountered an error: {e}"
                st.rerun()
