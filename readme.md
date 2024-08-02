# Pratham-QnA-Bot

A Question Answering Chatbot built using LangChain, Streamlit, and GROQ.

## Project Overview

Pratham-QnA-Bot is a web-based application that uses natural language processing (NLP) to answer questions based on a collection of documents. The application is built using LangChain, a Python library for building AI applications, Streamlit, a Python library for creating data apps, and GROQ, a GraphQL-like query language for vector databases.

The bot is designed to ingest PDF documents from a specified directory, split them into smaller chunks, and create a vector store using FAISS. The vector store is then used to retrieve relevant documents based on user queries. The bot uses LangChain's LLM (Language Model) to generate responses based on the retrieved documents.

## Getting Started

1. Install the required dependencies:
   - Create a virtual environment in your project directory
   - pip install -r requirements.txt

2. Create a `.env` file in your project directory and add the following environment variables:
   - `GROQ_API_KEY`: Your GROQ API key
   - `HUGGINGFACE_API_KEY`: Your HuggingFace API key
   - `OPENAI_API_KEY`: Your OpenApi API key

3. Run the main.py file
   - Open a terminal in your project directory
   - Run python main.py
   - Access the Streamlit app in your web browser by navigating to localhost
   - Click the Documents Embedding button to create Vector Store DB
   - After Vectore Store DB is created, questions can be asked of which a response and similar citations from the document will be provided

Additional Resources
   - LangChain documentation
   - Streamlit documentation
   - GROQ documentation
   - HuggingFace Embeddings documentation
   - FAISS documentation
   - LangChain Community documentation
   - Python-dotenv documentation
