from tools.search_tools.Google_search_tool import GoogleSearchTool
from llms.cross_encoder import CrossEncoder
from utils.text_summariser.text_summarisation import TextSummariser
from utils.utils import rearrange_search_result
import streamlit as st
import configparser
from global_config_path import config_path
import os

config = configparser.ConfigParser()
config.read(config_path)
os.environ['HUGGINGFACEHUB_API_TOKEN'] = config['APIs']['HF_TOKEN']


reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
summ = TextSummariser("meta-llama/Meta-Llama-3-8B-Instruct")
engine = GoogleSearchTool(reranker, summ) # May want to change the number of result to 10 max
# result = engine.search('Latest vulnerabilities in Google Chrome')
# structured_result = rearrange_search_result(result)

# Page setups
st.set_page_config(page_title="Better Search Engine", page_icon="🐍", layout="wide")
st.title("Better Search Engine")
# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search", value="")
# Show the result cards
if text_search:
    structured_result = engine.search(text_search)
    # structured_result = rearrange_search_result(result)
    N_cards_per_row = 3
    result_order_number = 0
    for key in structured_result.keys():
        i = result_order_number%N_cards_per_row
        if i==0:
            st.write("---")
            cols = st.columns(N_cards_per_row, gap="large")
        # draw the card
        with cols[result_order_number%N_cards_per_row]:
            st.caption(f"Score  {structured_result[key]['score']} ")
            st.markdown(f"*{structured_result[key]['summary'].strip()}*")
            st.markdown(f"**{structured_result[key]['url']}**")
        result_order_number = result_order_number + 1
