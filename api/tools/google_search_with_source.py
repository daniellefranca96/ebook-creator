"""Util that calls Google Search."""

from langchain.utilities import GoogleSearchAPIWrapper


class GoogleSearchAPIWithSourceWrapper(GoogleSearchAPIWrapper):

    def run(self, query: str) -> str:
        """Run query through GoogleSearch and parse result."""
        snippets = []
        results = self._google_search_results(query, num=self.k)
        if len(results) == 0:
            return "No good Google Search Result was found"
        for result in results:
            if "snippet" and "link" in result:
                snippets.append(result["snippet"] + "\nLink:" + result["link"])

        return " ".join(snippets)
