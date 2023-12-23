import streamlit as st
import streamlit.components.v1 as components
from helpers.youtube_utils import *
from helpers.openai_utils import *
from helpers.quiz_utils import *
from helpers.toast_messages import *
from helpers.web_search_utils import *
from helpers.summary_utils import *
import pytube
import openai
import os
from PyPDF2 import PdfReader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.llms import AzureOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from langchain.vectorstores import Chroma
import pinecone
from langchain.vectorstores import Chroma, Pinecone
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from streamlit_markmap import markmap
from streamlit_option_menu import option_menu

OPENAI_API_KEY =  "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"
st.set_page_config(layout="wide")

if 'file_status' not in st.session_state:
    st.session_state.file_status = False

if 'youtube_status' not in st.session_state:
    st.session_state.youtube_status = False

if 'website_status' not in st.session_state:
    st.session_state.website_status = False

if 'textupload_status' not in st.session_state:
    st.session_state.textupload_status = False

if 'file_content' not in st.session_state:
    st.session_state.file_content = ""

if 'youtube_content' not in st.session_state:
    st.session_state.youtube_content = ""

if 'website_content' not in st.session_state:
    st.session_state.website_content = ""

if 'textupload_content' not in st.session_state:
    st.session_state.textupload_content = ""

if 'summary' not in st.session_state:
    st.session_state.summary = ""

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask AI tutor a question about the subject!"}
    ]



data, chatbot = st.columns([5,3])

#"Resource Portal" and "Learning Commons"
with data:
    selected = option_menu(
            menu_title=None,
            options=["Resource Portal", "Learning Commons"],
            icons = ["books", "study"],
            menu_icon="cast",
            orientation = "horizontal"
    )
    if selected == "Resource Portal":
        tab_file, tab_youtube, tab_url, tab_text = st.tabs(["From a File", "From Youtube", "From a website", "From Your Own Text"])

        with tab_file:
            pdf_docs = st.file_uploader(
            "Upload one PDF at a time", accept_multiple_files=False)
            if st.button("Ready to learn!"):
                with st.spinner("Processing"):
                    # Extract text from the uploaded PDF file.
                    pdf_reader = PdfReader(pdf_docs)
                    raw_text = ""
                    for page in pdf_reader.pages:
                        raw_text += page.extract_text()
                    st.session_state.file_content = raw_text
                    st.write("Extracted file data, length:" + str(len(raw_text)))
                    
                    st.session_state.file_status = True
                    st.session_state.youtube_status = False
                    st.session_state.website_status = False
                    st.session_state.textupload_status = False
                    st.write("File content ready to go, click /'Learning Common/' to learn more!")
        with tab_youtube:
            with st.form("youtube_url"):
                YOUTUBE_URL = st.text_input("Enter the YouTube videos link:", value="https://www.youtube.com/watch?v=VpX6ts5Z2cU")
                # YOUTUBUE_PROMPT =st.text_input("Additional prompts for better processing:", value="summarize the key framework from the video")
                submitted = st.form_submit_button("Ready to learn!")
            if submitted:
                    video_id = extract_video_id_from_url(YOUTUBE_URL)
                    video_transcription = get_transcript_text(video_id)
                    st.session_state.youtube_content = video_transcription 
                    st.session_state.file_status = False
                    st.session_state.youtube_status = True
                    st.session_state.website_status = False
                    st.session_state.textupload_status = False
                    st.write("Extracted video transcript, click /'Learning Common/' to learn more!")
        with tab_url:
            with st.form("website_url"):
                WEB_URL = st.text_input("Enter the website link:", value="https://joyfulmicrobe.com/biodegradation-natures-recycling-system/")
                # WEB_PROMPT =st.text_input("Additional prompts for better processing:", value="summarize the key structure from the website")
                submitted = st.form_submit_button("Ready to learn!")
            if submitted:
                webcontent = scrape(WEB_URL)
                st.session_state.website_content = webcontent 
                st.session_state.file_status = False
                st.session_state.youtube_status = False
                st.session_state.website_status = True
                st.session_state.textupload_status = False
                st.write("Extracted website information, click /'Learning Common/' to learn more!")
        with tab_text:
            with st.form("user_input"):
                TEXT = st.text_area("Enter the website link:", value="https://en.wikipedia.org/wiki/ChatGPT")
                # TEXT_PROMPT =st.text_input("Additional prompts for better processing:", value="summarize the key structure from the website")
                submitted = st.form_submit_button("Ready to learn!")
            if submitted:
                st.session_state.textupload_content = TEXT 
                st.session_state.file_status = False
                st.session_state.youtube_status = False
                st.session_state.website_status = False
                st.session_state.textupload_status = True


    if selected == "Learning Commons":
        raw, summary, glossary, quiz, mindmap = st.tabs([ "Raw Data", "Summary", "Glossary", "Quiz", "Mindmap"])

        with raw:
            if (st.session_state.file_status == False and st.session_state.website_status == False and st.session_state.youtube_status == False and st.session_state.textupload_status == False):
                st.write("The raw data will be displayed here if data task is provided")
            raw_data = ""
            if st.session_state.file_status:
                content = st.session_state.file_content
                st.write(content)
            if st.session_state.website_status:
                content = st.session_state.website_content
                st.write(content)
            if st.session_state.youtube_status: 
                content = st.session_state.youtube_content
                st.write(content)
            if st.session_state.textupload_status:
                content = st.session_state.textupload_content 
                st.write(content)
        with summary:
            content = ""
            if st.session_state.file_status:
                content = st.session_state.file_content
            if st.session_state.website_status:
                content = st.session_state.website_content
            if st.session_state.youtube_status:
                content = st.session_state.youtube_content
            if st.session_state.textupload_status:
                content = st.session_state.textupload_content                

            if len(content) > 0:
                with st.spinner("Generating Summary...🤓"):
                    summary = getSummary(content)
                    st.session_state.summary = summary
                    st.write(summary)
        with glossary:
            content = ""
            if st.session_state.file_status:
                content = st.session_state.file_content
            if st.session_state.website_status:
                content = st.session_state.website_content
            if st.session_state.youtube_status:
                content = st.session_state.youtube_content
            if st.session_state.textupload_status:
                content = st.session_state.textupload_content                

            if len(content) > 0:
                with st.spinner("Generating Glossary...🤓"):
                    glossary = getGlossary(content)
                    st.write(glossary)

                                
        with quiz:
            st.write("this is quiz")  
            content = ""
            if st.session_state.file_status:
                content = st.session_state.file_content
            if st.session_state.website_status:
                content = st.session_state.website_content
            if st.session_state.youtube_status:
                content = st.session_state.youtube_content
            if st.session_state.textupload_status:
                content = st.session_state.textupload_content  
            if len(content) > 0:
                with st.spinner("Crafting your quiz...🤓"):  
                    quiz_data_str = get_quiz_data(content[:10000], OPENAI_API_KEY)
                    st.session_state.quiz_data_list = string_to_list(quiz_data_str)

                    if 'user_answers' not in st.session_state:
                        st.session_state.user_answers = [None for _ in st.session_state.quiz_data_list]
                    if 'correct_answers' not in st.session_state:
                        st.session_state.correct_answers = []
                    if 'randomized_options' not in st.session_state:
                        st.session_state.randomized_options = []

                    for q in st.session_state.quiz_data_list:
                        options, correct_answer = get_randomized_options(q[1:])
                        st.session_state.randomized_options.append(options)
                        st.session_state.correct_answers.append(correct_answer)
                    with st.form(key='quiz_form'):
                        st.subheader("🧠 Quiz Time: Test Your Knowledge!", anchor=False)
                        for i, q in enumerate(st.session_state.quiz_data_list):
                            options = st.session_state.randomized_options[i]
                            default_index = st.session_state.user_answers[i] if st.session_state.user_answers[i] is not None else 0
                            response = st.radio(q[0], options, index=default_index)
                            user_choice_index = options.index(response)
                            st.session_state.user_answers[i] = user_choice_index  # Update the stored answer right after fetching it


                        results_submitted = st.form_submit_button(label='Unveil My Score!')

                        if results_submitted:
                            score = sum([ua == st.session_state.randomized_options[i].index(ca) for i, (ua, ca) in enumerate(zip(st.session_state.user_answers, st.session_state.correct_answers))])
                            st.success(f"Your score: {score}/{len(st.session_state.quiz_data_list)}")

                            if score == len(st.session_state.quiz_data_list):  # Check if all answers are correct
                                st.balloons()
                            else:
                                incorrect_count = len(st.session_state.quiz_data_list) - score
                                if incorrect_count == 1:
                                    st.warning(f"Almost perfect! You got 1 question wrong. Let's review it:")
                                else:
                                    st.warning(f"Almost there! You got {incorrect_count} questions wrong. Let's review them:")

                            for i, (ua, ca, q, ro) in enumerate(zip(st.session_state.user_answers, st.session_state.correct_answers, st.session_state.quiz_data_list, st.session_state.randomized_options)):
                                with st.expander(f"Question {i + 1}", expanded=False):
                                    if ro[ua] != ca:
                                        st.info(f"Question: {q[0]}")
                                        st.error(f"Your answer: {ro[ua]}")
                                        st.success(f"Correct answer: {ca}")    

        with mindmap:
            st.write("this is mindmap")
            content = ""
            if st.session_state.file_status:
                content = st.session_state.file_content
                st.write("file_status")
            if st.session_state.website_status:
                content = st.session_state.website_content
                st.write("website_content")
            if st.session_state.youtube_status:
                content = st.session_state.youtube_content
                st.write("youtube_content")
            if st.session_state.textupload_status:
                content = st.session_state.textupload_content 
                st.write("textupload_status")
            if st.session_state.summary: 
                content = st.session_state.summary
                st.write("summary")
            
            # st.write(content)
            if len(content) > 0:
                with st.spinner("Generating mind map...🤓"):  
                    markup = getMarkupFromProvidedContent(content)
                    markmap(markup, height=400)

with chatbot:
    st.header("Interact with the learning materials with Ari, AI Tutor, anytime")
    components.html(
        """
<div class="askai-frame-embed" data-id="fbH3gNEqs5Ihf6MQpFGmPbt9ga1Iny"></div>
<script defer type="text/javascript" src="https://myaskai.com/embed-js-min"></script>
        """,
        scrolling = True,
        height = 400
    )
