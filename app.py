import os
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
import streamlit as st

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS


from langchain.memory import ChatMessageHistory

import streamlit as st
import os



load_dotenv()
GROQ_API_KEY=os.environ['GROQ_API_KEY']

loader=PyPDFLoader('data/loan_data.pdf')
docs=loader.load()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

formatted_docs=format_docs(docs)

# text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
# documents=text_splitter.split_documents(docs)



system_message=f"""
You are a chatbot assists customers of SmartBank with inquiries about their eligibility for loans 
and to provide information about the loan application process. You are to provide the following functionality.

Loan Eligibility Check: The system should allow users to check their eligibility for different types of loans  based on various criteria such as credit score, income level, employment status, and existing debts. 
Loan Products Information: Users should be able to obtain information about the different types of  loans offered by the institution, including their features, interest rates, repayment terms, and eligibility  requirements. 
Application Process Guidance: The system should guide users through the loan application process,  providing information about the documents required, the steps involved, and the timeline for approval  and disbursement. 
FAQs and Troubleshooting: The system should provide answers to frequently asked questions about  loans, such as how to improve credit score, what to do if an application is rejected, and how to calculate  loan repayments. 
Personalized Recommendations: Based on the user's financial situation, the system should offer  personalized recommendations for suitable loan products and tips for improving eligibility.

You are allowed to use the following information as context to answer user queries.
\n\n{formatted_docs}"""

print(system_message)
prompt=ChatPromptTemplate.from_messages(
    [
        ("system",system_message),
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