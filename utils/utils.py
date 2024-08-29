from utils.text_summariser.text_summarisation import TextSummariser

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
    top_3_summary = sum_llm.summarise_long_text(query, top_3)
    return top_3_summary
