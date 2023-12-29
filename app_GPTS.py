import base64

import streamlit as st
from streamlit_chat import message
from streamlit_modal import Modal
from streamlit_javascript import st_javascript
from GPTs_Utils_new import *
from streamlit_markmap import markmap
from utils import (
    text_split,
    parse_pdf,
    get_embeddings,
    get_sources,
    get_answer,
    get_condensed_question,
    get_answers_bis,
)

st.set_page_config(page_title="pdf-GPT", page_icon="📖", layout="wide")
st.header("pdf-GPT")

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

st.session_state.useCache = False

def clear_submit():
    st.session_state["submit"] = False


def displayPDF(upl_file, width):
    # Read file as bytes:
    bytes_data = upl_file.getvalue()

    # Convert to utf-8
    base64_pdf = base64.b64encode(bytes_data).decode("utf-8")

    # Embed PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width={str(width)} height={str(width*4/3)} type="application/pdf"></iframe>'

    # Display file
    st.markdown(pdf_display, unsafe_allow_html=True)

def displayPDFpage(upl_file, page_nr):
    # Read file as bytes:
    bytes_data = upl_file.getvalue()

    # Convert to utf-8
    base64_pdf = base64.b64encode(bytes_data).decode("utf-8")

    # Embed PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={page_nr}" width="700" height="1000" type="application/pdf"></iframe>'

    # Display file
    st.markdown(pdf_display, unsafe_allow_html=True)

with st.sidebar:

    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf"],
        help="Only PDF files are supported",
        on_change=clear_submit,
    )


col1, col2 = st.columns(spec=[1, 1], gap="small")

mindmap = '''
# Economics
## Microeconomics
- Study of individual agents
  - Consumers
  - Firms
- Market structures
  - Perfect competition
  - Monopoly
  - Oligopoly
- Supply and Demand
  - Price determination
  - Market equilibrium
## Macroeconomics
- Study of the economy as a whole
  - National income
  - Inflation
  - Unemployment
- Economic policies
  - Fiscal policy
  - Monetary policy
## Economic Theories
- Classical
- Keynesian
- Neoclassical
## Important Concepts
- Opportunity Cost
- Elasticity
- Comparative Advantage
- Economic Growth
## Branches of Economics
- Behavioral Economics
- Development Economics
- International Economics

'''

if uploaded_file:
    with col1:
        ui_width = st_javascript("window.innerWidth")
        displayPDF(uploaded_file, ui_width -10)

    with col2:
        Domain, Material = st.tabs([ "About the Domain", "About the Uploaded File"])
        assistant, file, thread = initAssistantWithFileUploads(uploaded_file)
        with Domain:
            domain,domain_structure_in_html, domain_mindmap = getDomainSummary(assistant,file,thread)
            st.write ("The uploaded material is about this Domain:", domain)
            components.html(domain_structure_in_html,
                    scrolling = True,
                    height = 500)
            
            modal = Modal(
                "Mindmap for " + str(domain), 
                key="mindmap" + str(domain),
                
                # Optional
                padding=10,    # default value
                max_width=800  # default value
            )
            domain_open_modal = st.button("Open Domain Mindmap")
            if domain_open_modal:
                modal.open()

            if modal.is_open():
                with modal.container():
                    markmap(domain_mindmap)
        with Material:
            material_structure_in_html, material_mindmap = getMaterialSummary(assistant, file,thread)
            components.html(material_structure_in_html,
                    scrolling = True,
                    height = 500)
            modal = Modal(
                "Mindmap for uploaded file", 
                key="demo-modal",
                
                # Optional
                padding=10,    # default value
                max_width=800  # default value
            )
            material_open_modal = st.button("Open Mindmap for the file")
            if material_open_modal:
                modal.open()

            if modal.is_open():
                with modal.container():
                    markmap(material_mindmap)
