#! /usr/bin/env python3

import os
import copy
import time

from groq import Groq
import wikipedia

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
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

def get_bot_response(user_query, message_history):
    """Get the bot's response to the user's message"""
    user_query_obj = {"role": "user", "content": user_query}
    message_history.append(user_query_obj)
    copied_message_history = copy.deepcopy(message_history)
    stream = client.chat.completions.create(
        messages=copied_message_history,
        model=MODEL,
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=True,
    )
    return stream, copied_message_history

def main():
    person = get_person()
    print(f"Person: {person}")
    page = get_wikipedia_page(person)
    if page:
        print(page.url)
    else:
        print(f"{person} not found on Wikipedia")
    messages = set_up_bot(person, page)
    print(messages[1]["content"])
    while True:
        user_query = input("User: ")
        bot_stream_response, messages = get_bot_response(user_query, messages)
        bot_full_response = ''
        print("Bot: ", end="")
        for chunk in bot_stream_response:
            content = chunk.choices[0].delta.content
            print(content if content else '', end="")
            bot_full_response += content if content else ''
        print()
        messages.append({"role": "assistant", "content": bot_full_response})


if __name__ == "__main__":
    main()
