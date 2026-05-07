from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


class Clock:
    def utcnow(self) -> datetime:  # pragma: no cover
        raise NotImplementedError


@dataclass(frozen=True)
class SystemClock(Clock):
    def utcnow(self) -> datetime:
        return datetime.utcnow()

