"""Command-line interface for WAF Bypass Scraper."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from curl_cffi.requests import RequestsError

from .scraper import WAFBypassScraper
from .parsers import RedditParser, GenericParser, TrafilaturaParser
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
    verbose: bool = False,
) -> None:
    """
    Scrape a URL and output the content.

    Args:
        url: URL to scrape
        browser: Browser to impersonate
        output_format: Output format (rich, json, text, markdown)
        output_file: Optional file to save output to
        timeout: Request timeout in seconds
        verbose: Show detailed progress messages
    """
    try:
        # Initialize scraper
        scraper = WAFBypassScraper(browser=browser, timeout=timeout)

        # Fetch content
        if verbose:
            print(f"Fetching: {url}", file=sys.stderr)
            print(f"Browser: {browser}", file=sys.stderr)
        html_content = scraper.fetch_text(url)
        if verbose:
            print("Fetch successful!", file=sys.stderr)

        # Parse content based on URL type
        if is_reddit_url(url):
            if verbose:
                print("Parsing Reddit content...", file=sys.stderr)
            parser = RedditParser(html_content)
            data = parser.parse_thread(url)
        else:
            if verbose:
                print("Parsing generic content with Trafilatura...", file=sys.stderr)
            parser = TrafilaturaParser(html_content, url=url)
            data = parser.extract_content()

        # Format output
        if output_format == "rich":
            formatter = RichFormatter()
            formatter.format(data)
        elif output_format == "json":
            formatter = JSONFormatter()
            output = formatter.format(data)
            if output_file:
                Path(output_file).write_text(output, encoding="utf-8")
                if verbose:
                    print(f"\nSaved to: {output_file}", file=sys.stderr)
            else:
                print(output)
        elif output_format == "text":
            formatter = PlainTextFormatter()
            output = formatter.format(data)
            if output_file:
                Path(output_file).write_text(output, encoding="utf-8")
                if verbose:
                    print(f"\nSaved to: {output_file}", file=sys.stderr)
            else:
                print(output)
        elif output_format == "markdown":
            formatter = MarkdownFormatter()
            output = formatter.format(data)
            if output_file:
                Path(output_file).write_text(output, encoding="utf-8")
                if verbose:
                    print(f"\nSaved to: {output_file}", file=sys.stderr)
            else:
                print(output)

    except RequestsError as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)


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

    parser.add_argument("url", nargs="?", help="URL to scrape")

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
        "--verbose",
        action="store_true",
        help="Show detailed progress messages",
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

    # Validate URL is provided for scraping
    if not args.url:
        parser.error("the following arguments are required: url")

    # Scrape URL
    scrape_url(
        url=args.url,
        browser=args.browser,
        output_format=args.format,
        output_file=args.output,
        timeout=args.timeout,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
