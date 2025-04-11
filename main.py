from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import pandas as pd
from flask_login import UserMixin
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer as Serializer
import datetime
from create_app import create_app
app, mail, db = create_app()

from main import db
from flask import current_app
from create_app import create_app
from flask_migrate import Migrate
import numpy as np
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Migrate setup
migrate = Migrate(app, db)  # Initialize Migrate here

# Login manager setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Email configurations (using your own email to send, dynamic user email as recipient)
app.config['MAIL_SERVER'] = 'localhost'  # Use the default SMTP server
app.config['MAIL_PORT'] = 25  # Default SMTP port
app.config['MAIL_USE_TLS'] = False  # No TLS
app.config['MAIL_USE_SSL'] = False  # No SSL
app.config['MAIL_USERNAME'] = None  # No username
app.config['MAIL_PASSWORD'] = None  # No password
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@example.com'  # Default sender address

mail = Mail(app)



# User model with hashed password
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)  # Compare with stored hash

    # Flask-Login requires these methods
    def is_active(self):
        return True  # You can modify this if you want to handle active/inactive users

    def get_id(self):
        return str(self.id)  # Return the user ID as a string

    def is_authenticated(self):
        return True  # This means the user is always considered authenticated

    def is_anonymous(self):
        return False  # This should be False for regular users

    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})  # No need to decode in Python 3

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)



# Load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Load ML model & encoders
model = joblib.load("crime_prediction_model.pkl")
location_encoder = joblib.load("location_encoder.pkl")
crime_encoder = joblib.load("crime_encoder.pkl")
scaler = joblib.load("scaler.pkl")
df = pd.read_csv("Datasets/Kiambu Dataset.csv")
df.columns = df.columns.str.strip()

# Mappings
city_dict = {
    "1": "Jomoko", "2": "Witeithie", "3": "Thika", "4": "Ruiru", "5": "Juja",
    "6": "Kimbo", "7": "Kiambu Town", "8": "Banana", "9": "Ruaka", "10": "Limuru",
    "11": "Ngoingwa", "12": "Githurai", "13": "Gatundu", "14": "Kikuyu",
    "15": "Githunguri", "16": "Ndumberi", "17": "Kiambaa", "18": "Kabete"
}

crime_dict = {
    "6": "All", "5": "Murder", "4": "Kidnapping", "3": "Cyber_Crimes",
    "2": "Sexual_Crimes", "1": "Theft", "0": "Assault"
}

# Routes
@app.route('/')
def home():
    return render_template('welcome.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))

        if existing_email:
            flash('Email already exists.', 'error')
            return redirect(url_for('register'))

        # Create new user with hashed password
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')

        # Pass the username to the redirect page
        return render_template('redirect.html', username=username)  # Pass username to the redirect template

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))  # Redirect to index page after successful login
        else:
            error = "Invalid username or password. Please try again or register for an account."
            return render_template("login.html", error=error)

    return render_template('login.html')




@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for('home'))


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        city_id = request.form.get('city')
        crime_id = request.form.get('crime')
        city = city_dict.get(city_id)
        crime = crime_dict.get(crime_id)

        crime_columns = ['Murder', 'Kidnapping', 'Sexual_Crimes', 'Assault', 'Theft', 'Cyber_Crimes']
        if crime == "All":
            total = df[df['Location'] == city][crime_columns].sum().sum()
        else:
            total = df[df['Location'] == city][crime].sum()

        loc_encoded = location_encoder.transform([city])[0]
        crime_encoded = crime_encoder.transform([crime])[0]

        input_data = scaler.transform([[loc_encoded, crime_encoded, total]])
        prediction = model.predict(input_data)[0]

        return render_template('result.html', city=city, crime=crime, prediction=prediction)

    return render_template('predict.html', cities=city_dict, crimes=crime_dict)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user_email = request.form['email']  # Get the user's email from the form
        msg = Message('Password Reset Request',
                      sender='your_email@gmail.com',  # This will be your email
                      recipients=[user_email])  # User's email is the recipient
        msg.body = 'Here is your password reset link: <link_to_reset_password>'
        try:
            mail.send(msg)
            return 'Email sent!'
        except Exception as e:
            return f'Error sending email: {str(e)}'
    return render_template('forgot_password.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first()

    if request.method == 'POST':
        new_password = request.form['new_password']

        # Password length check
        if len(new_password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for('reset_password', email=email))

        hashed_password = generate_password_hash(new_password)
        user.password = hashed_password
        db.session.commit()
        flash("Password reset successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html', email=email)

@app.route('/send_email')
def send_email():
    msg = Message('Test Subject', recipients=['recipient@example.com'])
    msg.body = 'This is a test email.'
    try:
        mail.send(msg)
        return 'Email sent successfully!'
    except Exception as e:
        return f'Error sending email: {e}'


# Create DB and insert default user if needed
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Optional: insert default user 'moses' with email 'njugunahmoses448@gmail.com' and password 'moses'
        if not User.query.filter_by(username='moses').first():
            hashed_password = generate_password_hash('moses')  # Hash the password
            default_user = User(username='moses', email='njugunahmoses448@gmail.com', password=hashed_password)
            db.session.add(default_user)
            db.session.commit()

    app.run(debug=True)

