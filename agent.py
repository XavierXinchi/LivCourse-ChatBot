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
        # print(ner_result)

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
                # print(graph_templates)
        # graph_templates = []
        # for key, template in GRAPH_TEMPLATE.items():
        #     replacements = {}  # 使用字典来存储替换值
        #     for slot in template['slots']:
        #         slot_values = ner_result.get(slot, [])
        #         if slot_values:  # 假设slot_values始终返回列表中的第一个元素作为替换值
        #             replacements[slot] = slot_values[0]  # 直接使用第一个值进行替换

        #     if replacements:
        #         graph_templates.append({
        #             'question': replace_token_in_string(template['question'], replacements),
        #             'cypher': replace_token_in_string(template['cypher'], replacements),
        #             'answer': replace_token_in_string(template['answer'], replacements),
        #         })

        if not graph_templates:
            return 
        
        # 计算问题相似度，筛选最相关问题
        graph_documents = [
            Document(page_content=template['question'], metadata=template)
            for template in graph_templates
        ]
        db = FAISS.from_documents(graph_documents, get_embeddings_model())
        graph_documents_filter = db.similarity_search_with_relevance_scores(query, k=3)
        # print(graph_documents_filter)

        def format_answer(answer_template, result):
            # 动态替换所有键值对
            for key, values in result.items():
                # 确保所有值都转换为字符串
                str_values = [str(value) for value in values]
                answer_template = answer_template.replace(f"%{key}%", ', '.join(str_values))
            return answer_template
        
        query_result = []
        neo4j_conn = get_neo4j_conn()
        for document in graph_documents_filter:
            question = document[0].page_content
            cypher = document[0].metadata['cypher']
            # print(cypher)
            answer_template = document[0].metadata['answer']
            try:
                results = neo4j_conn.run(cypher).data()
                # print(question)
                # print(results)
                if results:
                    # 将所有结果转换为{key: [values]}格式
                    aggregated_results = {}
                    for result in results:
                        for key, value in result.items():
                            if key not in aggregated_results:
                                aggregated_results[key] = [value]
                            else:
                                aggregated_results[key].append(value)
                    # 格式化回答字符串
                    answer_str = format_answer(answer_template, aggregated_results)
                    query_result.append(f'Question: {question}\nAnswer: {answer_str}')
            except Exception as e:
                pass
            print(query_result)

        # 总结答案
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