# from pydantic import BaseModel, Field
from langchain_core.exceptions import OutputParserException
import re

# class ActionParser(BaseModel):
#     action: str = Field(description="The tool name to complete an Action")
#     action_input: str = Field(description="The data to give to the tool to run an Action")

class ReActAgentParser():
    def __init__(self):
        self.thought_re_pattern = r'^#Thought: (.*?)$'
        self.action_re_pattern = r'^#action: (.*?)$'
        self.action_input_re_pattern = r'^#action_input: \"*(.*?)\"*$'
        self.final_answer_re_pattern = r'^#Final Answer:\s*\n*(.*?)$'

    def extract_thought(self, text):
        re_match = re.search(self.thought_re_pattern, text, re.MULTILINE)
        if re_match is None:
            return {"thought": ''}
        thought_str = re_match.group(1)
        return {"thought": thought_str}

    def extract_action(self, text):
        re_action_match = re.search(self.action_re_pattern, text, re.MULTILINE)
        re_action_input_match = re.search(self.action_input_re_pattern, text, re.MULTILINE)
        if re_action_match is None or re_action_input_match is None:
            raise OutputParserException(f"Could not parse LLM Output: {text}")
        action_str = re_action_match.group(1)
        action_input_str = re_action_input_match.group(1)
        return {"action": action_str, "action_input": action_input_str}
    
    def extract_final_answer(self, text):
        re_final_answer_match = re.search(self.final_answer_re_pattern, text, re.MULTILINE)
        if re_final_answer_match is None:
            raise OutputParserException(f"Could not parse LLM Output: {text}")
        final_answer_str = re_final_answer_match.group(1)
        return {"Final Answer": final_answer_str}
    
    def extract_llm_response(self, text):
        extracted_llm_response = {}
        extracted_llm_response.update(self.extract_thought(text))
        if "Final Answer" in text:
            extracted_llm_response.update(self.extract_final_answer(text))
        elif "action" in text and "action_input" in text:
            extracted_llm_response.update(self.extract_action(text))
        else:
            raise OutputParserException(f"Could not parse LLM Output: {text}")
        return extracted_llm_response

