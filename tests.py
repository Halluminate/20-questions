#! /usr/bin/env python3

import os
import copy
import json
import random
from typing import Generator


from groq import Groq
import wikipedia

with open('prompts.json') as prompts:
    prompts = json.load(prompts)


groq_api_key = os.environ.get("GROQ_API_KEY")

client = Groq(
    api_key=groq_api_key,
)
MODEL = "llama3-70b-8192"

def get_person():
    """Get a person's name from an LLM"""
    chat_completion = client.chat.completions.create(
        messages=[prompts["get_person"]["system"]], 
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
    
def get_wikipedia_content(person):
    try:
        page = wikipedia.page(person)
        return page.content
    except wikipedia.exceptions.DisambiguationError as e:
        return get_wikipedia_content(e.options[0])
    except wikipedia.exceptions.PageError:
        return None
    
person = get_person()
page = get_wikipedia_page(person)
content = get_wikipedia_content(person)
print(f"Person: {person}")
print(f"Page: {page}")
print(f"Content: {content}")
