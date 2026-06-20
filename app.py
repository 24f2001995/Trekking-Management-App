from flask import Flask
from database import db
from models import User, Trek, Booking, StaffProfile

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def home():
    return "Trekking Management Application"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database created successfully!")

    app.run(debug=True)