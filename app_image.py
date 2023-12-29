import pandas as pd
import numpy as np
import streamlit as st
import easyocr
from PIL import Image, ImageDraw
from image_utils import *
from GPTs_Utils_new import *

# main title
st.title("Mistake Review") 
# subtitle
# st.markdown("## EasyOCR with Streamlit")

# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "file_exist" not in st.session_state:
    st.session_state.file_exist = False
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []

def clear():
    st.session_state.file_exist = False

    
def displayAndReview(file):
    col1, col2 = st.columns([4,6],gap="medium")
    with col1:
        image = Image.open(file) # read image with PIL library
        # st.image(image) #display

        # Initialize the OCR reader
        reader = easyocr.Reader(['en'], gpu=False) 
        result = reader.readtext(np.array(image))  # turn image to numpy array

        #get raw text
        text = ""
        for idx in range(len(result)): 
            text = text+ " " + result[idx][1] 
        
        st.markdown("Exercise")
        st.write(text)
        # formatted_text = getSortedText(text)
        # st.write(formatted_text)
        # getOptionList(formatted_text)
        st.divider()
        correctAnswer = st.selectbox(
            "The correct answer is",
            ("A", "B", "C", "D","I don't know"))
        chosenAnswer = st.selectbox(
            "Your choice was",
            ("A", "B", "C", "D"))


        

    with col2:
        st.markdown("Reflection Table")


        st.write("This is the place where you reflect on:")
        st.write("a. the root cause of the wrong answer")
        st.write("b. the logic chain of your decision-making process")
        st.write("c. how to avoid making the same mistake")
        st.write("d. indicator of possible similar traps")
        st.write("and more")

        reflection = st.text_area(
            "start here",
            height = 200
        )
       
        save = {}
        if st.button("Save and get Reflection Tips"):
            

            save["text"] = text
            save["correct_answer"] = correctAnswer
            save["chosen_answer"] = chosenAnswer
            save["reflection"] = reflection
            
            st.write(f'You wrote a great review with {len(reflection)} characters.')
            tips = getReflectionTips(str(save))
            st.markdown("Tips:")
            st.write(tips)
            save["tips"] = tips
        st.divider()

        st.session_state["stored_session"].append(save)
        

# Set up sidebar with various options
with st.sidebar.expander("📁 Image Upload", expanded=False):
# upload image file
    file = st.file_uploader(label = "Upload your image", type=['png', 'jpg', 'jpeg'])
    if st.button("Start"):
        st.session_state.file_exist = True

st.sidebar.button("New Task", on_click = clear, type="primary")



# Check if a file is uploaded
if st.session_state.file_exist:
    displayAndReview(file)

else:
    st.write("Please upload an image file.")

# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
        with st.sidebar.expander(label= f"Previous-Reviews:{i}"):
            st.write(sublist)