"""
UI Utilities for Jupyter Notebooks

This module provides tools for creating beautiful, card-style UIs in Jupyter Notebooks.
It supports multimodal content rendering (images, dataframes, code, markdown) with scoped CSS.
"""

import base64
import pandas as pd
from typing import Any, Optional
from IPython.display import HTML, display, Markdown
from html import escape
import re
import markdown as md_lib

def print_html(content: Any, title: Optional[str] = None, is_image: bool = False, is_markdown: bool = False):
    """
    Renders content in a beautiful card-style UI within Jupyter Notebooks.
    
    Features:
    - Multimodal rendering (Images, DataFrames, Code, Markdown)
    - Scoped CSS (prevents global style pollution)
    - Visual hierarchy with titles
    - Auto-detection of Markdown content
    
    Args:
        content: The content to display.
            - str + is_image=True: Path to image file (embedded as Base64)
            - str + is_markdown=True: Markdown text (rendered with formatting)
            - pd.DataFrame/Series: Rendered as HTML table
            - Other: Rendered as code block (<pre><code>)
        title: Optional title for the card.
        is_image: Set to True if content is an image file path.
        is_markdown: Set to True to render content as Markdown. 
                     If None, auto-detects Markdown patterns.
    
    Examples:
        >>> print_html(code, title="📝 Generated Code")
        >>> print_html("chart.png", title="📊 Visualization", is_image=True)
        >>> print_html(df.head(), title="📋 Data Preview")
        >>> print_html(ai_response, title="🤖 AI Analysis", is_markdown=True)
    """
    def image_to_base64(image_path: str) -> str:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    
    def _is_likely_markdown(text: str) -> bool:
        """Auto-detect if text contains Markdown syntax."""
        if not isinstance(text, str):
            return False
        
        markdown_patterns = [
            r'^#{1,6}\s+',           # Headers
            r'\*\*[^*]+\*\*',        # Bold
            r'\*[^*]+\*',            # Italic
            r'^[-*+]\s+',            # Lists
            r'^\d+\.\s+',            # Numbered lists
            r'\[.+\]\(.+\)',         # Links
            r'```',                  # Code blocks
            r'`[^`]+`',              # Inline code
            r'^>\s+',                # Blockquotes
        ]
        
        for pattern in markdown_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True
        return False
    
    def _markdown_to_html(md_text: str) -> str:
        """
        Convert Markdown to HTML using standard markdown library.
        
        This ensures proper handling of:
        - Nested lists (ordered and unordered)
        - Indented sublists (normalize 2-3 spaces to 4 spaces)
        - Mixed content (headers, paragraphs, blockquotes)
        - Inline formatting (bold, italic, code)
        """
        # Pre-process: Normalize indentation for nested lists
        # LLM often outputs 2-3 spaces, but Markdown requires 4 spaces
        lines = md_text.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Detect lines starting with 2-3 spaces followed by list marker
            match = re.match(r'^( {2,3})([-*+]|\d+\.)\s', line)
            if match:
                # Replace 2-3 spaces with 4 spaces
                indent_replacement = '    '
                normalized_line = indent_replacement + line[len(match.group(1)):]
                normalized_lines.append(normalized_line)
            else:
                normalized_lines.append(line)
        
        normalized_text = '\n'.join(normalized_lines)
        
        # Use markdown library with extra extensions for better support
        html = md_lib.markdown(
            normalized_text,
            extensions=[
                'nl2br',      # Convert newlines to <br>
                'sane_lists'  # Better list handling
            ]
        )
        return html
    
    # Auto-detect markdown if not explicitly specified
    if is_markdown is False and isinstance(content, str) and not is_image:
        is_markdown = _is_likely_markdown(content)
    
    # Render content based on type
    if is_image and isinstance(content, str):
        try:
            b64 = image_to_base64(content)
            rendered = f'<img src="data:image/png;base64,{b64}" alt="Image" style="max-width:100%; height:auto; border-radius:8px;">'
        except Exception as e:
            rendered = f"<pre><code>Error loading image: {escape(str(e))}</code></pre>"
    elif is_markdown and isinstance(content, str):
        rendered = f'<div class="markdown-content">{_markdown_to_html(content)}</div>'
    elif isinstance(content, pd.DataFrame):
        rendered = content.to_html(classes="pretty-table", index=False, border=0, escape=False)
    elif isinstance(content, pd.Series):
        rendered = content.to_frame().to_html(classes="pretty-table", border=0, escape=False)
    elif isinstance(content, str):
        rendered = f"<pre><code>{escape(content)}</code></pre>"
    else:
        rendered = f"<pre><code>{escape(str(content))}</code></pre>"
    
    # Scoped CSS
    css = """
    <style>
    .pretty-card {
        font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
        border: 2px solid transparent;
        border-radius: 14px;
        padding: 14px 16px;
        margin: 10px 0;
        background: linear-gradient(#fff, #fff) padding-box,
                    linear-gradient(135deg, #3b82f6, #9333ea) border-box;
        color: #111;
        box-shadow: 0 4px 12px rgba(0,0,0,.08);
    }
    .pretty-title {
        font-weight: 700;
        margin-bottom: 8px;
        font-size: 14px;
        color: #111;
    }
    
    /* 🔒 Scoped styles for code */
    .pretty-card pre, 
    .pretty-card code {
        background: #f3f4f6;
        color: #111;
        padding: 8px;
        border-radius: 8px;
        display: block;
        overflow-x: auto;
        font-size: 13px;
        white-space: pre-wrap;
        font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
    }
    
    /* Inline code styling */
    .pretty-card .markdown-content code.inline-code {
        background: #f3f4f6;
        color: #e11d48;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9em;
        font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
        display: inline;
        white-space: normal;
    }
    
    /* Markdown content styling */
    .pretty-card .markdown-content {
        line-height: 1.7;
        color: #111;
    }
    .pretty-card .markdown-content h1 {
        font-size: 1.8em;
        font-weight: 700;
        margin: 1.2em 0 0.6em 0;
        color: #111;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.3em;
    }
    .pretty-card .markdown-content h2 {
        font-size: 1.5em;
        font-weight: 700;
        margin: 1em 0 0.5em 0;
        color: #111;
    }
    .pretty-card .markdown-content h3 {
        font-size: 1.25em;
        font-weight: 600;
        margin: 0.8em 0 0.4em 0;
        color: #374151;
    }
    .pretty-card .markdown-content p {
        margin: 0.8em 0;
        color: #374151;
    }
    .pretty-card .markdown-content strong {
        font-weight: 700;
        color: #111;
    }
    .pretty-card .markdown-content em {
        font-style: italic;
        color: #4b5563;
    }
    .pretty-card .markdown-content ul,
    .pretty-card .markdown-content ol {
        margin: 0.8em 0;
        padding-left: 1.8em;
    }
    .pretty-card .markdown-content ul {
        list-style-type: disc;
    }
    .pretty-card .markdown-content ol {
        list-style-type: decimal;
    }
    .pretty-card .markdown-content li {
        margin: 0.4em 0;
        color: #374151;
        display: list-item;
    }
    .pretty-card .markdown-content blockquote {
        border-left: 4px solid #3b82f6;
        padding-left: 1em;
        margin: 1em 0;
        color: #6b7280;
        font-style: italic;
    }
    
    /* Image styling */
    .pretty-card img { 
        max-width: 100%; 
        height: auto; 
        border-radius: 8px; 
    }
    
    /* Table styling */
    .pretty-card table.pretty-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 13px;
        color: #111;
    }
    .pretty-card table.pretty-table th, 
    .pretty-card table.pretty-table td {
        border: 1px solid #e5e7eb;
        padding: 6px 8px;
        text-align: left;
    }
    .pretty-card table.pretty-table th { 
        background: #f9fafb; 
        font-weight: 600; 
    }
    </style>
    """
    
    title_html = f'<div class="pretty-title">{title}</div>' if title else ""
    card = f'<div class="pretty-card">{title_html}{rendered}</div>'
    display(HTML(css + card))
