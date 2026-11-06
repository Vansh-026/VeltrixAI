
#LLM
#Tool-Google search tool
#Agent
#memory
#Streaming
#web interface

from dotenv import load_dotenv
load_dotenv()

from auth import authentication, logout
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_community.utilities import GoogleSerperAPIWrapper
from langgraph.checkpoint.memory import InMemorySaver
import streamlit as st

# Authentication
user = authentication()

with st.sidebar:
    st.markdown("## 🤖 **Veltrix AI**")
    st.write(f"Welcome, {user['username']}")

    if st.button("Logout"):
        logout()




model = ChatGroq(model="openai/gpt-oss-20b", streaming=True)
search = GoogleSerperAPIWrapper()
tools = [search.run]

if "memory" not in st.session_state:
    st.session_state.memory = InMemorySaver()
    st.session_state.history = []

# User-specific thread ID
thread_id = f"user_{user['id']}"

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="You are a helpful assistant that answers questions using Google Search results and also using your data.",
    checkpointer=st.session_state.memory
)

## Building web interface
st.subheader("Veltrix AI - Intelligence at the Speed of Thought")

for message in st.session_state.history:
    if message["role"] == "user":
        st.chat_message("user").markdown(message["content"])
    else:
        st.chat_message("AI").markdown(message["content"])


query = st.chat_input("Ask Anything")

if query:

    st.chat_message("user").markdown(query)
    st.session_state.history.append({"role": "user", "content": query})

    response = agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        {"configurable": {"thread_id": thread_id}},
        stream_mode="messages"
    )

    ai_container = st.chat_message("AI")

    with ai_container:
        space = st.empty()
        message = ""

        for chunk, metadata in response:
            if chunk.type == "AIMessageChunk" and isinstance(chunk.content, str):
                message += chunk.content
                space.markdown(message)

        space.markdown(message)

    st.session_state.history.append({"role": "AI", "content": message})
