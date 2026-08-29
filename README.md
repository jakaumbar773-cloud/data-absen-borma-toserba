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
- Dukungan koneksi ke database remote melalui environment variable `DATABASE_URL`.

Menghubungkan ke database server lain (contoh PostgreSQL)

1) Install dependensi (sudah di requirements.txt):
   pip install -r requirements.txt

2) Set environment variable `DATABASE_URL` di server aplikasi Anda. Format (Postgres):
   export DATABASE_URL="postgresql+psycopg2://DB_USER:DB_PASSWORD@DB_HOST:5432/DB_NAME"

   Contoh (Linux/macOS):
   export DATABASE_URL="postgresql+psycopg2://bob:secret@203.0.113.5:5432/absendb"

   Atau (Windows PowerShell):
   $env:DATABASE_URL = "postgresql+psycopg2://bob:secret@203.0.113.5:5432/absendb"

3) Pastikan server database mengizinkan koneksi remote:
   - PostgreSQL: edit postgresql.conf -> set listen_addresses = '*'
   - Edit pg_hba.conf untuk mengizinkan host Anda (contoh: host    all    all    203.0.113.0/24    md5)
   - Buka port 5432 di firewall pada server DB.

4) Skema tabel yang diharapkan (nama table: attendance)

```sql
CREATE TABLE attendance (
  id serial primary key,
  name varchar(255) NOT NULL,
  counter integer,
  date date,
  status varchar(100)
);

-- contoh insert
INSERT INTO attendance (name, counter, date, status) VALUES
('Andi Saputra', 1, '2026-08-01', 'Masuk'),
('Budi Santoso', 2, '2026-08-01', 'Masuk');
```

5) Jalankan aplikasi (set host/port agar dapat diakses jika perlu):
   FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT=5000 python app.py

6) Jika server DB tidak menerima koneksi publik, Anda bisa membuat SSH tunnel dari host aplikasi ke server DB:
   ssh -L 5433:localhost:5432 user@db-server.example.com
   -- lalu atur DATABASE_URL untuk mengarah ke localhost:5433

Catatan keamanan:
- Jangan simpan kredensial DB langsung dalam kode. Gunakan environment variables atau secret manager.
- Pastikan password disimpan dengan aman di server dan akses dibatasi.
- Untuk produksi gunakan koneksi TLS antara aplikasi dan DB bila tersedia.

Endpoint tambahan:
- /reload-data  : memaksa aplikasi memuat ulang data dari DB (atau CSV jika DB tidak diatur). Berguna saat data di server DB telah diperbarui.

Jika Anda mau, saya bisa:
- Menambahkan dukungan untuk MySQL (pymysql) juga.
- Menyimpan users di database dan meng-hash password.
- Menambahkan halaman admin untuk sinkronisasi data.

