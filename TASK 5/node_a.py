# Node A: pengirim pesan lewat Reticulum
# Pemakaian: python node_a.py <hash_destination_B> "isi pesan"

# argparse: modul bawaan Python, berfungsi untuk membaca argumen dari command line (hash tujuan dan isi pesan)
import argparse

# sys: modul bawaan Python, dibutuhkan untuk sys.exit() agar program keluar dengan kode status yang sesuai
import sys

# time: modul bawaan Python, berfungsi untuk time.sleep dan menghitung batas waktu tunggu
import time

# RNS: library Reticulum Network Stack, semua fungsi jaringan (Identity, Destination, Packet, Transport) ada di sini
import RNS

# Nama aplikasi dan aspek harus sama persis dengan yang dipakai Node B,
# karena hash destination dihitung dari nama ini dan identity pemiliknya
APP_NAME = "demo"
ASPECTS = ("pesan",)

# Batas waktu menunggu path ke tujuan (detik), supaya program tidak menunggu selamanya jika Node B mati
PATH_TIMEOUT = 30

# Batas waktu menunggu bukti terima dari Node B (detik)
RECEIPT_TIMEOUT = 30

# status: dictionary dipakai agar callback di bawah bisa mengubah nilainya
# (variabel biasa tidak bisa diubah dari dalam fungsi tanpa kata kunci global)
# None = belum ada hasil, True = terkirim, False = timeout
status = {"delivered": None}


# on_delivered: callback yang dipanggil Reticulum ketika bukti terima (proof) dari Node B sudah sampai
def on_delivered(receipt):
    # Tandai pesan berhasil sampai, loop tunggu di main() akan berhenti
    status["delivered"] = True
    print("[A] Terkirim: node tujuan mengonfirmasi penerimaan.")


# on_timeout: callback yang dipanggil jika bukti terima tidak datang sampai RECEIPT_TIMEOUT habis
def on_timeout(receipt):
    # Tandai gagal, loop tunggu di main() akan berhenti
    status["delivered"] = False
    print("[A] Timeout: tidak ada konfirmasi dari node tujuan.")


# main(): membungkus semua logika dalam satu fungsi, mengembalikan kode status (0 = sukses)
def main():
    # ArgumentParser membuat parser untuk argumen command line
    ap = argparse.ArgumentParser(description="Node A: kirim pesan via Reticulum")

    # Argumen posisi pertama: hash destination Node B dalam bentuk teks hex (dicetak oleh node_b.py)
    ap.add_argument("destination", help="hash destination tujuan (hex)")

    # Argumen posisi kedua: isi pesan yang akan dikirim
    ap.add_argument("message", help="isi pesan")

    # Argumen opsional --config: lokasi folder konfigurasi Reticulum, default None berarti memakai ~/.reticulum
    ap.add_argument("--config", default=None,
                    help="path direktori konfigurasi Reticulum (default: ~/.reticulum)")

    # parse_args membaca sys.argv dan mengisi objek args
    args = ap.parse_args()

    # try dipakai karena bytes.fromhex melempar ValueError jika teksnya bukan hex yang valid
    try:
        # strip("<>") membuang tanda < > bila hash disalin dari output prettyhexrep, replace membuang spasi
        # bytes.fromhex mengubah teks hex menjadi bytes, karena Reticulum bekerja dengan hash berbentuk bytes
        dest_hash = bytes.fromhex(args.destination.strip("<>").replace(" ", ""))
    except ValueError:
        print("Hash tujuan bukan hex yang valid.")
        return 1

    # TRUNCATED_HASHLENGTH bernilai 128 bit, dibagi 8 menjadi 16 byte (32 karakter hex)
    expected = RNS.Reticulum.TRUNCATED_HASHLENGTH // 8

    # Pemeriksaan panjang dilakukan di awal (fail-fast), supaya kesalahan input ketahuan sebelum jaringan dinyalakan
    if len(dest_hash) != expected:
        print(f"Panjang hash harus {expected * 2} karakter hex, dapat {len(dest_hash) * 2}.")
        return 1

    # .encode("utf-8") mengubah string menjadi bytes, karena paket jaringan hanya menerima bytes
    payload = args.message.encode("utf-8")

    # ENCRYPTED_MDU adalah ukuran data maksimum satu paket terenkripsi (383 byte pada RNS 1.5.7)
    # Destination SINGLE terenkripsi, jadi batas yang dipakai adalah ENCRYPTED_MDU, bukan PLAIN_MDU
    if len(payload) > RNS.Packet.ENCRYPTED_MDU:
        print(f"Pesan {len(payload)} byte melebihi batas satu paket terenkripsi "
              f"({RNS.Packet.ENCRYPTED_MDU} byte). Pakai RNS.Link/LXMF untuk pesan besar.")
        return 1

    # RNS.Reticulum() menginisialisasi stack Reticulum (membaca config, menyalakan interface)
    RNS.Reticulum(args.config)
    print("[A] Reticulum aktif.")

    # has_path mengecek apakah path_table sudah punya jalur ke destination tujuan
    # Path ada jika announce dari Node B sudah pernah diterima Node A
    if not RNS.Transport.has_path(dest_hash):
        print("[A] Meminta path ke tujuan...")

        # request_path menyiarkan path request ke jaringan, node yang tahu jalurnya akan menjawab
        RNS.Transport.request_path(dest_hash)

        # Catat waktu mulai untuk menghitung batas waktu tunggu
        start = time.time()

        # Ulangi pengecekan sampai path muncul di path_table
        while not RNS.Transport.has_path(dest_hash):
            # Jika sudah melewati PATH_TIMEOUT, berhenti agar program tidak menggantung
            if time.time() - start > PATH_TIMEOUT:
                print("[A] Path tidak ditemukan. Pastikan node B berjalan dan sudah announce.")
                return 2

            # sleep 0.2 detik agar loop tidak memakai CPU penuh
            time.sleep(0.2)

    # Identity.recall mengambil identity (kunci publik) Node B yang tersimpan dari announce
    # Kunci publik ini dibutuhkan untuk mengenkripsi pesan ke Node B
    identity = RNS.Identity.recall(dest_hash)

    # Pengecekan None diperlukan karena recall mengembalikan None jika identity belum dikenal
    if identity is None:
        print("[A] Identity tujuan belum dikenal (belum ada announce yang diterima).")
        return 2

    # RNS.Destination di sisi pengirim merepresentasikan alamat tujuan di Node B
    destination = RNS.Destination(
        # Argumen 1: identity pemilik destination (milik Node B, hasil recall)
        identity,
        # Argumen 2: OUT berarti destination ini tujuan trafik keluar, bukan milik node lokal
        RNS.Destination.OUT,
        # Argumen 3: SINGLE berarti pesan dienkripsi khusus untuk satu identity
        RNS.Destination.SINGLE,
        # Argumen 4: app_name, harus sama dengan Node B
        APP_NAME,
        # Argumen 5 dan seterusnya: aspek, harus sama dengan Node B (tanda * membuka tuple menjadi argumen terpisah)
        *ASPECTS,
    )

    # RNS.Packet membuat paket data berisi pesan untuk destination tersebut
    packet = RNS.Packet(destination, payload)

    # send() mengirim paket lewat path di path_table dan mengembalikan PacketReceipt
    # Jika pengiriman gagal, send() mengembalikan False
    receipt = packet.send()
    if not receipt:
        print("[A] Gagal mengirim paket.")
        return 3

    # Atur batas waktu menunggu bukti terima
    receipt.set_timeout(RECEIPT_TIMEOUT)

    # Daftarkan callback: on_delivered dipanggil jika bukti terima datang, on_timeout jika waktunya habis
    receipt.set_delivery_callback(on_delivered)
    receipt.set_timeout_callback(on_timeout)
    print(f"[A] Pesan dikirim ke {RNS.prettyhexrep(dest_hash)}, menunggu konfirmasi...")

    # Callback berjalan di thread lain, jadi main() menunggu sampai status berubah dari None
    while status["delivered"] is None:
        time.sleep(0.2)

    # Kode keluar 0 jika terkirim, 4 jika timeout
    return 0 if status["delivered"] else 4


# Baris ini bernilai True hanya jika file di-run langsung, bukan di-import dari file lain
# sys.exit meneruskan nilai kembalian main() sebagai kode keluar program
if __name__ == "__main__":
    sys.exit(main())
