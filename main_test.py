from utils.web_scraper_sync import WebScraperSyncMultiBrowsers
# from utils.web_scraper_async import WebScraperAsync
from tools.search_tools.Google_search_tool import GoogleSearchTool
from llms.cross_encoder import CrossEncoder
from utils.text_summariser.text_summarisation import TextSummariser



from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool

from agents.react.agent import Custom_ReAct_Agent
import configparser
from global_config_path import config_path
import os

config = configparser.ConfigParser()
config.read(config_path)
os.environ['HUGGINGFACEHUB_API_TOKEN'] = config['APIs']['HF_TOKEN']

# test = WebScraperAsync()
# a = test.get_website_content('https://httpbin.org/headers')
# print(a)


# test = WebScraperSyncMultiBrowsers()
# for i in range(0,1):
#     print(f'##{i}##')
#     print(test.get_website_html('https://httpbin.org/headers'))
#     print(test.get_website_content('https://httpbin.org/headers'))

# Testing the reranking cross encoder
# cross-encoder/ms-marco-MiniLM-L-6-v2 : this one is more okay
# cross-encoder/ms-marco-MiniLM-L-12-v2
# mixedbread-ai/mxbai-embed-large-v1
# reranker = CrossEncoder('mixedbread-ai/mxbai-embed-large-v1')
# query = 'Cats is the best animal'
# text_pairs = [
#     (query,"Cats are amazing pets"),
#     (query,"Cats are annoying"),
#     (query,"Horses are cool and quick."),
#     (query,"Dogs are better than cats"),
#     (query, "Cats are worse than horses"),
#     (query, "Cats are the most loved animal")
# ]
# print(reranker.rerank(text_pairs))


# Test search queries:
# Odoo 12.0 LFI vulnerabilities exploit code
# Latest vulnerabilities in Google Chrome
# reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
# summ = TextSummariser("meta-llama/Meta-Llama-3-8B-Instruct")
# test = GoogleSearchTool(reranker, summ)
# result = test.search('Latest vulnerabilities in Google Chrome')
# for k in result.keys():
#     print(f'###{k}')
#     # print(result[k][0][0][0])
#     print(result[k][0][0])
#     print(result[k][1])
    

# Testing the summariser
# summ = TextSummariser("meta-llama/Meta-Llama-3-8B-Instruct")
# test = WebScraperSyncMultiBrowsers()
# url ='https://www.exploit-db.com/exploits/48609'
# test_result = test.get_website_content(url)
# summ_text = summ.summarise_webcontent_text(test_result[0],test_result[1])
# print(test_result[0])
# print(summ_text['output_text'])

# Testing the summariser prompt
# summ = TextSummariser("meta-llama/Meta-Llama-3-8B-Instruct")
# summ_chain = build_summariser_chain(summ.summariser_llm, "Odoo 12.0 LFI vulnerabilities exploit code")
# print(summ_chain)

# test = WebScraperSyncMultiBrowsers()
# url ='https://www.exploit-db.com/exploits/48609'
# test_result = test.get_website_content(url)

# metadata = {
#             'source': url,
#             'title': url,
#             'language': 'en'
#             }
# docs = summ.get_text_chunks_langchain_from_plaintext(metadata, test_result[1])

# # summ_text = summ.summarise_webcontent_text(test_result[0],test_result[1])
# summ_text = summ_chain.invoke(docs)

# print(test_result[0])
# print(summ_text['output_text'])

# Test tool
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
web_summ = TextSummariser("meta-llama/Meta-Llama-3-8B-Instruct", "web_content_sum_prompt")
sum_sum = TextSummariser("mistralai/Mistral-7B-Instruct-v0.3","combine_prompt")
engine = GoogleSearchTool(reranker, web_summ)

class SearchEngineInput(BaseModel):
    query: str = Field(description="should be a search query")

search_tool = StructuredTool.from_function(
    func=engine.search,
    name="Search",
    description="useful for when you need to answer questions about current events",
    args_schema=SearchEngineInput
)

print(search_tool.name)
print(search_tool.description)
print(search_tool.args)
QUERY = "How to block .cpl extension files from executing in Windows devices"
result_dict = search_tool.run(QUERY)

top_3 = "\n".join([ result_dict[k]["summary"] for k in list(result_dict.keys())[:3] ])

for k in result_dict.keys():
    print(result_dict[k]['url'])

print(top_3)

print("Sum Sum:")
print(sum_sum.summarise_long_text(QUERY, top_3))

# print("Web prompt:")
# print(web_summ.chain)
# print("Combine prompt:")
# print(sum_sum.chain)

# Test agent
# Model: microsoft/Phi-3-mini-4k-instruct, google/gemma-1.1-7b-it, google/gemma-2-2b-it
# agent = Custom_ReAct_Agent("google/gemma-1.1-7b-it", [search_tool])
# agent.chat("How to make a shirt")