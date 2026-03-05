"""Markdown post-processing rules for rendered SDwC templates.

Applies 5 cleanup rules per generation_rules.md §11, in strict order:
1. Remove empty sections (exempt for Claude-managed files)
2. Merge consecutive dividers
3. Collapse excessive blank lines
4. Remove empty tables
5. Remove trailing whitespace
"""

from __future__ import annotations

import re

_CLAUDE_MANAGED_PREFIXES: frozenset[str] = frozenset(
    {
        "07-workplan",
        "09-working-log",
        "10-changelog",
        "11-troubleshooting",
        "12-runbook",
    }
)


def _is_claude_managed(output_path: str) -> bool:
    """Check if a file is Claude-managed (exempt from Rule 1).

    Args:
        output_path: Output path key from render_all (forward-slash separated).
    """
    basename = output_path.rsplit("/", 1)[-1]
    return any(basename.startswith(prefix) for prefix in _CLAUDE_MANAGED_PREFIXES)


def _remove_empty_sections_pass(content: str) -> str:
    """Single pass: remove ## or ### headers with no content before next same-or-higher header or ---."""
    lines = content.split("\n")
    to_remove: set[int] = set()

    i = 0
    while i < len(lines):
        match = re.match(r"^(#{2,3})\s", lines[i])
        if not match:
            i += 1
            continue

        header_level = len(match.group(1))

        # Look ahead past blank lines
        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1

        if j >= len(lines):
            # Header at end of file with only blanks after → empty section
            for k in range(i, j):
                to_remove.add(k)
            i = j
            continue

        next_line = lines[j]
        next_header = re.match(r"^(#{2,3})\s", next_line)
        is_divider = next_line.strip() == "---"

        if is_divider:
            for k in range(i, j):
                to_remove.add(k)
        elif next_header:
            next_level = len(next_header.group(1))
            if next_level <= header_level:
                # Same or higher level → empty section
                for k in range(i, j):
                    to_remove.add(k)

        i += 1

    return "\n".join(line for idx, line in enumerate(lines) if idx not in to_remove)


def rule_remove_empty_sections(content: str) -> str:
    """Remove ## or ### headers followed by same-or-higher level header or --- divider.

    Iterates until stable to handle cascading removal (removing ### may leave ## empty).
    Only targets ## and ### headers, not # (document title).
    """
    previous = ""
    result = content
    while result != previous:
        previous = result
        result = _remove_empty_sections_pass(result)
    return result


def rule_merge_consecutive_dividers(content: str) -> str:
    """Collapse multiple consecutive --- dividers (possibly separated by blank lines) into one."""
    lines = content.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == "---":
            result.append(lines[i])
            # Skip any following (blank lines + ---) sequences
            j = i + 1
            while j < len(lines):
                # Skip blank lines
                k = j
                while k < len(lines) and lines[k].strip() == "":
                    k += 1
                # If next non-blank is ---, skip the blank lines and the ---
                if k < len(lines) and lines[k].strip() == "---":
                    j = k + 1
                else:
                    break
            i = j
        else:
            result.append(lines[i])
            i += 1
    return "\n".join(result)


def rule_collapse_blank_lines(content: str) -> str:
    """Reduce 3+ consecutive blank lines to exactly 2."""
    lines = content.split("\n")
    result: list[str] = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)
    return "\n".join(result)


def rule_remove_empty_tables(content: str) -> str:
    """Remove tables with only header + separator row and no data rows."""
    lines = content.split("\n")
    to_remove: set[int] = set()

    i = 0
    while i < len(lines):
        # Detect empty table: header row + separator row with no data row following
        if (
            lines[i].startswith("|")
            and i + 1 < len(lines)
            and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1])
            and (i + 2 >= len(lines) or not lines[i + 2].startswith("|"))
        ):
            to_remove.add(i)
            to_remove.add(i + 1)
            i += 2
            continue
        i += 1

    return "\n".join(line for idx, line in enumerate(lines) if idx not in to_remove)


def rule_remove_trailing_whitespace(content: str) -> str:
    """Strip trailing whitespace from each line."""
    return "\n".join(line.rstrip() for line in content.split("\n"))


def _apply_rules(content: str, output_path: str) -> str:
    """Single pass of all post-processing rules."""
    result = content

    # Rule 1: Remove empty sections (exempt for Claude-managed files)
    if not _is_claude_managed(output_path):
        result = rule_remove_empty_sections(result)

    # Rule 2: Merge consecutive dividers
    result = rule_merge_consecutive_dividers(result)

    # Rule 3: Collapse excessive blank lines
    result = rule_collapse_blank_lines(result)

    # Rule 4: Remove empty tables
    result = rule_remove_empty_tables(result)

    # Rule 5: Remove trailing whitespace
    result = rule_remove_trailing_whitespace(result)

    return result


def post_process(content: str, output_path: str) -> str:
    """Apply all post-processing rules to rendered markdown content.

    Rules are applied in order 1→5, iterating until stable to handle
    cross-rule interactions (e.g., empty table removal creating empty sections).
    Rule 1 is skipped for Claude-managed files.

    Args:
        content: Rendered markdown content from Jinja2.
        output_path: Output file path (for Claude-managed file detection).
    """
    previous = ""
    result = content
    while result != previous:
        previous = result
        result = _apply_rules(result, output_path)
    return result
