# create_app.py
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions outside of create_app to use them globally
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['MAIL_SERVER'] = 'smtp.example.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Gmail address
    app.config['MAIL_PASSWORD'] = 'your_app_password'  # Generated app password, not the regular Gmail password


    # Initialize extensions
    mail = Mail(app)
    db.init_app(app)  # Initialize db with the app
    
    return app, mail, db
