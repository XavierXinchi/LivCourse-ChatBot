from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from py2neo import Graph
from config import *
import os
from dotenv import load_dotenv
load_dotenv()

def get_embeddings_model():
    model_map = {
        'openai': OpenAIEmbeddings(
            model = os.getenv('OPENAI_EMBEDDINGS_MODEL')
        )
    }
    return model_map.get(os.getenv('EMBEDDINGS_MODEL'))

def get_llm_model():
    model_map = {
        'openai': ChatOpenAI(
            model = os.getenv('OPENAI_LLM_MODEL'),
            temperature = os.getenv('TEMPERATURE'),
            max_tokens = os.getenv('MAX_TOKENS'),
        )
    }
    return model_map.get(os.getenv('LLM_MODEL'))

if __name__ == '__main__':
    llm_model = get_llm_model()
    print(llm_model.predict('what is university of liverpool?'))