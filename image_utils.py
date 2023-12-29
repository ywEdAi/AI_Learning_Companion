from openai import OpenAI
import time
import streamlit as st
import re

OPENAI_API_KEY =  "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"

client = OpenAI(api_key=OPENAI_API_KEY)

def getSortedText(content):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": "Format the oct-extracted text from an academic test below. Keep the original text and just reformat the content, prompt and options. Just return the formated text without pre and post wording "
            },
            {
            "role": "user",
            "content": content
            }
        ],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    assistant_reply = response.choices[0].message.content.strip()

    return assistant_reply   

def getOptionList(text):
    # Find the content starting with A)
    pattern = r'^A\)(.*?)B\)'
    match = re.search(pattern, text, re.DOTALL)
    st.write(text.split(" A)")[0])

    options = text.split(" A)")[1]
    option_list = re.split(r'\s*[A-D]\)', options)
    st.write(option_list)
            # st.write(options[0])
            # st.write(options[1])
            # st.write(options[2])
            # st.write(options[3])

