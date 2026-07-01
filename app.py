from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'gizli_anahtar_123'  # Burayı dilediğin gibi bırakabilirsin

# JSONBin Ayarları (Kendi anahtarlarını tırnakların içine yaz kanka)
BIN_ID = 'BURAYA_KENDI_BIN_ID_NI_YAZ'
MASTER_KEY = 'BURAYA_KENDI_MASTER_KEYINI_YAZ'

def load_data():
    """JSONBin'den öğrenci verilerini çeker."""
    try:
        url = f'https://api.jsonbin.io/v3/b/{BIN_ID}/latest'
        headers = {'X-Master-Key': MASTER_KEY}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('record', {})
        return {}
    except Exception as e:
        print(f"Veri yüklenirken hata oluştu: {e}")
        return {}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    hata = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 1. Admin Giriş Kontrolü
        if username == 'admin' and password == '1234':
            session['username'] = 'admin'
            return redirect(url_for('admin'))
        
        # 2. Öğrenci Giriş Kontrolü
        students = load_data()
        if username in students and students[username].get('password') == password:
            session['username'] = username
            return f"Hoş geldin {students[username].get('name')}! Girişin başarılı."
        
        hata = "Geçersiz kullanıcı adı veya şifre!"
        
    return render_template('login.html', hata=hata)

@app.route('/admin')
def admin():
    # Admin paneline izinsiz girişleri engelleme
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    
    students = load_data()
    return render_template('admin.html', students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    # Güvenlik kontrolü
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    
    # Formdan gelen yeni öğrenci bilgilerini alıyoruz
    new_user = request.form.get('username')
    new_name = request.form.get('name')
    new_pass = request.form.get('password')
    
    # Mevcut veritabanını çekiyoruz
    data = load_data()
    
    # Yeni öğrenciyi listeye ekliyoruz
    data[new_user] = {"name": new_name, "password": new_pass}
    
    # Güncellenmiş listeyi JSONBin veritabanına kaydediyoruz
    try:
        url = f'https://api.jsonbin.io/v3/b/{BIN_ID}'
        headers = {
            'X-Master-Key': MASTER_KEY, 
            'Content-Type': 'application/json'
        }
        requests.put(url, headers=headers, json=data)
    except Exception as e:
        print(f"Veritabanı güncellenirken hata oluştu: {e}")
        
    # Ekleme bitince admin panelini yenile
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
