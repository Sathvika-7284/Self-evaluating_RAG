import json
from pathlib import Path


class MemoryStore:
    """Persists recurring failure guidance for later lesson-generation runs."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "common_failures": {}, "successful_patterns": []
        }

    def guidance(self) -> str:
        items = [entry["guidance"] for entry in self.data.get("common_failures", {}).values() if entry.get("guidance")]
        return "\n".join(f"- {item}" for item in items)

    def learn_from(self, failed_checks: list[dict]) -> None:
        for check in failed_checks:
            key = check["name"].lower().replace(" ", "_")
            entry = self.data.setdefault("common_failures", {}).setdefault(
                key, {"count": 0, "guidance": check["required_change"]}
            )
            entry["count"] += 1
            entry["guidance"] = check["required_change"]
        self._save()

    def record_success(self) -> None:
        pattern = "A passing lesson used all required headings, a concrete example, and an explicit limitation."
        if pattern not in self.data.setdefault("successful_patterns", []):
            self.data["successful_patterns"].append(pattern)
        self._save()

    def reset(self) -> None:
        self.data = {"common_failures": {}, "successful_patterns": []}
        self._save()

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
