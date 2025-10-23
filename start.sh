#!/bin/bash
# Convenience script to run the WAF bypass scraper

uv run python -m waf_bypass_scraper.cli "$@"
