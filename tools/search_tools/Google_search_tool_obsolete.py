import configparser
from global_config_path import config_path
from bs4 import BeautifulSoup as bs
import requests
import re
from utils.text_summarisation import *

config = configparser.ConfigParser()
config.read(config_path)
GOOGLE_API_KEY = config['APIs']['GOOGLE_API_KEY']
GOOGLE_CSE_ID = config['APIs']['GOOGLE_CSE_ID']

bs_allowed_tags = [
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'p',
    'span'
]

code_tags = [
    'code'
]
# Test website: https://patchthenet.com/blog/linux-privilege-escalation-three-easy-ways-to-get-a-root-shell
headers={
      "Accept-Language": "en-US,en;q=0.9",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
def get_website_main_content(url, llm_model):
  req = requests.get(url=url,headers=headers)#, timeout=2) # why request throws errors when timeout, like a lot and except cannot handle them
  if req.status_code == 200:
    html_content = req.content.decode('utf-8')
    html_parser = bs(html_content, 'html.parser')
    webcontent_text_list = [t.strip().replace('\t', '').replace('\r\n', '') for t in html_parser.find_all(string=True) if t.parent.name in bs_allowed_tags and t.strip() != '']
    webcontent_text_list = [ text for text in webcontent_text_list if not re.match(r'^[^0-9a-zA-Z]+$', text) ]
    webcontent_code_list = [t.strip().replace('\t', '').replace('\r\n', '') for t in html_parser.find_all(string=True) if t.parent.name in code_tags and t.strip() != '']
    webcontent_text = ' '.join(webcontent_text_list)
    webcontent_code = '\n'.join(webcontent_code_list)
    webcontent_summary = summarize_webcontent_text(f'{webcontent_text}\n{webcontent_code_list}', url, llm_model)
    # print(f'{url}\n{webcontent_text}')
    return {'summary':webcontent_summary, 'code':webcontent_code}
  else:
    print(f'Error: {url} return code {req.status_code}')
    return ''

def google_custom_search(query, num_result=6):
  # llm_sum = llm
  url_encoded_query = requests.utils.requote_uri(query)
  url_encoded_query = url_encoded_query.replace('%20', '+')
  search_url = f'https://customsearch.googleapis.com/customsearch/v1?q={url_encoded_query}&cx={GOOGLE_CSE_ID}&num={num_result}&key={GOOGLE_API_KEY}'
  # print(search_url)
  req = requests.get(url=search_url, timeout=2)
  if req.status_code == 200:
    # print(req.content.decode('utf-8'))
    json_response = req.json()
    concatenated_search_results = ''
    result_summary_dict = {}
    for item in json_response['items']:
      snippet = item['snippet']
      if re.search(r'\.\.\.(.*?)\.\.\.', item['snippet']):
        snippet = re.search(r'\.\.\.(.*?)\.\.\.', item['snippet']).group(1)
      web_content = get_website_main_content(item['formattedUrl'], llm_sum)
      if not isinstance(web_content, str):
        result_summary_dict[item['formattedUrl']] = web_content['summary']
        print(f'{item["formattedUrl"]}\n{web_content["summary"]}\n###### CODE SECTION ######\n{web_content["code"]}')
        concatenated_search_results = f'{concatenated_search_results}\n{web_content["summary"]}'
    search_results_summary = summarize_multiple_texts(concatenated_search_results, llm_sum)
    result_sources = result_summary_dict.keys()
    result_sources = '\n'.join(result_sources)
    search_result = f'Based on these websites:\n{result_sources}\n{search_results_summary}'
    print("################# Search Summary #######################")
    print(concatenated_search_results)
    print("################################")
  else:
    search_result = f'Error code from google search: {req.status_code}'
  return search_result