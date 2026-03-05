"""Tests for engine.postprocess: markdown post-processing rules."""

from sdwc_api.engine.postprocess import (
    _is_claude_managed,
    post_process,
    rule_collapse_blank_lines,
    rule_merge_consecutive_dividers,
    rule_remove_empty_sections,
    rule_remove_empty_tables,
    rule_remove_trailing_whitespace,
)

# ===== TestIsClaudeManaged =====


class TestIsClaudeManaged:
    def test_workplan_is_exempt(self) -> None:
        assert _is_claude_managed("docs/common/07-workplan.md") is True

    def test_working_log_is_exempt(self) -> None:
        assert _is_claude_managed("docs/common/09-working-log.md") is True

    def test_changelog_is_exempt(self) -> None:
        assert _is_claude_managed("docs/common/10-changelog.md") is True

    def test_troubleshooting_is_exempt(self) -> None:
        assert _is_claude_managed("docs/common/11-troubleshooting.md") is True

    def test_runbook_is_exempt(self) -> None:
        assert _is_claude_managed("docs/common/12-runbook.md") is True

    def test_regular_doc_not_exempt(self) -> None:
        assert _is_claude_managed("docs/common/01-requirements.md") is False

    def test_claude_md_not_exempt(self) -> None:
        assert _is_claude_managed("CLAUDE.md") is False


# ===== TestRuleRemoveEmptySections =====


class TestRuleRemoveEmptySections:
    def test_empty_before_same_level(self) -> None:
        content = "## Section A\n\n## Section B\nContent here\n"
        result = rule_remove_empty_sections(content)
        assert "## Section A" not in result
        assert "## Section B" in result
        assert "Content here" in result

    def test_empty_before_higher_level(self) -> None:
        """### followed by ## means ### is empty."""
        content = "### Sub\n\n## Next\nContent\n"
        result = rule_remove_empty_sections(content)
        assert "### Sub" not in result
        assert "## Next" in result

    def test_non_empty_with_content(self) -> None:
        content = "## Section A\nSome text\n## Section B\nMore text\n"
        result = rule_remove_empty_sections(content)
        assert "## Section A" in result
        assert "Some text" in result

    def test_non_empty_with_subsection(self) -> None:
        """## with ### below is NOT empty (has sub-content)."""
        content = "## Parent\n\n### Child\nContent\n"
        result = rule_remove_empty_sections(content)
        assert "## Parent" in result
        assert "### Child" in result

    def test_empty_before_divider(self) -> None:
        content = "## Empty\n\n---\n"
        result = rule_remove_empty_sections(content)
        assert "## Empty" not in result
        assert "---" in result

    def test_cascading_removal(self) -> None:
        """Removing ### leaves ## empty, both should be removed."""
        content = "## Parent\n\n### Child\n\n## Next\nContent\n"
        result = rule_remove_empty_sections(content)
        assert "## Parent" not in result
        assert "### Child" not in result
        assert "## Next" in result

    def test_header_at_end_of_file(self) -> None:
        content = "## Content\nText\n## Trailing\n\n"
        result = rule_remove_empty_sections(content)
        assert "## Trailing" not in result
        assert "## Content" in result

    def test_h1_not_affected(self) -> None:
        """# headers (h1) are never targeted for removal."""
        content = "# Title\n\n## Section\nContent\n"
        result = rule_remove_empty_sections(content)
        assert "# Title" in result


# ===== TestRuleMergeConsecutiveDividers =====


class TestRuleMergeConsecutiveDividers:
    def test_two_consecutive_merged(self) -> None:
        content = "---\n\n---\n"
        result = rule_merge_consecutive_dividers(content)
        assert result.count("---") == 1

    def test_three_consecutive_merged(self) -> None:
        content = "---\n\n---\n\n---\n"
        result = rule_merge_consecutive_dividers(content)
        assert result.count("---") == 1

    def test_single_divider_unchanged(self) -> None:
        content = "Before\n---\nAfter\n"
        result = rule_merge_consecutive_dividers(content)
        assert result.count("---") == 1

    def test_non_consecutive_unchanged(self) -> None:
        content = "---\nContent between\n---\n"
        result = rule_merge_consecutive_dividers(content)
        assert result.count("---") == 2


# ===== TestRuleCollapseBlankLines =====


class TestRuleCollapseBlankLines:
    def test_three_blanks_to_two(self) -> None:
        content = "A\n\n\n\nB\n"
        result = rule_collapse_blank_lines(content)
        # Should have at most 2 consecutive blank lines
        assert "\n\n\n\n" not in result
        assert "A" in result
        assert "B" in result

    def test_five_blanks_to_two(self) -> None:
        content = "A\n\n\n\n\n\nB\n"
        result = rule_collapse_blank_lines(content)
        assert "\n\n\n\n" not in result

    def test_two_blanks_unchanged(self) -> None:
        content = "A\n\n\nB\n"
        result = rule_collapse_blank_lines(content)
        assert result == content


# ===== TestRuleRemoveEmptyTables =====


class TestRuleRemoveEmptyTables:
    def test_header_separator_only_removed(self) -> None:
        content = "Before\n| A | B |\n|---|---|\nAfter\n"
        result = rule_remove_empty_tables(content)
        assert "| A | B |" not in result
        assert "|---|---|" not in result
        assert "Before" in result
        assert "After" in result

    def test_table_with_data_kept(self) -> None:
        content = "| A | B |\n|---|---|\n| 1 | 2 |\n"
        result = rule_remove_empty_tables(content)
        assert "| A | B |" in result
        assert "| 1 | 2 |" in result

    def test_multiple_empty_tables_removed(self) -> None:
        content = "| X |\n|---|\nText\n| Y |\n|---|\n"
        result = rule_remove_empty_tables(content)
        assert "| X |" not in result
        assert "| Y |" not in result
        assert "Text" in result

    def test_pipe_in_text_not_affected(self) -> None:
        content = "Use | for pipes\nNot a table\n"
        result = rule_remove_empty_tables(content)
        assert result == content


# ===== TestRuleRemoveTrailingWhitespace =====


class TestRuleRemoveTrailingWhitespace:
    def test_trailing_spaces_removed(self) -> None:
        content = "hello   \nworld  \n"
        result = rule_remove_trailing_whitespace(content)
        assert result == "hello\nworld\n"

    def test_trailing_tabs_removed(self) -> None:
        content = "hello\t\n"
        result = rule_remove_trailing_whitespace(content)
        assert result == "hello\n"

    def test_clean_lines_unchanged(self) -> None:
        content = "hello\nworld\n"
        result = rule_remove_trailing_whitespace(content)
        assert result == content


# ===== TestPostProcess =====


class TestPostProcess:
    def test_all_rules_applied(self) -> None:
        """Content with multiple issues gets all fixed."""
        content = "## Empty\n\n## Real\nContent\n---\n\n---\n\n\n\n\n| X |\n|---|\ntrailing   \n"
        result = post_process(content, "docs/common/01-requirements.md")
        assert "## Empty" not in result  # Rule 1
        assert result.count("---") == 1  # Rule 2
        assert "\n\n\n\n" not in result  # Rule 3
        assert "| X |" not in result  # Rule 4
        assert "trailing   " not in result  # Rule 5
        assert "trailing" in result

    def test_claude_managed_skips_rule1(self) -> None:
        """Empty sections preserved for Claude-managed files."""
        content = "## Empty\n\n## Next\nContent\n"
        result = post_process(content, "docs/common/07-workplan.md")
        assert "## Empty" in result

    def test_claude_managed_applies_rules_2_to_5(self) -> None:
        """Rules 2-5 still apply to Claude-managed files."""
        content = "## Empty\n\n## Next\n---\n\n---\ntrailing   \n"
        result = post_process(content, "docs/common/07-workplan.md")
        assert "## Empty" in result  # Rule 1 skipped
        assert result.count("---") == 1  # Rule 2 applied
        assert "trailing   " not in result  # Rule 5 applied

    def test_empty_content(self) -> None:
        result = post_process("", "docs/common/01-requirements.md")
        assert result == ""

    def test_clean_content_unchanged(self) -> None:
        content = "# Title\n\n## Section\nContent here.\n"
        result = post_process(content, "docs/common/01-requirements.md")
        assert result == content
