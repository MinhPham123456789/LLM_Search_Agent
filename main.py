import os
import configparser
from global_config_path import config_path

config = configparser.ConfigParser()
config.read(config_path)
os.environ['GOOGLE_API_KEY'] = config['APIs']['GOOGLE_API_KEY']
os.environ['GOOGLE_CSE_ID'] = config['APIs']['GOOGLE_CSE_ID']
os.environ['HUGGINGFACEHUB_API_TOKEN'] = config['APIs']['HF_TOKEN']
HUGGINGFACEHUB_API_TOKEN = config['APIs']['HF_TOKEN']