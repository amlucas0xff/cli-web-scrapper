"""Core scraper functionality using curl_cffi for browser impersonation."""

from typing import Optional, Dict, Any
from curl_cffi import requests


class WAFBypassScraper:
    """Scraper that bypasses WAF/Bot protection using browser fingerprint impersonation."""

    SUPPORTED_BROWSERS = [
        "chrome", "chrome99", "chrome100", "chrome101", "chrome104", "chrome107",
        "chrome110", "chrome116", "chrome119", "chrome120", "chrome123", "chrome124",
        "safari", "safari15_3", "safari15_5", "safari17_0", "safari17_2_1",
        "safari18_0",
        "edge", "edge99", "edge101",
        "firefox", "firefox109",
    ]

    def __init__(
        self,
        browser: str = "chrome",
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the scraper.

        Args:
            browser: Browser to impersonate (default: chrome)
            timeout: Request timeout in seconds
            headers: Additional headers to include in requests
        """
        self.browser = browser
        self.timeout = timeout
        self.default_headers = headers or {}

    def fetch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Fetch a URL with browser impersonation.

        Args:
            url: URL to fetch
            headers: Additional headers for this request
            params: Query parameters

        Returns:
            Response object from curl_cffi

        Raises:
            requests.RequestException: If the request fails
        """
        # Use old Reddit for better scraping
        if "reddit.com" in url and "old.reddit.com" not in url:
            # Replace www.reddit.com or reddit.com with old.reddit.com (but not if already contains "old")
            if "www.reddit.com" in url:
                url = url.replace("www.reddit.com", "old.reddit.com")
            elif "://" in url and "old." not in url:
                # Replace reddit.com with old.reddit.com, but only after ://
                url = url.replace("://reddit.com", "://old.reddit.com")

        # Default headers that mimic a real browser
        default_browser_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }

        merged_headers = {**default_browser_headers, **self.default_headers, **(headers or {})}

        response = requests.get(
            url,
            impersonate=self.browser,
            timeout=self.timeout,
            headers=merged_headers,
            params=params,
        )

        response.raise_for_status()
        return response

    def fetch_text(self, url: str, **kwargs) -> str:
        """
        Fetch URL and return text content.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments for fetch()

        Returns:
            Response text content
        """
        response = self.fetch(url, **kwargs)
        return response.text

    def fetch_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch URL and parse JSON response.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments for fetch()

        Returns:
            Parsed JSON data
        """
        response = self.fetch(url, **kwargs)
        return response.json()
