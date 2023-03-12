import openai
import streamlit as st
import streamlit_ext as ste
from streamlit_chat import message


#page setting
st.set_page_config(page_title="AI Open Education ", page_icon="🤖", initial_sidebar_state="expanded")

hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

message_log = [
                {"role": "system", "content": "You are an open education development bot. You respond to queries as best as you can."}, 
                {"role": "user", "content": "Please help me develop educational content."}
                 ]

st.sidebar.header("About")
st.sidebar.markdown(
    """
This application was created by [Soroush Sabbaghan](mailto:ssabbagh@ucalgary.ca) using [Streamlit](https://streamlit.io/), [streamlit-chat](https://pypi.org/project/streamlit-chat/) and [OpenAI API](https://openai.com/api/)'s 
the most updated model [gpt-3.5-turbo](https://platform.openai.com/docs/models/overview) for educational purposes. 
"""
)


st.sidebar.header("Copyright")
st.sidebar.markdown(
    """
- This work is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/)
- [This application is open source](https://github.com/inproxima/interactive_oer_st)
"""
)

st.sidebar.header("Change Log")
st.sidebar.markdown(
    """
- Current OER AI Development Bot 2.0 powered by OpenAI (ChatGPT) gpt-3.5-turbo model
- OER AI Development Bot 1.0 powered by OpenAI text-davinci-003 model
"""
)


#Functions
def generate_response(prompt, temprature, max_tokens):
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message_log,
            temperature=temprature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    messages=response['choices'][0]['message']['content']
    return messages

def get_text(context, conversations):
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=context,
            temperature=0.0,
            max_tokens=700,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    return response.choices[0].message.content

#API and Topic session states
if 'api' not in st.session_state:
    st.session_state.api = []
if 'input' not in st.session_state:
    st.session_state.input = ""

#page design and input
st.title("Hi! I'm ARIA (Advanced Responsive Information Agent)")
st.markdown("""___""")
st.subheader("Step 1:")
st.subheader("Please input the following information:")
url = "https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key"
api = st.text_input("If you don't know your OpenAI API key click [here](%s)." % url, type="password", placeholder="Your API Key")
topic = st.text_input("What topic would you like to discuss with the Chatbot?")
col1, col2 = st.columns(2)
with col1:
     style = st.radio(
    "How would you like ARIA to respond to your questions?",
    ('Be Percise', 'Be Balanced', 'Be Creative'))

if style == 'Be Percise':
    temprature = 0.0
elif style == 'Be Balanced':
    temprature = 0.5
else:
     temprature = 1.0

with col2:
     max_tokens = st.slider("What is the maximum number of words that you'd like ARIA to produce for every response?", 100, 300, 150)   

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
user_input=st.text_input("User:", key='input')
conversations = []

#Chat process
if st.button("Send"):
    with st.spinner("By code and algorithm, hear my call, let this AI speak with rhyme for all :magic_wand:"):
        
        message_log.append({"role": "user", "content": user_input})
        output = generate_response(user_input, temprature, max_tokens)
        message_log.append({"role": "assistant", "content": output})
        #store the output
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        #store all outputs
        conversations = [(st.session_state['past'][i], st.session_state["generated"][i]) for i in range(len(st.session_state['generated']))]

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

st.markdown("""___""")

# Make OER resource
st.subheader("Step 3:")
st.subheader("When you are ready to write your article, click on the 'Make OER' button.")
if st.button("Make OER"):
    
    with st.spinner("AI, hear my incantation, write with rhyme and variation :magic_wand:"):
        conversations = [(st.session_state['past'][i], st.session_state["generated"][i]) for i in range(len(st.session_state['generated']))]
        context_title=[
                {"role": "system", "content": f'You are a title generator bot.'}, 
                {"role": "user", "content": f'write a title for the following text: {conversations}'}
                 ] 
        
        context_text=[
                {"role": "system", "content": f'You are a content generator bot.'}, 
                {"role": "user", "content": f'The following TEXT is a conversation between a human and a bot. Convert the text in to an academic article. TEXT: {conversations}'}
                 ] 
        title = get_text(context_title, conversations)
        st.title(title)
        academic_text = get_text(context_text, conversations)
        st.write(academic_text)
        #prepare for download
        article = title + "\n" + academic_text
        ste.download_button("Download Article", article, "article.txt")