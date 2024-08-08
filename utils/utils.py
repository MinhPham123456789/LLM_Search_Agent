def rearrange_search_result(search_result):
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
