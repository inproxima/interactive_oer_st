import openai
import streamlit as st
import streamlit_ext as ste
from streamlit_chat import message
import os 
import json

#page setting
st.set_page_config(page_title="AI Rubric Generator", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
"""
#st.markdown(hide_st_style, unsafe_allow_html=True)


#Functions
def generate_response(prompt, input, conversation, user_input):
    completion=openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    message=completion.choices[0].text
    return message

def get_text(prompt, conversations):
    completion=openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=3000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    text=completion.choices[0].text
    return text

#API and Topic session states
if 'api' not in st.session_state:
    st.session_state.api = []
if 'input' not in st.session_state:
    st.session_state.input = ""

#page design and input
st.title("OER Development Bot")
st.markdown("""___""")
st.subheader("Step 1:")
st.subheader("Please input the following information:")
url = "https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key"
api = st.text_input("If you don't know your OpenAI API key click [here](%s)." % url, type="password", placeholder="Your API Key")
topic = st.text_input("What topic would you like to discuss with the Chatbot?")

#check API
if st.button(label='Submit'):
    st.session_state.api = api
    st.session_state.input = topic 

    try:
    # Send a test request to the OpenAI API
        openai.api_key = api
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="What is the capital of France?",
            temperature=0.5
    )
        st.markdown("""___""")
        st.success("The API key is valid. You Can now start chatting about " + topic)
        
    except Exception as e:
        st.error("API key is invalid: {}".format(e))

#chatbot
st.markdown("""___""")
st.subheader("Step 2:")
st.subheader("Start chatting with the bot by asking a question related to your topic.")
if 'generated' not in st.session_state:
            st.session_state['generated'] = []
if 'past' not in st.session_state:
            st.session_state['past'] = []
    #variables 
user_input=st.text_input("You:", key='input')
conversations = []
if st.button("Send"):
    with st.spinner("By code and algorithm, hear my call, let this AI speak with rhyme for all :magic_wand:"):
        prompt = (f'You are a kind, caring and curious AI tutor bot. You are teaching {topic}. Drawing from {conversations}, respond to the following: {user_input}')
        output=generate_response(prompt, conversations, topic, user_input)
        #store the output
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        conversations = [(st.session_state['past'][i], st.session_state["generated"][i]) for i in range(len(st.session_state['generated']))]
if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
st.markdown("""___""")
conversations = json.dumps(conversations, indent=4, separators=(',', ': '))
conversations = conversations.replace("\\n", "")
conversations = conversations.replace("[", "")
conversations = conversations.replace("]", "")
ste.download_button("Download Chat", conversations, 'chat.txt')
# Make OER resource
# st.write(conversations)
st.subheader("Step 3:")
st.subheader("When you are ready to write your article, click on the 'Make OER' button.")
if st.button("Make OER"):
    st.markdown("""___""")
    with st.spinner("AI, hear my incantation, write with rhyme and variation :magic_wand:"):
        conversations = [(st.session_state['past'][i], st.session_state["generated"][i]) for i in range(len(st.session_state['generated']))]
        prompt_title = (f'write a title for the following text: {conversations}')
        prompt_text = (f'The following TEXT is a conversation between a human and a bot. Converst the text in to an academic article. TEXT: {conversations}')
        title = get_text(prompt_title, conversations)
        st.title(title)
        academic_text = get_text(prompt_text, conversations)
        st.write(academic_text)
        #prepare for download
        article = title + "\n" + academic_text
        ste.download_button("Download Article", article, "article.txt")
        