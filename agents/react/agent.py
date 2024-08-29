from langchain_core.prompts import ChatPromptTemplate
from agents.react.prompt import *
from langchain_community.llms import HuggingFaceEndpoint
from langchain.callbacks.tracers import ConsoleCallbackHandler
from agents.agent_utils import manage_tools
from agents.react.output_parser import ReActAgentParser

class Custom_ReAct_Agent:
    def __init__(self, model_name: str, tools:dict, max_iter_num:int = 5):
        self.tools = manage_tools(tools)
        self.memory = ''
        self.llm = HuggingFaceEndpoint(repo_id = model_name, stream=True, stop_sequences=["#Observation:", "#Query:", "# Query:"])
        self.max_iter_num = max_iter_num
        self.prompt = None
        self.parser = ReActAgentParser()

    def add_memory(self, data):
        self.memory = f'{self.memory}{data}\n'
    
    def get_memory(self):
        return self.memory
    
    def run_action(self, action_dict):
        result = self.tools[action_dict['action']].run(action_dict['action_input'])
        result = result.replace('{', "{{").replace('}', "}}") # Escape {} for prompt template
        return result

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

        # Add in memory/completed actions
        human_prompt = "\n\n".join(
            [
                HUMAN_MESSAGE,
                self.get_memory()
            ]
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [("system",system_prompt), ("user", human_prompt)]
        )
        return self.prompt

    def chat(self, user_input):
        # Head start Search action
#         head_start_search_result = self.tools["Search"].run(user_input)
#         # Inject memory
#         inject_memory = """Thought: Research on {input}.
# Action:
# ```
# {{
#   "action": "Search",
#   "action_input": "{input}"
# }}
# ```
# Observation: """
#         inject_memory = f'{inject_memory}{head_start_search_result}\nThought: '
#         self.add_memory(inject_memory)
        # Create agent prompt
        for i in range(0, self.max_iter_num):
            print(f"#########COUNT: {i}")
            agent_prompt = self.create_prompt()
            chain = agent_prompt | self.llm
            chain_output = chain.invoke({"input": user_input}) #s, config={"callbacks":[ConsoleCallbackHandler()]})
            # print("AAAAAAAAAAAAA")
            print(chain_output)
            # print("BBBBBBBBBBBBBBB")
            parsed_llm_response = self.parser.extract_llm_response(chain_output)
            # print(parsed_llm_response)
            if parsed_llm_response.get("Final Answer") is not None:
                print(f"#Final Answer: {parsed_llm_response['Final Answer']}")
                break
            observation = self.run_action(parsed_llm_response)
            parsed_llm_response['observation'] = observation
            print(f'#Observation: {observation}\n\n')
            # Update memory
            new_memory = """#Thought: {thought}
#action: {action},
#action_input: {action_input}
#Observation: {observation}

#Thought: 
""".format(**parsed_llm_response)
            self.add_memory(new_memory)
