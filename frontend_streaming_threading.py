# pip install streamlit
# At the terminal run this command to execute this frontend: streamlit run frontend_streaming_threading.py
# In this file the codes are for enhancing the UI such as:
# . Auto-naming conversations using the first user message
# . Sidebar shows only conversations that were created by user input (not on initial load)
# . Support for viewing previous conversations
# . Real-time streaming of assistant responses using st.write_stream
# . State tracking via st.session_state
# . Added Clear Chat option

import streamlit as st
from backend import chatbot
from langchain_core.messages import BaseMessage, HumanMessage
import uuid     # For generating random new thread id


# **************************************************** Utility functions ***********************************************
def generate_thread_id():                                   # This function is for creating unique ID for each new chat thread
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []                # Reset the message history to empty list
    st.session_state['new_chat'] = True

def add_thread(thread_id, name):
    st.session_state['chat_threads'].append({'id': thread_id, 'name': name})

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']      

# **************************************************** Session Setup ****************************************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    # st.session_state['thread_id'] = generate_thread_id()
    st.session_state['thread_id'] = None

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []                   # Each chat thread will be a dictionary: {'id': <UUID>, 'name': <Display name>}

if 'new_chat' not in st.session_state:
    st.session_state['new_chat'] = True    

# add_thread(st.session_state['thread_id'])

# If a thread ID exists, include it in the config, else use an empty configuration
if st.session_state['thread_id']:
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
else:
    CONFIG = {'configurable': {}}

# **************************************************** Sidebar UI *******************************************************
st.sidebar.title("Users  Chatbot")

if st.sidebar.button('New Chat'):                           # If the 'New Chat' button clicked then call reset_chat function
    reset_chat()

if st.sidebar.button("Clear All Chats"):
    st.session_state['chat_threads'] = []
    st.session_state['message_history'] = []

st.sidebar.header('Conversations History')

for thread in reversed(st.session_state['chat_threads']):   # For keeping the latest thread on top
    thread_id = thread['id']
    thread_name = thread['name']

    if st.sidebar.button(thread_name, key=thread_id):
        st.session_state['thread_id'] = thread_id
        st.session_state['new_chat'] = False
        messages = load_conversation(thread_id)

        temp_messages = []
        for each_message in messages:
            if isinstance(each_message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'   
            temp_messages.append({'role': role, 'content': each_message.content})

        st.session_state['message_history'] = temp_messages        

# ****************************************************** Main UI ********************************************************
# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# Chat input box
user_input = st.chat_input('Type here')

if user_input:
    # first add the message to message history
    if st.session_state['new_chat']:
        st.session_state['thread_id'] = generate_thread_id()
        CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
        add_thread(st.session_state['thread_id'], user_input.strip()[:40])
        st.session_state['new_chat'] = False

    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # Below code is for streaming - displaying the AI response in a streaming fashion for better UX
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
             {'messages': [HumanMessage(content=user_input)]},
               config= {'configurable': {'thread_id': st.session_state['thread_id']}},
               stream_mode='messages' 
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})