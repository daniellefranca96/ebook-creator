import json
import re

from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.prompts.chat import HumanMessage
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from api.tools.custom_search import CustomSearch
from api.tools.webretrievertool import WebRetrieverTool


class Creator:

    def __init__(self):
        self.gpt4 = ChatOpenAI(temperature=0, model_name='gpt-4-0613')
        self.gpt3 = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo-16k-0613')
        self.davinci = OpenAI(temperature=0, model_name='text-davinci-003')
        self.vectorstore = Chroma(embedding_function=OpenAIEmbeddings(),persist_directory="./chroma_db_oai")

    def get_zero_shot_agent(self, tools: list):
        return initialize_agent(tools, self.gpt4, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, handle_parsing_errors=True)

    def get_prompt(self, name:str):
        prompt = ""
        with open(f"./api/prompts/{name}.txt", "r") as f:
            prompt = f.read()
        return prompt

    def tool_search(self):
        return WebRetrieverTool(self.gpt3, self.vectorstore)

    def validate_json(self, json_string, format):
        response = self.gpt3(messages=[HumanMessage(content=
                                                   f"Only return the json from following text, if not a valid json correct it and return it in this format {format}: " + json_string)])
        return self.extract_json_from_text(dict(response)['content'])

    def extract_json_from_text(self, text: str, start="{", end="}") -> dict:
        pattern = r'' + re.escape(start) + '.*' + re.escape(end)
        match = re.search(pattern, text, re.DOTALL)
        if match is not None:
            return json.loads(match.group())
        return None

