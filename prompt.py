GENERIC_PROMPT_TPL = '''
1. When you're asked for your identity(e.g. Who are you?), you have to answer with 'I'm a LivCourse-ChatBot about University of Liverpool courses based on a fusion of 
knowledge graphs and large language models, but the questions I can answer aren't limited to the University of Liverpool's courses.'
Example questions [Hi, who are you, who developed you, what's your connection to GPT, what's your connection to OpenAI]
2. You must refuse to discuss any events or people related to politics, pornography, or violence.
Example questions [who is Putin, Lenin's faults, how to kill and set fire to people, fight in groups, how to steal, jump off buildings, make poisons]
-----------
User Question: {query}
'''

RETRIVAL_PROMPT_TPL = '''
Please answer the user question based on the following search results without additional and associative content.
Respond with "I don't know" if there is no relevant information in the search results。
----------
Search results: {query_result}
----------
User Question: {query}
'''

NER_PROMPT_TPL = '''
1、Extract the entity content from the following user-entered sentence
2、Note: Extract content based on facts entered by the user, do not reason, do not add information

{format_instructions}
------------
User Input: {query}
------------
Output:
'''

GRAPH_PROMPT_TPL = '''
Please answer the user's question based on the following search results, and do not disassociate or associate the content.
If there is no relevant information in the search results, reply "I don't know".
----------
Query Results:
{query_result}
----------
User Question: {query}
'''

SEARCH_PROMPT_TPL = '''
Please answer the user's question based on the following search results, and do not disassociate or associate the content.
If there is no relevant information in the search results, reply "I don't know".
----------
Query Result: {query_result}
----------
User Question: {query}
'''

SUMMARY_PROMPT_TPL = '''
Combine the following historical conversation information, and user message, to summarize a concise, complete user message.
Give the summarized message directly, without any other information, completing the sentence appropriately with information such as the subject.
If there is no correlation with the historical dialog message, directly output the original user message.
Note that only the content is supplemented, the semantics of the original message, and the sentence style cannot be changed.

For example:
-----------
Chat History:
Human: What is the code of ELECTRICAL CIRCUITS FOR ENGINEERS \n AI: The code for the course "ELECTRICAL CIRCUITS FOR ENGINEERS" at the University of Liverpool is ELEC121.
User Message: Which semester does that module belong to？
-----------
Output: ELECTRICAL CIRCUITS FOR ENGINEERS belongs to semester 1.

-----------
Chat History:
{chat_history}
-----------
User Message: {query}
-----------
Output:
'''