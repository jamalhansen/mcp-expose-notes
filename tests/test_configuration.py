from expose_notes.configuration import pydanticize_configuration

def test_pydanticize_configuration():
    """
    Test the pydanticize_configuration function with a mock YAML data.
    """
    yaml_data = {
        "notes": [
            {
                "source_id": 1,
                "name": "Test Note",
                "path": "/path/to/test_note.md",
                "description": "This is a test note."
            }
        ],
        "vault_path": "/path/to/vault",
        "daily_notes": {
            "enabled": True,
            "paths": ["/daily_notes"]
        }
    }

    config = pydanticize_configuration(yaml_data)

    assert config.notes[0].source_id == 1
    assert config.notes[0].name == "Test Note"
    assert config.vault_path == "/path/to/vault"
    assert config.daily_notes.enabled is True
    assert config.daily_notes.paths == ["/daily_notes"]

