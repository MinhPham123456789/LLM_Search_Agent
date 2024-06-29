import os
import configparser
from global_config_path import config_path
from langchain_core.tools import Tool
from tools.search_tools.Google_search_tool_obsolete import google_custom_search
from Search_Agent import Search_Agent

config = configparser.ConfigParser()
config.read(config_path)
os.environ['HUGGINGFACEHUB_API_TOKEN'] = config['APIs']['HF_TOKEN']
HUGGINGFACEHUB_API_TOKEN = config['APIs']['HF_TOKEN']

google_tool = Tool(
    name="Google-Internet-search",
    description="Useful for searching and research for more information",
    func=google_custom_search,
)
tools_list = [google_tool]
