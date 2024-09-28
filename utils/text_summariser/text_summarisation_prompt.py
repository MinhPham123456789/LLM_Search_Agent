from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

PROMPT_TEMPLATES = {
    "web_content_sum_prompt":"""Extract the important points and summarise each information point with relevant details for the following:


"{docs}"


The concise summary must closely answer the query "%s". Do not create unrelated comment or note or question.
CONCISE SUMMARY:""",

    "combine_prompt": """Extract and summarise each information point along with relevant details separately for the following:


"{docs}"


The concise summary must straightforwardly answer the query "%s". Do not create unrelated comment or note or question.
CONCISE SUMMARY:"""
}

def build_summariser_chain(llm, query, prompt_type):
    # Map Reduce Prompt
    # query = "Odoo 12.0 LFI vulnerabilities exploit code"
    prompt_template = PROMPT_TEMPLATES[prompt_type]%(query)
    # prompt_template = "Write a concise summary of the following:\n\n\"{docs}\"\n\nThe concise summary must answer the query \"" + query +"\".\nCONCISE SUMMARY:"
    
    map_reduce_prompt = PromptTemplate(template=prompt_template, input_variables=["docs"])

    map_chain = LLMChain(llm=llm, prompt=map_reduce_prompt)
    reduce_chain = LLMChain(llm=llm, prompt=map_reduce_prompt)

    # print("old:")
    # print(reduce_chain)

    # map_chain = map_reduce_prompt | llm
    # reduce_chain = map_reduce_prompt | llm
    # print("new:")
    # print(reduce_chain)

    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )

    # Combines and iteratively reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        # This is final chain that is called.
        combine_documents_chain=combine_documents_chain,
        # If documents exceed context for `StuffDocumentsChain`
        collapse_documents_chain=combine_documents_chain,
        # The maximum number of tokens to group documents into.
        token_max=4096,
    )

    # Combining documents by mapping a chain over them, then combining results
    map_reduce_chain = MapReduceDocumentsChain(
        # Map chain
        llm_chain=map_chain,
        # Reduce chain
        reduce_documents_chain=reduce_documents_chain,
        # The variable name in the llm_chain to put the documents in
        document_variable_name="docs",
        # Return the results of the map steps in the output
        return_intermediate_steps=False,
    )
    return map_reduce_chain

