from flask import Flask, render_template, request, redirect, url_for
import flask_login
from flask_sqlalchemy import SQLAlchemy
import time
import bcrypt
from uuid import uuid4
import statistics

app = Flask(__name__)

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Load the secret key from a file for session management
with open("secret.key", "r") as file:
    app.config["SECRET_KEY"] = file.read().strip()

#------------# DATABASE MODELS #------------#

class User(db.Model, flask_login.UserMixin):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.Integer, nullable=False)
    last_login = db.Column(db.Integer)

    def update_last_login(self):
        self.last_login = int(time.time())

class Weight(db.Model):
    __tablename__ = "weight"

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, primary_key=True)
    weight = db.Column(db.Integer, nullable=False)
    satisfaction = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.Integer, nullable=False)

#------------# DATABASE + BASIC SETUP #------------#

# Create the database tables
with app.app_context():
    db.create_all()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(email):
    return User.query.get(email)

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

#------------# AUTH ROUTES #------------#

@app.route("/account", methods=["GET"])
@flask_login.login_required
def account():
    user = flask_login.current_user
    weight_history = sorted(Weight.query.filter_by(user_id=user.id).all(), key=lambda w: w.created_at, reverse=True)
    weight_data = {
        "history": weight_history,
        "lowest_weight": min(weight_history, key=lambda w: w.weight),
        "highest_weight": max(weight_history, key=lambda w: w.weight),
        "average_satisfaction": statistics.mean([w.satisfaction for w in weight_history])
    }
    return render_template("account.html", user=user, weight_data=weight_data)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()  # Fetch user by email
        
        if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):  # Check hashed password
            user.update_last_login()
            db.session.commit()  # Save the updated last_login
            flask_login.login_user(user)  # Log in the user
            return redirect(url_for("account"))
        return render_template("login.html", error_message="Error: Invalid email or password.")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    flask_login.logout_user()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if email and password and confirm_password:
            if password == confirm_password:
                if User.query.filter_by(email=email).first():
                    return render_template("register.html", error_message="Error: Email is already in use.")
                
                # Hash the password using bcrypt
                hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

                created_at = int(time.time())
                new_user = User(id=str(uuid4()), email=email, password=hashed_password.decode("utf-8"), created_at=created_at, last_login=created_at)
                db.session.add(new_user)
                db.session.commit()
                flask_login.login_user(new_user)
                new_user.update_last_login()
                return redirect(url_for("account"))
            return render_template("register.html", error_message="Error: Passwords do not match.")
        return render_template("register.html", error_message="Error: Missing a required field.")
    
    return render_template("register.html")

#------------# API ROUTES #------------#

@app.route("/api/weight", methods=["POST"])
@flask_login.login_required
def api_weight():
    if request.method == "POST":
        weight = request.form.get("weight")
        satisfaction = request.form.get("satisfaction")
        
        if weight and satisfaction:
            user_id = flask_login.current_user.id
            created_at = int(time.time())
            new_weight = Weight(id=str(uuid4()), user_id=user_id, weight=weight, satisfaction=satisfaction, created_at=created_at)
            db.session.add(new_weight)
            db.session.commit()
            return redirect(request.referrer)
        else:
            return "Error: Missing a required field."

if __name__ == "__main__":
    app.run(port=80, debug=True)
