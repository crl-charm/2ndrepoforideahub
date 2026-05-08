from __future__ import annotations

import qrcode
import uuid
from io import BytesIO
from base64 import b64encode
from typing import Optional

from app import db
from app.models import SpaceType


class QRRepository:
    def generate_space_token(self, space_type_id: int) -> str:
        token = str(uuid.uuid4())[:8]
        space = db.session.query(SpaceType).filter_by(id=space_type_id).first()
        if space:
            space.qr_token = token
            db.session.commit()
        return token

    def get_space_by_token(self, token: str) -> Optional[SpaceType]:
        return db.session.query(SpaceType).filter_by(qr_token=token).first()

    def generate_qr_code(self, token: str, base_url: str = "http://localhost:5000") -> str:
        qr_url = f"{base_url}/order/{token}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
