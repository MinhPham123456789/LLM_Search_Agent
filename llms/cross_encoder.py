from langchain_community.cross_encoders import HuggingFaceCrossEncoder
import hashlib

"""
Try
cross-encoder/ms-marco-MiniLM-L-6-v2
mixedbread-ai/mxbai-embed-large-v1
"""
class CrossEncoder:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = HuggingFaceCrossEncoder(
            model_name = self.model_name
        )

    def rerank(self, text_pairs_list):
        return self.model.score(text_pairs_list)
    
    def rerank_search_result(self, query, search_result_hash_map):
        text_pairs = []
        for key in search_result_hash_map.keys():
            text_pairs.append(
                (
                    query,
                    search_result_hash_map[key][1]
                )
            )
        scores = self.rerank(text_pairs)
        print(scores)