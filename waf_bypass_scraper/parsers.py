"""Parsers for different website types."""

import sys
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass
import re
import json
from trafilatura import extract
from trafilatura.metadata import Document


@dataclass
class RedditComment:
    """Represents a Reddit comment."""

    author: str
    text: str
    score: Optional[str]
    timestamp: Optional[str]


@dataclass
class RedditThread:
    """Represents a Reddit thread."""

    title: str
    author: str
    subreddit: str
    score: Optional[str]
    text: Optional[str]
    url: str
    comments: List[RedditComment]


class RedditParser:
    """Parser for Reddit threads."""

    def __init__(self, html_content: str):
        """
        Initialize parser with HTML content.

        Args:
            html_content: Raw HTML from Reddit
        """
        self.soup = BeautifulSoup(html_content, "lxml")

    def parse_thread(self, url: str) -> RedditThread:
        """
        Parse Reddit thread from HTML.

        Args:
            url: Original URL of the thread

        Returns:
            Parsed RedditThread object
        """
        # Extract thread title
        title = self._extract_title()

        # Extract subreddit
        subreddit = self._extract_subreddit(url)

        # Extract post author
        author = self._extract_author()

        # Extract post score
        score = self._extract_score()

        # Extract post text
        text = self._extract_post_text()

        # Extract comments
        comments = self._extract_comments()

        return RedditThread(
            title=title,
            author=author,
            subreddit=subreddit,
            score=score,
            text=text,
            url=url,
            comments=comments,
        )

    def _extract_title(self) -> str:
        """Extract thread title."""
        # Try multiple selectors for title (old and new Reddit)
        title_selectors = [
            "a.title",  # Old Reddit
            "h1",
            '[slot="title"]',
            'shreddit-post h1',
            '[data-testid="post-title"]',
            'p.title a.title',  # Old Reddit specific
        ]

        for selector in title_selectors:
            title_elem = self.soup.select_one(selector)
            if title_elem:
                return title_elem.get_text(strip=True)

        # Fallback to page title
        title_elem = self.soup.find("title")
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            # Remove " : r/subreddit" suffix if present
            title_text = re.sub(r"\s*:\s*r/\w+\s*$", "", title_text)
            return title_text

        return "Unknown Title"

    def _extract_subreddit(self, url: str) -> str:
        """Extract subreddit name from URL."""
        match = re.search(r"r/(\w+)", url)
        if match:
            return match.group(1)
        return "Unknown"

    def _extract_author(self) -> str:
        """Extract post author."""
        author_selectors = [
            'a.author',  # Old Reddit
            '[slot="authorName"]',
            'shreddit-post [slot="authorName"]',
            'a[href*="/user/"]',
            'p.tagline a.author',  # Old Reddit specific
        ]

        for selector in author_selectors:
            author_elem = self.soup.select_one(selector)
            if author_elem:
                return author_elem.get_text(strip=True).replace("u/", "")

        return "Unknown"

    def _extract_score(self) -> Optional[str]:
        """Extract post score/upvotes."""
        score_selectors = [
            'div.score.unvoted',  # Old Reddit
            'div.score',  # Old Reddit alternative
            '[slot="score"]',
            'shreddit-post [slot="score"]',
            '[data-testid="post-score"]',
        ]

        for selector in score_selectors:
            score_elem = self.soup.select_one(selector)
            if score_elem:
                return score_elem.get_text(strip=True)

        # Try to find score in attributes (old Reddit)
        score_elem = self.soup.select_one('[class*="score"]')
        if score_elem and score_elem.get('title'):
            return score_elem.get('title')

        return None

    def _extract_post_text(self) -> Optional[str]:
        """Extract post text content."""
        # Try to find post content (old and new Reddit)
        text_selectors = [
            'div.usertext-body',  # Old Reddit
            'div.md',  # Old Reddit markdown content
            '[slot="text-body"]',
            'div[data-testid="post-content"]',
            'shreddit-post div[slot="text-body"]',
            'form.usertext div.md',  # Old Reddit specific
        ]

        for selector in text_selectors:
            text_elem = self.soup.select_one(selector)
            if text_elem:
                # Get text with line breaks preserved
                return text_elem.get_text(separator="\n", strip=True)

        return None

    def _extract_comments(self) -> List[RedditComment]:
        """Extract comments from thread."""
        comments = []

        # Try to find comment elements (old and new Reddit)
        comment_selectors = [
            "div.comment",  # Old Reddit
            "div.entry",  # Old Reddit alternative
            "shreddit-comment",
            '[data-testid="comment"]',
            "div.Comment",
        ]

        comment_elements = []
        for selector in comment_selectors:
            comment_elements = self.soup.select(selector)
            if comment_elements:
                break

        # For old Reddit, we need to filter to only top-level divs with class "comment"
        if comment_elements and any("comment" in str(elem.get('class', [])) for elem in comment_elements):
            # Filter to direct comment divs, not nested ones
            filtered = []
            for elem in comment_elements:
                classes = elem.get('class', [])
                if 'comment' in classes and 'entry' not in classes:
                    filtered.append(elem)
            if filtered:
                comment_elements = filtered

        for idx, comment_elem in enumerate(comment_elements, start=1):
            try:
                # Extract comment author
                author = self._extract_comment_author(comment_elem)

                # Extract comment text
                text = self._extract_comment_text(comment_elem)

                # Skip if no text found
                if not text or not text.strip():
                    continue

                # Extract score
                score = self._extract_comment_score(comment_elem)

                # Extract timestamp
                timestamp = self._extract_comment_timestamp(comment_elem)

                comments.append(
                    RedditComment(
                        author=author,
                        text=text,
                        score=score,
                        timestamp=timestamp,
                    )
                )
            except Exception as e:
                # Warn about problematic comments but continue parsing
                print(f"Warning: Failed to parse comment #{idx}: {type(e).__name__}: {e}", file=sys.stderr)
                continue

        return comments

    def _extract_comment_author(self, comment_elem) -> str:
        """Extract author from comment element."""
        author_selectors = [
            'a.author',  # Old Reddit
            '[slot="authorName"]',
            'a[href*="/user/"]',
            'p.tagline a.author',  # Old Reddit specific
        ]

        for selector in author_selectors:
            author_elem = comment_elem.select_one(selector)
            if author_elem:
                return author_elem.get_text(strip=True).replace("u/", "")
        return "Unknown"

    def _extract_comment_text(self, comment_elem) -> Optional[str]:
        """Extract text from comment element."""
        text_selectors = [
            'div.md',  # Old Reddit
            'div.usertext-body div.md',  # Old Reddit specific
            '[slot="comment"]',
            'div[data-testid="comment-text"]',
        ]

        for selector in text_selectors:
            text_elem = comment_elem.select_one(selector)
            if text_elem:
                return text_elem.get_text(separator="\n", strip=True)
        return None

    def _extract_comment_score(self, comment_elem) -> Optional[str]:
        """Extract score from comment element."""
        score_selectors = [
            'span.score.unvoted',  # Old Reddit
            'span.score',  # Old Reddit alternative
            '[slot="score"]',
            '[data-testid="vote-score"]',
        ]

        for selector in score_selectors:
            score_elem = comment_elem.select_one(selector)
            if score_elem:
                text = score_elem.get_text(strip=True)
                # Old Reddit sometimes has "X points"
                text = re.sub(r'\s*points?$', '', text)
                return text
        return None

    def _extract_comment_timestamp(self, comment_elem) -> Optional[str]:
        """Extract timestamp from comment element."""
        time_selectors = [
            'time',
            'p.tagline time',  # Old Reddit
            '[slot="timestamp"]',
        ]

        for selector in time_selectors:
            time_elem = comment_elem.select_one(selector)
            if time_elem:
                # Try to get the title attribute first (absolute time)
                if time_elem.get('title'):
                    return time_elem.get('title')
                return time_elem.get_text(strip=True)
        return None


class GenericParser:
    """Generic HTML parser for non-specific websites."""

    def __init__(self, html_content: str):
        """
        Initialize parser with HTML content.

        Args:
            html_content: Raw HTML content
        """
        self.soup = BeautifulSoup(html_content, "lxml")

    def extract_text(self) -> str:
        """
        Extract main text content from page.

        Returns:
            Extracted text content
        """
        # Remove script and style elements
        for script in self.soup(["script", "style"]):
            script.decompose()

        # Get text
        text = self.soup.get_text(separator="\n", strip=True)

        # Clean up multiple newlines
        text = re.sub(r"\n\s*\n", "\n\n", text)

        return text

    def extract_links(self) -> List[Dict[str, str]]:
        """
        Extract all links from page.

        Returns:
            List of dictionaries with 'text' and 'url' keys
        """
        links = []
        for link in self.soup.find_all("a", href=True):
            links.append({"text": link.get_text(strip=True), "url": link["href"]})
        return links

    def extract_title(self) -> str:
        """
        Extract page title.

        Returns:
            Page title
        """
        title = self.soup.find("title")
        if title:
            return title.get_text(strip=True)
        return "No title found"


@dataclass
class TrafilaturaContent:
    """Represents content extracted by Trafilatura."""

    title: Optional[str]
    author: Optional[str]
    date: Optional[str]
    url: Optional[str]
    description: Optional[str]
    text: str
    markdown: str
    links: List[str]
    language: Optional[str]


class TrafilaturaParser:
    """
    Intelligent HTML parser using Trafilatura for content extraction.

    This parser uses Trafilatura to intelligently extract main content,
    removing boilerplate, navigation, ads, and other non-content elements.
    """

    def __init__(self, html_content: str, url: Optional[str] = None):
        """
        Initialize parser with HTML content.

        Args:
            html_content: Raw HTML content
            url: Original URL (used for converting relative links to absolute)
        """
        self.html_content = html_content
        self.url = url

    def extract_content(self) -> TrafilaturaContent:
        """
        Extract main content from page using Trafilatura.

        Returns:
            TrafilaturaContent object with extracted data
        """
        # Extract text content
        text_content = extract(
            self.html_content,
            output_format="txt",
            include_comments=False,
            url=self.url,
        ) or ""

        # Extract markdown with formatting and links
        markdown_content = extract(
            self.html_content,
            output_format="markdown",
            include_formatting=True,
            include_links=True,
            include_images=True,
            url=self.url,
        ) or ""

        # Extract metadata
        metadata = self._extract_metadata()

        # Extract links
        links = self._extract_links()

        return TrafilaturaContent(
            title=metadata.get("title"),
            author=metadata.get("author"),
            date=metadata.get("date"),
            url=metadata.get("url") or self.url,
            description=metadata.get("description"),
            text=text_content,
            markdown=markdown_content,
            links=links,
            language=metadata.get("language"),
        )

    def _extract_metadata(self) -> Dict[str, Optional[str]]:
        """Extract metadata from the HTML content."""
        from trafilatura import bare_extraction

        # Use bare_extraction to get metadata
        result = bare_extraction(
            self.html_content,
            url=self.url,
            with_metadata=True,
        )

        if result:
            return {
                "title": result.get("title"),
                "author": result.get("author"),
                "date": result.get("date"),
                "url": result.get("url"),
                "description": result.get("description"),
                "language": result.get("language"),
            }

        return {
            "title": None,
            "author": None,
            "date": None,
            "url": None,
            "description": None,
            "language": None,
        }

    def _extract_links(self) -> List[str]:
        """Extract all links from content."""
        from trafilatura import bare_extraction

        result = bare_extraction(
            self.html_content,
            include_links=True,
            url=self.url,
        )

        if result and "links" in result:
            return result.get("links", [])

        return []
