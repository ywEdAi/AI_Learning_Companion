import fitz  # Import the fitz library
import os
from openai import OpenAI
import streamlit as st
import time

REFORMAT_TEXT_PROMPT = '''
Follow these instructions to reformat an academic text by removing extraneous elements while preserving the original content and enhancing readability.
Steps:
1. Section Identification: Identify and separate key sections of the text, such as the title, author information, abstract, introduction, main body, and conclusion.
2. Removal of Non-Essential Elements: Carefully remove page headers, footers, and numbers to focus on the primary content.
3. Preservation of Original Content: Maintain the original wording and structure of the academic content to ensure accuracy and integrity.
4. Organization:Arrange the text into clearly defined sections. Ensure logical flow by placing the title, author details, and abstract at the beginning, followed by the main sections and conclusion.
5. Formatting for Clarity:Implement proper paragraphing and spacing between sections. Use clear headings and subheadings to demarcate different parts of the text. Add new line after each section and paragraph. 
6. Consistency Check: Ensure consistent formatting throughout the document, including heading styles and paragraph spacing.
7. Final Review: Conduct a final review to confirm that extraneous elements are removed, essential content is preserved, and the text is presented in a clear, organized, and readable format.
Outcome:A restructured and clean version of the academic text that is easy to read and navigate, with the focus solely on the essential content.
'''

openai_api_key =  "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"
os.environ["OPENAI_API_KEY"] = openai_api_key
client = OpenAI()

def getText(byte_io):
    doc = fitz.open("pdf", byte_io)

    text = ""
    for page in doc:
        text_blocks = page.get_text("blocks")  # Extract text blocks from the page
        text_blocks.sort(key=lambda block: (block[1], block[0]))  # Sort blocks top to bottom, left to right

        for block in text_blocks:
            if block[6] == 0:  # Check if the block is a text block
                text = text + block[4]  # Print the text in the block
    return text


def substring_up_to_last_newline(s, max_length=3000):
    # Limit the string to the maximum length
    limited_string = s[:max_length]

    # Find the index of the last newline character in the limited string
    last_newline_index = limited_string.rfind('\n')
    
    # If a newline character is found, return the substring up to this character
    # If no newline character is found, return the whole limited string
    return limited_string[:last_newline_index] if last_newline_index != -1 else limited_string

def getReformatByOpenAI(content):
    start_time = time.time()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {
            "role": "system",
            "content": REFORMAT_TEXT_PROMPT
            },
            {
            "role": "user",
            "content": content
            }
        ],
        temperature=0,
        max_tokens=3000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    assistant_reply = response.choices[0].message.content.strip()
    end_time = time.time()
    st.write("OpenAI call time:", str(end_time - start_time))
    return assistant_reply

def getChunks(text, max_length=3000):
    chunks = []
    while text:
        substring = substring_up_to_last_newline(text, max_length)
        if not substring:  # Avoids infinite loop in case of no newline in the first chunk
            substring = text[:max_length]
        chunks.append(substring)
        text = text[len(substring):]
    return chunks


def getFormattedPdfContent(byte_io):
    text = getText(byte_io)
    st.write("get texts")
    chunks = getChunks(text, 3000)
    st.write("get chunks")
    st.write("chunk size:", len(chunks))
    result = ""
    a = 0
    if chunks and len(chunks) >0:
        
        for c in chunks:
            while a <3:    
                result = result + getReformatByOpenAI(c)
                a = a+1
    st.write("get OpenAI Results")
    return result
