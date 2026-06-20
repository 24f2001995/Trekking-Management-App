from app import app
from database import db
from models import User


with app.app_context():
    admin = User.query.filter_by(email="admin@tma.com").first()

    if admin:
        print("Admin already exists.")
    else:
        admin = User(
            name="Admin",
            email="admin@tma.com",
            password="admin123",
            role="admin",
            phone="1234567891",
            is_approved=True,
            is_blacklisted=False
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully.")