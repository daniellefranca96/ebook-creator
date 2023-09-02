import logging
from typing import List

from langchain.callbacks.manager import (
    CallbackManagerForRetrieverRun,
)
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.document_transformers import Html2TextTransformer
from langchain.prompts import PromptTemplate
from langchain.retrievers.web_research import WebResearchRetriever
from langchain.schema import Document

from api.tools.async_html_loader import AsyncHTMLoaderFixed

logger = logging.getLogger(__name__)
class WebResearchRetrieverFixed(WebResearchRetriever):

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        """Search Google for documents related to the query input.

        Args:
            query: user query

        Returns:
            Relevant documents from all various urls.
        """

        # Get search questions
        logger.info("Generating questions for Google Search ...")
        result = self.llm_chain({"question": query})
        logger.info(f"Questions for Google Search (raw): {result}")
        questions = getattr(result["text"], "lines", [])
        logger.info(f"Questions for Google Search: {questions}")

        # Get urls
        logger.info("Searching for relevat urls ...")
        urls_to_look = []
        for query in questions:
            # Google search
            search_results = self.search_tool(query, self.num_search_results)
            logger.info("Searching for relevat urls ...")
            logger.info(f"Search results: {search_results}")
            for res in search_results:
                urls_to_look.append(res["link"])

        # Relevant urls
        urls = set(urls_to_look)

        # Check for any new urls that we have not processed
        new_urls = list(urls.difference(self.url_database))

        logger.info(f"New URLs to load: {new_urls}")
        # Load, split, and add new urls to vectorstore
        if new_urls:
            loader = AsyncHTMLoaderFixed(new_urls, requests_per_second=5)
            html2text = Html2TextTransformer()
            logger.info("Indexing new urls...")
            docs = loader.load()
            if len(docs) > 0:
                docs = list(html2text.transform_documents(docs))
                docs = self.text_splitter.split_documents(docs)
                self.vectorstore.add_documents(docs)
                self.url_database.extend(new_urls)

        # Search for relevant splits
        # TODO: make this async
        logger.info("Grabbing most relevant splits from urls...")
        docs = []
        for query in questions:
            docs.extend(self.vectorstore.similarity_search(query+"please quote sources when possible"))

        # Get unique docs
        unique_documents_dict = {
            (doc.page_content, tuple(sorted(doc.metadata.items()))): doc for doc in docs
        }
        unique_documents = list(unique_documents_dict.values())
        return self.summarize(unique_documents, query)


    def summarize(self, docs, query):
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
        prompt_template = """Extract the main parts of the text and write an comprehensive summary explaining them with less words possible but still passing same content
        "{text}"
        SUMMARY:"""
        prompt = PromptTemplate.from_template(prompt_template)
        llm_chain = LLMChain(llm=llm, prompt=prompt)

        text = ""
        for d in docs:
            text = text + llm_chain.run(d)

        return docs
