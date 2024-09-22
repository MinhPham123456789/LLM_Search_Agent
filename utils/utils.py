from utils.text_summariser.text_summarisation import TextSummariser
from langchain.callbacks.base import BaseCallbackHandler
from time import time

def rearrange_search_result(search_result: dict):
    """Deconstruct the search result and put them in a dictionary
    to support easy interpretation

    Args:
        search_result (dict): an ordered search result
        summarised_ordered_result_hash_map is a dict, 
        key: scraped_web_content's hash, value is 
        (((url, scraped_web_content), ranker_score), summary)


    Returns:
        dict: deconstructed search result
    """
    structured_search_result = {}
    for k in search_result.keys():
        structured_search_result[k] = {
            'url':search_result[k][0][0][0],
            'web_content': search_result[k][0][0][1],
            'score': search_result[k][0][1],
            'summary': search_result[k][1]
        }
    return structured_search_result

# summarised_ordered_result_hash_map is a dict, key: scraped_web_content's hash, value is (((url, scraped_web_content), ranker_score), summary)

def get_top_3_and_summarise(search_result: dict, query: str, sum_llm: TextSummariser):
    top_3 = "\n".join([ search_result[k]["summary"] for k in list(search_result.keys())[:3] ])
    # print(f"Check top 3 results:\n{top_3}")
    top_3_summary = sum_llm.summarise_long_text(query, top_3)
    return top_3_summary

class LLMMonitor(BaseCallbackHandler):
    def __init__(self):
        self.llm_calls = 0
        self.total_duration = 0
        self.call_durations = []

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_time = time()
        self.llm_calls += 1

    def on_llm_end(self, response, **kwargs):
        duration = time() - self.start_time
        self.total_duration += duration
        self.call_durations.append(duration)

    def get_metrics(self):
        return {
            "total_llm_calls": self.llm_calls,
            "total_duration": self.total_duration,
            "average_duration": self.total_duration / self.llm_calls if self.llm_calls > 0 else 0,
            "call durations": self.call_durations
        }
