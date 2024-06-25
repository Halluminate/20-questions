# #! /usr/bin/env python3

import os
import copy

import streamlit as st
from typing import Generator

from groq import Groq
import wikipedia

st.set_page_config(page_icon="💬", layout="wide",
                   page_title="20 Questions")

groq_api_key = os.environ.get("GROQ_API_KEY")

client = Groq(
    api_key=groq_api_key,
)
MODEL = "llama3-70b-8192"

def get_person():
    """Get a person's name from an LLM"""
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Name someone famous enough to have their own page on Wikipedia. Only put their name, nothing else.",
            }
        ],
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content

def get_wikipedia_page(person):
    """Get the Wikipedia page given a person's name"""
    try:
        page = wikipedia.page(title=person, auto_suggest=False)
        return page
    except wikipedia.exceptions.PageError as pe:
        print(f"PageError: {pe} - {person} not found on Wikipedia")
        return None

def set_up_bot(person, page):
    """Set up the bot with the person and their Wikipedia page"""
    system_content = f"You are a playing 20 questions. You are thinking of this person: {person}. The user is trying to guess this person. They will ask you yes or no questions, and you must respond accurately. For context on this person, look at their wikipedia page: {page.url}. " \
            "If the question from the user can't be answered with a simple yes or no, respond with 'I can only answer Yes or No questions'. If the user guesses the person, respond with 'Correct!'. If the user gives up, respond with 'Better luck next time!'."
    system_prompt = {
        "role": "system",
        "content": system_content
    }
    first_message = "Hello! Welcome to 20 Questions! You can ask me Yes or No questions, or you can guess the person. Let's get started! Now, who am I thinking of..."
    first_message_obj = {"role": "assistant", "content": first_message}
    messages = [system_prompt, first_message_obj]
    return messages

def get_bot_response(message_history):
    """Get the bot's response to the user's message"""
    stream = client.chat.completions.create(
        messages=message_history,
        model=MODEL,
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=True,
    )
    return stream


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )
icon("💬")

st.title("20 Questions")
st.subheader("Are you smarter than a large language model?", divider="rainbow", anchor=False)
def clicked():
    st.session_state.person = get_person()
    st.session_state.page = get_wikipedia_page(st.session_state.person)
    st.session_state.messages = set_up_bot(
        st.session_state.person, st.session_state.page)
    st.session_state.selected_model = None
    st.session_state.messages = []
    st.session_state.selected_model = None
st.button('🔄 Reset', on_click=clicked)

if "person" not in st.session_state:
    st.session_state.person = get_person()


if "page" not in st.session_state:
    st.session_state.page = get_wikipedia_page(st.session_state.person)

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = set_up_bot(
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
    st.session_state.messages = set_up_bot(
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
        bot_stream_response = get_bot_response(st.session_state.messages)
        with st.chat_message("assistant", avatar="🤖"):
            generator = generate_chat_responses(bot_stream_response)
            bot_full_response = st.write_stream(generator)

        # Append the full response to session_state.messages
        if isinstance(bot_full_response, str):
            st.session_state.messages.append(
                {"role": "assistant", "content": bot_full_response})
        else:
            # Handle the case where full_response is not a string
            combined_response = "\n".join(str(item) for item in bot_full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": combined_response})
        
    except Exception as e:
        st.error(e, icon="🚨")
