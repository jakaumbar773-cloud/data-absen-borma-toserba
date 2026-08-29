# Data Absen - Borma Toserba (Flask)

Contoh aplikasi Flask sederhana menampilkan data absen Head Office Borma Toserba.
Tampilan menggunakan palet kuning → orange, menampilkan logo, dan form filter:
- Pilih Nama (dropdown)
- Counter (angka)
- Tanggal Awal (date)
- Tanggal Akhir (date)
Tombol "Oke" untuk menampilkan hasil, dan "Print" untuk mencetak (window.print).

Tambahan:
- Menu login sederhana: username=admin, password=admin1

Cara menjalankan:
1. Buat virtualenv:
   python -m venv venv
   source venv/bin/activate  (Linux/macOS) atau venv\\Scripts\\activate (Windows)

2. Install dependensi:
   pip install -r requirements.txt

3. Jalankan aplikasi:
   python app.py

4. Buka di browser:
   http://127.0.0.1:5000

Login credentials (untuk development):
- username: admin
- password: admin1

Catatan:
- Ganti file data/attendance.csv dengan data nyata atau ubah app.py untuk membaca database (SQLite/MySQL).
- Logo saat ini berupa static/logo.svg; ganti dengan logo resmi Borma Toserba bila tersedia.
- Jangan gunakan `app.secret_key` yang ada sekarang di produksi; ganti dengan nilai acak yang aman.
