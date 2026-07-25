"""Tests for API-key resolution, including reading a local .env file."""

from src import config


def test_reads_key_from_env_file(tmp_path, monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    # Tolerate spaces and quotes around the value.
    (tmp_path / ".env").write_text('# a comment\nMISTRAL_API_KEY = "sk-test-123"\n')
    monkeypatch.setattr(config, "_ROOT", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    assert config.get_mistral_api_key() == "sk-test-123"


def test_environment_variable_takes_priority(tmp_path, monkeypatch):
    monkeypatch.setenv("MISTRAL_API_KEY", "sk-from-env")
    (tmp_path / ".env").write_text("MISTRAL_API_KEY=sk-from-file\n")
    monkeypatch.setattr(config, "_ROOT", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    assert config.get_mistral_api_key() == "sk-from-env"


def test_missing_key_returns_empty(tmp_path, monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.setattr(config, "_ROOT", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    assert config.get_mistral_api_key() == ""
