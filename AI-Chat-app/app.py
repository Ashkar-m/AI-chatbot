from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from flask_bcrypt import Bcrypt
import stripe
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask import jsonify


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2000@localhost:5432/chat'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
Bootstrap(app)

stripe.api_key = "sk_test_51QV6ZtIqpMVb5nWecYRXgtp0OeIxWp5CQWzCsv7r0wqH6J3hXEax1Ja0sqn7hoBM9BHvV6nMuBl1rh5sthGqE1l400tPh2r0W0"
PUBLISHABLE_KEY = "pk_test_51QV6ZtIqpMVb5nWenzdEG2jpLAF9KuRngPXgiX09m07cVDoGxLVmKnocHZuLSaW7gfOwiw1N3VJ77CtNzZUaqIko00n2xNTnsh"
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("signup"))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            session["email"] = user.email
            return redirect(url_for("timer"))
        flash("Invalid credentials!", "danger")
    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/timer")
@login_required
def timer():
    return render_template("timer.html", email=session.get("email", ""))

@app.route("/email", methods=["GET", "POST"])
@login_required
def email_page():
    if request.method == "POST":
        return redirect(url_for("payment"))
    return render_template("email.html", email=session.get("email", ""))


@app.route("/payment", methods=["POST", "GET"])
@login_required
def payment():
    if request.method == "GET":
        # Render the payment page (payment form)
        return render_template('payment.html')
    elif request.method == "POST":
        # Handle payment submission
        try:
            # Ensure request contains JSON data
            data = request.get_json()

            if not data:
                return jsonify({'success': False, 'error': 'Invalid JSON'}), 400

            token = data.get('token')

            if not token:
                return jsonify({'success': False, 'error': 'No token provided'}), 400

            # Process payment logic
            # current_email = request.session.get('email')
            # print(current_email)
            charge = stripe.Charge.create(
                # receipt_email=current_email,
                amount=5000,  # Example amount ($50)
                currency="usd",
                source=token,
                description="Test Product"
            )

            if charge.status == "succeeded":
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Payment failed'}), 400

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/success")
@login_required
def success():
    return render_template("success.html")

@app.route("/failure")
@login_required
def failure():
    return render_template("failure.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)