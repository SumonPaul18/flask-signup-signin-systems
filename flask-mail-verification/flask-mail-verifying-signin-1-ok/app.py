from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

db = SQLAlchemy(app)
mail = Mail(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        user = User(email=email)
        db.session.add(user)
        db.session.commit()
        
        token = s.dumps(email, salt='email-confirm')
        link = url_for('confirm_email', token=token, _external=True)
        
        msg = Message('Confirm your email', sender='noreply@demo.com', recipients=[email])
        msg.html = render_template('email_template.html', link=link)
        mail.send(msg)
        
        flash('A confirmation email has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    
    user = User.query.filter_by(email=email).first_or_404()
    user.confirmed = True
    db.session.commit()
    
    flash('Your account has been confirmed!', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user and user.confirmed:
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Please confirm your email first.', 'warning')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    users = User.query.all()
    return render_template('dashboard.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)