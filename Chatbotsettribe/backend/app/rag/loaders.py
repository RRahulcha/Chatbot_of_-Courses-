import os
from langchain_community.document_loaders import TextLoader, JSONLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents_from_dir(directory_path: str):
    documents = []
    
    # Load Text files
    txt_loader = DirectoryLoader(directory_path, glob="**/*.txt", loader_cls=TextLoader)
    documents.extend(txt_loader.load())
    
    # We can add PDF, JSON loaders here similarly
    
    return documents

def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
