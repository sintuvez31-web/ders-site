from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'cok_gizli_anahtar_123'

# --- JSONBIN AYARLARI ---
BIN_ID = '6a452d96f5f4af5e294e2344'
MASTER_KEY = 'BURAYA_MASTER_KEY_YAZ' # Burayı kendi Master Key'inle doldur!
HEADERS = {'X-Master-Key': MASTER_KEY, 'Content-Type': 'application/json'}

def load_data():
    try:
        url = f'https://api.jsonbin.io/v3/b/{BIN_ID}/latest'
        response = requests.get(url, headers={'X-Master-Key': MASTER_KEY})
        # JSONBin'in veriyi koyduğu 'record' kutusunu açıyoruz:
        return response.json().get('record', {})
    except:
        return {}

def save_data(data):
    url = f'https://api.jsonbin.io/v3/b/{BIN_ID}'
    # JSONBin'e kayıt yaparken veriyi 'record' kutusuyla sarmalıyoruz:
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
        
        students = load_data()
        if username == "admin" and password == "ily123":
            session['username'] = "admin"
            return redirect(url_for('admin_dashboard'))
        
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
    return render_template('dashboard.html', user_data=students.get(session['username']))

@app.route('/admin')
def admin_dashboard():
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html', students=load_data())

@app.route('/admin/add', methods=['GET', 'POST'])
def add_student():
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username').lower()
        password = request.form.get('password')
        name = request.form.get('name')
        
        students = load_data()
        students[username] = {'password': password, 'name': name, 'phone': '0', 'balance': 0, 'total_attended_courses': 0}
        save_data(students)
        return redirect(url_for('admin_dashboard'))
        
    return render_template('add_student.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
