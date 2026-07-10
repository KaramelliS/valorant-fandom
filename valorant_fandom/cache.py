import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Optional


class Cache:
    def __init__(self, cache_dir: Optional[str] = None, ttl: int = 3600):
        if cache_dir is None:
            cache_dir = os.path.join(Path.home(), ".valorant_cache")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl

    def _key_path(self, key: str) -> Path:
        h = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{h}.json"

    def get(self, key: str) -> Optional[Any]:
        path = self._key_path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if time.time() - data["_ts"] > self.ttl:
                path.unlink()
                return None
            return data["_value"]
        except (json.JSONDecodeError, KeyError):
            path.unlink(missing_ok=True)
            return None

    def set(self, key: str, value: Any) -> None:
        path = self._key_path(key)
        data = {"_ts": time.time(), "_value": value}
        path.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")

    def clear(self) -> int:
        count = 0
        for f in self.cache_dir.glob("*.json"):
            f.unlink()
            count += 1
        return count
