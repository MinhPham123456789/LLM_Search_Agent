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

# Page setups
st.set_page_config(page_title="Agent Search Engine", page_icon="📜🔍", layout="wide")
st.title("Agent Search Engine")
# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search", value="")
if text_search:
    cols = st.columns([6,4], gap="large")
    with cols[0]:
        st.markdown(f"*{'A'*1000}*")
    for key in range(1,7):
        with cols[1]:
            st.write("---")
            st.caption(f"Score  {key} ")
            st.markdown(f"*{key}*")
            st.markdown(f"**{key}**")