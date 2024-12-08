from flask import Flask, render_template, request, redirect, url_for, flash,jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from werkzeug.utils import secure_filename
import bcrypt
import os
from werkzeug.utils import secure_filename

# Inisialisasi Flask
app = Flask(__name__)

# Konfigurasi folder pengajar
UPLOAD_FOLDER = 'static/pengajar'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'pengajar')

# Pastikan folder upload ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Koneksi ke MongoDB
client = MongoClient("mongodb+srv://test:sparta@cluster0.kbfqt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['bimble_bbc']  # Replace with your MongoDB database name
users_collection = db['users']
programs_collection = db['programs']
pendaftaran_collection = db['pendaftaran']
pengajar_collection = db['pengajar']
pesan_collection = db['pesan']


# Set a secret key for sessions
app.secret_key = 'bbc_pati'

# Direktori untuk menyimpan file upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Kode verifikasi admin
ADMIN_VERIFICATION_CODE = '778899'  # Ganti dengan kode rahasia yang aman

# Middleware untuk proteksi login
def login_required(f):
    def wrap(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

def admin_required(f):
    def wrap(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Halaman ini hanya untuk admin.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

# Halaman utama (user dashboard)
@app.route('/')
def index():
    programs = list(programs_collection.find({}))  # Mengambil semua data program
    return render_template('index.html', programs=programs)


# Halaman About:
@app.route('/about')
def about():
    pengajar_collection = db['pengajar'].find()  
    pengajar = list(pengajar_collection) 
    
    return render_template('about.html', pengajar=pengajar)

# Halaman Form:
@app.route('/form')
@login_required
def form():
    flash("Silakan isi formulir untuk mendaftar.", "info")
    return render_template("form.html")

@app.route('/submit-form', methods=['POST'])
def submit_form():
    # Ambil data dari form
    complitename = request.form.get('complitename')
    address = request.form.get('address')
    gender = request.form.get('gender')
    parents = request.form.get('parents')
    program = request.form.get('program')
    phone = request.form.get('phone')
    level = request.form.get('level')
    payment_proof = request.files.get('paymentProof')

    # Simpan bukti pembayaran ke server
    if payment_proof:
        filename = secure_filename(payment_proof.filename)
        payment_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        payment_proof.save(payment_path)
    else:
        filename = None

    # Simpan hanya nama file
    data = {
        "complitename": complitename,
        "address": address,
        "gender": gender,
        "parents": parents,
        "program": program,
        "phone": phone,
        "level": level,
        "payment_proof": filename  # Simpan nama file saja
    }
    pendaftaran_collection.insert_one(data)

    # Redirect ke halaman indeks
    return redirect(url_for('index'))

# Halaman Contact:    
@app.route('/contact')
def contact():
    return render_template('contact.html')

#Input pesan kontak
@app.route('/kirim_pesan', methods=['POST'])
def kirim_pesan():
    data = request.json  # Ambil data JSON dari permintaan
    print(data)  # Debug: Cetak data yang diterima

    nama = data.get('nama')
    no_Hp = data.get('no_Hp')
    pesan = data.get('pesan')

    if not nama or not no_Hp or not pesan:
        return jsonify({'error': 'Semua kolom harus diisi !'}), 400

    # Simpan data ke koleksi "pesan"
    pesan_collection.insert_one({'nama': nama, 'no_Hp': no_Hp, 'pesan': pesan})
    return jsonify({'success': 'Pesan berhasil terkirim'}), 200


# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Cari pengguna berdasarkan username
        user = users_collection.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']

            flash('Login berhasil.', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Username atau password salah.', 'danger')

    return render_template('login.html')

# Halaman register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Periksa apakah username sudah ada
        if users_collection.find_one({'username': username}):
            flash('Username sudah digunakan. Silakan pilih yang lain.', 'danger')
            return render_template('register.html')

        # Jika role adalah admin, periksa kode verifikasi
        if role == 'admin':
            verification_code = request.form['verification_code']
            if verification_code != ADMIN_VERIFICATION_CODE:
                flash('Kode verifikasi salah. Anda tidak dapat mendaftar sebagai admin.', 'danger')
                return render_template('register.html')

        # Simpan data pengguna ke database
        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': role
        })
        flash('Registrasi berhasil. Silakan login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Halaman admin dashboard
@app.route('/admin')
@login_required
@admin_required
def admin():
    # Hitung jumlah pengguna dan program
    total_users = users_collection.count_documents({})
    total_programs = programs_collection.count_documents({})
    total_pendaftar = pendaftaran_collection.count_documents({})

    # Kirim data ke template
    return render_template(
        'admin.html', 
        total_users=total_users, 
        total_programs=total_programs,
        total_pendaftar=total_pendaftar,
    )

# Halaman admin user:
@app.route('/user')
def user():
    users = db.users.find()
    return render_template('user.html', users=users)

# Halaman admin program: 
@app.route('/program-admin')
@login_required
@admin_required
def program_admin():
    programs = db.programs.find()
    return render_template('program-admin.html', programs=programs)

@app.route('/program-admin/add', methods=['POST'])
@login_required
@admin_required
def add_program():
    if request.method == 'POST':
        # Ambil data dari form
        kategori = request.form['kategori']
        level = request.form['level']
        harga = request.form['harga']
        jadwal = request.form['jadwal']

        # Simpan data ke MongoDB
        programs_collection.insert_one({
            'kategori': kategori,
            'level': level,
            'harga': harga,
            'jadwal': jadwal
        })

        # Berikan pesan sukses dan redirect ke halaman program-admin
        flash('Program berhasil ditambahkan.', 'success')
        return redirect(url_for('program_admin'))

@app.route('/program-admin/edit/<program_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_program(program_id):
    program = db.programs.find_one({'_id': ObjectId(program_id)})

    if not program:
        flash('Program tidak ditemukan.', 'danger')
        return redirect(url_for('program_admin'))

    if request.method == 'POST':
        kategori = request.form['kategori']
        level = request.form['level']
        harga = request.form['harga']
        jadwal = request.form['jadwal']

        db.programs.update_one(
            {'_id': ObjectId(program_id)},
            {'$set': {
                'kategori': kategori,
                'level': level,
                'harga': harga,
                'jadwal': jadwal
            }}
        )

        flash('Program berhasil diupdate.', 'success')
        return redirect(url_for('program_admin'))

    return render_template('edit_program.html', program=program)

@app.route('/program-admin/view/<program_id>', methods=['GET'])
@login_required
@admin_required
def view_program(program_id):
    program = db.programs.find_one({'_id': ObjectId(program_id)})

    if not program:
        flash('Program tidak ditemukan.', 'danger')
        return redirect(url_for('program_admin'))

    return render_template('view_program.html', program=program)

@app.route('/program-admin/delete/<program_id>', methods=['POST'])
@login_required
@admin_required
def delete_program(program_id):
    db.programs.delete_one({'_id': ObjectId(program_id)})
    flash('Program berhasil dihapus.', 'success')
    return redirect(url_for('program_admin'))

  
# Halaman Program: 
@app.route('/program')
def program():
    return render_template('program.html')

# Halaman Detail Program: 
@app.route('/program/<program_name>')
def program_detail(program_name):
    programs = {
        "children": {
            "title": "English for Children",
            "description": "English for Children adalah program pelatihan Bahasa Inggris yang diperuntukkan bagi pelajar SD yang fokus pada penguasaan kosa kata, frasa serta ungkapan sederhana dalam komunikasi sehari-hari.",
            "goals": [
                "Menguasai kosa kata dan frasa serta ungkapan-ungkapan sederhana dalam komunikasi sehari-hari.",
                "Membangun kebiasaan berbahasa Inggris.",
                "Mempersiapkan kemampuan dasar bahasa Inggris menuju jenjang SMP.",
                "Menanamkan karakter unggul seperti disiplin, tanggungjawab, kepedulian, percaya diri, ketakwaan, dll",
            ],
            "levels": [
                "Kindergarden 1","Kindergarden 2","Prepatory Class 1A","Prepatory Class 1B","Prepatory Class 2A","Prepatory Class 2B","Prepatory Class 3A","Prepatory Class 3B","Prepatory Class 4A","Prepatory Class 4B","Prepatory Class 5A","Prepatory Class 5B","Prepatory Class 6A","Prepatory Class 6B","Dynamic Conversation for Children"
            ]
        },

        "teens": {
            "title": "English for Teens",
            "description": "English for Teens adalah program pelatihan Bahasa Inggris yang diperuntukkan bagi pelajar SMP. Program ini merupakan perpaduan kurikulum bertaraf internasional serta mengacu pada materi belajar di sekolah.",
            "goals": [
                "Meningkatkan kompetensi Speaking.",
                "Mengembangkan kepercayaan diri dalam berbahasa Inggris.",
                "Meningkatkan pengetahuan dan penguasaan grammar.",
                "Meningkatkan prestasi bahasa Inggris"
            ],
            "levels": [
                "Pre Beginner 1","Pre Beginner 2","Dynamic Conversation for Teens 1","Beginner 1","Beginner 2","Dynamic Conversation for Teens 2","Pre Elementary 1","Pre Elementary 2","Dynamic Conversation for Teens 3"
            ]
        },

        "adult": {
            "title": "English for Adult",
            "description": "English for Adults adalah program pelatihan Bahasa Inggris yang diperuntukkan bagi pelajar SMA/SMK sederajat dan dewasa seperti mahasiswa, karyawan, profesional, pelaku bisnis, ibu rumah tangga, dan lainnya.",
            "goals": [
                "Meningkatkan keterampilan Listening, Speaking, Reading dan Writing.",
                "Meningkatkan kepercayaan diri dalam menggunakan bahasa Inggris secara aktif dalam berbagai situasi..",
                "Mengingkatkan penguasaan grammar untuk akurasi bahasa Inggris yang lebih baik."
            ],
            "levels": [
                "Basic 1","Basic 2","Dynamic Conversation for Adult 1","Elementary 1","Elementary 2","Dynamic Conversation for Adult 2","Intermediate 1","Intermediate 2","Dynamic Conversation for Adult 3",
                "Post Intermediate 1","Post Intermediate 2","Dynamic Conversation for Adult 4","Advance 1","Advance 2"
            ]
        },

        "private": {
            "title": "English Private Class",
            "description": "English Private Class adalah program pelatihan Bahasa Inggris yang diperuntukkan bagi individu yang ingin mendapatkan pengalaman belajar yang lebih personal dan terfokus.",
            "goals": [
                "Meningkatkan Kepercayaan Diri dalam Penggunaan Bahasa Inggris.",
                "Meningkatkan kemampuan berbahasa Inggris untuk kebutuhan spesifik.",
                "Meningkatkan keterampilan Listening, Speaking, Reading dan Writing."
            ],
            "levels": [
                "Private di BBC",
                "Private di Luar",
            ]
        },

        "toefl": {
            "title": "TOEFL/TOEIC Preparation",
            "description": "TOEFL/TOEIC Preparation adalah program pelatihan Bahasa Inggris untuk mempersiapkan peserta didik menghadapi tes standar nasional dan internasional seperti TOEFL/TOEIC.",
            "goals": [
                "Meningkatkan Keterampilan Berbahasa Inggris untuk mempersiapkan ujian.",
                "Membantu peserta mencapai target skor TOEFL untuk keperluan akademik, beasiswa, atau pekerjaan.",
                "Membiasakan peserta dengan struktur dan jenis soal dalam setiap bagian tes: Reading, Listening, Speaking, dan Writing."
            ],
            "levels": [
                "Test TOEFL/TOEIC",
                "Preparation TOEFL",
                "Preparation IELTS",
            ]
        }
    }

    program = programs.get(program_name)
    if not program:
        return render_template('404.html'), 404

    return render_template('program_detail.html', program=program)

# Halaman logout
@app.route('/logout')
def logout():
    session.clear()  # Hapus semua data di session
    flash('Anda telah keluar.', 'success')
    return redirect(url_for('index'))

# Edit, view, delete admin menu users:
# View user details
@app.route('/user/<user_id>')
@login_required
@admin_required
def view_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        flash('Pengguna tidak ditemukan.', 'danger')
        return redirect(url_for('user'))
    return render_template('view_user.html', user=user)

# Edit user details
@app.route('/user/<user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        flash('Pengguna tidak ditemukan.', 'danger')
        return redirect(url_for('user'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        
        # Update user in the database
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"username": username, "email": email, "role": role}}
        )
        flash('Data pengguna berhasil diperbarui.', 'success')
        return redirect(url_for('user'))
    
    return render_template('edit_user.html', user=user)

# Delete user
@app.route('/user/<user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        flash('Pengguna tidak ditemukan.', 'danger')
    else:
        users_collection.delete_one({"_id": ObjectId(user_id)})
        flash('Pengguna berhasil dihapus.', 'success')
    return redirect(url_for('user'))


# Halaman admin pengajar:
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:  # Check if file part is in the request
        return 'No file part', 400  # Return an error response if no file part

    file = request.files['file']  # Get the file from the request

    if file.filename == '':  # Check if a file was selected
        return 'No selected file', 400  # Return an error if no file was selected

    if file:  # If file is valid, save it
        filename = secure_filename(file.filename)  # Secure the filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save file to the correct folder
        return 'File uploaded successfully', 200  # Return success message

@app.route('/pengajar')
@login_required
@admin_required
def pengajar():
    pengajar = list(pengajar_collection.find())
    return render_template('pengajar.html', pengajar=pengajar)

@app.route('/pengajar/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_pengajar():
    if request.method == 'POST':
        nama = request.form['nama']
        file = request.files['foto']

        if file:
            # Simpan file dengan nama aslinya
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Mengubah path menjadi menggunakan '/' alih-alih '\'
            foto_path = os.path.join('pengajar', filename).replace("\\", "/")

            pengajar_collection.insert_one({
                'nama': nama,
                'foto': foto_path
            })
            flash('Data pengajar berhasil ditambahkan.', 'success')
            return redirect(url_for('pengajar'))

@app.route('/pengajar/edit/<pengajar_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_pengajar(pengajar_id):
    pengajar = pengajar_collection.find_one({'_id': ObjectId(pengajar_id)})

    if not pengajar:
        flash('Pengajar tidak ditemukan.', 'danger')
        return redirect(url_for('pengajar'))

    if request.method == 'POST':
        nama = request.form['nama']
        file = request.files['foto']

        update_data = {
            'nama': nama,
        }

        if file:
            # Simpan file dengan nama aslinya
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Mengubah path menjadi menggunakan '/' alih-alih '\'
            update_data['foto'] = os.path.join('pengajar', filename).replace("\\", "/")

        pengajar_collection.update_one(
            {'_id': ObjectId(pengajar_id)},
            {'$set': update_data}
        )
        flash('Data pengajar berhasil diperbarui.', 'success')
        return redirect(url_for('pengajar'))

    return render_template('edit_pengajar.html', pengajar=pengajar)

@app.route('/pengajar/delete/<pengajar_id>', methods=['POST'])
@login_required
@admin_required
def delete_pengajar(pengajar_id):
    pengajar = pengajar_collection.find_one({'_id': ObjectId(pengajar_id)})

    if pengajar:
        pengajar_collection.delete_one({'_id': ObjectId(pengajar_id)})
        flash('Pengajar berhasil dihapus.', 'success')
    else:
        flash('Pengajar tidak ditemukan.', 'danger')

    return redirect(url_for('pengajar'))

@app.route('/pengajar/view/<pengajar_id>', methods=['GET'])
@login_required
@admin_required
def view_pengajar(pengajar_id):
    pengajar = pengajar_collection.find_one({'_id': ObjectId(pengajar_id)})

    if not pengajar:
        flash('Program tidak ditemukan.', 'danger')
        return redirect(url_for('pengajar'))

    return render_template('view_pengajar.html', pengajar=pengajar)

# Tampilan admin menu pendaftaran:
@app.route('/form-admin')
@login_required
@admin_required
def form_admin():
    pendaftaran = list(pendaftaran_collection.find())  # Ambil semua data dari koleksi pendaftaran
    return render_template('form-admin.html', pendaftaran=pendaftaran)

# View formulir admin
@app.route('/form-admin/view/<data_id>', methods=['GET'])
@login_required
@admin_required
def view_form(data_id):
    pendaftaran = pendaftaran_collection.find_one({'_id': ObjectId(data_id)})

    if not pendaftaran:
        flash('Formulir tidak ditemukan.', 'danger')
        return redirect(url_for('form_admin'))

    return render_template('view_form.html', pendaftaran=pendaftaran)

# Delete Formulir admin
@app.route('/form-admin/delete/<data_id>', methods=['POST'])
@login_required
@admin_required
def delete_form(data_id):
    db.pendaftaran.delete_one({'_id': ObjectId(data_id)})
    flash('Formulir berhasil dihapus.', 'success')
    return redirect(url_for('form_admin'))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)