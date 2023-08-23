import asyncio
from typing import List
import logging
from aiohttp import ServerDisconnectedError

from langchain.docstore.document import Document
from langchain.document_loaders import AsyncHtmlLoader
from typing import Any, Dict, Iterator, List, Optional, Union


logger = logging.getLogger(__name__)

class AsyncHTMLoaderFixed(AsyncHtmlLoader):

    def __init__(self, web_path: Union[str, List[str]], requests_per_second=2):
        super().__init__(web_path, requests_per_second=requests_per_second)

    def load(self) -> List[Document]:
        """Load text from the url(s) in web_path."""
        results = []
        try:
            results = asyncio.run(self.get_web_path_from_urls(self.web_paths))
        except:
            pass
        docs = []
        for i, text in enumerate(results):
            try:
                metadata = {"source": self.web_paths[i]}
                text = text+'Source: ' + self.web_paths[i]
                docs.append(Document(page_content=text, metadata=metadata))
            except:
                pass

        return docs

    async def get_web_path_from_urls(self, urls: List[str]) -> List[str]:
        """Load the HTML from the urls."""
        try:
            results = await self.fetch_all(self.web_paths)
        except ServerDisconnectedError as e:
            logger.error(f"Server disconnected when trying to access URLs: {e}")
            results = []
        return results