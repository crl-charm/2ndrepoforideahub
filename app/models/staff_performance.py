from datetime import datetime, date
from decimal import Decimal
from app import db


class StaffPerformanceLog(db.Model):
    __tablename__ = "staff_performance_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    shift_date = db.Column(db.Date, nullable=False)
    orders_handled = db.Column(db.Integer, nullable=False, default=0)
    avg_order_minutes = db.Column(db.Numeric(8, 2), nullable=False, default=0)
    sessions_managed = db.Column(db.Integer, nullable=False, default=0)
    upsell_count = db.Column(db.Integer, nullable=False, default=0)
    admin_note = db.Column(db.Text, nullable=True)
    score = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="performance_logs")

    def calculate_score(self) -> Decimal:
        score = (
            Decimal(str(self.orders_handled)) * Decimal("1.0")
            + Decimal(str(self.sessions_managed)) * Decimal("2.0")
            + Decimal(str(self.upsell_count)) * Decimal("1.5")
            - Decimal(str(self.avg_order_minutes)) * Decimal("0.1")
        )
        return score.quantize(Decimal("0.01"))
