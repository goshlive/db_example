# Studi kasus Python Restaurant

Salin folder `example-casestudy` utuh sejajar dengan `example-cars`, `example-orm1`, dan contoh lain pada workspace DB di VS Code. Tidak perlu menimpa berkas proyek lama.

Database dan empat tabel CUSTOMER, CUSTOMER_ORDER, MENU_ITEM, ORDER_ITEM harus sudah ada. Proyek ini tidak membuat atau mengubah struktur tabel. Sesuaikan DB_NAME dengan nama skema Restaurant Bapak dan perhatikan huruf besar nama tabel.

## Persiapan Windows PowerShell

```powershell
cd example-casestudy
py -3 -m venv .venv
$casePython = ".\.venv\Scripts\python.exe"
& $casePython -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` yang baru disalin. Isi akun MySQL dan nama skema yang sudah ada. Environment variable terminal mengalahkan `.env`; `.env` pada folder induk tidak dibaca. Jika memakai environment lama yang sesuai, lewati pembuatan `.venv` dan arahkan `$casePython` ke Python environment tersebut. Pilih interpreter yang sama di VS Code. Tidak diperlukan aktivasi PowerShell.

```powershell
& $casePython check_database.py
# Opsional HANYA jika keempat tabel yang sudah ada masih kosong:
& $casePython seed_sample.py
& $casePython console.py --mode prepared crud-demo
& $casePython console.py --mode orm orders --id C01
& $casePython console.py --mode prepared details --id O101
& $casePython web_app.py
```

Buka http://127.0.0.1:5000. Hentikan dengan Ctrl+C. Pada terminal baru, tetapkan kembali `$casePython`. Untuk macOS/Linux, buat environment dengan `python3 -m venv .venv` dan ganti `& $casePython` dengan `.venv/bin/python`.

## CRUD console satu per satu

```powershell
& $casePython console.py --mode prepared create --id CDEMO --name "Dewi"
& $casePython console.py --mode prepared get --id CDEMO
& $casePython console.py --mode prepared update --id CDEMO --name "Dewi Putri"
& $casePython console.py --mode prepared delete --id CDEMO
```

Ulangi dengan `--mode orm`. Untuk versi SQL yang sengaja tidak aman, ubah `ALLOW_UNSAFE_SQL=true` pada `.env`, mulai ulang aplikasi web, lalu pilih `--mode raw` atau mode raw pada halaman. Aplikasi ini untuk praktikum lokal; server Flask memakai localhost dengan debug nonaktif, tanpa login atau deployment produksi.

```powershell
& $casePython console.py --mode raw injection-demo
& $casePython console.py --mode prepared injection-demo
& $casePython console.py --mode orm injection-demo
& $casePython verify_live.py
```

Data acuan menghasilkan dua pesanan C01 (O101, O103), dua detail O101 (50000 dan 8000), dan total 58000. Tanpa data contoh, hasil join kosong adalah wajar. `seed_sample.py` menolak tabel yang sudah berisi data, tidak melakukan reset, dan tidak menghapus data. Jalankan hanya saat tidak ada pengguna lain menulis ke database praktikum.

## Isi dan penggunaan kembali kode

- `raw_sql.py`: SQL interpolasi yang sengaja rentan, khusus praktikum lokal.
- `prepared_sql.py`: SQL manual dengan `prepared=True` dan parameter `%s`.
- `models.py`, `orm_repository.py`: empat kelas ORM, objek asosiasi, dan kueri.
- `repositories.py`: memilih implementasi dengan antarmuka fungsi sama.
- `dto.py`: data lepas dari koneksi/session serta konversi tanggal/desimal.
- `db.py`, `config.py`: umur koneksi dan konfigurasi folder ini.
- `console.py`, `web_app.py`, `templates/index.html`: pemanggil console dan web.
- `check_database.py`, `seed_sample.py`, `verify_live.py`: pemeriksaan awal, data opsional, dan uji langsung.

Kedua aplikasi memakai list_customers, get_customer, create_customer, update_customer, delete_customer, search_customers, customer_orders, dan order_details. Route tidak menulis SQL; repository tidak mengimpor Flask atau mencetak hasil.

Setiap operasi tulis repository adalah satu transaksi. `crud-demo` menjalankan beberapa operasi yang masing-masing di-commit dan menghapus CTEST di akhir; jika CTEST sudah ada, demonstrasi ditolak. Untuk membuat pesanan beserta detail, jangan menggabungkan fungsi yang commit sendiri-sendiri: layanan beberapa tabel perlu berbagi satu koneksi/session dan transaksi. C01 tidak bisa dihapus karena memiliki pesanan. FK biasa tidak menjamin setiap pesanan memiliki minimal satu detail. Tidak ada cascade delete.

Rowcount UPDATE langsung dapat nol jika nilainya tidak berubah, sedangkan ORM mengembalikan satu untuk pelanggan yang ditemukan. Periksa data hasil, bukan menyamakan makna kedua hitungan tersebut.

Raw SQL tidak selalu tidak aman; masalahnya adalah interpolasi input tidak tepercaya. Binding ORM bukan jaminan server-side prepared statement. SQL tekstual dengan interpolasi tetap dapat membuat SQLAlchemy rentan. Placeholder mewakili nilai, bukan nama tabel/kolom dinamis.

## Demonstrasi web

Pilih prepared; buat CWEB, baca, ubah, baca lagi, lalu hapus. Ulangi pada ORM dan raw opsional. Coba join 1-N dengan C01 dan M-N dengan O101. Pada pencarian nama persis, bandingkan Made, `' OR '1'='1`, dan O'Connor pada semua mode. Payload raw menampilkan semua pelanggan; O'Connor raw menghasilkan kesalahan. Mode aman menganggapnya nilai literal. Contoh JSON: `/api/customers?mode=prepared` dan `/api/orders/O101/items?mode=orm`.

Form POST membawa token session; gunakan form yang ditampilkan. GET tidak membuat, mengubah, atau menghapus data. Demonstrasi SQL Injection cukup memakai SELECT, tanpa payload penghapusan.

## Pemecahan masalah

- Access denied: periksa akun, password, host, dan hak akses skema.
- Unknown database/table: sesuaikan DB_NAME dan empat nama tabel huruf besar.
- Modul tidak ditemukan: instal requirements dengan Python yang sama untuk menjalankan kode.
- Port terpakai: ubah FLASK_PORT=5001 dan mulai ulang.
- Raw nonaktif: aktifkan flag praktikum lokal dan mulai ulang; tidak ada perbaikan escaping manual.
- ID duplikat: pilih ID sementara lain; data lama tidak otomatis ditimpa.
- FK menolak: gunakan CWEB/CTEST untuk latihan penghapusan biasa; jangan hapus data terkait tanpa kebutuhan latihan.
- UPDATE: nilai yang tidak berubah dapat menghasilkan nol baris berubah di MySQL.

Rujukan teknis tersedia pada README_English.md dan kedua panduan DOCX. Semua komentar kode berbahasa Inggris.
