from utils import *

import os
from glob import glob
from langchain.vectorstores.chroma import Chroma
from langchain_community.document_loaders import CSVLoader, PyMuPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def doc2vec():
    # Define a text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 300,
        chunk_overlap = 50
    )

    # Read and split files
    dir_path = os.path.join(os.path.dirname(__file__), './inputs/')
    documents = []
    for file_path in glob(dir_path + '*.*'):
        loader = None
        if '.csv' in file_path:
            loader = CSVLoader(file_path)
        if '.pdf' in file_path:
            loader = PyMuPDFLoader(file_path)
        if '.txt' in file_path:
            loader = TextLoader(file_path)
        if loader:
            documents += loader.load_and_split(text_splitter)
            
    # vectorize and store
    if documents:
        vdb = Chroma.from_documents(
            documents = documents, 
            embedding = get_embeddings_model(),
            persist_directory = os.path.join(os.path.dirname(__file__), './data/db/')
        )
        vdb.persist()
    print(documents)


if __name__ == '__main__':
    doc2vec()