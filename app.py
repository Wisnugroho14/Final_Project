from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Koneksi ke MongoDB
client = MongoClient("mongodb+srv://test:sparta@cluster0.kbfqt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")


# Halaman Utama: 
@app.route('/')
def index():
    return render_template('index.html')

# Halaman About:
@app.route('/about')
def about():
    return render_template('about.html')

# Halaman Form:
@app.route('/form')
def form():
    return render_template('form.html')

# Halaman Contact:    
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Halaman Login: 
@app.route('/login')
def login():
    return render_template('login.html')

# Halaman Register: 
@app.route('/register')
def register():
    return render_template('register.html')

# Halaman Admin: 
@app.route('/admin')
def admin():
    return render_template('admin.html')

# Halaman admin user:
@app.route('/user')
def user():
    return render_template('user.html')

# Halaman admin program: 
@app.route('/program-admin')
def programAdmin():
    return render_template('program-admin.html')
  
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
            "title": "English for Adult",
            "description": "English for Adults adalah program pelatihan Bahasa Inggris yang diperuntukkan bagi pelajar SMA/SMK sederajat dan dewasa seperti mahasiswa, karyawan, profesional, pelaku bisnis, ibu rumah tangga, dan lainnya.",
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
            "title": "English for Adult",
            "description": "English for Adults adalah program pelatihan Bahasa Inggris yang diperuntukkan bagi pelajar SMA/SMK sederajat dan dewasa seperti mahasiswa, karyawan, profesional, pelaku bisnis, ibu rumah tangga, dan lainnya.",
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

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)