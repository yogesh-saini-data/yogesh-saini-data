"""
test_renderer.py — Unit tests for template loading, replacement, and validation.
"""

import sys
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from renderer import replace_section, validate_readme


def test_replace_section():
    template = "Header\n<!-- TEST_START -->\nOld Content\n<!-- TEST_END -->\nFooter"
    result = replace_section(template, "TEST", "New Content")

    assert "Old Content" not in result
    assert "New Content" in result
    assert "<!-- TEST_START -->" in result
    assert "<!-- TEST_END -->" in result


def test_validate_readme_valid():
    content = "# Title\n\nSome body text\n\n## Section\n- Item 1\n- Item 2"
    errors = validate_readme(content)
    assert len(errors) == 0


def test_validate_readme_invalid():
    errors = validate_readme("")
    assert "README is empty" in errors
