from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import HuggingFaceEndpoint
import configparser
from global_config_path import config_path
from utils.text_summariser.text_summarisation_prompt import build_summariser_chain
import os


"""
metadata structure
metadata_content = {
           'source':,
           'title':,
           'language': 'en'
        }

Summarisation test urls
https://www.exploit-db.com/exploits/48609
https://patchthenet.com/blog/linux-privilege-escalation-three-easy-ways-to-get-a-root-shell

"""
class TextSummariser:
    def __init__(self, model_name):
        self.model_name = model_name
        config = configparser.ConfigParser()
        self.apis_db = config.read(config_path)
        # HUGGINGFACEHUB_API_TOKEN = config['APIs']['HF_TOKEN']
        os.environ['HUGGINGFACEHUB_API_TOKEN'] = config['APIs']['HF_TOKEN']
        self.summariser_llm = HuggingFaceEndpoint(repo_id=self.model_name, temperature=0.2) 
        # mistralai/Mistral-7B-Instruct-v0.3, meta-llama/Meta-Llama-3-8B-Instruct, meta-llama/Meta-Llama-3-8B (require meta permission on Hugging), HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1
        # self.chain = load_summarize_chain(self.summariser_llm, chain_type="map_reduce")
        self.chain = None

    def set_summary_chain(self, query):
        self.chain = build_summariser_chain(self.summariser_llm, query)

    def get_text_chunks_langchain_from_plaintext(self, metadata, text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=8192, chunk_overlap=100, length_function=len)
        metadata_content = metadata
        docs = [Document(page_content=x, metadata=metadata_content) for x in text_splitter.split_text(text)]
        return docs
    
    def summarise_webcontent_text(self, url, webcontent_text):
        metadata = {
            'source': url,
            'title': url,
            'language': 'en'
        }
        docs = self.get_text_chunks_langchain_from_plaintext(metadata, webcontent_text)
        output = self.chain.invoke(docs)
        summary = output['output_text']
        return summary
    
    def summarise_long_text(self, long_text):
        metadata_content = {'source':'multiple texts','language':'en'}
        docs = self.get_text_chunks_langchain_from_plaintext(metadata_content, long_text)
        output = self.chain.invoke(docs)
        summary = output['output_text']
        return summary
    
    def summarise_search_result(self, query, search_result_hash_map):
        self.set_summary_chain(query)
        for key in search_result_hash_map.keys():
            summary = self.summarise_webcontent_text(search_result_hash_map[key][0][0],
                                                     search_result_hash_map[key][0][1])
            search_result_hash_map[key] = (search_result_hash_map[key], summary)
        return search_result_hash_map