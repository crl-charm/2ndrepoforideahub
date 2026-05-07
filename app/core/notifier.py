from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


class Notifier:
    def session_checked_out(self, payload: Dict[str, Any]) -> None:  # pragma: no cover
        raise NotImplementedError


@dataclass(frozen=True)
class NoopNotifier(Notifier):
    def session_checked_out(self, payload: Dict[str, Any]) -> None:
        return


@dataclass(frozen=True)
class SocketIONotifier(Notifier):
    socketio: Any

    def session_checked_out(self, payload: Dict[str, Any]) -> None:
        self.socketio.emit("session_checked_out", payload)

