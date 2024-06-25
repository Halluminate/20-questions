# #! /usr/bin/env python3

import os
import copy

import streamlit as st
from typing import Generator

import twenty_questions

st.set_page_config(page_icon="💬", layout="wide",
                   page_title="20 Questions")


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )
icon("💬")

st.header("20 Questions")
st.subheader("Are you smarter than a large language model?", divider="rainbow", anchor=False)

if "person" not in st.session_state:
    person = twenty_questions.get_person()
    st.session_state.person = twenty_questions.get_person()


if "page" not in st.session_state:
    st.session_state.page = twenty_questions.get_wikipedia_page(st.session_state.person)

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = twenty_questions.set_up_bot(
        st.session_state.person, st.session_state.page)

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# Define model details
models = {
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
}

# Layout for model selection and max_tokens slider
col1, col2 = st.columns(2)

with col1:
    model_option = st.selectbox(
        "Choose a model:",
        options=list(models.keys()),
        format_func=lambda x: models[x]["name"],
        index=2  # Default to mixtral
    )

# Detect model change and clear chat history if model has changed
if st.session_state.selected_model != model_option:
    st.session_state.messages = twenty_questions.set_up_bot(
        st.session_state.person, st.session_state.page)
    st.session_state.selected_model = model_option

max_tokens_range = models[model_option]["tokens"]

with col2:
    # Adjust max_tokens slider dynamically based on the selected model
    max_tokens = st.slider(
        "Max Tokens:",
        min_value=512,  # Minimum value to allow some flexibility
        max_value=max_tokens_range,
        # Default value or max allowed if less
        value=min(32768, max_tokens_range),
        step=512,
        help=f"Adjust the maximum number of tokens (words) for the model's response. Max for selected model: {max_tokens_range}"
    )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


if prompt := st.chat_input("Enter your guess here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar='👨‍💻'):
        st.markdown(prompt)

    # Fetch response from Groq API
    try:
        bot_stream_response, messages = twenty_questions.get_bot_response(prompt, copy.deepcopy(st.session_state.messages))
        bot_full_response = ""
        with st.chat_message("assistant", avatar="🤖"):
            generator = generate_chat_responses(bot_stream_response)
            bot_full_response = st.write_stream(generator)
    except Exception as e:
        st.error(e, icon="🚨")

    # Append the full response to session_state.messages
    if isinstance(bot_full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": bot_full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in bot_full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})
