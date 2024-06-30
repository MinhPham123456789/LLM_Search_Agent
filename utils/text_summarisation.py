from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import HuggingFaceEndpoint
import configparser
from global_config_path import config_path
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
        self.summariser_llm = HuggingFaceEndpoint(repo_id=self.model_name) 
        # mistralai/Mistral-7B-Instruct-v0.3, meta-llama/Meta-Llama-3-8B-Instruct, meta-llama/Meta-Llama-3-8B (require meta permission on Hugging), HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1

    def get_text_chunks_langchain_from_plaintext(self, metadata, text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=8192, chunk_overlap=100, length_function=len)
        metadata_content = metadata
        docs = [Document(page_content=x, metadata=metadata_content) for x in text_splitter.split_text(text)]
        return docs
    
    def summarise_webcontent_text(self, webcontent_text, url):
       metadata = {
          'source': url,
           'title': url,
           'language': 'en'
       }
       docs = self.get_text_chunks_langchain_from_plaintext(metadata, webcontent_text)
       chain = load_summarize_chain(self.summariser_llm, chain_type="map_reduce")
       summary = chain.run(docs)
       return summary
    
    def summarise_long_text(self, long_text):
       metadata_content = {'source':'multiple texts','language':'en'}
       docs = self.get_text_chunks_langchain_from_plaintext(metadata_content, long_text)
       chain = load_summarize_chain(self.summariser_llm, chain_type="map_reduce")
       summary = chain.run(docs)
       return summary

def get_text_chunks_langchain_from_plaintext(original_docs_for_metadata, text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=8192, chunk_overlap=100, length_function=len)
    metadata_content = original_docs_for_metadata[0].metadata
    docs = [Document(page_content=x, metadata=metadata_content) for x in text_splitter.split_text(text)]
    return docs

def summarize_webcontent_text(webcontent_text, url, llm_model):
    loader = WebBaseLoader(url)
    docs_4_metadata = loader.load()
    docs = get_text_chunks_langchain_from_plaintext(docs_4_metadata, webcontent_text)
    chain = load_summarize_chain(llm_model, chain_type="map_reduce")
    summary = chain.run(docs)
    return summary

def summarize_multiple_texts(concatenated_texts, llm_model):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=8192, chunk_overlap=100, length_function=len)
    metadata_content = {'source':'multiple texts','language':'en'}
    docs = [Document(page_content=x, metadata=metadata_content) for x in text_splitter.split_text(concatenated_texts)]
    chain = load_summarize_chain(llm_model, chain_type="stuff")
    summary = chain.run(docs)
    return summary