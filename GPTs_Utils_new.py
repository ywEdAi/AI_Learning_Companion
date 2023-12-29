from openai import OpenAI
import time
import streamlit as st
import re
import streamlit.components.v1 as components

OPENAI_API_KEY =  "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"
# domainExpert_assistant_id = 'asst_aSStWUzMCalIH1xIIBBtuNDF'

if 'domain_structure' not in st.session_state:
    st.session_state.domain_structure = ""

if 'domain' not in st.session_state:
    st.session_state.domain = ""    

if 'material_structure' not in st.session_state:
    st.session_state.material_structure = ""



DOMAIN_CONFIGURATION = '''
You are an experienced pedagogy practitioner, instructional design and teacher. Students seek your help to understand advanced materials, concept, knowledge and theories that are usually  beyond their current educated levels. Your need to understand the materials and students' needs, extract the key concept and frameworks from the learning materials, and tailor it to the current student's level.  You will provide the theme/scope, fundamental knowledge, knowledge structure and learning path. 

You will read carefully of the PDF file uploaded. It might be a course lecture, a reading material such as academic paper, or a book. As a responsible teacher, you will become a domain expert by mastering the contents fast and effectively before you explain to your students or answer their questions. Below is your analysis process:
1.  You need to get the main theme, scope and structure of the materials
2. based on the main theme, you will form your own structure of key concepts, theories, frameworks, and applications that can best be understood by the student. If needed, you can do internet research to get relevant ideas, examples or illustrations. When you form a domain knowledge base on the materials provided, this knowledge base needs to be comprehensive and accurate. You CANNOT create new things or make a guess. It MUST be justified true knowledge of the subject. 

In terms of output:
2 .For each sub section, in the knowledge structure/map, You need to edit and format it in a way that is digestible but still clear and accurate. 
3. For each sub section, in the knowledge structure/map, you should try your best to connect the domain, student's level and the contents from the uploaded material, make association, comparisons and contrast.  THIS IS VERY IMPORTANT. 
4. All your explanation regarding key concepts and theories need to involve scaffolding techniques to allow students reflect and engage.

Attention!!! When you get the uploaded documents, do not return the document key concepts first. First you need to give an overview of the document. Then you need to give an overview of the bigger domain as a context to the students. Do NOT just focus on the material. Then you need to blend and connect the material information with the domain information and student's learning profiles. 

All outputs are listed in bullet and sub-bullets and even multiple hierarchies if necessary.
'''

DOMAIN_STRUCTURE_PROMPT= ''', give me an overview of the subject discipline (NOT limited to the contents in the provided material), including key persons, key theory and concepts, application, the relationship between the key ideas and concepts, applications. It should be like a crash course, or intro-level course.  Just like a Wikipedia but presented in a curriculum for students. 
1. Your should include at least 3 different theories if there are and key concepts in each theory.  5 different fundamental concepts or constructs for the discipline. Each with elaborations and examples for easy understanding.  
2. In you want to include activities, please focus on specific learning activities or suggestions to how to effectively learn the concept with actionable examples. 
4. For each key concepts and theories, please elaborate with 2-3 sentences. Provide examples if necessary
5. do NOT include source
6. Your output should always be in bullet point in digits, NO - or dot. For EVERY sub-bullet, it should start with digits as indicators of hierarchy, such as  1.1, or 1.2.1. 
7. Your output will be displayed as knowledge structure on websites for students to refer
8. No pre or post wording. Directly return the name of the domain in triple brackets, without html.  Then return the bulleted summary in HTML collapsiblesMake sure every single sub bullet are formatted using the <details> and <summary>, <list> tags in HTML to create sections that users can click to expand or collapse).
'''

MATERIAL_STRUCTURE_PROMPT= '''
, give me an overview of the contents in the provided material from the uploaded PDF, including key persons, key theory and concepts, application, the relationship between the key ideas and concepts, etc. It should be like a crash course, or intro-level course.  Just like a Wikipedia but presented in a curriculum for students. 
1. Your should organize the contents using bullet points. Each with elaborations and examples for easy understanding.Provide examples if necessary
2. do NOT include source
3. Your output should always be in bullet point in digits, NO - or dot. For EVERY sub-bullet, it should start with digits as indicators of hierarchy, such as  1.1, or 1.2.1. 
4. Your output will be displayed as knowledge structure on websites for students to refer
5. No pre or post wording. ONLY return the bulleted knowledge structure in HTML collapsibles. Make sure every single sub bullet are formatted using the <details> and <summary>, <list> tags in HTML to create sections that users can click to expand or collapse).

'''

COMPARISON_PROMPT= '''
Identify any gaps in the lecture content relative to the domain and suggest additional topics or areas that need to be included for learners to fully grasp the key concepts and theories. Present your findings in a structured format that clearly outlines these alignments, gaps, and suggestions.
'''

MINDMAP_PROMPT= '''
based on the domain discipline and the knowledge structure provided below, generate a mindmap using markmap syntax.
'''

client = OpenAI(api_key=OPENAI_API_KEY)


def initAssistantWithFileUploads(PDF):
    file = client.files.create(
        file = PDF,
        # file = open("/Users/yiwang/Documents/ChatYoutube/AI_Learning_Companion_2/data/angeli-valanides-2013-technology-mapping-an-approach-for-developing-technological-pedagogical-content-knowledge.pdf", "rb"),
        purpose='assistants'
    )

    assistant = client.beta.assistants.create(
        name="DomainExpert",
        instructions=DOMAIN_CONFIGURATION,
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview"
    )
    thread = client.beta.threads.create()

    return assistant, file, thread

def getDomainSummary(assistant, file, thread):

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content='''Based on the pdf file uploaded with id =''' + file.id + DOMAIN_STRUCTURE_PROMPT,
        file_ids=[file.id]
    )
    run = client.beta.threads.runs.create(
        assistant_id=assistant.id,
        thread_id=thread.id
    )

    start_time = time.time()
    while run.status!= "completed":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status in ["failed", "cancelled", "expired", "requires_action"]:
            print(f"run failed: {run.last_error}")
            break

    end_time = time.time()

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    result =  messages.data[0].content[0].text.value
    domain_name = extract_triple_brackets(result)
    html = remove_triple_brackets(result)


    if "1" in html and "2" in html and "<details>" in html:
        st.session_state.domain_structure = html
    if "cannot" in html and "file" in html:
        return "problem!!!"

    mindmap = getMindMap(html)
    return domain_name, str(html).replace("```html", "").replace("```", ""), mindmap

def getMaterialSummary(assistant, file, thread):

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content='''Based on the pdf file uploaded with id =''' + file.id + MATERIAL_STRUCTURE_PROMPT,
        file_ids=[file.id]
    )
    run = client.beta.threads.runs.create(
        assistant_id=assistant.id,
        thread_id=thread.id
    )

    start_time = time.time()
    while run.status!= "completed":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status in ["failed", "cancelled", "expired", "requires_action"]:
            print(f"run failed: {run.last_error}")
            break

    end_time = time.time()

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    result =  messages.data[0].content[0].text.value

    if "1" in result and "2" in result:
        st.session_state.material_structure = result
    if "cannot" in result and "file" in result:
        return "problem!!!"
    
    mindmap = getMindMap(result)

    return str(result).replace("```html", "").replace("```", ""),mindmap

def getMindMap(content):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": "based on the domain discipline and the knowledge structure provided below, generate a mindmap using markmap syntax. "
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


def getReflectionTips(content):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": "please review the SAT exercise with students answers and reflections on why they made a mistake. Please extract and summarize, and give specific recommendation and todos."
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


def extract_triple_brackets(text):
    pattern = r"\{{3}(.*?)\}{3}"
    matches = re.findall(pattern, text)
    return matches

def remove_triple_brackets(text):
    pattern = r"\{{3}.*?\}{3}"
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text