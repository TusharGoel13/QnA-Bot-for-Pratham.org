import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
import faiss

from dotenv import load_dotenv

load_dotenv()

## Load the GROQ API KEY 
groq_api_key = os.getenv('GROQ_API_KEY')
# os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['HUGGINGFACE_API_KEY'] = os.getenv("HUGGINGFACE_API_KEY")

if not groq_api_key:
    st.error("GROQ_API_KEY not found in the environment variables.")
    st.stop()

st.title("Pratham.org QnA Chatbot")

llm = ChatGroq(groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")

prompt = ChatPromptTemplate.from_template(
"""
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question
<context>
{context}
<context>
Questions: {input}
"""
)

def vector_embedding():
    # Check if embeddings are already created
    if "vectors" not in st.session_state:
        # Initialize HuggingFace embeddings
        st.session_state.embeddings = HuggingFaceEmbeddings()
        
        # Load documents from a directory
        st.session_state.loader = PyPDFDirectoryLoader("./qna_data")  # Data Ingestion
        st.session_state.docs = st.session_state.loader.load()  # Document Loading
        
        # Check if documents are loaded
        if not st.session_state.docs:
            st.error("No documents loaded.")
            return
        
        # Split documents into smaller chunks
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs[:20])
        
        # Check if documents are split
        if not st.session_state.final_documents:
            st.error("No documents after splitting.")
            return

        # Create a FAISS vector store from the embeddings
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)
        
        # Check if the vector store is created
        if not st.session_state.vectors:
            st.error("Failed to create vector store.")
            return
        
st.write("Click Document Embeddings to create Vector Store DB. After it is ready, you can ask questions.")        
if st.button("Documents Embedding"):
    vector_embedding()
    st.write("Vector Store DB Is Ready")

prompt1 = st.text_input("Enter Your Question.")

import time

if prompt1:
    # Create a chain to combine documents and generate a response
    document_chain = create_stuff_documents_chain(llm, prompt)
    
    # Create a retrieval chain using the vector store
    retriever = st.session_state.vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    # Measure the response time
    start = time.process_time()
    response = retrieval_chain.invoke({'input': prompt1})
    print("Response time :", time.process_time() - start)
    
    # Display the response
    st.write(response['answer'])

    # With a streamlit expander, display the relevant chunks from the documents
    with st.expander("Document Similarity Search"):
        # Iterate over the relevant chunks
        for i, doc in enumerate(response["context"]):
            st.write(doc.page_content)
            st.write("--------------------------------")