import base64
import io
import streamlit as st
from streamlit_chat import message
from streamlit_modal import Modal
from streamlit_javascript import st_javascript
from GPTs_Utils_new import *
from streamlit_markmap import markmap
from streamlit_annotation_tools import text_highlighter, text_labeler
from pdf_extract_utils import *

from utils import (
    text_split,
    parse_pdf,
    get_embeddings,
    get_sources,
    get_answer,
    get_condensed_question,
    get_answers_bis,
)

st.set_page_config(page_title="AI Learning Buddy", page_icon="📖", layout="wide")

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

title='''
Title: Technology Mapping: An Approach for Developing Technological Pedagogical Content Knowledge 

'''

authors = '''
Authors: Charoula Angeli, Nicos Valanides
Institution: University of Cyprus

'''

abstract = '''
Abstract:
Technology mapping is proposed as an approach for developing technological pedagogical content knowledge (TPCK). This study discusses instructional design guidelines in relation to the enactment of TM and reports on empirical findings from a study with 72 pre-service primary teachers, focusing on teaching them how to teach with Excel. Repeated Measures MANOVA findings indicated that TM was effective and efficient in developing TPCK competencies; however, the development of TPCK competencies was directly related to the complexity of the design task, as determined by the educational affordances of Excel.

'''

introduction = '''
Introduction:
Technological Pedagogical Content Knowledge (TPCK) was introduced to the educational research community as a framework for what teachers need to know to teach with technology. The framework has been embraced and extensively researched. However, unresolved issues remain, justifying the need for further research to advance the theoretical conceptualization of TPCK and methods for its development and assessment. This study adopts a specific theoretical stance on TPCK and discusses technology mapping as a method for its development.

'''

part1 = '''
Current Theoretical Conceptions of TPCK:
In literature, two dominant theoretical models exist regarding the conceptualization of TPCK - the integrative model and the transformative model.

The integrative model, proposed by Koehler and Mishra, views TPCK as an integrative body of knowledge defined by the intersections between content, pedagogy, and technology. The transformative model, proposed by Angeli and Valanides, conceptualizes TPCK as a unique body of knowledge, considering content, pedagogy, learners, technology, and context as significant contributors to the development of TPCK. Both models extend Shulman’s concept of pedagogical content knowledge (PCK).

'''
methodology ='''
Methodology:
Participants in this study were 72 junior students from a teacher education department, enrolled in an instructional technology course focusing on designing and developing learning activities with Excel for young learners. The course duration was 13 weeks, with each section meeting once a week for 2.5 hours. The course's challenge encompassed teaching the technical functions of Excel, its educational affordances, and designing technology-enhanced learning activities with Excel.

'''

results = '''
Results:
Students' TPCK was assessed based on their performance on five design tasks, each representing one of the five educational affordances of Excel discussed during the semester. The performance on the first design task was consistently high across all TPCK competencies. However, performance decreased progressively with the complexity of the tasks, indicating that students found it more challenging to use Excel for more complex tasks like modeling phenomena.

'''

discussion = '''
Discussion:
Teaching how to teach with technology, as exemplified by the Technology Mapping approach, requires integrating knowledge about tool affordances, content, pedagogy, and learners in a real and authentic design task setting. This study demonstrates that TPCK can be effectively developed in such learning environments.

'''

conclusions = '''
Concluding Remarks:
This study contributes both theoretically and practically to the field of educational technology. Theoretically, it validates the effectiveness of the Technology Mapping approach in developing TPCK as a unique body of knowledge. Practically, it provides step-by-step instructional design guidelines for teaching with tools like Excel. The study’s findings can serve as baseline data for future research aimed at further validating or modifying the Technology Mapping methodology.


'''

references = '''
References:
(References are listed, ranging from work by Abbitt, J. in 2011 to Yoon, F. S., Ho, J., & Hedberg, J. G. in 2005. For brevity, the full list of references is not included here.)

'''

contact = '''
Contact:
Dr. Charoula Angeli
11-13 Dramas St., Dept. of Education, University of Cyprus, Nicosia 1678, Cyprus
Email: cangeli@ucy.ac.cy

'''

if not uploaded_file:
    with col1:
        # st.title("Pdf Content Below")
        # if uploaded_file is not None:
        #     bytes_data = io.BytesIO(uploaded_file.getvalue())
        #     st.write("get file")
        #     text = getFormattedPdfContent(bytes_data)
        labels = {}
        outputs_title = text_labeler(title, labels, in_snake_case=False)
        outputs_title = text_labeler(authors, labels, in_snake_case=False)
        outputs_title = text_labeler(abstract, labels, in_snake_case=False)
        outputs_title = text_labeler(introduction, labels, in_snake_case=False)
        outputs_title = text_labeler(part1, labels, in_snake_case=False)
        outputs_title = text_labeler(methodology, labels, in_snake_case=False)    
        outputs_title = text_labeler(results, labels, in_snake_case=False)
        outputs_title = text_labeler(discussion, labels, in_snake_case=False)
        outputs_title = text_labeler(conclusions, labels, in_snake_case=False)


    with col2:
        markmap(mindmap, height = 200)
        st.divider()
        st.write(outputs_title)

