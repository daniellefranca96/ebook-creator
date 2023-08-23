import re
from typing import List
from typing import Optional

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain.prompts import PromptTemplate
from api.tools.web_research import WebResearchRetrieverFixed
from langchain.schema.language_model import BaseLanguageModel
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.vectorstores import VectorStore
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)

load_dotenv()


class LineList(BaseModel):
    """List of questions."""

    lines: List[str] = Field(description="Questions")


class QuestionListOutputParser(PydanticOutputParser):
    """Output parser for a list of numbered questions."""

    def __init__(self) -> None:
        super().__init__(pydantic_object=LineList)

    def parse(self, text: str) -> LineList:
        lines = re.findall(r"\d+\..*?\n", text)
        return LineList(lines=lines)


class WebRetrieverTool(BaseTool):
    name = "CustomSearch"
    description = "useful for searching something on the internet"

    llm_chain: LLMChain = None
    web_research_retriever: WebResearchRetrieverFixed = None
    llm: BaseLanguageModel = None
    prompt: PromptTemplate = None
    vectorstore: VectorStore = None
    search: GoogleSearchAPIWrapper = None

    def __init__(self, llm: BaseLanguageModel, vectorstore: VectorStore, prompt: PromptTemplate = None):
        super().__init__()
        self.set_llm(llm)
        self.set_prompt(prompt)
        self.set_vectorstore(vectorstore)
        self.llm_chain = self.get_chain()
        self.search = GoogleSearchAPIWrapper()
        self.web_research_retriever = self.get_web_search_retriever()

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool synchronously."""
        return str(self.web_research_retriever.get_relevant_documents(query))

    async def _arun(
            self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")

    def set_llm(self, llm: BaseLanguageModel):
        self.llm = llm

    def set_prompt(self, prompt: PromptTemplate):
        self.prompt = prompt if prompt is not None else self.get_prompt()

    def set_vectorstore(self, vectorstore: VectorStore):
        if vectorstore is None:
            raise ValueError("Vectorstore must be provided")
        self.vectorstore = vectorstore

    def get_chain(self) -> LLMChain:
        return LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            output_parser=QuestionListOutputParser(),
        )

    def get_web_search_retriever(self) -> WebResearchRetrieverFixed:
        return WebResearchRetrieverFixed(
            vectorstore=self.vectorstore,
            llm_chain=self.llm_chain,
            search=self.search,
            num_search_results=1
        )


    def get_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["question"],
            template="""You are an assistant tasked with improving Google search
        results. Generate FIVE Google search queries about the input. The output should be a numbered list of questions and each
        should have a question mark at the end: {question}""",
        )
