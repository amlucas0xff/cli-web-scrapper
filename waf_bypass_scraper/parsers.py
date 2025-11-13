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


@dataclass
class YouTubeComment:
    """Represents a YouTube comment."""

    author: str
    text: str
    likes: Optional[str]
    timestamp: Optional[str]
    is_pinned: bool = False
    is_hearted: bool = False


@dataclass
class YouTubeVideo:
    """Represents a YouTube video."""

    title: str
    channel_name: str
    description: str
    description_links: List[Dict[str, str]]  # [{"text": "...", "url": "..."}]
    view_count: Optional[str]
    upload_date: Optional[str]
    like_count: Optional[str]
    video_id: str
    url: str
    comments: Optional[List[YouTubeComment]] = None
    comments_truncated: bool = False


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
        # IMPORTANT: Must exclude sidebar content which also has usertext-body class
        text_selectors = [
            'div.expando div.usertext-body',  # Old Reddit - post content (not sidebar)
            'div.expando div.md',  # Old Reddit markdown content in post
            'form.usertext div.md',  # Old Reddit specific
            '[slot="text-body"]',  # New Reddit
            'div[data-testid="post-content"]',  # New Reddit
            'shreddit-post div[slot="text-body"]',  # New Reddit
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


class YouTubeParser:
    """Parser for YouTube videos."""

    def __init__(self, html_content: str, scraper=None):
        """
        Initialize parser with HTML content.

        Args:
            html_content: Raw HTML from YouTube
            scraper: WAFBypassScraper instance for making additional requests
        """
        self.html_content = html_content
        self.scraper = scraper
        self.yt_initial_data = None
        self._extract_initial_data()

    def _extract_initial_data(self) -> None:
        """Extract ytInitialData JSON from HTML."""
        pattern = r'var ytInitialData = ({.*?});'
        match = re.search(pattern, self.html_content, re.DOTALL)

        if match:
            try:
                self.yt_initial_data = json.loads(match.group(1))
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse ytInitialData: {e}", file=sys.stderr)
                self.yt_initial_data = None
        else:
            print("Warning: Could not find ytInitialData in HTML", file=sys.stderr)

    def parse_video(self, url: str, include_comments: bool = False,
                   comment_char_limit: int = 50000) -> YouTubeVideo:
        """
        Parse YouTube video from HTML.

        Args:
            url: Original URL of the video
            include_comments: Whether to fetch and include comments
            comment_char_limit: Maximum characters for all comments combined

        Returns:
            Parsed YouTubeVideo object
        """
        if not self.yt_initial_data:
            raise ValueError("Failed to extract YouTube data from page")

        video_id = self._extract_video_id(url)
        video_details = self._get_video_details()

        title = self._extract_title(video_details)
        channel_name = self._extract_channel_name()
        description = self._extract_description()
        description_links = self._extract_description_links()
        view_count = self._extract_view_count(video_details)
        upload_date = self._extract_upload_date(video_details)
        like_count = self._extract_like_count()

        comments = None
        comments_truncated = False
        if include_comments and self.scraper:
            comments, comments_truncated = self._extract_comments(
                video_id, comment_char_limit
            )

        return YouTubeVideo(
            title=title,
            channel_name=channel_name,
            description=description,
            description_links=description_links,
            view_count=view_count,
            upload_date=upload_date,
            like_count=like_count,
            video_id=video_id,
            url=url,
            comments=comments,
            comments_truncated=comments_truncated,
        )

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be/([0-9A-Za-z_-]{11})',
            r'embed/([0-9A-Za-z_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        raise ValueError(f"Could not extract video ID from URL: {url}")

    def _get_video_details(self) -> Dict[str, Any]:
        """Get video details from ytInitialData."""
        try:
            contents = (
                self.yt_initial_data
                .get("contents", {})
                .get("twoColumnWatchNextResults", {})
                .get("results", {})
                .get("results", {})
                .get("contents", [])
            )

            for item in contents:
                if "videoPrimaryInfoRenderer" in item:
                    return item["videoPrimaryInfoRenderer"]

            return {}
        except (AttributeError, KeyError, TypeError):
            return {}

    def _extract_title(self, video_details: Dict[str, Any]) -> str:
        """Extract video title."""
        try:
            runs = video_details.get("title", {}).get("runs", [])
            if runs:
                return runs[0].get("text", "Unknown Title")
        except (KeyError, IndexError, TypeError):
            pass
        return "Unknown Title"

    def _extract_channel_name(self) -> str:
        """Extract channel name."""
        try:
            contents = (
                self.yt_initial_data
                .get("contents", {})
                .get("twoColumnWatchNextResults", {})
                .get("results", {})
                .get("results", {})
                .get("contents", [])
            )

            for item in contents:
                if "videoSecondaryInfoRenderer" in item:
                    owner = item["videoSecondaryInfoRenderer"].get("owner", {})
                    runs = (
                        owner.get("videoOwnerRenderer", {})
                        .get("title", {})
                        .get("runs", [])
                    )
                    if runs:
                        return runs[0].get("text", "Unknown Channel")

            return "Unknown Channel"
        except (AttributeError, KeyError, IndexError, TypeError):
            return "Unknown Channel"

    def _extract_description(self) -> str:
        """Extract full video description."""
        try:
            contents = (
                self.yt_initial_data
                .get("contents", {})
                .get("twoColumnWatchNextResults", {})
                .get("results", {})
                .get("results", {})
                .get("contents", [])
            )

            for item in contents:
                if "videoSecondaryInfoRenderer" in item:
                    description_content = (
                        item["videoSecondaryInfoRenderer"]
                        .get("attributedDescription", {})
                        .get("content", "")
                    )
                    return description_content

            return ""
        except (AttributeError, KeyError, TypeError):
            return ""

    def _extract_description_links(self) -> List[Dict[str, str]]:
        """Extract links from video description."""
        from urllib.parse import unquote

        links = []

        try:
            contents = (
                self.yt_initial_data
                .get("contents", {})
                .get("twoColumnWatchNextResults", {})
                .get("results", {})
                .get("results", {})
                .get("contents", [])
            )

            for item in contents:
                if "videoSecondaryInfoRenderer" in item:
                    secondary_info = item["videoSecondaryInfoRenderer"]
                    attributed_desc = secondary_info.get("attributedDescription", {})
                    command_runs = attributed_desc.get("commandRuns", [])
                    desc_text = attributed_desc.get("content", "")

                    for run in command_runs:
                        start_idx = run.get("startIndex", 0)
                        length = run.get("length", 0)
                        link_text = desc_text[start_idx:start_idx + length] if desc_text else ""

                        url = (
                            run.get("onTap", {})
                            .get("innertubeCommand", {})
                            .get("urlEndpoint", {})
                            .get("url", "")
                        )

                        if url:
                            # Handle YouTube redirect URLs (both relative and absolute)
                            if "/redirect?" in url or "youtube.com/redirect" in url:
                                # Extract the actual URL from the 'q' parameter
                                actual_url_match = re.search(r'[?&]q=([^&]+)', url)
                                if actual_url_match:
                                    url = unquote(actual_url_match.group(1))
                            elif url.startswith("/"):
                                # Handle other relative URLs
                                url = f"https://www.youtube.com{url}"

                            if not link_text:
                                link_text = url

                            links.append({
                                "text": link_text,
                                "url": url
                            })

            return links
        except (AttributeError, KeyError, IndexError, TypeError):
            return []

    def _extract_view_count(self, video_details: Dict[str, Any]) -> Optional[str]:
        """Extract view count."""
        try:
            view_count_text = (
                video_details
                .get("viewCount", {})
                .get("videoViewCountRenderer", {})
                .get("viewCount", {})
                .get("simpleText", None)
            )
            return view_count_text
        except (AttributeError, KeyError, TypeError):
            return None

    def _extract_upload_date(self, video_details: Dict[str, Any]) -> Optional[str]:
        """Extract upload date."""
        try:
            date_text = (
                video_details
                .get("dateText", {})
                .get("simpleText", None)
            )
            return date_text
        except (AttributeError, KeyError, TypeError):
            return None

    def _extract_like_count(self) -> Optional[str]:
        """Extract like count."""
        try:
            contents = (
                self.yt_initial_data
                .get("contents", {})
                .get("twoColumnWatchNextResults", {})
                .get("results", {})
                .get("results", {})
                .get("contents", [])
            )

            for item in contents:
                if "videoPrimaryInfoRenderer" in item:
                    buttons = (
                        item["videoPrimaryInfoRenderer"]
                        .get("videoActions", {})
                        .get("menuRenderer", {})
                        .get("topLevelButtons", [])
                    )

                    for button in buttons:
                        if "segmentedLikeDislikeButtonRenderer" in button:
                            like_button = (
                                button["segmentedLikeDislikeButtonRenderer"]
                                .get("likeButton", {})
                                .get("toggleButtonRenderer", {})
                            )

                            label = (
                                like_button
                                .get("defaultText", {})
                                .get("accessibility", {})
                                .get("accessibilityData", {})
                                .get("label", "")
                            )

                            if label:
                                match = re.search(r'([\d,KMB]+)\s*like', label, re.IGNORECASE)
                                if match:
                                    return match.group(1)

            return None
        except (AttributeError, KeyError, IndexError, TypeError):
            return None

    def _extract_comments(
        self, video_id: str, char_limit: int
    ) -> tuple:
        """
        Extract comments by making additional API call.

        Args:
            video_id: YouTube video ID
            char_limit: Maximum characters for all comments combined

        Returns:
            Tuple of (comments list, truncated flag)
        """
        if not self.scraper:
            return None, False

        try:
            continuation_token = self._extract_continuation_token()

            if not continuation_token:
                print("Warning: Could not find continuation token for comments", file=sys.stderr)
                return None, False

            comments_data = self._fetch_comments_api(continuation_token)

            if not comments_data:
                return None, False

            comments = []
            total_chars = 0
            truncated = False

            comment_threads = self._extract_comment_threads(comments_data)

            for thread in comment_threads:
                comment = self._parse_comment_thread(thread)
                if comment:
                    comment_text_len = len(comment.text)

                    if total_chars + comment_text_len > char_limit:
                        truncated = True
                        break

                    comments.append(comment)
                    total_chars += comment_text_len

            return comments if comments else None, truncated

        except Exception as e:
            print(f"Warning: Failed to extract comments: {type(e).__name__}: {e}", file=sys.stderr)
            return None, False

    def _extract_continuation_token(self) -> Optional[str]:
        """Extract continuation token for comments API."""
        try:
            contents = (
                self.yt_initial_data
                .get("contents", {})
                .get("twoColumnWatchNextResults", {})
                .get("results", {})
                .get("results", {})
                .get("contents", [])
            )

            for item in contents:
                if "itemSectionRenderer" in item:
                    section = item["itemSectionRenderer"]
                    contents_list = section.get("contents", [])

                    for content in contents_list:
                        if "continuationItemRenderer" in content:
                            token = (
                                content["continuationItemRenderer"]
                                .get("continuationEndpoint", {})
                                .get("continuationCommand", {})
                                .get("token", None)
                            )
                            if token:
                                return token

            return None
        except (AttributeError, KeyError, TypeError):
            return None

    def _fetch_comments_api(self, continuation_token: str) -> Optional[Dict[str, Any]]:
        """Fetch comments from YouTube API."""
        try:
            from curl_cffi import requests

            api_url = "https://www.youtube.com/youtubei/v1/next"

            payload = {
                "continuation": continuation_token,
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": "2.20231120.00.00",
                    }
                }
            }

            response = requests.post(
                api_url,
                json=payload,
                impersonate=self.scraper.browser,
                timeout=self.scraper.timeout,
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"Warning: Comments API request failed: {e}", file=sys.stderr)
            return None

    def _extract_comment_threads(self, comments_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract comment data from YouTube's new API format."""
        try:
            # YouTube now uses frameworkUpdates with entity mutations
            mutations = (
                comments_data
                .get("frameworkUpdates", {})
                .get("entityBatchUpdate", {})
                .get("mutations", [])
            )

            # Build a map of commentId to comment data
            comment_map = {}

            for mutation in mutations:
                payload = mutation.get("payload", {})

                # Extract comment entity payload
                if "commentEntityPayload" in payload:
                    comment_payload = payload["commentEntityPayload"]
                    properties = comment_payload.get("properties", {})
                    comment_id = properties.get("commentId")

                    if comment_id:
                        comment_map[comment_id] = {
                            "author": comment_payload.get("author", {}),
                            "properties": properties,
                            "toolbar": comment_payload.get("toolbar", {}),
                        }

            # Return list of comment data
            return list(comment_map.values())

        except (AttributeError, KeyError, IndexError, TypeError):
            return []

    def _parse_comment_thread(self, comment_data: Dict[str, Any]) -> Optional[YouTubeComment]:
        """Parse a single comment from YouTube's new API format."""
        try:
            # Extract author information
            author_info = comment_data.get("author", {})
            author_name = author_info.get("displayName", "Unknown")

            # Extract properties
            properties = comment_data.get("properties", {})

            # Extract comment text
            content_data = properties.get("content", {})
            text = content_data.get("content", "")

            # Extract timestamp
            published_time = properties.get("publishedTime", None)

            # Extract toolbar information
            toolbar = comment_data.get("toolbar", {})

            # Get like count (try both liked and not-liked states)
            like_count = toolbar.get("likeCountNotliked", toolbar.get("likeCountLiked", None))

            # Check if hearted by creator
            is_hearted = "heartActiveTooltip" in toolbar

            # Check if pinned (pinned comments usually appear first in reply level 0)
            # For now, we'll assume not pinned as this info isn't clearly in the new format
            is_pinned = False

            if not text:
                return None

            return YouTubeComment(
                author=author_name,
                text=text,
                likes=like_count,
                timestamp=published_time,
                is_pinned=is_pinned,
                is_hearted=is_hearted,
            )

        except (AttributeError, KeyError, IndexError, TypeError) as e:
            print(f"Warning: Failed to parse comment: {e}", file=sys.stderr)
            return None
