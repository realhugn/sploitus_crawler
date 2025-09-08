from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class ExploitData:
    id: str
    title: str
    published: str
    source: str
    score: float | None = None
    href: str | None = None
    type: str | None = None
    language: str | None = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get_hash(self) -> str:
        import hashlib
        return hashlib.md5(self.id.encode()).hexdigest()