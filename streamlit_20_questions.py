# #! /usr/bin/env python3

import os
import copy

import streamlit as st
from groq import Groq
import wikipedia

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def get_person():
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
    try:
        page = wikipedia.page(title=person, auto_suggest=False)
        return page
    except wikipedia.exceptions.PageError as pe:
        print(f"PageError: {pe} - {person} not found on Wikipedia")
        return None

# def conversation_loop(person, wikipedia_page_url):
#     # Set the system prompt
#     system_prompt = {
#         "role": "system",
#         "content":
#             f"You are a playing 20 questions. You are thinking of this person: {person}. The user is trying to guess this person. They will ask you yes or no questions, and you must respond accurately. For context on this person, look at their wikipedia page: {wikipedia_page_url}." \
#             "If the question from the user can't be answered with a simple yes or no, respond with 'I can only answer Yes or No questions'. If the user guesses the person, respond with 'Correct!'. If the user gives up, respond with 'Better luck next time!'."
#     }
#     # Initialize the chat history
#     chat_history = [system_prompt]
#     first_message = "Hello! Welcome to 20 Questions! You can ask me Yes or No questions, or you can guess the person. Let's get started! Now, who am I thinking of..."
#     st.write(first_message)
#     while True:
#         user_input = st.text_input("You: ", key="user_input")
#         if st.button("Send", key="send_button"):
#             chat_history.append({"role": "user", "content": user_input})
#             response = client.chat.completions.create(
#                 messages=chat_history,
#                 model="llama3-70b-8192",
#             )
#             assistant_response = response.choices[0].message.content
#             chat_history.append({
#                 "role": "assistant",
#                 "content": assistant_response
#             })
#             st.write(f"> {assistant_response}")

def generate_response(query, person, wikipedia_page_url, chat_history):
    system_prompt = {
        "role": "system",
        "content":
            f"You are a playing 20 questions. You are thinking of this person: {person}. The user is trying to guess this person. They will ask you yes or no questions, and you must respond accurately. For context on this person, look at their wikipedia page: {wikipedia_page_url}." \
            "If the question from the user can't be answered with a simple yes or no, respond with 'I can only answer Yes or No questions'. If the user guesses the person, respond with 'Correct!'. If the user gives up, respond with 'Better luck next time!'."
    }
    chat_history.insert(0, system_prompt)
    # chat_history.append({"role": "user", "content": query})
    response_obj = client.chat.completions.create(
                messages=chat_history,
                model="llama3-70b-8192",
            )
    response = response_obj.choices[0].message.content
    # chat_history.append({
    #             "role": "assistant",
    #             "content": response
    #         })
    return response
    
# def main():
#     st.title("20 Questions")
#     print('yo')
    
#     person = get_person()
#     print(f"Person: {person}")
    
#     page = get_wikipedia_page(person)
    
#     if page:
#         print(f"Wikipedia page URL: {page.url}")
#         # conversation_loop(person, page.url)
    
#     first_message = "Hello! Welcome to 20 Questions! You can ask me Yes or No questions, or you can guess the person. Let's get started! Now, who am I thinking of..."
#     first_message_obj = {"role": "assistant", "content": first_message}

#     # Initialize chat history
#     if "messages" not in st.session_state:
#         st.session_state.messages = [first_message_obj]

#     # Display chat messages from history on app rerun
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#     # Accept user input
#     if prompt := st.chat_input(">"):
#         # Add user message to chat history
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         # Display user message in chat message container
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         # Display assistant response in chat message container
#         with st.chat_message("assistant"):
#             chat_history = copy.deepcopy(st.session_state.messages)
#             response = generate_response(prompt, person, page.url, chat_history)
#             # response = st.write_stream(response_generator())
#             st.markdown(response)
#         # Add assistant response to chat history
#         st.session_state.messages.append({"role": "assistant", "content": response})


# if __name__ == "__main__":
#     main()

import streamlit as st
from typing import Generator
from groq import Groq

st.set_page_config(page_icon="💬", layout="wide",
                   page_title="Groq Goes Brrrrrrrr...")


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


icon("🏎️")

st.subheader("Groq Chat Streamlit App", divider="rainbow", anchor=False)

if "person" not in st.session_state:
    st.session_state.person = get_person()

if "page" not in st.session_state:
    st.session_state.page = get_wikipedia_page(st.session_state.person)

first_message = "Hello! Welcome to 20 Questions! You can ask me Yes or No questions, or you can guess the person. Let's get started! Now, who am I thinking of..."
first_message_obj = {"role": "assistant", "content": first_message}

system_prompt = {
    "role": "system",
    "content":
        f"You are a playing 20 questions. You are thinking of this person: {st.session_state.person}. The user is trying to guess this person. They will ask you yes or no questions, and you must respond accurately. For context on this person, look at their wikipedia page: {st.session_state.page.url}." \
        "If the question from the user can't be answered with a simple yes or no, respond with 'I can only answer Yes or No questions'. If the user guesses the person, respond with 'Correct!'. If the user gives up, respond with 'Better luck next time!'."
}

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = [system_prompt, first_message_obj]

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
    st.session_state.messages = [system_prompt, first_message_obj]
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


if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar='👨‍💻'):
        st.markdown(prompt)

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
            max_tokens=max_tokens,
            stream=True
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(e, icon="🚨")

    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})