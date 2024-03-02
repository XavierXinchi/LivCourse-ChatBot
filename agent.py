from utils import *
from config import *
from prompt import *

import os
from langchain.chains import LLMChain, LLMRequestsChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores.chroma import Chroma
from langchain.vectorstores.faiss import FAISS
from langchain.schema import Document
from langchain.agents import ZeroShotAgent, AgentExecutor, Tool, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain import hub


class Agent():
    def __init__(self):
        self.vdb = Chroma(
            persist_directory = os.path.join(os.path.dirname(__file__), './data/db'), 
            embedding_function = get_embeddings_model()
        )
    
    def generic_func(self, query):
        prompt = PromptTemplate.from_template(GENERIC_PROMPT_TPL)
        llm_chain = LLMChain(
            llm = get_llm_model(), 
            prompt = prompt,
            verbose = os.getenv('VERBOSE')
        )
        return llm_chain.invoke(query)['text']
    
    def retrival_func(self, query):
        # Recall and filter documents
        documents = self.vdb.similarity_search_with_relevance_scores(query, k=5)
        query_result = [doc[0].page_content for doc in documents if doc[1]>0.7]
        
        # Fill in the prompts and summarize the answers
        prompt = PromptTemplate.from_template(RETRIVAL_PROMPT_TPL)
        retrival_chain = LLMChain(
            llm = get_llm_model(),
            prompt = prompt,
            verbose = os.getenv('VERBOSE')
        )
        inputs = {
            'query': query,
            'query_result': '\n\n'.join(query_result) if len(query_result) else 'Not Found'
        }
        return retrival_chain.invoke(inputs)['text']
    
    def graph_func(self, query):
        # 命名实体识别
        response_schemas = [
            ResponseSchema(type='list', name='university', description='university entity'),
            ResponseSchema(type='list', name='degree', description='degree entity'),
            ResponseSchema(type='list', name='Year', description='degree year entity'),
            ResponseSchema(type='list', name='CompulsoryModule', description='compulsory modules entity'),
            ResponseSchema(type='list', name='OptionalModule', description='optional modules entity')
        ]

        output_parser = StructuredOutputParser(response_schemas=response_schemas)
        format_instructions = structured_output_parser(response_schemas)

        ner_prompt = PromptTemplate(
            template = NER_PROMPT_TPL,
            partial_variables = {'format_instructions': format_instructions},
            input_variables = ['query']
        )

        ner_chain = LLMChain(
            llm = get_llm_model(),
            prompt = ner_prompt,
            verbose = os.getenv('VERBOSE')
        )

        result = ner_chain.invoke({
            'query': query
        })['text']
        
        ner_result = output_parser.parse(result)
        print(ner_result)

if __name__ == '__main__':
    agent = Agent()
    # print(agent.generic_func('Who are you'))
    # print(agent.retrival_func('Introduce the campus gym'))
    print(agent.graph_func('what are the compulsory modules in year2 of the degree BEng Avionic Systems(Hons) of the University of Liverpool?'))