from tools.search_tools.Google_search_tool import GoogleSearchTool
from llms.cross_encoder import CrossEncoder
from utils.text_summariser.text_summarisation import TextSummariser
from utils.utils import rearrange_search_result
import streamlit as st
from utils.utils import LLMMonitor
import configparser
from global_config_path import config_path
import os

config = configparser.ConfigParser()
config.read(config_path)
os.environ['HUGGINGFACEHUB_API_TOKEN'] = config['APIs']['HF_TOKEN']
os.environ['GROQ_API_KEY'] = config['APIs']['GROQ_TOKEN']

web_sum_mon = LLMMonitor()
sum_sum_mon = LLMMonitor()

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
web_sum = TextSummariser("llama3-8b-8192", "web_content_sum_prompt", web_sum_mon)
sum_sum = TextSummariser("llama3-8b-8192","combine_prompt", sum_sum_mon)
engine = GoogleSearchTool(reranker, web_sum, sum_sum) # May want to change the number of result to 10 max

# To continuously add content to client side with streamlit
# https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state

# Isolate customise CSS container in Streamlit WITHOUT unsafe_allow_html
# https://medium.com/snowflake/style-and-customize-your-streamlit-in-snowflake-apps-4a8495b8e469

# Page setups
st.set_page_config(page_title="Better Search Engine", page_icon="🔍", layout="wide")
st.title("Better Search Engine")
# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search", value="")
# Show the result cards
if text_search:
    search_AI_response, search_result_dict = engine.tool_search(text_search)
    N_cards_per_row = 3
    result_order_number = 0
    with st.container():
        st.subheader(f"{text_search}")
        st.markdown(f"{search_AI_response}")
    for key in search_result_dict.keys():
        i = result_order_number%N_cards_per_row
        if i==0:
            st.write("---")
            if result_order_number == 0:
                st.write("Response References")
            elif result_order_number == 3:
                st.write("Extra Relevant Links")
            cols = st.columns(N_cards_per_row, gap="large")
        # draw the card
        with cols[result_order_number%N_cards_per_row]:
            st.caption(f"Score  {search_result_dict[key]['score']} ")
            st.markdown(f"{search_result_dict[key]['summary'].strip()}")
            st.markdown(f"{search_result_dict[key]['url']}")
        result_order_number = result_order_number + 1

    print(f"Web Summary monitor:\n{web_sum_mon.get_metrics()}")
    print(f"Sum Summary monitor:\n{sum_sum_mon.get_metrics()}")


