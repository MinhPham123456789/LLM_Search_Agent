from langchain_core.prompts import ChatPromptTemplate
from agents.react.prompt import *
from langchain_community.llms import HuggingFaceEndpoint
from langchain.callbacks.tracers import ConsoleCallbackHandler
from agents.agent_utils import manage_tools
from agents.react.output_parser import ReActAgentParser

class Custom_ReAct_Agent:
    def __init__(self, model_name: str, tools:dict, callback, max_iter_num:int = 5):
        self.tools = manage_tools(tools)
        self.memory = ''
        self.llm = HuggingFaceEndpoint(
            repo_id = model_name, 
            callbacks=[callback],
            stream=True, 
            stop_sequences=["##Observation:", "##Query:", "## Query:", "# Query:"])
        self.max_iter_num = max_iter_num
        self.prompt = None
        self.parser = ReActAgentParser()

    def add_memory(self, data):
        self.memory = f'{self.memory}{data}\n'
    
    def get_memory(self):
        return self.memory
    
    def run_action(self, action_dict):
        result, search_result_dict = self.tools[action_dict['action']].run(action_dict['action_input'])
        result = result.replace('{', "{{").replace('}', "}}") # Escape {} for prompt template
        return result, search_result_dict

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

    def create_concluding_prompt(self):
        concluding_system_prompt = CONCLUDING_PROMPT_SYSTEM.format(**{
            "memory": self.memory,
        })
        concluding_human_prompt = CONCLUDING_PROMPT_HUMAN
        return ChatPromptTemplate.from_messages(
            [("system",concluding_system_prompt), ("user", concluding_human_prompt)]
        )

    def chat_conclude(self, user_input):
        agent_concluding_prompt = self.create_concluding_prompt()
        chain = agent_concluding_prompt | self.llm
        chain_output = chain.invoke({"input": user_input})#, config={"callbacks":[ConsoleCallbackHandler()]})
        self.add_memory(f'##Conclusion: {chain_output}')
        # print(f'##Conclusion: {chain_output}')

    def chat(self, user_input, DEBUG=not True):
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
        search_result_dict_list = []
        for i in range(0, self.max_iter_num):
            print(f"#########COUNT: {i}")
            agent_prompt = self.create_prompt()
            chain = agent_prompt | self.llm
            chain_output = chain.invoke({"input": user_input})#, config={"callbacks":[ConsoleCallbackHandler()]})
            parsed_llm_response = self.parser.extract_llm_response(chain_output)
            # print(parsed_llm_response)
            if parsed_llm_response.get("Final Answer") is not None:
                if DEBUG:
                    print(f"##Final Answer: {parsed_llm_response['Final Answer']}")
                self.add_memory(f"##Final Answer: {parsed_llm_response['Final Answer']}")
                self.chat_conclude(user_input)
                break
            observation, search_result_dict = self.run_action(parsed_llm_response)
            search_result_dict_list.append(search_result_dict)
            parsed_llm_response['observation'] = observation

            if DEBUG:
                print(chain_output)
                print(f'##Observation: {observation}\n\n')
                for k in search_result_dict.keys():
                    print(f"{search_result_dict[k]['url']} {search_result_dict[k]['score']}")
                    print(f"{search_result_dict[k]['summary']}")
            
            # Update memory
            new_memory = """##Thought: {thought}
##Action: {action}
##Action Input: {action_input}
##Observation: {observation}

##Thought: 
""".format(**parsed_llm_response)
            self.add_memory(new_memory)
        print(f"Memory: {self.memory}")
        return self.memory, search_result_dict_list
