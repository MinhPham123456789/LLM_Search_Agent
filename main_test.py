from utils.web_scraper_sync import WebScraperSyncMultiBrowsers
# from utils.web_scraper_async import WebScraperAsync
from tools.search_tools.Google_search_tool import GoogleSearchTool
from llms.cross_encoder import CrossEncoder
from utils.text_summarisation import TextSummariser

# test = WebScraperAsync()
# a = test.get_website_content('https://httpbin.org/headers')
# print(a)


# test = WebScraperSyncMultiBrowsers()
# for i in range(0,1):
#     print(f'##{i}##')
#     print(test.get_website_html('https://httpbin.org/headers'))
#     print(test.get_website_content('https://httpbin.org/headers'))

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
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
summ = TextSummariser("meta-llama/Meta-Llama-3-8B-Instruct")
test = GoogleSearchTool(reranker, summ)
result = test.search('Latest vulnerabilities in Google Chrome')
for k in result.keys():
    print(f'###{k}')
    # print(result[k][0][0][0])
    print(result[k][0][0])
    print(result[k][1])
    


# summ = TextSummariser("meta-llama/Meta-Llama-3-8B-Instruct")
# test = WebScraperSyncMultiBrowsers()
# test_result = test.get_website_content('https://www.exploit-db.com/exploits/48609')
# summ_text = summ.summarise_webcontent_text(test_result[0],test_result[1])
# print(test_result[0])
# print(summ_text)
