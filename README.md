# WAF Bypass Scraper

A Python CLI tool for scraping WAF and Bot Management protected websites using intelligent browser impersonation and content extraction.

## Features

- **WAF Bypass**: Browser fingerprint impersonation via `curl_cffi` to bypass Cloudflare, DataDome, and other protections
- **Intelligent Content Extraction**: Uses Trafilatura to extract clean content, removing navigation, ads, and boilerplate
- **Reddit Specialization**: Dedicated parser for Reddit threads with comments extraction
- **Multiple Output Formats**: Rich console, JSON, Plain text, Markdown
- **Metadata Extraction**: Automatically extracts title, author, date, description, and language
- **Link Preservation**: Converts relative URLs to absolute URLs

## Legal Notice

**IMPORTANT: This tool is intended for authorized testing, research, and educational purposes only.**

Users are solely responsible for:
- Compliance with website Terms of Service and robots.txt directives
- Respecting rate limits and avoiding server overload
- Compliance with applicable laws including CFAA, GDPR, and data protection regulations
- Obtaining proper authorization before testing security controls
- Respecting intellectual property and copyright laws

**The authors assume no liability for misuse of this tool.** Web scraping and WAF bypass techniques should only be used:
- On websites you own or control
- With explicit written permission from the website owner
- For authorized security testing and penetration testing
- For academic research with proper ethical approval
- In accordance with applicable laws and regulations

Unauthorized access to computer systems is illegal in most jurisdictions. Use responsibly.

## Installation

Install dependencies using uv:

```bash
uv sync
```

## Usage

### Quick Start

Scrape any website with rich terminal output:

```bash
cli-web-scrapper https://docs.claude.com/en/docs/claude-code/skills
```

Or use the start script:

```bash
./start.sh https://example.com
```

Or use the Python module directly:

```bash
uv run python -m waf_bypass_scraper.cli https://example.com
```

### Output Formats

**Rich Format (Default)** - Beautiful terminal output with colors and formatting:

```bash
cli-web-scrapper https://example.com
```

**Markdown** - Save clean documentation:

```bash
cli-web-scrapper -f markdown -o docs.md https://example.com
```

**JSON** - Structured data with metadata:

```bash
cli-web-scrapper -f json -o data.json https://example.com
```

**Plain Text** - Clean, readable text:

```bash
cli-web-scrapper -f text https://example.com
```

### Browser Impersonation

Use different browsers to bypass specific protections:

```bash
# Safari browser
cli-web-scrapper -b safari https://example.com

# Specific Chrome version
cli-web-scrapper -b chrome124 https://example.com

# List all available browsers
cli-web-scrapper --list-browsers
```

### Examples

**Scrape Documentation**:

```bash
cli-web-scrapper -f markdown -o api-docs.md https://docs.example.com/api
```

**Reddit Thread**:

```bash
cli-web-scrapper https://www.reddit.com/r/programming/comments/...
```

**Protected Website with JSON Output**:

```bash
cli-web-scrapper -f json -o output.json https://protected-site.com
```

**With Verbose Output** (show progress messages):

```bash
cli-web-scrapper --verbose -f markdown -o docs.md https://example.com
```

## Command-Line Options

```
usage: cli-web-scrapper [-h] [-b BROWSER] [-f {rich,json,text,markdown}]
                        [-o FILE] [-t TIMEOUT] [--verbose] [--list-browsers]
                        [--version] url

positional arguments:
  url                   URL to scrape

options:
  -h, --help            show this help message and exit
  -b BROWSER, --browser BROWSER
                        Browser to impersonate (default: chrome)
  -f {rich,json,text,markdown}, --format {rich,json,text,markdown}
                        Output format (default: rich)
  -o FILE, --output FILE
                        Output file (default: stdout)
  -t TIMEOUT, --timeout TIMEOUT
                        Request timeout in seconds (default: 30)
  --verbose             Show detailed progress messages
  --list-browsers       List supported browsers and exit
  --version             show program's version number and exit
```

## Supported Browsers

- **Chrome**: chrome, chrome99, chrome100, chrome101, chrome104, chrome107, chrome110, chrome116, chrome119, chrome120, chrome123, chrome124
- **Safari**: safari, safari15_3, safari15_5, safari17_0, safari17_2_1, safari18_0
- **Edge**: edge, edge99, edge101
- **Firefox**: firefox, firefox109

## How It Works

This tool uses a two-layer approach for reliable web scraping:

### 1. WAF Bypass Layer (curl_cffi)
- Impersonates browser TLS fingerprints
- Mimics HTTP/2 behavior
- Bypasses Cloudflare, DataDome, and other bot protection systems

### 2. Content Extraction Layer (Trafilatura)
- Intelligently identifies main content
- Removes navigation, ads, footers, and boilerplate
- Extracts metadata (title, author, date, description)
- Preserves formatting and links
- Handles 500+ languages

### Process Flow

```
URL → curl_cffi (bypass WAF) → HTML → Trafilatura (extract content) → Formatted Output
```

## Output Structure

### JSON Format
```json
{
  "title": "Page Title",
  "author": "Author Name",
  "date": "2024-01-01",
  "url": "https://example.com",
  "description": "Page description",
  "text": "Plain text content...",
  "markdown": "# Markdown formatted content...",
  "links": ["https://link1.com", "https://link2.com"],
  "language": "en"
}
```

### Markdown Format
```markdown
# Page Title

**Author:** Author Name
**Date:** 2024-01-01
**URL:** https://example.com

> Page description

## Content

Main content with formatting, links, and structure preserved...
```

## Use Cases

- **Documentation Archiving**: Save online documentation as clean markdown files
- **Reddit Analysis**: Extract Reddit threads with comments for analysis
- **Research**: Collect articles from paywalled or protected sites
- **Content Aggregation**: Scrape multiple sources into structured JSON
- **Knowledge Base**: Build offline documentation from various sources

## Performance

- Battle-tested extraction engine used by HuggingFace, IBM, Microsoft Research, Stanford
- Highest F1 score (0.937) among open-source extractors
- Fast and efficient with minimal dependencies

## License

MIT
