from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    phone = db.Column(db.String(20))

    is_approved = db.Column(db.Boolean, default=False)

    is_blacklisted = db.Column(db.Boolean, default=False)

    #created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    location = db.Column(db.String(120), nullable=False)

    difficulty = db.Column(db.String(20), nullable=False)

    duration = db.Column(db.Integer, nullable=False)

    available_slots = db.Column(db.Integer, nullable=False)

    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    status = db.Column(db.String(20), default="Pending")

    start_date = db.Column(db.Date)

    end_date = db.Column(db.Date)

    assigned_staff = db.relationship("User", foreign_keys=[assigned_staff_id])
    


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)

    booking_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default="Booked")

    payment_status = db.Column(db.String(20), default="Unpaid")

    attendance = db.Column(db.Boolean, default=False)
    user = db.relationship("User", backref="bookings")
    trek = db.relationship("Trek", backref="bookings")

class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    experience = db.Column(db.String(100))

    contact_details = db.Column(db.String(200))