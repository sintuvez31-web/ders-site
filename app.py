from flask import Flask, render_template, request, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = 'cok_gizli_anahtar_123'

# JSONBin Ayarları
BIN_ID = 'BURAYA_BIN_ID_YAZ'
MASTER_KEY = 'BURAYA_MASTER_KEY_YAZ'
HEADERS = {'X-Master-Key': MASTER_KEY, 'Content-Type': 'application/json'}

def load_data():
    try:
        url = f'https://api.jsonbin.io/v3/b/{BIN_ID}/latest'
        response = requests.get(url, headers={'X-Master-Key': MASTER_KEY})
        return response.json()['record']
    except:
        return {}

def save_data(data):
    url = f'https://api.jsonbin.io/v3/b/{BIN_ID}'
    requests.put(url, json=data, headers=HEADERS)

# --- ROTALAR ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        if username == "admin" and password == "ily123":
            session['username'] = "admin"
            return redirect(url_for('admin_dashboard'))
        
        students = load_data()
        if username in students and students[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
            
        return "Hatalı Giriş!", 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session or session['username'] == 'admin':
        return redirect(url_for('login'))
    
    students = load_data()
    user_data = students.get(session['username'])
    return render_template('dashboard.html', user_data=user_data)

@app.route('/admin')
def admin_dashboard():
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html', students=load_data())

# EĞER ADMIN PANELİNDE GÜNCELLEME YAPIYORSAN, 
# ORADA save_data(yeni_veriler) KOMUTUNU KULLANMAYI UNUTMA!

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
