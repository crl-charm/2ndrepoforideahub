from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from app.repositories.qr_repository import QRRepository


@dataclass(frozen=True)
class QRService:
    repo: QRRepository

    def get_space_qr(self, space_type_id: int, base_url: str) -> dict[str, Any]:
        token = self.repo.generate_space_token(space_type_id)
        qr_code = self.repo.generate_qr_code(token, base_url)
        return {
            "success": True,
            "data": {
                "token": token,
                "qr_code": qr_code,
                "order_url": f"{base_url}/order/{token}",
            },
        }

    def get_space_by_token(self, token: str) -> dict[str, Any] | tuple[dict[str, Any], int]:
        space = self.repo.get_space_by_token(token)
        if not space:
            return {"error": "Invalid QR token"}, 404
        return {
            "success": True,
            "data": {
                "space_id": space.id,
                "space_name": space.name,
                "rate_per_minute": float(space.rate_per_minute),
            },
        }
