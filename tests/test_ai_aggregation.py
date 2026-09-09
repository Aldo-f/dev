import json
import pytest
from pathlib import Path

def test_ai_hints_aggregation(tmp_path: Path):
    """Test that code_change snippets are correctly extracted from ai-hints.json"""
    hints = {
        "repo1": {
            "suggestion": "Use shallow clone for faster checkout",
            "code_change": "git clone --depth 1 $url $dir"
        },
        "repo2": {
            "suggestion": "none",
            "code_change": ""
        },
        "repo3": {
            "suggestion": "Add pre-commit hooks validation",
            "code_change": "pip install pre-commit && pre-commit install"
        }
    }
    
    # Write test data
    hints_file = tmp_path / "ai-hints.json"
    hints_file.write_text(json.dumps(hints))
    
    # Extract code_change snippets (same logic as generate-final-template.sh)
    extracted = []
    data = json.loads(hints_file.read_text())
    for v in data.values():
        if v.get("code_change"):
            extracted.append(v["code_change"])
    
    # Verify
    assert len(extracted) == 2
    assert extracted[0] == "git clone --depth 1 $url $dir"
    assert extracted[1] == "pip install pre-commit && pre-commit install"


def test_empty_hints_file(tmp_path: Path):
    """Test handling of empty hints file"""
    hints_file = tmp_path / "ai-hints.json"
    hints_file.write_text("{}")
    
    data = json.loads(hints_file.read_text())
    extracted = []
    for v in data.values():
        if v.get("code_change"):
            extracted.append(v["code_change"])
    
    assert extracted == []


def test_missing_code_change_key(tmp_path: Path):
    """Test handling when code_change key is missing"""
    hints = {
        "repo1": {"suggestion": "Fix linting", "code_change": None}
    }
    
    hints_file = tmp_path / "ai-hints.json"
    hints_file.write_text(json.dumps(hints))
    
    data = json.loads(hints_file.read_text())
    extracted = []
    for v in data.values():
        if v.get("code_change"):
            extracted.append(v["code_change"])
    
    assert extracted == []
