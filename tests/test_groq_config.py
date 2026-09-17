import importlib
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))


def test_groq_api_key_is_loaded_from_groq_or_gouq_env(monkeypatch):
    monkeypatch.setenv('GOUQ_API_KEY', 'gsk_test_key')
    monkeypatch.delenv('GROQ_API_KEY', raising=False)
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('LLM_API_KEY', raising=False)

    import app.config as config_module
    importlib.reload(config_module)

    assert config_module.settings.groq_api_key == 'gsk_test_key'
    assert config_module.settings.llm_api_key == 'gsk_test_key'
