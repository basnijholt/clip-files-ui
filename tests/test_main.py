"""Tests for the main application logic, focusing on configuration handling."""

import os
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml

# Assuming main.py is in the parent directory relative to tests/
# Adjust sys.path if needed based on your test runner setup
try:
    # Ensure save_config is imported
    from main import CONFIG_FILE, Config, RepoConfig, load_config, save_config
except ImportError:
    import sys

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    # Ensure save_config is imported here too
    from main import CONFIG_FILE, Config, RepoConfig, load_config, save_config


# --- Tests for load_config ---


# Note: Use forward slashes in patch targets even on Windows
@patch("main.os.path.exists")
# Use triple single quotes for the multiline string data
@patch(
    "main.open",
    new_callable=mock_open,
    read_data="""\
repositories:
  - name: repo1
    url: http://example.com/repo1.git
    branch: main
    patterns:
      core:
        - src/*.py
      docs:
        - docs/*.md
""",
)
@patch("main.yaml.safe_load")
def test_load_config_success(
    mock_safe_load: Mock,
    mock_file_open: Mock,
    mock_exists: Mock,
) -> None:
    """Test successfully loading a valid config file."""
    mock_exists.return_value = True
    mock_config_data = {
        "repositories": [
            {
                "name": "repo1",
                "url": "http://example.com/repo1.git",
                "branch": "main",
                "patterns": {"core": ["src/*.py"], "docs": ["docs/*.md"]},
            },
        ],
    }
    mock_safe_load.return_value = mock_config_data

    config = load_config()

    assert isinstance(config, Config)
    assert len(config.repositories) == 1
    assert config.repositories[0].name == "repo1"
    assert config.repositories[0].url == "http://example.com/repo1.git"
    assert config.repositories[0].branch == "main"
    assert config.repositories[0].patterns["core"] == ["src/*.py"]
    mock_exists.assert_called_once_with(CONFIG_FILE)
    # Check open was called correctly for reading
    mock_file_open.assert_called_once_with(CONFIG_FILE)
    mock_safe_load.assert_called_once()


@patch("main.os.path.exists")
def test_load_config_file_not_found(mock_exists: Mock) -> None:
    """Test loading config when the file does not exist."""
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError, match=f"Configuration file {CONFIG_FILE} not found"):
        load_config()
    mock_exists.assert_called_once_with(CONFIG_FILE)


@patch("main.os.path.exists")
@patch("main.open", new_callable=mock_open, read_data="")  # Empty file
@patch("main.yaml.safe_load")
def test_load_config_empty_file(
    mock_safe_load: Mock,
    mock_file_open: Mock,
    mock_exists: Mock,
) -> None:
    """Test loading config when the file is empty."""
    mock_exists.return_value = True
    mock_safe_load.return_value = None  # Simulate empty YAML load result

    with pytest.raises(ValueError, match="Configuration file is empty"):
        load_config()

    mock_exists.assert_called_once_with(CONFIG_FILE)
    mock_file_open.assert_called_once_with(CONFIG_FILE)
    mock_safe_load.assert_called_once()


@patch("main.os.path.exists")
@patch("main.open", new_callable=mock_open, read_data="invalid yaml: :")
@patch("main.yaml.safe_load")
def test_load_config_yaml_error(
    mock_safe_load: Mock,
    mock_file_open: Mock,
    mock_exists: Mock,
) -> None:
    """Test loading config with invalid YAML content."""
    mock_exists.return_value = True
    # Simulate yaml parser raising an error
    mock_safe_load.side_effect = yaml.YAMLError("Bad YAML")

    with pytest.raises(yaml.YAMLError):
        load_config()

    mock_exists.assert_called_once_with(CONFIG_FILE)
    mock_file_open.assert_called_once_with(CONFIG_FILE)
    mock_safe_load.assert_called_once()


# --- Tests for save_config ---


@patch("main.open", new_callable=mock_open)
@patch("main.yaml.dump")
# Need to mock json.loads as it's called inside save_config
@patch("main.json.loads")
def test_save_config_success(
    mock_json_loads: Mock,
    mock_yaml_dump: Mock,
    mock_file_open: Mock,
) -> None:
    """Test successfully saving a config object."""
    # Sample config object to save
    repo = RepoConfig(
        name="repo2",
        url="http://example.com/repo2.git",
        branch="dev",
        patterns={"all": ["*"]},
    )
    config_to_save = Config(repositories=[repo])

    # Mock json.loads to return a dictionary that yaml.dump expects
    # config_to_save.model_dump_json() produces a JSON string, json.loads parses it back to dict
    mock_parsed_dict = {
        "repositories": [
            {
                "name": "repo2",
                "url": "http://example.com/repo2.git",
                "branch": "dev",
                "patterns": {"all": ["*"]},
            },
        ],
    }
    # This is what json.loads should return after parsing the model's JSON output
    mock_json_loads.return_value = mock_parsed_dict

    save_config(config_to_save)

    # Check open was called correctly for writing
    mock_file_open.assert_called_once_with(CONFIG_FILE, "w")
    # Get the file handle mock from mock_open
    file_handle = mock_file_open()
    # Check json.loads was called with the Pydantic model's JSON output
    mock_json_loads.assert_called_once_with(config_to_save.model_dump_json())
    # Check yaml.dump received the dictionary parsed from JSON and the file handle
    mock_yaml_dump.assert_called_once_with(mock_parsed_dict, file_handle)
