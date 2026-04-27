import json
import os
import time
from collections import deque
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.config import settings


@dataclass
class ScrapedPage:
    url: str
    title: str
    text: str


class BankWebsiteScraper:
    """Scraper simple con BFS limitado al dominio base."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.target_base_url
        self.domain = urlparse(self.base_url).netloc
        self.headers = {"User-Agent": settings.user_agent}

    def _is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and parsed.netloc == self.domain

    def _extract_links(self, soup: BeautifulSoup, current_url: str) -> Iterable[str]:
        for tag in soup.find_all("a", href=True):
            href = tag.get("href")
            absolute_url = urljoin(current_url, href).split("#")[0]
            if self._is_valid_url(absolute_url):
                yield absolute_url

    def _extract_text(self, soup: BeautifulSoup) -> str:
        for element in soup(["script", "style", "noscript", "header", "footer"]):
            element.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return " ".join(text.split())

    def scrape(self, max_pages: int | None = None) -> list[ScrapedPage]:
        max_pages = max_pages or settings.max_pages
        visited = set()
        queue = deque([self.base_url])
        pages: list[ScrapedPage] = []

        while queue and len(pages) < max_pages:
            url = queue.popleft()
            if url in visited:
                continue
            visited.add(url)

            try:
                response = requests.get(url, headers=self.headers, timeout=settings.request_timeout)
                response.raise_for_status()
                if "text/html" not in response.headers.get("Content-Type", ""):
                    continue

                soup = BeautifulSoup(response.text, "lxml")
                title = soup.title.string.strip() if soup.title and soup.title.string else url
                text = self._extract_text(soup)

                if len(text) > 200:
                    pages.append(ScrapedPage(url=url, title=title, text=text))

                for link in self._extract_links(soup, url):
                    if link not in visited:
                        queue.append(link)

                time.sleep(0.2)
            except requests.RequestException as exc:
                print(f"[WARN] Error scraping {url}: {exc}")

        return pages

    def save_raw(self, pages: list[ScrapedPage]) -> str:
        os.makedirs(settings.raw_data_path, exist_ok=True)
        output_path = os.path.join(settings.raw_data_path, "scraped_pages.json")
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump([page.__dict__ for page in pages], file, ensure_ascii=False, indent=2)
        return output_path


if __name__ == "__main__":
    scraper = BankWebsiteScraper()
    pages = scraper.scrape()
    output_path = scraper.save_raw(pages)

    print(f"Páginas scrapeadas: {len(pages)}")
    print(f"Archivo guardado en: {output_path}")
