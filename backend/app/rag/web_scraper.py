
# app/rag/web_scraper.py

import os
import logging
from typing import List, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# from app.rag.web_scraper import extract_course_catalog, fetch_page, get_internal_links, normalize_url, should_skip_url, split_documents

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# WEBSITE CONFIGURATION
# ---------------------------------------------------------

SETTRIBE_URL = os.getenv("SETTRIBE_WEBSITE_URL", "").strip()
STEP_URL = os.getenv("STEP_WEBSITE_URL", "").strip()

REQUEST_TIMEOUT = int(os.getenv("WEB_REQUEST_TIMEOUT", "15"))
MAX_PAGES = int(os.getenv("WEB_MAX_PAGES", "50"))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
    )
}

# ---------------------------------------------------------
# PAGES TO SKIP
# ---------------------------------------------------------

SKIP_PATHS = {
    "/login",
    "/login.php",
    "/iac",
    "/gallery",
    "/blog",
    "/career",
    "/testimonials",
    "/book_slot.php",
    "/courses/book_slot.php",
}


def should_skip_url(url: str) -> bool:
    """
    Return True for website pages that are not useful
    for the student/course RAG knowledge base.
    """

    parsed = urlparse(url)
    path = parsed.path.lower().rstrip("/")

    if path in SKIP_PATHS:
        return True

    # Skip Cloudflare email-protection URLs
    if "/cdn-cgi/" in path:
        return True

    return False


# ---------------------------------------------------------
# URL HELPERS
# ---------------------------------------------------------

def normalize_url(url: str) -> str:
    """Normalize a URL so duplicate pages are avoided."""

    url = url.strip()

    if url.endswith("/"):
        url = url[:-1]

    return url


def is_same_domain(url: str, base_url: str) -> bool:
    """Check whether URL belongs to the same website."""

    return urlparse(url).netloc == urlparse(base_url).netloc


# ---------------------------------------------------------
# FETCH WEBPAGE
# ---------------------------------------------------------

def fetch_page(url: str) -> str:
    """Download a webpage and return cleaned text."""

    if should_skip_url(url):
        logger.info("Skipping irrelevant page: %s", url)
        return ""

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove elements that are normally not useful for RAG
        for element in soup(
            ["script", "style", "noscript", "svg", "header", "footer"]
        ):
            element.decompose()

        text = soup.get_text(separator="\n")

        lines = []

        for line in text.splitlines():
            line = " ".join(line.split())

            if line:
                lines.append(line)

        return "\n".join(lines)

    except requests.RequestException as exc:
        logger.warning("Could not fetch %s: %s", url, exc)
        return ""


# ---------------------------------------------------------
# FIND LINKS
# ---------------------------------------------------------

def get_internal_links(url: str, base_url: str) -> Set[str]:
    """Find internal links from a webpage."""

    links = set()

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all("a", href=True):

            href = tag.get("href")

            if not href:
                continue

            full_url = urljoin(url, href)

            # Remove fragments
            full_url = full_url.split("#")[0]

            # Only HTTP/HTTPS
            if not full_url.startswith(("http://", "https://")):
                continue

            # Only same-domain pages
            if not is_same_domain(full_url, base_url):
                continue

            # Ignore common files
            if full_url.lower().endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif",
                    ".svg",
                    ".pdf",
                    ".zip",
                    ".mp4",
                    ".mp3",
                )
            ):
                continue

            full_url = normalize_url(full_url)

            # Skip irrelevant pages before adding them to queue
            if should_skip_url(full_url):
                continue


            links.add(full_url)

    except requests.RequestException as exc:
        logger.warning("Could not find links on %s: %s", url, exc)

    return links


# ---------------------------------------------------------
# SCRAPE WEBSITE
# ---------------------------------------------------------

def scrape_website(
    website_url: str,
    source_name: str,
    max_pages: int = MAX_PAGES,
) -> List[Document]:
    """
    Extract course names listed in the website's course-selection
    dropdowns/forms.

    IMPORTANT:
    This creates a catalog of course names only.
    It does NOT invent duration, fees, tools, skills, syllabus,
    eligibility, or any other course details.
    """

    if not website_url:
        logger.warning(
            "%s website URL is not configured.", 
            source_name
        )
        return []

    start_url = normalize_url(website_url)

    visited = set()
    queue = [start_url]
    documents = []

    while queue and len(visited) < max_pages:

        current_url = queue.pop(0)

        if current_url in visited:
            continue

        visited.add(current_url)

        logger.info(
            "[%s] Scraping %s (%s/%s)",
            source_name,
            current_url,
            len(visited),
            max_pages,
        )

        text = fetch_page(current_url)

        if text:

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": source_name,
                        "source_url": current_url,
                        "content_type": "website",
                    },
                )
            )

        # Discover additional internal pages
        links = get_internal_links(
            current_url,
            start_url,
        )

        for link in links:

            if link not in visited and link not in queue:
                queue.append(link)

    logger.info(
        "%s: scraped %s pages",
        source_name,
        len(documents),
    )

    return documents


# ---------------------------------------------------------
# SPLIT WEBSITE CONTENT
# ---------------------------------------------------------

def split_documents(
    documents: List[Document],
) -> List[Document]:
    """Split webpage content into RAG-friendly chunks."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
        ],
    )

    chunks = splitter.split_documents(documents)

    # Add useful chunk metadata
    for index, chunk in enumerate(chunks):

        chunk.metadata["chunk_id"] = index

    logger.info(
        "Created %s chunks from %s documents",
        len(chunks),
        len(documents),
    )

    return chunks

# ---------------------------------------------------------
# COURSE CATALOG FROM WEBSITE
# ---------------------------------------------------------

def extract_course_catalog(
    website_url: str,
    source_name: str,
) -> List[Document]:
    """
    Extract course names listed in the website's course-selection
    dropdowns/forms.

    IMPORTANT:
    This creates a catalog of course names only.
    It does NOT invent duration, fees, tools, skills, syllabus,
    or any other course details.
    """

    if not website_url:
        logger.warning(
            "%s website URL is not configured.",
            source_name,
        )
        return []

    try:
        response = requests.get(
            website_url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        course_names = []

        # Look through select dropdowns
        for select in soup.find_all("select"):

            for option in select.find_all("option"):

                course_name = option.get_text(
                    " ",
                    strip=True,
                )

                if not course_name:
                    continue

                normalized = course_name.lower().strip()

                # Ignore placeholder options
                if normalized in {
                    "select",
                    "select course",
                    "select course *",
                    "select course*",
                    "select qualification",
                    "class 12th or below",
                    "12th or below",
                    "undergraduate",
                    "graduate",
                    "post graduate",
                    "postgraduate",
                    "diploma",
                    "phd",
                    "other",
                    
                }:
                    continue

                if course_name not in course_names:
                    course_names.append(course_name)

        if not course_names:
            logger.info(
                "%s: no course options found.",
                source_name,
            )
            return []

        catalog_text = (
            f"{source_name} Course Catalog\n\n"
            "The following course options are listed on the official "
            f"{source_name} website:\n\n"
        )

        for index, course_name in enumerate(
            course_names,
            start=1,
        ):
            catalog_text += (
                f"{index}. {course_name}\n"
            )

        catalog_text += (
            "\nImportant:\n"
            "The course names above are course options listed on the "
            "official website. Detailed information such as duration, "
            "fees, mode, location, tools, skills, syllabus, projects "
            "or eligibility should only be provided when that "
            "information is available in the knowledge base."
        )

        logger.info(
            "%s: found %s course options.",
            source_name,
            len(course_names),
        )

        return [
            Document(
                page_content=catalog_text,
                metadata={
                    "source": source_name,
                    "source_url": normalize_url(website_url),
                    "content_type": "course_catalog",
                },
            )
        ]

    except requests.RequestException as exc:
        logger.warning(
            "Could not extract course catalog from %s: %s",
            website_url,
            exc,
        )

        return []
    


# ---------------------------------------------------------
# MAIN WEBSITE LOADER
# ---------------------------------------------------------

def load_website_documents() -> List[Document]:
    """
    Scrape SETTribe and STEP websites,
    then return split LangChain Documents.
    """

    all_documents = []

    # SETTribe
    if SETTRIBE_URL:
        settribe_docs = scrape_website(
            website_url=SETTRIBE_URL,
            source_name="SETTribe",
        )

        all_documents.extend(settribe_docs)

        # Extract course options listed on SETTribe
        settribe_catalog = extract_course_catalog(
            website_url=SETTRIBE_URL,
            source_name="SETTribe",
        )

        all_documents.extend(settribe_catalog)


    # STEP
    if STEP_URL:
        step_docs = scrape_website(
            website_url=STEP_URL,
            source_name="STEP",
        )

        all_documents.extend(step_docs)

        # Extract course options listed on STEP
        step_catalog = extract_course_catalog(
            website_url=STEP_URL,
            source_name="STEP",
        )

        all_documents.extend(step_catalog)


    if not all_documents:
        logger.warning("No website documents were loaded.")
        return []

    return split_documents(all_documents)


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    documents = load_website_documents()

    print("\n======================================")
    print("WEBSITE SCRAPER TEST")
    print("======================================")
    print(f"Documents/chunks: {len(documents)}")

    for document in documents[:3]:

        print("\nSOURCE:")
        print(document.metadata.get("source"))

        print("\nURL:")
        print(document.metadata.get("source_url"))

        print("\nCONTENT:")
        print(document.page_content[:500])

        print("--------------------------------------")








        