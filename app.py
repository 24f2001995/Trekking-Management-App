from flask import Flask, render_template, request, redirect, session
from database import db
from models import User, Trek, Booking, StaffProfile
from sqlalchemy import or_

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

    total_users = User.query.filter_by(role="user").count()
    total_staff = User.query.filter_by(
    role="staff",
    is_approved=True
    ).count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings
    )


@app.route("/staff/dashboard")
def staff_dashboard():
    if "user_id" not in session or session["role"] != "staff":
        return redirect("/login")

    staff = User.query.get(session["user_id"])

    assigned_treks = Trek.query.filter_by(
        assigned_staff_id=staff.id
    ).all()

    return render_template(
        "staff_dashboard.html",
        staff=staff,
        assigned_treks=assigned_treks
    )


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

@app.route("/admin/treks", methods=["GET", "POST"])
def admin_treks():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        difficulty = request.form["difficulty"]
        duration = request.form["duration"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        available_slots = request.form["available_slots"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        new_trek = Trek(
            new_trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            start_date=start_date,
            end_date=end_date,
            available_slots=available_slots,
            status="Open"
        )
        )

        db.session.add(new_trek)
        db.session.commit()

        return redirect("/admin/treks")

    treks = Trek.query.all()
    staff_list = User.query.filter_by(
        role="staff",
        is_approved=True,
        is_blacklisted=False
        ).all()

    return render_template(
        "admin_treks.html",
        treks=treks,
        staff_list=staff_list
        )

@app.route("/admin/users")
def admin_users():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    users = User.query.filter_by(role="user").all()
    return render_template("admin_users.html", users=users)


@app.route("/admin/delete-trek/<int:trek_id>")
def delete_trek(trek_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    trek = Trek.query.get(trek_id)

    if trek:
        db.session.delete(trek)
        db.session.commit()

    return redirect("/admin/treks")


@app.route("/admin/edit-trek/<int:trek_id>", methods=["GET", "POST"])
def edit_trek(trek_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    trek = Trek.query.get(trek_id)

    if request.method == "POST":
        trek.name = request.form["name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration = request.form["duration"]
        trek.start_date = request.form["start_date"]
        trek.end_date = request.form["end_date"]
        trek.available_slots = request.form["available_slots"]

        db.session.commit()

        return redirect("/admin/treks")

    return render_template("edit_trek.html", trek=trek)

@app.route("/admin/blacklist-user/<int:user_id>")
def blacklist_user(user_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    user = User.query.get(user_id)

    if user and user.role == "user":
        user.is_blacklisted = True
        db.session.commit()

    return redirect("/admin/users")


@app.route("/admin/unblacklist-user/<int:user_id>")
def unblacklist_user(user_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    user = User.query.get(user_id)

    if user and user.role == "user":
        user.is_blacklisted = False
        db.session.commit()

    return redirect("/admin/users")

@app.route("/admin/blacklist-staff/<int:staff_id>")
def blacklist_staff(staff_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    staff = User.query.get(staff_id)

    if staff and staff.role == "staff":
        staff.is_blacklisted = True
        db.session.commit()

    return redirect("/admin/staff")


@app.route("/admin/unblacklist-staff/<int:staff_id>")
def unblacklist_staff(staff_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    staff = User.query.get(staff_id)

    if staff and staff.role == "staff":
        staff.is_blacklisted = False
        db.session.commit()

    return redirect("/admin/staff")

@app.route("/admin/assign-staff/<int:trek_id>", methods=["POST"])
def assign_staff(trek_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    staff_id = int(request.form["staff_id"])

    trek = Trek.query.get(trek_id)

    if trek:
        if staff_id == 0:
            trek.assigned_staff_id = None
        else:
            staff = User.query.get(staff_id)

            if staff and staff.role == "staff" and staff.is_approved and not staff.is_blacklisted:
                trek.assigned_staff_id = staff.id

        db.session.commit()

    return redirect("/admin/treks")

@app.route("/admin/bookings")
def admin_bookings():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    bookings = Booking.query.all()
    return render_template("admin_bookings.html", bookings=bookings)

@app.route("/admin/search")
def admin_search():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    keyword = request.args.get("keyword", "")

    trek_results = []
    user_results = []
    staff_results = []

    if keyword:
        trek_results = Trek.query.filter(
            or_(
                Trek.name.contains(keyword),
                Trek.location.contains(keyword),
                Trek.difficulty.contains(keyword),
                Trek.id == keyword if keyword.isdigit() else False
            )
        ).all()

        user_results = User.query.filter(
            User.role == "user",
            or_(
                User.name.contains(keyword),
                User.email.contains(keyword),
                User.id == keyword if keyword.isdigit() else False
            )
        ).all()

        staff_results = User.query.filter(
            User.role == "staff",
            or_(
                User.name.contains(keyword),
                User.email.contains(keyword),
                User.id == keyword if keyword.isdigit() else False
            )
        ).all()

    return render_template(
        "admin_search.html",
        keyword=keyword,
        trek_results=trek_results,
        user_results=user_results,
        staff_results=staff_results
    )

@app.route("/staff/manage-trek/<int:trek_id>", methods=["GET", "POST"])
def staff_manage_trek(trek_id):
    if "user_id" not in session or session["role"] != "staff":
        return redirect("/login")

    staff_id = session["user_id"]

    trek = Trek.query.get(trek_id)

    if not trek or trek.assigned_staff_id != staff_id:
        return "You are not allowed to manage this trek."

    if request.method == "POST":
        trek.available_slots = request.form["available_slots"]
        trek.status = request.form["status"]

        db.session.commit()

        return redirect("/staff/dashboard")

    return render_template("manage_trek.html", trek=trek)

@app.route("/staff/participants/<int:trek_id>")
def staff_participants(trek_id):
    if "user_id" not in session or session["role"] != "staff":
        return redirect("/login")

    staff_id = session["user_id"]

    trek = Trek.query.get(trek_id)

    # Only the assigned staff can view participants
    if not trek or trek.assigned_staff_id != staff_id:
        return "You are not allowed to view participants for this trek."

    bookings = Booking.query.filter_by(trek_id=trek.id).all()

    return render_template(
        "staff_participants.html",
        trek=trek,
        bookings=bookings
    )

@app.route("/staff/profile", methods=["GET", "POST"])
def staff_profile():
    if "user_id" not in session or session["role"] != "staff":
        return redirect("/login")

    staff = User.query.get(session["user_id"])

    if request.method == "POST":
        staff.name = request.form["name"]
        staff.phone = request.form["phone"]
        staff.password = request.form["password"]

        db.session.commit()

        return redirect("/staff/dashboard")

    return render_template("staff_profile.html", staff=staff)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database created successfully!")

    app.run(debug=True)