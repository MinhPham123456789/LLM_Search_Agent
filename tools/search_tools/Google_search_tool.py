import configparser
from global_config_path import config_path
import requests
from utils.web_scraper_sync import WebScraperSyncMultiBrowsers, WebScraperSyncOneBrowser
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha1
from llms.cross_encoder import CrossEncoder
from utils.text_summariser.text_summarisation import TextSummariser
from utils.utils import rearrange_search_result
from utils.utils import get_top_3_and_summarise

class GoogleSearchTool:
    def __init__(self, reranker: CrossEncoder, website_summariser: TextSummariser, summaries_summariser: TextSummariser, num_result:int = 6):
        config = configparser.ConfigParser()
        self.apis_db = config.read(config_path)
        self.GOOGLE_API_KEY = config['APIs']['GOOGLE_API_KEY']
        self.GOOGLE_CSE_ID = config['APIs']['GOOGLE_CSE_ID']
        self.reranker = reranker
        self.website_summariser = website_summariser
        self.summaries_summariser = summaries_summariser
        self.num_result = num_result

    def Google_search(self, query):
        url_encoded_query = requests.utils.requote_uri(query)
        url_encoded_query = url_encoded_query.replace('%20', '+')
        # print(url_encoded_query)
        search_url = f'https://customsearch.googleapis.com/customsearch/v1?q={url_encoded_query}&cx={self.GOOGLE_CSE_ID}&num={self.num_result}&key={self.GOOGLE_API_KEY}'
        req = requests.get(url=search_url, timeout=2)
        if req.status_code == 200:
            json_response = req.json()
            result_urls = []
            for item in json_response['items']:
                result_urls.append(item['link'])
            return result_urls
        else:
            search_result = f'Error code from google search: {req.status_code}'
            return search_result
        
    def get_website_content_async(self, urls_list):
        web_scraper = WebScraperSyncMultiBrowsers()
        with ThreadPoolExecutor(max_workers=4) as executor:
            result= list(executor.map(web_scraper.get_website_content, urls_list))      
        return result
    
    def get_website_content_sync(self, urls_list):
        web_scraper = WebScraperSyncOneBrowser()
        return [web_scraper.get_website_content(url) for url in urls_list]
    
    def generate_Google_result_hash_map(self, Google_results, hash_map=None):
        if hash_map == None:
            result_hash_map = {}
            for result in Google_results:
                sha1_hash = sha1(result[1].encode()).hexdigest()
                result_hash_map[sha1_hash] = result
        else:
            result_hash_map = hash_map
            for result in Google_results:
                sha1_hash = sha1(result[1].encode()).hexdigest()
                result_hash_map[sha1_hash] = result
        return result_hash_map
    
    def generate_Google_summarised_result_hash_map(self, Google_results, hash_map=None):
        if hash_map == None:
            result_hash_map = {}
            for result in Google_results:
                # output = self.summariser.summarise_webcontent_text(result[0], result[1])
                summary = self.website_summariser.summarise_webcontent_text(result[0], result[1]) #output['output_text']
                sha1_hash = sha1(summary.encode()).hexdigest()
                result_hash_map[sha1_hash] = (result,summary)
        else:
            result_hash_map = hash_map
            for result in Google_results:
                # output = self.summariser.summarise_webcontent_text(result[0], result[1])
                summary = self.website_summariser.summarise_webcontent_text(result[0], result[1]) #output['output_text']
                sha1_hash = sha1(summary.encode()).hexdigest()
                result_hash_map[sha1_hash] = (result,summary)
        return result_hash_map


    def search(self, query):
        # Increase number of result to 10 per Google search
        # Add method to remove 4xx and 5xx websites
        Google_urls_result = self.Google_search(query)
        if 'Error code' in Google_urls_result:
            return Google_urls_result
        # web_contents is a list of tuples (url, scraped_web_content)
        web_contents = self.get_website_content_async(Google_urls_result)
        # result_hash_map is a dict, key: scraped_web_content's hash, value is (url, scraped_web_content)
        # result_hash_map = self.generate_Google_summarised_result_hash_map(web_contents)
        result_hash_map = self.generate_Google_result_hash_map(web_contents)
        ordered_result_hash_map = self.reranker.rerank_search_result(query, result_hash_map)
        # ordered_result_hash_map is a dict, key: scraped_web_content's hash, value is ((url, scraped_web_content), ranker_score)
        summarised_ordered_result_hash_map = self.website_summariser.summarise_search_result(query, ordered_result_hash_map)
        # summarised_ordered_result_hash_map is a dict, key: scraped_web_content's hash, value is (((url, scraped_web_content), ranker_score), summary)
        the_result = rearrange_search_result(summarised_ordered_result_hash_map)
        return the_result

    def agent_tool_search(self, query): # Just wrapper on top the search method, which is the main one
        result_dict = self.search(query)
        return get_top_3_and_summarise(result_dict, query, self.summaries_summariser)

    def tool_search(self, query): # Just wrapper on top the search method, which is the main one
        result_dict = self.search(query)
        return get_top_3_and_summarise(result_dict, query, self.summaries_summariser), result_dict

