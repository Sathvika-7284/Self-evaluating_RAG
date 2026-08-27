import json

from src.memory import MemoryStore


def test_failed_check_becomes_future_guidance(tmp_path):
    store = MemoryStore(tmp_path / "memory.json")
    store.learn_from([{"name": "No unexplained jargon", "required_change": "Define embeddings."}])
    saved = json.loads((tmp_path / "memory.json").read_text())
    assert saved["common_failures"]["no_unexplained_jargon"]["count"] == 1
    assert "Define embeddings" in store.guidance()
