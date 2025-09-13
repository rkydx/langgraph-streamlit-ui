from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model='gpt-4o-mini')

# Create Class
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState) -> ChatState:
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages': response}

# Create graph
graph = StateGraph(ChatState)

# Add node/s
graph.add_node('chat_node', chat_node)

# Add edge/s
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# Checkpointer
checkpointer = InMemorySaver()

# Compile the graph
chatbot = graph.compile(checkpointer=checkpointer)
