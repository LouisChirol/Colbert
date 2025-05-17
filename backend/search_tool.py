import time
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from loguru import logger


class WebsiteSearchTool:
    def __init__(self, preferred_websites: Optional[List[str]] = None):
        self.search = DuckDuckGoSearchRun()
        self.preferred_websites = preferred_websites or [
            "service-public.fr",
            "legifrance.gouv.fr",
            "ants.gouv.fr",
            "gouvernement.fr",
        ]
        self.last_search_time = 0
        self.min_delay = 2  # Minimum delay between searches in seconds

    def _filter_results(self, query: str, results: str) -> str:
        """Filter search results to only include preferred websites."""
        if not self.preferred_websites:
            return results

        filtered_lines = []
        for line in results.split("\n"):
            if any(website in line.lower() for website in self.preferred_websites):
                filtered_lines.append(line)

        return "\n".join(filtered_lines) if filtered_lines else results

    def _fallback_search(self, query: str) -> str:
        """Fallback search using direct requests to service-public.fr."""
        try:
            # Add French government websites to the search
            search_url = "https://www.service-public.fr/particuliers/vosdroits/N358"
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.get_text()

            # Extract relevant information
            relevant_info = []
            for website in self.preferred_websites:
                if website in content.lower():
                    relevant_info.append(f"Information trouvée sur {website}")

            return (
                "\n".join(relevant_info)
                if relevant_info
                else "Aucune information trouvée sur les sites préférés."
            )

        except Exception as e:
            logger.error(f"Error during fallback search: {str(e)}")
            return ""

    def search_web(self, query: str) -> str:
        """Search the web and filter results based on preferred websites."""
        try:
            # Add delay between searches to avoid rate limits
            current_time = time.time()
            time_since_last_search = current_time - self.last_search_time
            if time_since_last_search < self.min_delay:
                time.sleep(self.min_delay - time_since_last_search)

            self.last_search_time = time.time()

            try:
                results = self.search.run(query)
                filtered_results = self._filter_results(query, results)
                if filtered_results:
                    return filtered_results
            except Exception as e:
                logger.warning(f"DuckDuckGo search failed: {str(e)}")

            # If DuckDuckGo fails or returns no results, try fallback
            fallback_results = self._fallback_search(query)
            if fallback_results:
                return fallback_results

            return (
                "Désolé, je n'ai pas pu trouver d'informations pertinentes. "
                "Veuillez consulter directement le site service-public.fr pour des informations à jour."
            )

        except Exception as e:
            logger.error(f"Error during web search: {str(e)}")
            return "Désolé, une erreur est survenue lors de la recherche web."

    def get_tool(self) -> Tool:
        """Return the search tool for use in the agent."""
        return Tool(
            name="web_search",
            description="Search the web for information, focusing on French government websites.",
            func=self.search_web,
        )
