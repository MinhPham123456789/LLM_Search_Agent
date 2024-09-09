from tools.search_tools.Google_search_tool import GoogleSearchTool
from llms.cross_encoder import CrossEncoder
from utils.text_summariser.text_summarisation import TextSummariser
from utils.utils import rearrange_search_result
import streamlit as st
import configparser
from global_config_path import config_path
import os

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool

from agents.react.agent import Custom_ReAct_Agent

config = configparser.ConfigParser()
config.read(config_path)
os.environ['HUGGINGFACEHUB_API_TOKEN'] = config['APIs']['HF_TOKEN']

# Agent Initialisation
# Tool setup
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
web_summ = TextSummariser("mistralai/Mistral-7B-Instruct-v0.3", "web_content_sum_prompt")
sum_sum = TextSummariser("mistralai/Mistral-7B-Instruct-v0.3","combine_prompt") # mistralai/Mistral-7B-Instruct-v0.3, meta-llama/Meta-Llama-3-8B-Instruct
engine = GoogleSearchTool(reranker, web_summ, sum_sum)

class SearchEngineInput(BaseModel):
    query: str = Field(description="should be a search query")

search_tool = StructuredTool.from_function(
    func=engine.tool_search,
    name="Search",
    description="useful for when you need to answer questions about current events",
    args_schema=SearchEngineInput
)

# Agent
agent = Custom_ReAct_Agent("microsoft/Phi-3-mini-4k-instruct", [search_tool])

# Page setups
st.set_page_config(page_title="Agent Search Engine", page_icon="📜🔍", layout="wide")
st.title("Agent Search Engine")
# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search", value="")
if text_search:
    agent_memory, result_dict_list = agent.chat(text_search)
    cols = st.columns([6,4], gap="large")
    with cols[0]:
        st.subheader(text_search)
        st.markdown(f"*{agent_memory}*")
    for i in range(0, len(result_dict_list)):
        with cols[1]:
            st.subheader(f"Observation {i}")
            result_dict = result_dict_list[i]
            for key in list(result_dict.keys())[:3]: # Show the top 3 only
                st.caption(f"Score  {result_dict[key]['score']} ")
                st.markdown(f"*{result_dict[key]['summary'].strip()}*")
                st.markdown(f"**{result_dict[key]['url']}**")
        if i != len(result_dict_list) - 1:
            st.write("---")