from flask import Flask, render_template, request, redirect, url_for, session
import requests
import json

app = Flask(__name__)
app.secret_key = 'cok_gizli_anahtar_123'

# --- AYARLAR ---
BIN_ID = 'BURAYA_BIN_ID_YAZ'
MASTER_KEY = 'BURAYA_MASTER_KEY_YAZ'
HEADERS = {
    'X-Master-Key': MASTER_KEY,
    'Content-Type': 'application/json'
}

def load_data():
    try:
        url = f'https://api.jsonbin.io/v3/b/{BIN_ID}/latest'
        response = requests.get(url, headers={'X-Master-Key': MASTER_KEY})
        # JSONBin veriyi 'record' anahtarı içinde tutar
        return response.json().get('record', {})
    except Exception as e:
        print(f"Okuma hatası: {e}")
        return {}

def save_data(data):
    url = f'https://api.jsonbin.io/v3/b/{BIN_ID}'
    # JSONBin'e gönderirken veriyi 'record' olarak sarmalamalıyız
    payload = data 
    response = requests.put(url, json=payload, headers=HEADERS)
    if response.status_code != 200:
        print(f"Kayıt hatası: {response.text}")

# --- ROTALAR ---

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

@app.route('/admin')
def admin_dashboard():
    if session.get('username') != 'admin': return redirect(url_for('login'))
    return render_template('admin.html', students=load_data())

@app.route('/admin/add', methods=['GET', 'POST'])
def add_student():
    if session.get('username') != 'admin': return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form.get('username').lower()
        password = request.form.get('password')
        name = request.form.get('name')
        
        students = load_data()
        students[username] = {'password': password, 'name': name}
        save_data(students)
        return redirect(url_for('admin_dashboard'))
    return render_template('add_student.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
