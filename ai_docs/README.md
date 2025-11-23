# AI Documentation

This directory contains architecture and AI-focused documentation for the cli-web-scrapper project.

## Documentation Index

### Architecture

- **[blueprint.md](blueprint.md)** - Comprehensive architecture blueprint
  - Major components and their responsibilities
  - Module dependencies and integration points
  - Data flow diagrams with Mermaid visualizations
  - Architecture patterns (Strategy, Layered, DTOs)
  - Areas for improvement and architectural concerns
  - Last updated: 2025-11-23

## Documentation Structure

### ai_docs/ vs docs/

- **ai_docs/** (this directory) - Architecture documentation, design decisions, and system blueprints for AI agents
- **docs/** - Implementation notes, feature development logs, and historical documentation
  - `20251023-154754-WAF-Bypass-Scraper-Implementation.md` - Initial WAF bypass implementation
  - `20251110-202029-YouTube-Scraping-Implementation.md` - YouTube parser implementation
  - `images/` - Screenshots and visual documentation

## Regenerating the Blueprint

The architecture blueprint is generated using the `/generate-blueprint` command, which:

1. Analyzes the codebase with `cntxtpy` to create a knowledge graph
2. Uses Gemini CLI with large context window to analyze the knowledge graph
3. Generates structured architecture documentation with Mermaid diagrams

**When to regenerate:**
- After major refactoring or architectural changes
- When adding new parsers or formatters
- After significant feature additions
- When module dependencies change

**How to regenerate:**
```bash
/generate-blueprint /home/amlucas/dev/cli-web-scrapper
```

## Blueprint Generation Configuration

The blueprint generation is guided by `.gemini/GEMINI.md`, which specifies:
- Required sections (Overview, Components, Dependencies, Data Flow, Integration Points, Patterns)
- Mermaid diagram requirements
- Output format and structure

## Contributing to Documentation

When adding new documentation:
1. Place architecture docs in `ai_docs/`
2. Place implementation logs in `docs/`
3. Update this README.md to reference new files
4. Use markdown format with clear headers
5. Include Mermaid diagrams for visual clarity where appropriate
