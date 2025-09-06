import streamlit as st
import requests
import json
import os

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

st.set_page_config(page_title="Smart Chat App", page_icon="🤖")

st.title("🤖 Smart Chat App")
st.write("Chat with your AI assistant powered by Ollama!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What would you like to know?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call backend API
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"message": prompt, "history": st.session_state.messages[:-1]},
                    timeout=30
                )
                
                if response.status_code == 200:
                    assistant_response = response.json()["response"]
                    st.markdown(assistant_response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {str(e)}")

# Sidebar with model selection and settings
with st.sidebar:
    st.header("Settings")
    
    # Model selection
    try:
        models_response = requests.get(f"{BACKEND_URL}/models", timeout=10)
        if models_response.status_code == 200:
            models = models_response.json()["models"]
            selected_model = st.selectbox("Select Model", models, key="model_select")
            
            # Update model if changed
            if st.button("Update Model"):
                requests.post(f"{BACKEND_URL}/set_model", json={"model": selected_model})
                st.success(f"Model updated to {selected_model}")
        else:
            st.warning("Could not fetch available models")
    except:
        st.warning("Backend not available")
    
    # Clear chat history
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()