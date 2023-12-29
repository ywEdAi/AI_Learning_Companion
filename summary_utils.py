import os
import json

from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain import PromptTemplate
import openai
from dotenv import load_dotenv
from openai import OpenAI

openai_api_key =  "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"
os.environ["OPENAI_API_KEY"] = openai_api_key
client = OpenAI()

def getSummary(content):
    if len(content) > 8000:
        long_summary= summarize_long(content)
        return long_summary
    else:  
        short_summary= summarize_short(content)  
        return summarize_short(short_summary)    
    
def getGlossary(content):
    if len(content) > 8000:
        long_summary= glossary_long(content)
        return long_summary
    else:  
        short_summary= glossary_short(content)  
        return summarize_short(short_summary)      

def summarize_long(text):
    chunks = split_string_into_chunks(text, 5000)
    summaries = ""
    for chunk in chunks:
        summary = summarize_short(chunk)
        summaries = summaries + summary

    if len(summaries) > 8000:
        chunks = split_string_into_chunks(text, 2500)
        summaries = ""
        for chunk in chunks:
            summary = summarize_short(chunk)
            summaries = summaries + summary
        return summarize_short(summaries)
    else:
        return summarize_short(summaries)
    

def summarize_short(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": "please extract the key ideas, concepts, frameworks and theories from the text to help a high school student learn systematically"
            },
            {
            "role": "user",
            "content": text
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

def glossary_long(text):
    chunks = split_string_into_chunks(text, 8000)
    glossaries = ""
    for chunk in chunks:
        glossary = glossary_short(chunk)
        glossaries = glossaries + glossary

    return glossaries

def glossary_short(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": "please extract and generate a list of glossaries pertaining to the subject and domains in the content with definiton and explanations,  to help a high school student learn systematically"
            },
            {
            "role": "user",
            "content": text
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

def getTopic(content):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": "Please research the relavent and important information, conepts, framework and methodologies regarding the topic provided, as rich as can generate a mindmap, to help a high school student learn systematically."
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

def getMarkupFromProvidedContent(content):
    if len(content) > 10000:
        content = content[:10000]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": "please extract the key concepts and ideas from the content for the purpose of generating a mindmap to help a high school student learn systematically. PLEASE GENERATE OUTPUT AS MARKUP LANGUAGE."
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


def split_string_into_chunks(text, chunk_size):
    chunks = []
    start = 0
    end = chunk_size

    while start < len(text):
        chunks.append(text[start:end])
        start = end
        end += chunk_size

    return chunks