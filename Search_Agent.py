from langchain_community.llms import HuggingFaceEndpoint
from langchain.agents import initialize_agent, AgentType

class Search_Agent:
    def __init__(self, tools:list, agent_model_name="google/gemma-7b", summarisation_model_name="meta-llama/Meta-Llama-3-8B-Instruct") -> None:
        self.agent_llm = HuggingFaceEndpoint(repo_id=agent_model_name, streaming=True)
        self.summarisation_llm = HuggingFaceEndpoint(repo_id=summarisation_model_name)
        self.tools = tools
        self.agent = initialize_agent(tools=self.tools,
                       llm=self.agent_llm,
                       agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                      #  verbose=True,
                       max_iterations=5,
                       handle_parsing_errors=True)
        
    async def stream_chat(self, query):
        chunks = []
        async for chunk in self.agent.astream({"input": query}):
            chunks.append(chunk)
            if 'actions' in chunk:
                for action in chunk['actions']:
                    print(action.log)
            elif 'steps' in chunk:
                for step in chunk['steps']:
                    print(step.observation)
                    print('###')
            elif 'output' in chunk:
                print(chunk['output'])
            else:
                print(chunk)
        return chunks

    