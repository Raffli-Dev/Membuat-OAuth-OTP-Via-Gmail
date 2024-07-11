from flask import Flask, redirect, url_for, render_template, request, jsonify, session
from flask_mail import Mail, Message
from random import randint
import os
from os.path import join, dirname
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')  # Ganti 'default_secret_key' dengan secret key yang aman

# Konfigurasi email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

mail = Mail(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/send_otp', methods=['GET', 'POST'])
def send_otp():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            session['email'] = email
            otp = randint(100000, 999999)
            msg = Message('Kode Verifikasi Gmail', sender=os.environ.get('MAIL_USERNAME'), recipients=[email])
            msg.body = f'Ini adalah kode OTP anda, {otp}. Jangan berikan kepada siapapun.'
            try:
                mail.send(msg)
                session['otp'] = otp
                return jsonify({'msg': 'Tunggu konfirmasi email anda.'})
            except Exception as e:
                return jsonify({'msg': f'Gagal mengirim email: {str(e)}'}), 500
        return jsonify({'msg': 'Email tidak boleh kosong.'}), 400  # Respon jika email kosong
    return render_template('otp.html')

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    otp_entered = request.form.get('otp')
    if otp_entered:
        otp_sent = session.get('otp')
        if otp_sent and otp_entered == str(otp_sent):
            session.pop('otp')
            return redirect(url_for('berhasil'))
        else:
            return jsonify({'error': 'Kode OTP yang anda masukkan salah.'}), 400
    else:
        return jsonify({'error': 'Kode OTP tidak boleh kosong.'}), 400

@app.route("/berhasil")
def berhasil():
    return render_template('sukses.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
