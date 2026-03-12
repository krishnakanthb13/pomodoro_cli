import json
import pytest
from pathlib import Path
from unittest.mock import patch
import templates_manager

@pytest.fixture(autouse=True)
def reset_cache():
    templates_manager._TEMPLATE_CACHE = None
    yield

@pytest.fixture
def mock_templates_dir(tmp_path):
    # We need to patch TEMPLATES_DIR in the templates_manager module
    with patch('templates_manager.TEMPLATES_DIR', tmp_path):
        # Also ensure the directory exists for ensure_templates_dir()
        tmp_path.mkdir(exist_ok=True)
        yield tmp_path

def test_load_template_success_by_filename(mock_templates_dir):
    template_data = {"name": "Test Template", "work": 25}
    template_file = mock_templates_dir / "test.json"
    template_file.write_text(json.dumps(template_data), encoding='utf-8')

    result = templates_manager.load_template("test")
    assert result == template_data

def test_load_template_success_by_name(mock_templates_dir):
    template_data = {"name": "Deep Work", "work": 50}
    template_file = mock_templates_dir / "custom.json"
    template_file.write_text(json.dumps(template_data), encoding='utf-8')

    result = templates_manager.load_template("Deep Work")
    assert result == template_data

def test_load_template_invalid_json_filename_match(mock_templates_dir):
    template_file = mock_templates_dir / "invalid.json"
    template_file.write_text("invalid json {", encoding='utf-8')

    result = templates_manager.load_template("invalid")
    assert result is None

def test_load_template_invalid_json_name_match_loop(mock_templates_dir):
    # Create an invalid JSON file
    (mock_templates_dir / "a_invalid.json").write_text("invalid json", encoding='utf-8')

    # Create a valid JSON file that matches the name
    template_data = {"name": "Target", "work": 25}
    (mock_templates_dir / "b_valid.json").write_text(json.dumps(template_data), encoding='utf-8')

    # load_template should skip the invalid one and find the valid one
    result = templates_manager.load_template("Target")
    assert result == template_data

def test_load_template_io_error(mock_templates_dir):
    template_file = mock_templates_dir / "error.json"
    template_file.write_text('{"name": "error"}', encoding='utf-8')

    # Patching open within templates_manager to raise IOError
    with patch("templates_manager.open", side_effect=IOError):
        result = templates_manager.load_template("error")
        assert result is None

def test_load_template_not_found(mock_templates_dir):
    result = templates_manager.load_template("nonexistent")
    assert result is None
