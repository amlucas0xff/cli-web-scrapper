"""Output formatters for different formats."""

import json
from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from toon import ToonEncoder

from .parsers import RedditThread, TrafilaturaContent, YouTubeVideo


class OutputFormatter:
    """Base class for output formatters."""

    def format(self, data: Any) -> str:
        """Format data for output."""
        raise NotImplementedError


class JSONFormatter(OutputFormatter):
    """JSON output formatter."""

    def format(self, data: Any) -> str:
        """Format data as JSON."""
        if hasattr(data, "__dict__"):
            return json.dumps(self._to_dict(data), indent=2, ensure_ascii=False)
        return json.dumps(data, indent=2, ensure_ascii=False)

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


class PlainTextFormatter(OutputFormatter):
    """Plain text output formatter."""

    def format(self, data: Any) -> str:
        """Format data as plain text."""
        if isinstance(data, RedditThread):
            return self._format_reddit_thread(data)
        elif isinstance(data, TrafilaturaContent):
            return self._format_trafilatura_content(data)
        elif isinstance(data, YouTubeVideo):
            return self._format_youtube_video(data)
        return str(data)

    def _format_reddit_thread(self, thread: RedditThread) -> str:
        """Format Reddit thread as plain text."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"TITLE: {thread.title}")
        lines.append(f"SUBREDDIT: r/{thread.subreddit}")
        lines.append(f"AUTHOR: u/{thread.author}")
        if thread.score:
            lines.append(f"SCORE: {thread.score}")
        lines.append(f"URL: {thread.url}")
        lines.append("=" * 80)

        if thread.text:
            lines.append("\nPOST CONTENT:")
            lines.append("-" * 80)
            lines.append(thread.text)
            lines.append("-" * 80)

        if thread.comments:
            lines.append(f"\nCOMMENTS ({len(thread.comments)}):")
            lines.append("=" * 80)

            for i, comment in enumerate(thread.comments, 1):
                lines.append(f"\n[{i}] u/{comment.author}")
                if comment.score:
                    lines.append(f"Score: {comment.score}")
                if comment.timestamp:
                    lines.append(f"Time: {comment.timestamp}")
                lines.append("-" * 80)
                lines.append(comment.text)
                lines.append("-" * 80)

        return "\n".join(lines)

    def _format_trafilatura_content(self, content: TrafilaturaContent) -> str:
        """Format Trafilatura content as plain text."""
        lines = []
        lines.append("=" * 80)
        if content.title:
            lines.append(f"TITLE: {content.title}")
        if content.author:
            lines.append(f"AUTHOR: {content.author}")
        if content.date:
            lines.append(f"DATE: {content.date}")
        if content.url:
            lines.append(f"URL: {content.url}")
        if content.language:
            lines.append(f"LANGUAGE: {content.language}")
        lines.append("=" * 80)

        if content.description:
            lines.append(f"\nDESCRIPTION:\n{content.description}\n")

        if content.text:
            lines.append("\nCONTENT:")
            lines.append("-" * 80)
            lines.append(content.text)
            lines.append("-" * 80)

        return "\n".join(lines)

    def _format_youtube_video(self, video: YouTubeVideo) -> str:
        """Format YouTube video as plain text."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"TITLE: {video.title}")
        lines.append(f"CHANNEL: {video.channel_name}")
        if video.view_count:
            lines.append(f"VIEWS: {video.view_count}")
        if video.upload_date:
            lines.append(f"UPLOADED: {video.upload_date}")
        if video.like_count:
            lines.append(f"LIKES: {video.like_count}")
        lines.append(f"VIDEO ID: {video.video_id}")
        lines.append(f"URL: {video.url}")
        lines.append("=" * 80)

        if video.description:
            lines.append("\nDESCRIPTION:")
            lines.append("-" * 80)
            lines.append(video.description)
            lines.append("-" * 80)

        if video.description_links:
            lines.append(f"\nLINKS IN DESCRIPTION ({len(video.description_links)}):")
            lines.append("-" * 80)
            for i, link in enumerate(video.description_links, 1):
                lines.append(f"[{i}] {link['text']}")
                lines.append(f"    {link['url']}")
            lines.append("-" * 80)

        if video.comments:
            lines.append(f"\nCOMMENTS ({len(video.comments)}):")
            if video.comments_truncated:
                lines.append("(Truncated due to character limit)")
            lines.append("=" * 80)

            for i, comment in enumerate(video.comments, 1):
                lines.append(f"\n[{i}] {comment.author}")
                if comment.is_pinned:
                    lines.append("(PINNED)")
                if comment.is_hearted:
                    lines.append("(HEARTED)")
                if comment.likes:
                    lines.append(f"Likes: {comment.likes}")
                if comment.timestamp:
                    lines.append(f"Time: {comment.timestamp}")
                lines.append("-" * 80)
                lines.append(comment.text)
                lines.append("-" * 80)

        return "\n".join(lines)


class RichFormatter(OutputFormatter):
    """Rich formatted console output."""

    def __init__(self):
        """Initialize Rich console."""
        self.console = Console()

    def format(self, data: Any) -> None:
        """Format and print data using Rich."""
        if isinstance(data, RedditThread):
            self._format_reddit_thread(data)
        elif isinstance(data, TrafilaturaContent):
            self._format_trafilatura_content(data)
        elif isinstance(data, YouTubeVideo):
            self._format_youtube_video(data)
        else:
            self.console.print(str(data))

    def _format_reddit_thread(self, thread: RedditThread) -> None:
        """Format Reddit thread with Rich formatting."""
        # Thread header
        header_text = Text()
        header_text.append(thread.title, style="bold cyan")
        header_text.append(f"\n\nr/{thread.subreddit}", style="blue")
        header_text.append(f" • u/{thread.author}", style="green")
        if thread.score:
            header_text.append(f" • {thread.score} points", style="yellow")

        self.console.print(
            Panel(header_text, title="Reddit Thread", border_style="cyan")
        )

        # Post content
        if thread.text:
            self.console.print("\n[bold]Post Content:[/bold]")
            self.console.print(Panel(thread.text, border_style="dim"))

        # Comments
        if thread.comments:
            self.console.print(f"\n[bold]Comments ({len(thread.comments)}):[/bold]\n")

            for i, comment in enumerate(thread.comments, 1):
                # Comment header
                comment_header = Text()
                comment_header.append(f"[{i}] ", style="dim")
                comment_header.append(f"u/{comment.author}", style="green")

                if comment.score:
                    comment_header.append(f" • {comment.score}", style="yellow")
                if comment.timestamp:
                    comment_header.append(f" • {comment.timestamp}", style="dim")

                # Comment body
                self.console.print(comment_header)
                self.console.print(
                    Panel(comment.text, border_style="dim", padding=(0, 2))
                )
                self.console.print()

    def _format_trafilatura_content(self, content: TrafilaturaContent) -> None:
        """Format Trafilatura content with Rich formatting."""
        # Header with metadata
        header_text = Text()
        if content.title:
            header_text.append(content.title, style="bold cyan")

        metadata_parts = []
        if content.author:
            metadata_parts.append(f"Author: {content.author}")
        if content.date:
            metadata_parts.append(f"Date: {content.date}")
        if content.language:
            metadata_parts.append(f"Language: {content.language}")

        if metadata_parts:
            header_text.append("\n\n", style="dim")
            header_text.append(" • ".join(metadata_parts), style="dim")

        self.console.print(
            Panel(header_text, title="Web Content", border_style="cyan")
        )

        # Description
        if content.description:
            self.console.print("\n[bold]Description:[/bold]")
            self.console.print(Panel(content.description, border_style="dim"))

        # Main content as markdown
        if content.markdown:
            self.console.print("\n[bold]Content:[/bold]")
            self.console.print(Markdown(content.markdown))
        elif content.text:
            self.console.print("\n[bold]Content:[/bold]")
            self.console.print(Panel(content.text, border_style="dim"))

    def _format_youtube_video(self, video: YouTubeVideo) -> None:
        """Format YouTube video with Rich formatting."""
        # Video header
        header_text = Text()
        header_text.append(video.title, style="bold cyan")
        header_text.append(f"\n\n{video.channel_name}", style="blue")

        metadata_parts = []
        if video.view_count:
            metadata_parts.append(f"{video.view_count}")
        if video.like_count:
            metadata_parts.append(f"{video.like_count} likes")
        if video.upload_date:
            metadata_parts.append(video.upload_date)

        if metadata_parts:
            header_text.append("\n", style="dim")
            header_text.append(" • ".join(metadata_parts), style="yellow")

        self.console.print(
            Panel(header_text, title="YouTube Video", border_style="red")
        )

        # Description
        if video.description:
            self.console.print("\n[bold]Description:[/bold]")
            self.console.print(Panel(video.description, border_style="dim"))

        # Description links
        if video.description_links:
            self.console.print(f"\n[bold]Links in Description ({len(video.description_links)}):[/bold]\n")
            for i, link in enumerate(video.description_links, 1):
                link_text = Text()
                link_text.append(f"[{i}] ", style="dim")
                link_text.append(link['text'], style="cyan")
                link_text.append(f"\n    ", style="dim")
                link_text.append(link['url'], style="blue underline")
                self.console.print(link_text)

        # Comments
        if video.comments:
            comment_header = f"Comments ({len(video.comments)})"
            if video.comments_truncated:
                comment_header += " [TRUNCATED]"
            self.console.print(f"\n[bold]{comment_header}:[/bold]\n")

            for i, comment in enumerate(video.comments, 1):
                # Comment header
                comment_header_text = Text()
                comment_header_text.append(f"[{i}] ", style="dim")
                comment_header_text.append(comment.author, style="green")

                badges = []
                if comment.is_pinned:
                    badges.append("PINNED")
                if comment.is_hearted:
                    badges.append("HEARTED")

                if badges:
                    comment_header_text.append(f" [{', '.join(badges)}]", style="yellow bold")

                if comment.likes:
                    comment_header_text.append(f" • {comment.likes} likes", style="yellow")
                if comment.timestamp:
                    comment_header_text.append(f" • {comment.timestamp}", style="dim")

                # Comment body
                self.console.print(comment_header_text)
                self.console.print(
                    Panel(comment.text, border_style="dim", padding=(0, 2))
                )
                self.console.print()


class MarkdownFormatter(OutputFormatter):
    """Markdown output formatter."""

    def format(self, data: Any) -> str:
        """Format data as Markdown."""
        if isinstance(data, RedditThread):
            return self._format_reddit_thread(data)
        elif isinstance(data, TrafilaturaContent):
            return self._format_trafilatura_content(data)
        elif isinstance(data, YouTubeVideo):
            return self._format_youtube_video(data)
        return str(data)

    def _format_reddit_thread(self, thread: RedditThread) -> str:
        """Format Reddit thread as Markdown."""
        lines = []

        # Thread header
        lines.append(f"# {thread.title}\n")
        lines.append(f"**Subreddit:** r/{thread.subreddit}  ")
        lines.append(f"**Author:** u/{thread.author}  ")
        if thread.score:
            lines.append(f"**Score:** {thread.score}  ")
        lines.append(f"**URL:** {thread.url}\n")

        # Post content
        if thread.text:
            lines.append("## Post Content\n")
            lines.append(thread.text)
            lines.append("")

        # Comments
        if thread.comments:
            lines.append(f"## Comments ({len(thread.comments)})\n")

            for i, comment in enumerate(thread.comments, 1):
                lines.append(f"### Comment {i}\n")
                lines.append(f"**Author:** u/{comment.author}  ")
                if comment.score:
                    lines.append(f"**Score:** {comment.score}  ")
                if comment.timestamp:
                    lines.append(f"**Posted:** {comment.timestamp}  ")
                lines.append("")
                lines.append(comment.text)
                lines.append("\n---\n")

        return "\n".join(lines)

    def _format_trafilatura_content(self, content: TrafilaturaContent) -> str:
        """Format Trafilatura content as Markdown."""
        lines = []

        # Title
        if content.title:
            lines.append(f"# {content.title}\n")

        # Metadata
        metadata = []
        if content.author:
            metadata.append(f"**Author:** {content.author}")
        if content.date:
            metadata.append(f"**Date:** {content.date}")
        if content.url:
            metadata.append(f"**URL:** {content.url}")
        if content.language:
            metadata.append(f"**Language:** {content.language}")

        if metadata:
            lines.append("  \n".join(metadata))
            lines.append("")

        # Description
        if content.description:
            lines.append(f"> {content.description}\n")

        # Main content - use markdown from Trafilatura
        if content.markdown:
            lines.append(content.markdown)
        elif content.text:
            lines.append(content.text)

        return "\n".join(lines)

    def _format_youtube_video(self, video: YouTubeVideo) -> str:
        """Format YouTube video as Markdown."""
        lines = []

        # Video header
        lines.append(f"# {video.title}\n")
        lines.append(f"**Channel:** {video.channel_name}  ")
        if video.view_count:
            lines.append(f"**Views:** {video.view_count}  ")
        if video.like_count:
            lines.append(f"**Likes:** {video.like_count}  ")
        if video.upload_date:
            lines.append(f"**Uploaded:** {video.upload_date}  ")
        lines.append(f"**Video ID:** `{video.video_id}`  ")
        lines.append(f"**URL:** {video.url}\n")

        # Description
        if video.description:
            lines.append("## Description\n")
            lines.append(video.description)
            lines.append("")

        # Description links
        if video.description_links:
            lines.append(f"## Links in Description ({len(video.description_links)})\n")
            for i, link in enumerate(video.description_links, 1):
                # Escape markdown in link text
                link_text = link['text'].replace('[', '\\[').replace(']', '\\]')
                lines.append(f"{i}. [{link_text}]({link['url']})")
            lines.append("")

        # Comments
        if video.comments:
            comment_header = f"## Comments ({len(video.comments)})"
            if video.comments_truncated:
                comment_header += " [TRUNCATED]"
            lines.append(f"{comment_header}\n")

            for i, comment in enumerate(video.comments, 1):
                lines.append(f"### Comment {i}\n")

                badges = []
                if comment.is_pinned:
                    badges.append("PINNED")
                if comment.is_hearted:
                    badges.append("HEARTED")

                lines.append(f"**Author:** {comment.author}  ")
                if badges:
                    lines.append(f"**Badges:** {', '.join(badges)}  ")
                if comment.likes:
                    lines.append(f"**Likes:** {comment.likes}  ")
                if comment.timestamp:
                    lines.append(f"**Posted:** {comment.timestamp}  ")
                lines.append("")
                lines.append(comment.text)
                lines.append("\n---\n")

        return "\n".join(lines)


class TOONFormatter(OutputFormatter):
    """TOON output formatter for minimal LLM token usage."""

    def __init__(self, delimiter: str = "\t"):
        """Initialize TOON encoder with tab delimiter for token efficiency."""
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
