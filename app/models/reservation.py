from datetime import datetime, date, time
from app import db


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_contact = db.Column(db.String(100), nullable=True)
    space_type_id = db.Column(db.Integer, db.ForeignKey("space_types.id"), nullable=False)
    reserved_date = db.Column(db.Date, nullable=False)
    reserved_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False, default=60)
    number_of_people = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), default="pending", nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    space_type = db.relationship("SpaceType", backref="reservations")
