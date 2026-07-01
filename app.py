from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'cok_gizli_anahtar_123'

# Buraya kendi bilgilerini gir
BIN_ID = '6a452d96f5f4af5e294e2344'
MASTER_KEY = 'BURAYA_KENDI_MASTER_KEYINI_YAZ' 

def load_data():
    try:
        response = requests.get(f'https://api.jsonbin.io/v3/b/{BIN_ID}/latest', headers={'X-Master-Key': MASTER_KEY})
        return response.json().get('record', {})
    except: return {}

@app.route('/login', methods=['GET', 'POST'])
def login():
    hata = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        if username == "admin" and password == "ily123":
            session['username'] = "admin"
            return redirect(url_for('admin_dashboard'))
        
        students = load_data()
        if username in students and str(students[username].get('password')) == str(password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        
        hata = "Kullanıcı adı veya şifre hatalı!"
        
    return render_template('login.html', hata=hata)

@app.route('/admin')
def admin_dashboard():
    if session.get('username') != 'admin': return redirect(url_for('login'))
    return render_template('admin.html', students=load_data())

@app.route('/dashboard')
def dashboard():
    if 'username' not in session or session['username'] == 'admin': return redirect(url_for('login'))
    return render_template('dashboard.html', user_data=load_data().get(session['username']))

if __name__ == '__main__':
    app.run(debug=True)
