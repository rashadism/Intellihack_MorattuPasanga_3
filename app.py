import os
from dotenv import load_dotenv

import streamlit as st

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)

from langchain.memory import ChatMessageHistory

import streamlit as st
import os

load_dotenv()
GROQ_API_KEY=os.environ['GROQ_API_KEY']

prompt=ChatPromptTemplate.from_messages(
    [
        ("system","You are an assistant who gives information on bank loans. Please answer the questions"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ]
)

llm=ChatGroq(model="llama3-70b-8192")

output_parser=StrOutputParser()
chain=prompt|llm|output_parser

chat_history = ChatMessageHistory()

msgs=StreamlitChatMessageHistory(key="chat_messages")

if len(msgs.messages) == 0:
    msgs.add_ai_message("Hi I am bank assistant. How can I help you?")

history_chain = RunnableWithMessageHistory(
  chain,
  lambda session_id: msgs,
  input_messages_key="question",
  history_messages_key="history"
)

for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

if prompt := st.chat_input():
    st.chat_message("human").write(prompt)

    config = {"configurable": {"session_id": "any"}}
    response = history_chain.invoke({"question": prompt}, config)
    st.chat_message("ai").write(response)