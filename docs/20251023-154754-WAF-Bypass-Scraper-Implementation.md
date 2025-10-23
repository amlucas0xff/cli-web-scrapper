# WAF Bypass Scraper Implementation

**Date:** 2025-10-23
**Author:** AI Assistant
**Status:** Completed

## Overview

Successfully created a Python CLI tool to read WAF and Bot Management protected websites using browser fingerprint impersonation via the `curl_cffi` library.

## Project Structure

```
waf-bypass-scraper/
├── waf_bypass_scraper/
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Command-line interface
│   ├── scraper.py           # Core scraping functionality
│   ├── parsers.py           # HTML parsers (Reddit, Generic)
│   └── formatters.py        # Output formatters (JSON, Text, Markdown, Rich)
├── docs/                    # Documentation
├── pyproject.toml           # Project configuration
├── README.md                # User documentation
└── start.sh                 # Convenience startup script
```

## Key Features Implemented

### 1. Browser Fingerprint Impersonation
- Uses `curl_cffi` library to mimic real browser TLS fingerprints
- Supports multiple browsers: Chrome, Safari, Firefox, Edge
- Automatically redirects to old.reddit.com for better scraping
- Includes realistic browser headers

### 2. Reddit-Specific Parser
- Extracts thread title, author, subreddit, score
- Parses post content
- Extracts all comments with author, text, score, and timestamp
- Supports both old and new Reddit HTML structures

### 3. Multiple Output Formats
- **Rich**: Colored console output with panels and formatting
- **JSON**: Machine-readable structured data
- **Markdown**: Human-readable documentation format
- **Plain Text**: Simple text format

### 4. Generic Parser
- Fallback for non-Reddit websites
- Extracts main text content
- Finds all links on the page
- Extracts page title

## Technical Implementation Details

### Core Scraper (scraper.py)

The `WAFBypassScraper` class handles HTTP requests with browser impersonation:

```python
class WAFBypassScraper:
    - Browser fingerprint selection
    - Automatic old.reddit.com redirection
    - Realistic browser headers
    - Timeout configuration
```

Key features:
- Replaces www.reddit.com with old.reddit.com for easier parsing
- Adds comprehensive browser headers (Accept, User-Agent via impersonation, etc.)
- Supports custom headers and parameters

### Reddit Parser (parsers.py)

The `RedditParser` class uses BeautifulSoup with lxml to parse HTML:

- **Old Reddit support**: Primary target for reliable scraping
- **Multiple selector strategies**: Falls back if primary selectors fail
- **Comment extraction**: Handles nested comment structures
- **Data classes**: RedditThread and RedditComment for structured data

Challenges solved:
- Reddit's multiple HTML structures (old vs new)
- Nested comment threads
- Missing or optional fields (scores, timestamps)

### Output Formatters (formatters.py)

Four formatter classes provide flexible output:

1. **JSONFormatter**: Serializes objects to JSON
2. **PlainTextFormatter**: ASCII-friendly text output
3. **MarkdownFormatter**: Creates markdown documents
4. **RichFormatter**: Terminal UI with colors and panels

## Testing Results

Successfully tested with the provided Reddit thread:
- URL: https://www.reddit.com/r/LocalLLaMA/comments/1oe0y11/
- Extracted: Title, author, subreddit, score, post text
- Parsed: 74 comments with all metadata
- Output formats: All working (JSON, Text, Markdown, Rich)

## Usage Examples

### Basic Usage
```bash
./start.sh https://www.reddit.com/r/LocalLLaMA/comments/1oe0y11/...
```

### Save as JSON
```bash
./start.sh -f json -o output.json https://reddit.com/r/...
```

### Different Browser
```bash
./start.sh -b safari https://example.com
```

### List Supported Browsers
```bash
./start.sh --list-browsers
```

## Dependencies

- **curl-cffi**: Browser impersonation and HTTP requests
- **beautifulsoup4**: HTML parsing
- **lxml**: Fast HTML parser backend
- **rich**: Terminal formatting and colors

## Installation

Using uv package manager:
```bash
uv sync
```

## Lessons Learned

1. **Old Reddit is easier to scrape**: More consistent HTML structure
2. **Browser impersonation is critical**: curl_cffi successfully bypasses WAF
3. **Multiple selectors needed**: Websites change their HTML frequently
4. **URL normalization matters**: Prevented double-replacement bug (old.old.reddit.com)

## Future Enhancements

Potential improvements:
- Session management for authenticated scraping
- Proxy support
- Rate limiting/retry logic
- More website-specific parsers (HackerNews, StackOverflow, etc.)
- Async support for bulk scraping
- Cookie management
- JavaScript rendering (for heavy JS sites)

## Conclusion

Successfully created a working WAF bypass scraper that can read protected websites using browser impersonation. The tool successfully scraped the provided Reddit thread with all comments and metadata, proving the effectiveness of the curl_cffi approach.
