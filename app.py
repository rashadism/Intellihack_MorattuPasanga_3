import os
from dotenv import load_dotenv

import streamlit as st

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
GROQ_API_KEY = os.environ['GROQ_API_KEY']

llm = ChatGroq(model="llama3-70b-8192")
