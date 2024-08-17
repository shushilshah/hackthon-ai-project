import streamlit as st
from streamlit_quill import st_quill
import requests
from spellchecker import SpellChecker

# Turboline API details
turboline_api_key = '7a202888c4b845b9b7c2a0a09e8850a7'
turboline_url = 'https://api.turboline.ai/openai/chat/completions'

# Initialize SpellChecker
spell = SpellChecker()


# Function to call Turboline API for text summarization


def summarize_text(content, model="gpt-4o-mini"):
    headers = {
        'X-TL-Key': turboline_api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'model': model,
        "messages": [
            {
                "role": "user",
                "content": f"Summarize the following text within 150 characters:\n\n{content}"
            }
        ],
        'max_tokens': 150
    }
    response = requests.post(
        turboline_url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        summary = response_data.get('choices', [])[0].get(
            'message', {}).get('content', '').strip()
        return summary
    else:
        st.error(
            f"An error occurred: {response.status_code} - {response.text}")
        return "Error in summarization"

# API implementation for language translations


def lang_translate(content, model='gpt-4o-mini'):
    headers = {
        'X-TL-Key': turboline_api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'model': model,
        "messages": [
            {
                'role': 'user',
                'content': f"Translate the following text into Nepali language:\n\n{content}"
            }
        ]
    }

    response_trans = requests.post(
        turboline_url, headers=headers, json=data)

    if response_trans.status_code == 200:
        response_trans_data = response_trans.json()
        translation = response_trans_data.get('choices', [])[0].get(
            'message', {}).get('content', '').strip()
        return translation
    else:
        st.error(
            f"An error occured: {response_trans.status_code} - {response_trans.text}")
        return "Error in translation"


# Fact checking implementation with Turboline api

def fact_check(content, model="gpt-4o-mini"):
    headers = {
        'X-TL-Key': turboline_api_key,
        'Content-Type': 'application/json'
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assitant that fact-checks statement"
            },
            {
                "role": "user",
                "content": f"fact check the following statement: \'{content}' and explain if it is true or false."
            }
        ]
    }

    response = requests.post(turboline_url, headers=headers, json=data)

    # check for succesful response
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    else:
        return f"Error: {response.status_code} - {response.text}"


# Function to check spelling of the text


def check_spelling(text):
    misspelled = spell.unknown(text.split())
    corrections = {word: spell.correction(word) for word in misspelled}
    return corrections


# Streamlit UI setup

st.set_page_config(layout="wide")
st.title("Content Creation Collaboration")

# Create a Quill editor in the Streamlit app
editor_content = st_quill()


button_col1, button_col2, button_col3 = st.columns(3)

# Button to summarize the content

with button_col1:
    if st.button("Summarize Text"):
        if editor_content:
            summary = summarize_text(editor_content)
            st.subheader("Summary")
            st.write(summary)
        else:
            st.error("Please enter some content to summarize.")


# Button to check spelling of the content
# if st.button("Check Spelling"):
#     if editor_content:
#         corrections = check_spelling(editor_content)
#         if corrections:
#             st.subheader("Spelling Corrections")
#             for word, correction in corrections.items():
#                 st.write(f"{word} -> {correction}")
#         else:
#             st.write("No spelling mistakes found.")
#     else:
#         st.error("Please enter some content to check spelling.")


with button_col2:
    if st.button("Translate"):
        if editor_content:
            translated = lang_translate(editor_content)
            st.subheader("Translation")
            st.write(translated)
        else:
            st.error("Not tranlated")


with button_col3:
    if st.button("Fact Check"):
        if editor_content:
            check = fact_check(editor_content)
            st.subheader("Actual Fact")
            st.write(check)
        else:
            st.error("Error in something")
