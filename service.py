from prompt import *
from utils import *
from agent import *

from langchain.chains import LLMChain
from langchain.prompts import Prompt

class Service():
    def __init__(self):
        self.agent = Agent()

    def get_summary_message(slef, message, history):
        llm = get_llm_model()
        prompt = Prompt.from_template(SUMMARY_PROMPT_TPL)
        llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=os.getenv('VERBOSE'))
        chat_history = ''
        for q, a in history[-2:]:
            chat_history += f'Question:{q}, Answer:{a}\n'
        return llm_chain.invoke({'query':message, 'chat_history':chat_history})['text']

    def answer(self, message, history):
        if history:
            message = self.get_summary_message(message, history)
        return self.agent.query(message)


if __name__ == '__main__':
    service = Service()
    print(service.answer('hi', []))
