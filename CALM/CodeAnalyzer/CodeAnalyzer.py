from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
import re

class CodeAnalyzer:
    def __init__(self, model: str):
        self.patterns = [
            r'\* `(\w+)`\: (.+)',  # format: * `function_name`: description
            r'\d+\.\s`?(\w+)`: (.+)',  # format: 1. `function_name`: description or 1. function_name: description
            r'`?(\w+)`: (.+)',  # format: `function_name`: description or function_name: description
            r'\* `?(\w+)\(.*?\)`: (.+)',  # format: * `function_name(params)`: description or * function_name(params): description
            r'\d+\.\s`?(\w+)\(.*?\)`: (.+)',  # format: 1. `function_name(params)`: description or 1. function_name(params): description
            r'`?(\w+)\(.*?\)`: (.+)'  # format: `function_name(params)`: description or function_name(params): description
        ]


        self.model = model
        self.llm = Ollama(
            model=self.model,
            callback_manager=CallbackManager([])
        )
    
    def analyze_code(self, source_code):
        test_prompt = f'''
        Given the following Python code summarize each function, class, and major blocks of the code.
        Please provide concise and short step-by-step explanation of them.
        Also, please return them in key: value format. For example:
        "sort(my_list: list)": this is a function for sorting the input list
        ```python\n{source_code}```'''

        prefix = f'''You are an expert Python programmer, here is your task: {test_prompt}'''

        # Invoke the LLM and capture the result
        result = self.llm.invoke(prefix)
        return result
    
    def organize_output(self, llm_output: str):
        comments_map = {}

        for pattern in self.patterns:
            matches = re.findall(pattern, llm_output)
            if matches:
                for match in matches:
                    # match[0] is the function/class name, match[1] is the description
                    comments_map[match[0]] = match[1]

        if not comments_map:
            raise ValueError(f"No key-value pairs found in {self.model} output matching the desired patterns.")

        return comments_map
