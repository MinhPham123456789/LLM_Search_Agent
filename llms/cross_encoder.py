from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from hashlib import sha1

"""
Try
cross-encoder/ms-marco-MiniLM-L-6-v2 (sort_reverse: True)
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
    
    def rerank_search_result(self, query, search_result_hash_map, reverse_signal=True):
        text_pairs = []
        for key in search_result_hash_map.keys():
            text_pairs.append(
                (
                    query,
                    search_result_hash_map[key][1]
                )
            )
        scores = self.rerank(text_pairs)

        # Debug raning integrity
        # print("DEBUG MODE in cross_encoder.py")
        # for c in range(0, len(search_result_hash_map.values())):
        #     print(f'{list(search_result_hash_map.values())[c][0]}, {scores[c]}')
        
        # Add the ranking score
        for i in range(0, len(scores)):
            content_hash = sha1(text_pairs[i][1].encode()).hexdigest()
            search_result_hash_map[content_hash] = (search_result_hash_map[content_hash], scores[i])
        
        # Reorder the Google results
        ordered_result_hash_map = {k: v for k, v in sorted(search_result_hash_map.items(), key=lambda item: item[1][1], reverse=reverse_signal)}
        return ordered_result_hash_map