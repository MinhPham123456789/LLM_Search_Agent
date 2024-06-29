from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

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