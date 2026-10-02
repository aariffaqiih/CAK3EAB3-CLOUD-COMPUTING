# ------------------------------------------------------------------------------
# 1. SINTAKS: import hashlib
# ------------------------------------------------------------------------------
# Syntax ini berfungsi untuk meng-import library bawaan Python bernama 'hashlib', library ini menyediakan interface ke berbagai fungsi hash kriptografi satu arah (one-way cryptographic hash functions), khususnya SHA-256 yang termasuk keluarga SHA-2 (Secure Hash Algorithm 2). Di materi distributed system seperti Naming & Security, fungsi hash kriptografi berfungsi sebagai fondasi untuk membuat 'Self-Certifying Names' dan 'Flat Naming Spaces' (ruang pengalamatan datar), jadi kita tidak perlu pendaftaran terpusat seperti DNS atau Certificate Authority.
# Penggunaan 'hashlib' di code ini bertujuan untuk memperlihatkan bahwa alamat di Reticulum Network Stack (RNS) bisa dihitung ulang secara matematis dan hasilnya pasti sama (deterministik). RNS menggunakan fungsi hash untuk mengompresi identitas kriptografi dan nama aplikasi (Attribute-Based Naming) menjadi alamat 16 byte (128 bit), ukuran sekecil ini sangat hemat untuk dikirim lewat media fisik berkapasitas rendah seperti radio LoRa atau koneksi kabel berkecepatan rendah.
import hashlib

# ------------------------------------------------------------------------------
# 2. SINTAKS: import sys
# ------------------------------------------------------------------------------
# Syntax ini berfungsi untuk meng-import modul 'sys', modul ini menyediakan akses ke variabel dan fungsi yang berhubungan langsung dengan interpreter Python dan lingkungan sistem operasi. Di distributed system, kontrol terhadap proses runtime (process management) penting agar program tetap stabil ketika terjadi kegagalan.
# Fungsi 'sys.exit()' dari modul ini digunakan untuk menghentikan proses secara rapi (graceful termination) saat terjadi kegagalan fatal, misalnya library jaringan belum terpasang atau konfigurasi gagal dimuat. Dengan begitu tidak ada proses gantung (zombie processes), dan sistem operasi atau container manager menerima exit status code yang jelas.
import sys

# ------------------------------------------------------------------------------
# 3. SINTAKS: try ... import RNS ... except ImportError ...
# ------------------------------------------------------------------------------
# Blok try-except ini berfungsi untuk mengecek apakah modul 'RNS' (Reticulum Network Stack) sudah terpasang di lingkungan runtime local sebelum program dilanjutkan. Di distributed system (seperti pada referensi 02.pptx dan 04.pptx), RNS berperan sebagai 'Layered Middleware Architecture', yaitu perangkat lunak lapisan tengah yang berada di antara aplikasi user dan interface jaringan fisik.
# Jika library RNS belum terpasang, maka 'sys.exit()' akan dipanggil untuk menghentikan program dan memberikan instruksi perbaikan ('pip install rns') ke pengguna. Ini menerapkan fail-fast principle, jadi sistem langsung memberi tahu kesalahannya dengan jelas, daripada membiarkan cascading failures terjadi di bagian eksekusi yang lebih dalam.
try:
    import RNS
except ImportError:
    sys.exit("Library 'rns' belum terpasang. Jalankan: pip install rns")

# ------------------------------------------------------------------------------
# 4. SINTAKS: APP_NAME = "aarif_rahmaan"
# ------------------------------------------------------------------------------
# Variabel 'APP_NAME' berfungsi untuk menentukan root namespace dari aplikasi. Di distributed system yang punya sistem pemberian nama (seperti LDAP, Named Data Networking / NDN, atau DNS), string teks seperti ini menjadi konteks paling atas yang menandai jenis aplikasi atau kelompok layanan.
# Reticulum tidak menggunakan nomor port angka tetap (seperti port 80 untuk HTTP atau 443 untuk HTTPS). Sebagai gantinya, Reticulum menggunakan 'Attribute-Based Naming' berbasis string teks yang bisa diatur bebas. String 'aarif_rahmaan' berfungsi sebagai komponen pertama untuk membentuk nama lengkap dari Destination Endpoint, yaitu titik tujuan yang akan diakses oleh node lain di jaringan.
APP_NAME = "aarif_rahmaan"

# ------------------------------------------------------------------------------
# 5. SINTAKS: ASPECTS = ("jalaluddin_faqiih",)
# ------------------------------------------------------------------------------
# Variabel 'ASPECTS' berupa tuple Python yang berisi satu atau lebih string aspek tambahan (sub-namespace). Aspek berfungsi sebagai kualifikasi tambahan untuk mempersempit fungsi atau jalur komunikasi di dalam aplikasi utama, contohnya fungsi pesan, transfer file, atau kontrol.
# Dengan menggabungkan 'APP_NAME' dan 'ASPECTS', developer bisa membuat banyak endpoint yang berdiri sendiri di bawah satu Identitas Kriptografi yang sama tanpa terjadi data collision. Tuple dipilih karena tuple itu immutable (tidak bisa diubah setelah didefinisikan), jadi atribut nya tetap konsisten selama aplikasi berjalan.
ASPECTS = ("jalaluddin_faqiih",)

# ------------------------------------------------------------------------------
# 6. SINTAKS: FULL_NAME = ".".join((APP_NAME, *ASPECTS))
# ------------------------------------------------------------------------------
# [Konteks Teori Resolusi Nama Tekstual ke Alamat Kriptografi]
# Perintah ini berfungsi untuk menggabungkan 'APP_NAME' dan semua elemen di 'ASPECTS' menggunakan tanda titik ('.') sebagai penyambung, maka hasilnya adalah string nama lengkap '"aarif_rahmaan.jalaluddin_faqiih"'.
#
# Secara teori, string ini adalah 'Human-Readable Structured Name' (nama terstruktur yang mudah dibaca manusia). Tapi karena Reticulum berjalan di jaringan tanpa server terpusat (Uncentralized Network), nama teks ini tidak dikirim mentah ke dalam paket data, agar bandwidth tetap hemat. Jadi nama terstruktur ini akan diubah otomatis menjadi hash biner singkat lewat perhitungan matematis.
FULL_NAME = ".".join((APP_NAME, *ASPECTS))

# ------------------------------------------------------------------------------
# 7. SINTAKS: NAME_HASH_BYTES = RNS.Identity.NAME_HASH_LENGTH // 8
# ------------------------------------------------------------------------------
# [Konteks Kompresi Alamat dan Truncation Mathematics]
# Konstanta 'NAME_HASH_BYTES' berfungsi untuk menghitung panjang byte dari hash nama aplikasi, caranya adalah membagi panjang bit 'RNS.Identity.NAME_HASH_LENGTH' (128 bit) dengan 8, maka hasilnya tepat 16 byte (128 bit).
#
# Memotong (truncating) hasil SHA-256 dari 32 byte menjadi 16 byte adalah keputusan desain yang sangat penting di Reticulum Network Stack:
# 1. Ukuran 128 bit (16 byte) memberikan ruang alamat sebesar 2^128 (sekitar 3,4 x 10^38 kombinasi), jadi secara matematis sangat aman dari serangan tabrakan (Birthday Attack) walaupun digunakan di skala global.
# 2. Ukuran yang lebih kecil ini menghemat overhead header paket cukup banyak, sehingga Reticulum tetap ringan walaupun berjalan di media jaringan ber-bandwidth sangat rendah (seperti LoRa 150-250 bps atau Packet Radio), karena di media itu setiap byte data sangat berharga.
NAME_HASH_BYTES = RNS.Identity.NAME_HASH_LENGTH // 8

# ------------------------------------------------------------------------------
# 8. SINTAKS: DEST_HASH_BYTES = RNS.Reticulum.TRUNCATED_HASHLENGTH // 8
# ------------------------------------------------------------------------------
# [Konteks Standarisasi Header Paket dan Blind Routing]
# Konstanta 'DEST_HASH_BYTES' berfungsi untuk menghitung panjang byte dari 'Destination Hash' final di jaringan Reticulum, yaitu 'RNS.Reticulum.TRUNCATED_HASHLENGTH' (128 bit) dibagi 8 = 16 byte.
#
# Nilai 16 byte ini adalah ukuran tetap untuk Destination Address Field di header paket Reticulum. Pada arsitektur 'Blind Routing', node transport di sepanjang jalur tidak perlu tahu nama teks asli atau identitas lengkap penerima, mereka cukup mencocokkan nilai biner 16 byte ini dengan tabel jalur local (Path Table) agar paket data diteruskan ke tujuan yang benar.
DEST_HASH_BYTES = RNS.Reticulum.TRUNCATED_HASHLENGTH // 8

# ------------------------------------------------------------------------------
# 9. SINTAKS: def hitung_hash_manual(identity):
# ------------------------------------------------------------------------------
# [Konteks Pengecekan Algoritma dan Transparansi Kriptografi]
# Fungsi 'hitung_hash_manual(identity)' dibuat untuk meng-implementasi ulang (re-implement) rumus perhitungan Destination Hash dari Reticulum secara manual, menggunakan library bawaan Python 'hashlib'.
#
# Dengan adanya fungsi ini, kita bisa melihat bahwa penentuan alamat di Reticulum itu murni deterministik dan transparan. Tidak ada prosedur rahasia dan tidak bergantung pada server pihak ketiga, makanya siapa pun yang punya Identitas dan nama aplikasi yang sama akan selalu mendapatkan Destination Hash yang sama persis, di mana pun posisinya.
def hitung_hash_manual(identity):
    # [Langkah 1 Hitung Hash Nama]:
    # String 'FULL_NAME' ("aarif_rahmaan.jalaluddin_faqiih") diubah menjadi deretan biner UTF-8 lewat '.encode("utf-8")'.
    # Kemudian hasilnya dihitung dengan hash SHA-256 menggunakan 'hashlib.sha256(...)'.
    # Output biner 32 byte dari '.digest()' dipotong (sliced) menggunakan '[:NAME_HASH_BYTES]', sehingga hanya 16 byte pertama yang diambil.
    # Secara matematis: name_hash = Truncate128( SHA256( UTF8(FULL_NAME) ) )
    name_hash = hashlib.sha256(FULL_NAME.encode("utf-8")).digest()[:NAME_HASH_BYTES]
    
    # [Langkah 2 Hitung Destination Hash Final]:
    # Nilai 'name_hash' (16 byte) digabungkan (concatenated) dengan 'identity.hash' (16 byte, yaitu hash dari kunci publik identitas).
    # Gabungan 32 byte biner ini (name_hash + identity.hash) kemudian di-hash lagi menggunakan SHA-256.
    # Output 32 byte nya dipotong lagi untuk mengambil 16 byte pertama lewat '[:DEST_HASH_BYTES]'.
    # Secara matematis: destination_hash = Truncate128( SHA256( name_hash || identity.hash ) )
    #
    # Rumus ini menghasilkan 'Self-Certifying Destination Address' (Alamat Tujuan Tersertifikasi Mandiri) yang mengikat nama aplikasi dan identitas pemilik secara permanen, tanpa perlu Certificate Authority (CA).
    return hashlib.sha256(name_hash + identity.hash).digest()[:DEST_HASH_BYTES]

# ------------------------------------------------------------------------------
# 10. SINTAKS: def main():
# ------------------------------------------------------------------------------
# [Konteks Modularitas dan Entry Point]
# Fungsi 'main()' berfungsi sebagai titik masuk utama (main entry point) dari program. Di rekayasa perangkat lunak untuk distributed system, menaruh logika utama di dalam fungsi 'main()' menjaga global namespace tetap bersih, serta mempermudah pengujian modul dan pengaturan daur hidup proses.
def main():
    # [Inisialisasi Stack Reticulum dengan Log Quiet]:
    # Pemanggilan 'RNS.Reticulum(loglevel=RNS.LOG_ERROR)' berfungsi untuk menjalankan instance Reticulum local di device ini, dan mengatur log sistem agar hanya mencatat error fatal (LOG_ERROR).
    # Langkah ini akan memuat konfigurasi sistem (~/.reticulum/config), menyiapkan driver interface fisik (Wi-Fi, LoRa, kabel data), dan menjalankan thread pengolah paket di latar belakang (background routing thread).
    RNS.Reticulum(loglevel=RNS.LOG_ERROR)

    # [Membuat Identitas Kriptografi Mandiri (Self-Sovereign Identity)]:
    # Pemanggilan 'identity = RNS.Identity()' berfungsi untuk membuat sepasang kunci kriptografi, privat dan publik, sepanjang 512 bit (64 byte) secara local.
    # Pasangan kunci ini terdiri dari algoritma Ed25519 untuk tanda tangan digital dan X25519 untuk pertukaran kunci efemeral (ECDH).
    # Identitas ini disebut 'Self-Sovereign' karena dibuat sendiri tanpa perlu daftar ke otoritas terpusat mana pun.
    identity = RNS.Identity()

    # [Membuat Titik Tujuan Aplikasi (Destination Endpoint)]:
    # Baris ini membuat objek Destination yang menghubungkan Identitas pemegang kunci dengan jalur aplikasi 'APP_NAME' dan 'ASPECTS'.
    # Parameter 'RNS.Destination.IN' berfungsi untuk mendaftarkan endpoint ini sebagai listening endpoint, yaitu penerima paket masuk di routing engine local.
    # Parameter 'RNS.Destination.SINGLE' berarti komunikasi ke endpoint ini adalah unicast titik-ke-titik, dan enkripsinya otomatis dari ujung ke ujung (Encryption as Gravity) dengan Perfect Forward Secrecy (PFS).
    destination = RNS.Destination(
        identity,
        RNS.Destination.IN,      # menerima paket masuk
        RNS.Destination.SINGLE,  # dienkripsi untuk satu identity
        APP_NAME,
        *ASPECTS,
    )

    # [Pengecekan Kesamaan Kriptografis (Cryptographic Equivalence Testing)]:
    # Properti biner 'destination.hash' (dihitung internal oleh library RNS) dibandingkan dengan output dari 'hitung_hash_manual(identity)'.
    # Variabel 'cocok' akan bernilai Boolean 'True' jika kedua byte string itu sama persis.
    cocok = destination.hash == hitung_hash_manual(identity)

    # [Menampilkan Nama Gabungan]:
    # Baris ini melakukan print string nama lengkap aplikasi ("aarif_rahmaan.jalaluddin_faqiih") ke konsol terminal.
    print(f"Nama Destination : {FULL_NAME}")

    # [Menampilkan Hash Identitas dalam Format Hexadecimal]:
    # Properti 'identity.hexhash' berfungsi untuk mengubah nilai biner hash identitas (16 byte) menjadi string heksadesimal 32 karakter.
    # Hasilnya adalah Alamat Identitas Kriptografis yang unik dan bisa dibawa ke mana saja di jaringan Reticulum.
    print(f"Hash Identitas   : {identity.hexhash}")

    # [Menampilkan Hash Destination dalam Format Hexadecimal]:
    # Properti 'destination.hexhash' berfungsi untuk mengubah nilai biner hash destination (16 byte) menjadi string heksadesimal 32 karakter.
    # Hash inilah yang menjadi alamat tujuan utama di header paket Reticulum untuk proses routing di distributed system.
    print(f"Hash Destination : {destination.hexhash}")

    # [Menampilkan Format Ringkas dengan Tanda Kurung Sudut]:
    # Fungsi 'RNS.prettyhexrep(...)' berfungsi untuk mengubah data biner hash menjadi string heksadesimal yang dibungkus tanda '<...>', agar developer lebih mudah membaca dan mencatat log.
    print(f"Format Ringkas   : {RNS.prettyhexrep(destination.hash)}")

    # [Menampilkan Hasil Pengecekan Matematika]:
    # Baris ini melakukan print string 'YA' jika variabel Boolean 'cocok' bernilai True, artinya hasil hitung hash manual kita 100% konsisten dengan spesifikasi resmi Reticulum.
    print(f"Cocok Hitung Manual (hashlib): {'YA' if cocok else 'TIDAK'}")

# ------------------------------------------------------------------------------
# 11. SINTAKS: if __name__ == "__main__":
# ------------------------------------------------------------------------------
# [Konteks Eksekusi Modul dan Import library]
# Kondisi standar Python ini berfungsi untuk mengecek apakah script dijalankan langsung sebagai program utama ('__main__') atau di-import sebagai modul oleh script lain. Jadi fungsi 'main()' hanya akan di-run jika script dipanggil langsung dari terminal.
if __name__ == "__main__":
    # [Blok Penanganan Exception Runtime Global]:
    # Pemanggilan 'main()' dibungkus dengan try-except global, untuk menangkap semua kegagalan yang tidak terduga selama program berjalan.
    try:
        main()
    except Exception as e:
        # Jika terjadi error runtime, maka program akan berhenti menggunakan 'sys.exit()' sambil melakukan print nama class exception dan pesan error ke standard error.
        sys.exit(f"Terjadi kesalahan: {type(e).__name__}: {e}")
