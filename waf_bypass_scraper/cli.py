"""Command-line interface for WAF Bypass Scraper."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .scraper import WAFBypassScraper
from .parsers import RedditParser, GenericParser
from .formatters import (
    JSONFormatter,
    PlainTextFormatter,
    RichFormatter,
    MarkdownFormatter,
)


def is_reddit_url(url: str) -> bool:
    """Check if URL is a Reddit URL."""
    return "reddit.com" in url


def scrape_url(
    url: str,
    browser: str = "chrome",
    output_format: str = "rich",
    output_file: Optional[str] = None,
    timeout: int = 30,
) -> None:
    """
    Scrape a URL and output the content.

    Args:
        url: URL to scrape
        browser: Browser to impersonate
        output_format: Output format (rich, json, text, markdown)
        output_file: Optional file to save output to
        timeout: Request timeout in seconds
    """
    try:
        # Initialize scraper
        scraper = WAFBypassScraper(browser=browser, timeout=timeout)

        # Fetch content
        print(f"Fetching: {url}", file=sys.stderr)
        print(f"Browser: {browser}", file=sys.stderr)
        html_content = scraper.fetch_text(url)
        print("Fetch successful!", file=sys.stderr)

        # Parse content based on URL type
        if is_reddit_url(url):
            print("Parsing Reddit content...", file=sys.stderr)
            parser = RedditParser(html_content)
            data = parser.parse_thread(url)
        else:
            print("Parsing generic content...", file=sys.stderr)
            parser = GenericParser(html_content)
            data = {
                "title": parser.extract_title(),
                "text": parser.extract_text(),
                "links": parser.extract_links(),
            }

        # Format output
        if output_format == "rich":
            formatter = RichFormatter()
            formatter.format(data)
        elif output_format == "json":
            formatter = JSONFormatter()
            output = formatter.format(data)
            if output_file:
                Path(output_file).write_text(output, encoding="utf-8")
                print(f"\nSaved to: {output_file}", file=sys.stderr)
            else:
                print(output)
        elif output_format == "text":
            formatter = PlainTextFormatter()
            output = formatter.format(data)
            if output_file:
                Path(output_file).write_text(output, encoding="utf-8")
                print(f"\nSaved to: {output_file}", file=sys.stderr)
            else:
                print(output)
        elif output_format == "markdown":
            formatter = MarkdownFormatter()
            output = formatter.format(data)
            if output_file:
                Path(output_file).write_text(output, encoding="utf-8")
                print(f"\nSaved to: {output_file}", file=sys.stderr)
            else:
                print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape WAF/Bot protected websites using browser impersonation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape Reddit thread with rich formatting
  waf-scraper https://www.reddit.com/r/LocalLLaMA/comments/1oe0y11/...

  # Scrape and save as JSON
  waf-scraper -f json -o output.json https://example.com

  # Use Safari browser impersonation
  waf-scraper -b safari https://example.com

  # Save as Markdown
  waf-scraper -f markdown -o thread.md https://reddit.com/r/...

Supported browsers:
  chrome (default), safari, firefox, edge, and specific versions like
  chrome124, safari18_0, firefox109, etc.
        """,
    )

    parser.add_argument("url", help="URL to scrape")

    parser.add_argument(
        "-b",
        "--browser",
        default="chrome",
        help="Browser to impersonate (default: chrome)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["rich", "json", "text", "markdown"],
        default="rich",
        help="Output format (default: rich)",
    )

    parser.add_argument(
        "-o", "--output", help="Output file (default: stdout)", metavar="FILE"
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )

    parser.add_argument(
        "--list-browsers",
        action="store_true",
        help="List supported browsers and exit",
    )

    parser.add_argument(
        "--version", action="version", version="waf-bypass-scraper 0.1.0"
    )

    args = parser.parse_args()

    # List browsers if requested
    if args.list_browsers:
        print("Supported browsers:")
        for browser in WAFBypassScraper.SUPPORTED_BROWSERS:
            print(f"  - {browser}")
        sys.exit(0)

    # Scrape URL
    scrape_url(
        url=args.url,
        browser=args.browser,
        output_format=args.format,
        output_file=args.output,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    main()
