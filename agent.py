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
    
    def generic_func(self, x, query):
        prompt = PromptTemplate.from_template(GENERIC_PROMPT_TPL)
        llm_chain = LLMChain(
            llm = get_llm_model(), 
            prompt = prompt,
            verbose = os.getenv('VERBOSE')
        )
        return llm_chain.invoke(query)['text']
    
    def retrival_func(self, x, query):
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
    
    def graph_func(self, x, query):
        # NER
        response_schemas = [
            ResponseSchema(type='list', name='University', description='university entity'),
            ResponseSchema(type='list', name='Degree', description='degree entity'),
            ResponseSchema(type='list', name='Year', description='degree year entity, with degree puls year, the format is like "Aerospace Engineering BEng (Hons) Year3"'),
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

        graph_templates = []
        for key, template in GRAPH_TEMPLATE.items():
            slot = template['slots'][0]
            slot_values = ner_result[slot]
            for value in slot_values:
                graph_templates.append({
                    'question': replace_token_in_string(template['question'], [[slot, value]]),
                    'cypher': replace_token_in_string(template['cypher'], [[slot, value]]),
                    'answer': replace_token_in_string(template['answer'], [[slot, value]]),
                })
        if not graph_templates:
            return 
        
        # Calculate problem similarity and filter the most relevant problems
        graph_documents = [
            Document(page_content=template['question'], metadata=template)
            for template in graph_templates
        ]
        db = FAISS.from_documents(graph_documents, get_embeddings_model())
        graph_documents_filter = db.similarity_search_with_relevance_scores(query, k=3)

        def format_answer(answer_template, result):
            # Dynamically replace all key-value pairs
            for key, values in result.items():
                # Make sure all values are converted to strings
                str_values = [str(value) for value in values]
                answer_template = answer_template.replace(f"%{key}%", ', '.join(str_values))
            return answer_template
        
        query_result = []
        neo4j_conn = get_neo4j_conn()
        for document in graph_documents_filter:
            question = document[0].page_content
            cypher = document[0].metadata['cypher']
            answer_template = document[0].metadata['answer']
            try:
                results = neo4j_conn.run(cypher).data()
                if results:
                    # Convert all results to {key: [values]} format
                    aggregated_results = {}
                    for result in results:
                        for key, value in result.items():
                            if key not in aggregated_results:
                                aggregated_results[key] = [value]
                            else:
                                aggregated_results[key].append(value)
                    # Format the answer string
                    answer_str = format_answer(answer_template, aggregated_results)
                    query_result.append(f'Question: {question}\nAnswer: {answer_str}')
            except Exception as e:
                pass
            print(query_result)

        # Summarize the answers
        prompt = PromptTemplate.from_template(GRAPH_PROMPT_TPL)
        graph_chain = LLMChain(
            llm = get_llm_model(),
            prompt = prompt,
            verbose = os.getenv('VERBOSE')
        )
        inputs = {
            'query': query,
            'query_result': '\n\n'.join(query_result) if len(query_result) else 'Not found'
        }
        return graph_chain.invoke(inputs)['text']
    
    def search_func(self, query):
        prompt = PromptTemplate.from_template(SEARCH_PROMPT_TPL)
        llm_chain = LLMChain(
            llm = get_llm_model(),
            prompt = prompt,
            verbose = os.getenv('VERBOSE')
        )
        llm_request_chain = LLMRequestsChain(
            llm_chain = llm_chain,
            requests_key = 'query_result'
        )
        inputs = {
            'query': query,
            'url': 'https://www.google.com/search?q='+query.replace(' ', '+')
        }
        return llm_request_chain.invoke(inputs)['output']
    
    def query(self, query):
        tools = [
            Tool.from_function(
                name = 'generic_func',
                func = lambda x: self.generic_func(x, query),
                description = 'For answering questions in generalized areas of knowledge, such as greeting, asking who you are, etc.',
            ),
            Tool.from_function(
                name = 'retrival_func',
                func = lambda x: self.retrival_func(x, query),
                description = 'For answering questions from additional corpus, e.g. campus gym information',
            ),
            Tool(
                name = 'graph_func',
                func = lambda x: self.graph_func(x, query),
                description = 'For answering questions about University of Liverpool courses, degrees, modules, etc.',
            ),
            Tool(
                name = 'search_func',
                func = self.search_func,
                description = 'For answering generalized questions through a search engine when other tools don\'t have the correct answers',
            ),
        ]

        prefix = """Answer the following questions to the best of your ability. You can use the following tools:"""
        suffix = """Begin!

        History: {chat_history}
        Question: {input}
        Thought:{agent_scratchpad}"""

        agent_prompt = ZeroShotAgent.create_prompt(
            tools=tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=['input', 'agent_scratchpad', 'chat_history']
        )
        llm_chain = LLMChain(llm=get_llm_model(), prompt=agent_prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain)

        memory = ConversationBufferMemory(memory_key='chat_history')
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent = agent, 
            tools = tools, 
            memory = memory, 
            verbose = os.getenv('VERBOSE')
        )
        return agent_chain.invoke({'input': query})


if __name__ == '__main__':
    agent = Agent()
    # print(agent.generic_func('hi'))
    # print(agent.generic_func('Who are you'))
    # print(agent.retrival_func('Introduce the campus gym'))
    # print(agent.graph_func('What degrees does the university of liverpool offer?'))
    # print(agent.graph_func('What are the academic years included in the Aerospace Engineering BEng (Hons) at the university of liverpool'))
    # print(agent.graph_func('What is the code of ELECTRICAL CIRCUITS FOR ENGINEERS'))
    # print(agent.graph_func('How many credits does ELECTRICAL CIRCUITS FOR ENGINEERS have?'))
    # print(agent.graph_func('Which semester does ELECTRICAL CIRCUITS FOR ENGINEERS belong to?'))
    # print(agent.graph_func('What is the description of the module ELECTRICAL CIRCUITS FOR ENGINEERS')) 
    # print(agent.graph_func('What optional modules does Computer Science BSc (Hons) with Computer Science BSc (Hons) Year2 include at the university of liverpool'))
    # print(agent.graph_func('What compulsory modules does Computer Science BSc (Hons) with Computer Science BSc (Hons) Year3 include at the university of liverpool'))
    # print(agent.graph_func('How many modules the university of liverpool offered in Computer Science BSc (Hons) with Computer Science BSc (Hons) Year3?'))
    # print(agent.graph_func('How many compulsory modules the university of liverpool offered in Computer Science BSc (Hons) with Computer Science BSc (Hons) Year3?'))
    # print(agent.graph_func('How many optional modules the university of liverpool offered in Computer Science BSc (Hons) with Computer Science BSc (Hons) Year3?'))
    # print(agent.search_func('Where is the University of Liverpool?'))
    # print(agent.query('What optional modules does Computer Science BSc (Hons) with Computer Science BSc (Hons) Year2 include at the university of liverpool?'))