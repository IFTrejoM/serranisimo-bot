# Run as python pdf_vectorizer.py -i route\to\file\pdf_file.pdf -o route\to\save\pdf_file_vectors.pkl
# python pdf_vectorizer.py -i serranisimo-script.pdf -o serranisimo-script.pkl

import argparse
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import pickle
from dotenv import load_dotenv
import os

# Cargar las variables del .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#openai.api_key = OPENAI_API_KEY

def get_text_from_pdf(pdf_path):
    """Function that extracts text from the PDF"""
    
    text = ""
    pdf_reader = PdfReader(pdf_path)
        
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    return text 

def get_text_chunks(text):
    """Function that chunks the text"""
    
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
        )
    text_chunks = text_splitter.split_text(text)

    return text_chunks

def create_vector_store(text_chunks):
    """Function that creates a vector store with FAISS"""
    
    word_vectors = OpenAIEmbeddings()
    
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=word_vectors)
    
    return vectorstore

def vectorize_pdf(pdf_path, output_path):
    raw_text = get_text_from_pdf(pdf_path)
    text_chunks = get_text_chunks(raw_text)
    vector_store = create_vector_store(text_chunks)

    data = {
        "vector_store": vector_store,
        "text_chunks": text_chunks
    }

    # Guardar los datos
    with open(output_path, 'wb') as f:
        pickle.dump(data, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vectorize a PDF.")
    parser.add_argument("-i", "--input", required=True, help="Path to PDF.")
    parser.add_argument("-o", "--output", default="vectorstore.pkl", help="Output path of vectors. Default is 'vectorstore.pkl'.")

    args = parser.parse_args()
    
    vectorize_pdf(args.input, args.output)