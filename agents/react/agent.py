from langchain_core.prompts import ChatPromptTemplate
from agents.react.prompt import *
from langchain_community.llms import HuggingFaceEndpoint
from langchain.callbacks.tracers import ConsoleCallbackHandler
from agents.agent_utils import manage_tools

class Custom_ReAct_Agent:
    def __init__(self, model_name: str, tools:dict, max_iter_num:int = 5):
        self.tools = manage_tools(tools)
        self.memory = ''
        self.llm = HuggingFaceEndpoint(repo_id = model_name, stream=True)
        self.max_iter_num = max_iter_num
        self.prompt = None

    def create_prompt(self):
        tool_descs = "\n".join([f"{self.tools[k].name}: {self.tools[k].description}" for k in self.tools.keys()])
        tool_names = ", ".join([self.tools[k].name for k in self.tools.keys()])
        system_message_prefix = SYSTEM_MESSAGE_PREFIX.format(**{
            "max_iter_num": self.max_iter_num
        })

        format_instructions = FORMAT_INSTRUCTIONS.format(**{
            "tool_names": tool_names,
            "max_iter_num": self.max_iter_num
        })

        system_prompt = "\n\n".join(
            [
                system_message_prefix,
                tool_descs,
                format_instructions,
                SYSTEM_MESSAGE_SUFFIX
            ]
        )
        human_prompt = HUMAN_MESSAGE
        self.prompt = ChatPromptTemplate.from_messages(
            [("system",system_prompt), ("user", human_prompt)]
        )
        return self.prompt
        

    def add_memory(self, data):
        self.memory = f'{self.memory}{data}\n'
    
    def get_memory(self):
        return self.memory
    
    def chat(self, user_input):
        agent_prompt = self.create_prompt()
        chain = agent_prompt | self.llm
        print(chain.invoke({"input": user_input}, config={"callbacks":[ConsoleCallbackHandler()]}))