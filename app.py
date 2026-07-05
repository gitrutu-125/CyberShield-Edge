from flask import Flask, redirect, url_for, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_dance.contrib.google import make_google_blueprint
from werkzeug.security import generate_password_hash

# -------------------------------
# Initialize Extensions
# -------------------------------
db = SQLAlchemy()
login_manager = LoginManager()


# -------------------------------
# User Model
# -------------------------------
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(100))

    username = db.Column(db.String(50), unique=True)

    organization = db.Column(db.String(100))

    phone = db.Column(db.String(15))

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=True)

    google_id = db.Column(db.String(100), unique=True)

    name = db.Column(db.String(100))

    picture = db.Column(db.Text)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------------------
# Create Flask App
# -------------------------------
def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "cybershield_secret_key"

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://postgres:root@localhost:5433/cybershield_db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager.init_app(app)

    login_manager.login_view = "login"

    # ---------------------------------------
    # Google OAuth
    # ---------------------------------------
    google_bp = make_google_blueprint(
        client_id="21441301027-u9hd397kltm2o23dhknd82895is2mpq2.apps.googleusercontent.com",
        client_secret="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",
        scope=[
            "profile",
            "email"
        ]
    )

    app.register_blueprint(
        google_bp,
        url_prefix="/login"
    )

    with app.app_context():
        db.create_all()

    # ---------------------------------------
    # Home
    # ---------------------------------------
    @app.route("/")
    def home():
        return redirect(url_for("login"))

    # ---------------------------------------
    # Login
    # ---------------------------------------
    @app.route("/login")
    def login():
        return render_template("login.html")

    # ---------------------------------------
    # Register
    # ---------------------------------------
    @app.route("/register", methods=["GET", "POST"])
    def register():

        if request.method == "POST":

            fullname = request.form["fullname"]
            username = request.form["username"]
            email = request.form["email"]
            organization = request.form["organization"]
            phone = request.form["phone"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]

            # Password Validation
            if password != confirm_password:
                flash("Passwords do not match.")
                return redirect(url_for("register"))

            # Username Check
            existing_username = User.query.filter_by(username=username).first()

            if existing_username:
                flash("Username already exists.")
                return redirect(url_for("register"))

            # Email Check
            existing_email = User.query.filter_by(email=email).first()

            if existing_email:
                flash("Email already registered.")
                return redirect(url_for("register"))

            # Hash Password
            hashed_password = generate_password_hash(password)

            # Save User
            new_user = User(
                fullname=fullname,
                username=username,
                organization=organization,
                phone=phone,
                email=email,
                password=hashed_password
            )

            db.session.add(new_user)
            db.session.commit()

            flash("Registration Successful. Please Login.")

            return redirect(url_for("login"))

        return render_template("register.html")

    # ---------------------------------------
    # Logout
    # ---------------------------------------
    @app.route("/logout")
    def logout():
        return redirect(url_for("login"))

    # ---------------------------------------
    # Dashboard
    # ---------------------------------------
    @app.route("/dashboard")
    def dashboard():

        if not google.authorized:
            return redirect(url_for("google.login"))

        resp = google.get("/oauth2/v2/userinfo")

        if not resp.ok:
            return "Failed to fetch user information."

        info = resp.json()

        user = User.query.filter_by(email=info["email"]).first()

        if not user:

            user = User(
                google_id=info["id"],
                name=info["name"],
                email=info["email"],
                picture=info["picture"]
            )

            db.session.add(user)
            db.session.commit()

        return render_template(
            "dashboard.html",
            user=user
        )

    # ---------------------------------------
    # Upload Dataset
    # ---------------------------------------
    @app.route("/upload")
    def upload_dataset():
        return "Upload Dataset"

    # ---------------------------------------
    # Preprocessing
    # ---------------------------------------
    @app.route("/preprocess")
    def preprocess():
        return "Data Preprocessing"

    # ---------------------------------------
    # Train Model
    # ---------------------------------------
    @app.route("/train")
    def train_model():
        return "Training ML Model"

    # ---------------------------------------
    # Prediction
    # ---------------------------------------
    @app.route("/predict")
    def predict():
        return "Intrusion Detection Prediction"

    # ---------------------------------------
    # Reports
    # ---------------------------------------
    @app.route("/reports")
    def reports():
        return "Reports Page"

    return app


# ---------------------------------------
# Run App
# ---------------------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)