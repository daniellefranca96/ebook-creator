from typing import Optional

import tiktoken
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
from langchain.tools import BaseTool

from api.tools.google_search_with_source import GoogleSearchAPIWithSourceWrapper


class CustomSearch(BaseTool):
    name = "CustomSearch"
    description = "useful for searching something on the internet"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def count(self, query):
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding.encode(query))

    def _run(
            self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        google_search = GoogleSearchAPIWithSourceWrapper()
        text = google_search.run(query)
        if self.count(text) > 1000:
            text = text[:1000]
        return text

    async def _arun(
            self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")
