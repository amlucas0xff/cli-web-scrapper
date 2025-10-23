# WAF Bypass Scraper

A Python CLI tool to read WAF and Bot Management protected websites using browser fingerprint impersonation via `curl_cffi`.

## Features

- Browser fingerprint impersonation to bypass WAF/Bot protection
- Support for multiple browsers (Chrome, Safari, Firefox, Edge)
- Reddit thread parsing with comments extraction
- Multiple output formats: Rich console, JSON, Plain text, Markdown
- Easy-to-use CLI interface

## Installation

Install dependencies using uv:

```bash
uv sync
```

## Usage

### Basic Usage

Scrape a Reddit thread with rich formatting:

```bash
./start.sh https://www.reddit.com/r/LocalLLaMA/comments/1oe0y11/i_found_a_perfect_coder_model_for_my_rtx409064gb/
```

Or using uv directly:

```bash
uv run waf_bypass_scraper/cli.py https://www.reddit.com/r/LocalLLaMA/comments/...
```

### Output Formats

Save as JSON:

```bash
./start.sh -f json -o output.json https://example.com
```

Save as Markdown:

```bash
./start.sh -f markdown -o thread.md https://reddit.com/r/...
```

Plain text output:

```bash
./start.sh -f text https://example.com
```

### Browser Impersonation

Use Safari instead of Chrome:

```bash
./start.sh -b safari https://example.com
```

Use specific browser version:

```bash
./start.sh -b chrome124 https://example.com
```

List all supported browsers:

```bash
./start.sh --list-browsers
```

### Command-line Options

```
usage: cli.py [-h] [-b BROWSER] [-f {rich,json,text,markdown}] [-o FILE]
              [-t TIMEOUT] [--list-browsers] [--version]
              url

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
  --list-browsers       List supported browsers and exit
  --version            show program's version number and exit
```

## Supported Browsers

- Chrome: chrome, chrome99, chrome100, chrome101, chrome104, chrome107, chrome110, chrome116, chrome119, chrome120, chrome123, chrome124
- Safari: safari, safari15_3, safari15_5, safari17_0, safari17_2_1, safari18_0
- Edge: edge, edge99, edge101
- Firefox: firefox, firefox109

## How It Works

This tool uses `curl_cffi`, which impersonates browser TLS and HTTP/2 fingerprints to bypass WAF and bot detection systems. It:

1. Fetches the webpage using browser impersonation
2. Parses the HTML content (with special handling for Reddit)
3. Formats the output in your preferred format

## Examples

### Reddit Thread

```bash
./start.sh https://www.reddit.com/r/LocalLLaMA/comments/1oe0y11/i_found_a_perfect_coder_model_for_my_rtx409064gb/
```

### Save Reddit Thread as Markdown

```bash
./start.sh -f markdown -o discussion.md https://www.reddit.com/r/programming/comments/...
```

### Generic Website with JSON Output

```bash
./start.sh -f json -o data.json https://protected-site.com
```

## License

MIT
