from flask import Flask, render_template, request
from flask_mail import Mail, Message
from random import randint
import os

app = Flask(__name__, template_folder="templates")
mail = Mail(app)

# Configuring mail server using environment variables
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

otp = randint(100000, 999999)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/verify', methods=["POST"])
def verify():
    email = request.form['email']
    msg = Message(subject='OTP', sender=os.environ.get('MAIL_USERNAME'), recipients=[email])
    msg.body = str(otp)
    mail.send(msg)
    return render_template('verify.html')

@app.route('/validate', methods=['POST'])
def validate():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        return "<h3>Email verification successful</h3>"
    return "<h3>Please Try Again</h3>"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
