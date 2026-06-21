from flask import Flask, render_template, request, redirect, session
from database import db
from models import User, Trek, Booking, StaffProfile

app = Flask(__name__)
app.secret_key = "simple-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def home():
    return """
    <h1>Trekking Management Application</h1>

    <a href="/login">Login</a><br><br>

    <a href="/register">Register</a>
    """

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            if user.is_blacklisted:
                return "Your account is blacklisted."

            if user.role == "staff" and not user.is_approved:
                return "Your staff account is waiting for admin approval."

            session["user_id"] = user.id
            session["role"] = user.role

            if user.role == "admin":
                return redirect("/admin/dashboard")
            elif user.role == "staff":
                return redirect("/staff/dashboard")
            else:
                return redirect("/user/dashboard")

        return "Invalid email or password."

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        role = request.form["role"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered."

        new_user = User(
            name=name,
            email=email,
            password=password,
            phone=phone,
            role=role,
            is_approved=True if role == "user" else False,
            is_blacklisted=False
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    return """
    <h1>Admin Dashboard</h1>

    <a href="/admin/staff">Manage Staff</a><br><br>

    <a href="/logout">Logout</a>
    """


@app.route("/staff/dashboard")
def staff_dashboard():
    if "user_id" not in session or session["role"] != "staff":
        return redirect("/login")

    return "Staff Dashboard"


@app.route("/user/dashboard")
def user_dashboard():
    if "user_id" not in session or session["role"] != "user":
        return redirect("/login")

    return """
    <h1>User Dashboard</h1>

    <a href="/user/treks">View Available Treks</a><br><br>

    <a href="/user/bookings">My Bookings / Trekking History</a><br><br>

    <a href="/user/profile">Edit Profile</a><br><br>

    <a href="/logout">Logout</a>
    """

@app.route("/user/treks")
def user_treks():
    if "user_id" not in session or session["role"] != "user":
        return redirect("/login")

    return "Available Treks Page"


@app.route("/user/bookings")
def user_bookings():
    if "user_id" not in session or session["role"] != "user":
        return redirect("/login")

    return "My Bookings and Trekking History Page"


@app.route("/user/profile")
def user_profile():
    if "user_id" not in session or session["role"] != "user":
        return redirect("/login")

    return "Edit Profile Page"

@app.route("/admin/staff")
def admin_staff():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    staff_list = User.query.filter_by(role="staff").all()
    return render_template("admin_staff.html", staff_list=staff_list)


@app.route("/admin/approve-staff/<int:staff_id>")
def approve_staff(staff_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    staff = User.query.get(staff_id)

    if staff and staff.role == "staff":
        staff.is_approved = True
        db.session.commit()

    return redirect("/admin/staff")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database created successfully!")

    app.run(debug=True)