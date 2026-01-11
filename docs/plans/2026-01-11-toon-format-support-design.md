# TOON Format Support Design

**Date:** 2026-01-11
**Status:** Approved
**Author:** Claude (brainstorming session with Mr. Memento)

## Summary

Add TOON (Token-Oriented Object Notation) as a new output format for cli-web-scrapper to reduce LLM token costs by 30-60% compared to JSON output.

## Context

- **Primary use case:** LLM context injection - minimizing tokens when feeding scraped content to language models
- **Usage pattern:** Direct CLI output piped to prompts or saved to files
- **Dependency choice:** `toon-formatter` Python library (zero external deps, 146 tests, full spec support)

## Architecture

### Data Flow

```
Parsed Data (RedditThread/YouTubeVideo/TrafilaturaContent)
    |
    v
TOONFormatter.format(data)
    |
    v
_to_dict() converts dataclass -> dict
    |
    v
ToonEncoder().encode(dict)
    |
    v
TOON string output (30-60% fewer tokens)
```

### Files Modified

1. `pyproject.toml` - add `toon-formatter` dependency
2. `waf_bypass_scraper/formatters.py` - add `TOONFormatter` class
3. `waf_bypass_scraper/cli.py` - add `toon` to format choices

## Implementation Details

### TOONFormatter Class

```python
from toon import ToonEncoder

class TOONFormatter(OutputFormatter):
    """TOON output formatter for minimal LLM token usage."""

    def __init__(self, delimiter: str = "\t"):
        # Tab delimiter for maximum token efficiency
        self.encoder = ToonEncoder(delimiter=delimiter)

    def format(self, data: Any) -> str:
        """Format data as TOON."""
        if hasattr(data, "__dict__"):
            return self.encoder.encode(self._to_dict(data))
        return self.encoder.encode(data)

    def _to_dict(self, obj: Any) -> Any:
        """Convert object to dictionary recursively."""
        if hasattr(obj, "__dict__"):
            result = {}
            for key, value in obj.__dict__.items():
                if isinstance(value, list):
                    result[key] = [self._to_dict(item) for item in value]
                else:
                    result[key] = self._to_dict(value)
            return result
        return obj
```

### Key Design Decision: Tab Delimiter

Using `\t` (tab) instead of comma because:
- Tabs tokenize more efficiently than commas
- Single character, rarely appears in natural text
- Reduces need for quoting values

### CLI Changes

Format choices updated from:
```python
choices=["rich", "json", "text", "markdown"]
```

To:
```python
choices=["rich", "json", "text", "markdown", "toon"]
```

### Example Output

**YouTube video in TOON format:**
```toon
title:	How to Build AI Agents
channel_name:	Tech Channel
view_count:	1.2M views
video_id:	abc123
comments[3	]{author	text	likes}:
UserA	Great video!	42
UserB	Very helpful	18
UserC	Thanks for sharing	5
```

## CLI Usage

```bash
# Basic usage
cli-web-scrapper -f toon https://example.com

# Save to file
cli-web-scrapper -f toon -o data.toon https://youtube.com/watch?v=VIDEO_ID

# Pipe to LLM context
cli-web-scrapper -f toon https://reddit.com/r/LocalLLaMA/... | llm "summarize"
```

## Testing Strategy

### Manual Verification

1. Install dependency: `uv add toon-formatter`
2. Test each content type:
   - Generic webpage: `cli-web-scrapper -f toon https://example.com`
   - YouTube: `cli-web-scrapper -f toon https://youtube.com/watch?v=...`
   - Reddit: `cli-web-scrapper -f toon https://reddit.com/r/.../comments/...`
3. Verify file output: `cli-web-scrapper -f toon -o test.toon https://example.com`

### Edge Cases

- Empty comments array
- Special characters (quotes, tabs, newlines)
- Unicode/emoji handling

## References

- [TOON Format Specification](https://toonformat.dev/guide/format-overview.html)
- [TOON for LLM Prompts](https://toonformat.dev/guide/llm-prompts.html)
- [toon-formatter PyPI](https://pypi.org/project/toon-formatter/)
