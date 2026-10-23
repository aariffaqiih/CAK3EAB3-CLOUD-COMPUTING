# Node B: penerima pesan (untuk menguji node_a.py)
# Pemakaian: python node_b.py, lalu salin hash destination yang dicetak ke node_a.py

# argparse: modul bawaan Python, berfungsi untuk membaca opsi command line (config, identity, interval announce)
import argparse

# os: modul bawaan Python, dibutuhkan untuk mengecek apakah file identity sudah ada di disk (os.path.isfile)
import os

# time: modul bawaan Python, berfungsi untuk time.sleep di loop utama agar CPU tidak terpakai penuh
import time

# RNS: library Reticulum Network Stack, semua fungsi jaringan (Identity, Destination, Packet) ada di sini
import RNS

# Nama aplikasi dan aspek harus sama persis dengan yang dipakai Node A,
# karena hash destination dihitung dari nama ini dan identity pemiliknya
APP_NAME = "demo"
ASPECTS = ("pesan",)


# on_packet: callback yang dipanggil Reticulum setiap kali ada paket data masuk ke destination ini
# Parameter data berisi isi pesan (bytes), packet adalah objek paket lengkapnya
def on_packet(data, packet):
    # decode mengubah bytes kembali menjadi string, errors="replace" mengganti byte yang rusak
    # supaya program tidak crash jika pengirim mengirim data yang bukan teks UTF-8
    print(f"[B] Pesan diterima: {data.decode('utf-8', errors='replace')}")


# main(): membungkus semua logika dalam satu fungsi
def main():
    # ArgumentParser membuat parser untuk opsi command line
    ap = argparse.ArgumentParser(description="Node B: penerima pesan Reticulum")

    # --config: lokasi folder konfigurasi Reticulum, default None berarti memakai ~/.reticulum
    ap.add_argument("--config", default=None)

    # --identity: file tempat identity disimpan, supaya hash destination tidak berubah setiap program di-run
    ap.add_argument("--identity", default="node_b.identity",
                    help="file identity (dibuat jika belum ada, agar hash tetap sama)")

    # --announce-interval: jeda antar announce dalam detik
    # Announce diulang agar Node A yang dijalankan belakangan tetap bisa menemukan Node B
    ap.add_argument("--announce-interval", type=int, default=20)

    # parse_args membaca sys.argv dan mengisi objek args
    args = ap.parse_args()

    # RNS.Reticulum() menginisialisasi stack Reticulum (membaca config, menyalakan interface)
    RNS.Reticulum(args.config)

    # os.path.isfile bernilai True jika identity sudah pernah dibuat di run sebelumnya
    if os.path.isfile(args.identity):
        # from_file membaca key dari file, hasilnya identity yang sama dengan run sebelumnya
        identity = RNS.Identity.from_file(args.identity)
    else:
        # RNS.Identity() membuat pasangan key kriptografi baru (publik dan privat)
        identity = RNS.Identity()
        # to_file menyimpan key ke disk, jadi run berikutnya memakai identity yang sama
        identity.to_file(args.identity)

    # RNS.Destination adalah alamat yang bisa dituju di jaringan Reticulum, dibuat dari identity + nama aspek
    destination = RNS.Destination(
        # Argumen 1: identity pemilik destination, dari sini hash destination dihitung
        identity,
        # Argumen 2: IN berarti destination ini menerima trafik masuk (milik node lokal)
        RNS.Destination.IN,
        # Argumen 3: SINGLE berarti destination terenkripsi untuk satu identity, dan hanya tipe ini yang boleh di-announce
        RNS.Destination.SINGLE,
        # Argumen 4: app_name, harus sama dengan Node A
        APP_NAME,
        # Argumen 5 dan seterusnya: aspek, harus sama dengan Node A (tanda * membuka tuple menjadi argumen terpisah)
        *ASPECTS,
    )

    # PROVE_ALL membuat Node B otomatis mengirim bukti terima (proof) untuk setiap paket yang masuk
    # Bukti inilah yang memicu callback on_delivered di Node A
    destination.set_proof_strategy(RNS.Destination.PROVE_ALL)

    # set_packet_callback mendaftarkan on_packet agar dipanggil setiap ada paket masuk
    destination.set_packet_callback(on_packet)

    # destination.hash berupa bytes, .hex() mengubahnya menjadi teks hex yang bisa disalin ke node_a.py
    print(f"[B] Hash destination: {destination.hash.hex()}")
    print("[B] Menunggu pesan (Ctrl+C untuk berhenti)...")

    # try dipakai untuk menangkap KeyboardInterrupt (Ctrl+C), jadi program berhenti dengan pesan rapi, bukan traceback
    try:
        # while True membuat loop tanpa akhir, karena Node B harus tetap hidup untuk menerima pesan
        while True:
            # announce() memberi tahu jaringan bahwa destination ini ada, beserta kunci publik identity-nya
            # Node A memakai informasi ini untuk membuat path dan mengenkripsi pesan
            destination.announce()

            # sleep menahan program selama jeda announce, supaya jaringan tidak dibanjiri announce
            time.sleep(args.announce_interval)

    # except KeyboardInterrupt jalan jika pengguna menekan Ctrl+C
    except KeyboardInterrupt:
        print("\n[B] Berhenti.")


# Baris ini bernilai True hanya jika file di-run langsung, bukan di-import dari file lain
# Jadi main() tidak berjalan otomatis ketika file ini di-import
if __name__ == "__main__":
    main()
