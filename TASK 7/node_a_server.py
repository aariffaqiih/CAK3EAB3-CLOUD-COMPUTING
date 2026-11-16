# argparse: modul bawaan Python, dipakai untuk membaca opsi command line (--config, --identity) secara terstruktur dan otomatis punya --help

import argparse

# sys: modul bawaan Python, dipakai untuk sys.exit() agar program keluar dengan kode status yang jelas

import sys

# threading: modul bawaan Python, dipakai untuk menjalankan announce berkala di thread terpisah supaya tidak memblokir input chat

import threading

# RNS: library Reticulum Network Stack, dipakai untuk Reticulum(), Destination, dan prettyhexrep

import RNS

# Impor nama-nama dari modul chat_common (satu file bersama) agar konstanta dan logika tidak ditulis ulang di dua node

from chat_common import (

    # Nama aplikasi untuk nama terstruktur destination

    APP_NAME,

    # Aspek pertama nama terstruktur ("chat")

    ASPECT_CHAT,

    # Aspek kedua nama terstruktur (berisi NIM)

    ASPECT_NIM,

    # Jeda antar announce dalam detik

    ANNOUNCE_INTERVAL,

    # NIM dipakai juga di app_data announce sebagai penanda unik

    NIM,

    # Class yang menyimpan status dan logika sesi chat

    SesiChat,

    # Fungsi untuk mencetak banner berisi identitas mahasiswa

    cetak_banner,

    # Fungsi untuk mencetak teks dengan warna favorit

    cetak_warna,

    # Fungsi untuk memuat atau membuat identity yang disimpan di disk

    muat_atau_buat_identity,

)

# Label tampilan Node A, muncul sebagai nama pengirim di sisi Node B

LABEL_NODE = "Node A"

# Nama file identity bawaan, disimpan agar hash destination tetap sama setiap Node A dijalankan ulang

FILE_IDENTITY_DEFAULT = "node_a_identity"


# Fungsi yang dijalankan di thread terpisah: mengumumkan keberadaan Node A ke jaringan secara berkala

def loop_announce(destination, event_berhenti, app_data):

    # Ulangi selama thread utama belum meminta berhenti lewat Event

    while not event_berhenti.is_set():

        # announce memberi tahu jaringan bahwa destination ini ada, beserta public key identity-nya (app_data ikut terbawa)

        destination.announce(app_data=app_data)

        # Event.wait berfungsi seperti sleep, bedanya langsung terbangun saat Event di-set sehingga program bisa berhenti cepat

        event_berhenti.wait(ANNOUNCE_INTERVAL)


# Fungsi utama membungkus seluruh logika program agar tidak ada variabel global berserakan

def main():

    # ArgumentParser membuat parser command line, description tampil saat pengguna menjalankan --help

    parser = argparse.ArgumentParser(description="Node A - chat Reticulum (server)")

    # --config opsional: folder konfigurasi Reticulum alternatif, None berarti memakai folder bawaan (~/.reticulum)

    parser.add_argument("--config", default=None, help="path folder konfigurasi Reticulum alternatif")

    # --identity opsional: lokasi file identity, bawaannya node_a_identity

    parser.add_argument("--identity", default=FILE_IDENTITY_DEFAULT, help="path file identity Node A")

    # parse_args membaca sys.argv dan mengisi objek args, jika ada opsi salah maka program berhenti dengan pesan error

    args = parser.parse_args()

    # Inisialisasi stack Reticulum (membaca config, menyalakan interface), wajib dilakukan sebelum membuat Destination

    # Variabel reticulum disimpan supaya objeknya tetap hidup selama program berjalan

    reticulum = RNS.Reticulum(args.config)

    # Muat identity dari disk, atau buat baru jika belum ada

    identity = muat_atau_buat_identity(args.identity)

    # Destination adalah alamat yang bisa dituju di jaringan Reticulum, dibuat dari identity + nama terstruktur

    destination = RNS.Destination(

        # Argumen 1: identity pemilik destination, hash destination dihitung dari identity dan nama terstruktur

        identity,

        # Argumen 2: IN berarti destination ini menerima trafik masuk (milik node lokal)

        RNS.Destination.IN,

        # Argumen 3: SINGLE berarti terenkripsi untuk satu identity, wajib agar klien bisa membuat Link ke destination ini

        RNS.Destination.SINGLE,

        # Argumen 4: app_name, bagian pertama nama terstruktur

        APP_NAME,

        # Argumen 5: aspek pertama, menandakan fungsinya chat

        ASPECT_CHAT,

        # Argumen 6: aspek kedua berisi NIM, nama lengkapnya "assessment.chat.nim103112430182"

        ASPECT_NIM,

    )

    # Buat objek sesi chat, keluar_saat_tutup=False karena server harus tetap hidup saat satu klien putus

    sesi = SesiChat(LABEL_NODE, keluar_saat_tutup=False)

    # Daftarkan callback: setiap klien yang membuat Link ke destination ini akan diserahkan ke sesi.terima_link_masuk

    destination.set_link_established_callback(sesi.terima_link_masuk)

    # Tampilkan banner berisi nama, NIM, kelas, dan warna favorit

    cetak_banner("NODE A - CHAT SERVER (RETICULUM)")

    # hash destination berupa bytes, .hex() mengubahnya menjadi teks heksadesimal tanpa tanda < > agar bisa langsung disalin ke Node B

    hash_hex = destination.hash.hex()

    # Tampilkan hash destination, nilai inilah yang harus dimasukkan sebagai argumen di Node B

    cetak_warna(f"Hash Destination : {hash_hex}")

    # Tampilkan hash identity dalam format prettyhexrep (dibungkus < >) hanya sebagai informasi

    cetak_warna(f"Hash Identitas   : {RNS.prettyhexrep(identity.hash)}")

    # Tampilkan nama terstruktur lengkap agar mudah dicocokkan dengan Node B

    cetak_warna(f"Nama Terstruktur : {APP_NAME}.{ASPECT_CHAT}.{ASPECT_NIM}")

    # Beri petunjuk perintah yang harus dijalankan di terminal lain untuk Node B

    cetak_warna(f"Jalankan Node B  : python node_b_client.py {hash_hex}")

    # Informasikan bahwa Node A siap menerima koneksi

    cetak_warna("[+] Menunggu Node B terhubung...")

    # String app_data berisi label dan NIM, disertakan di announce sebagai penanda unik

    # .encode("utf-8") wajib karena paket jaringan hanya menerima bytes, bukan string

    app_data = f"{LABEL_NODE} | {NIM}".encode("utf-8")

    # Event adalah "bendera" thread-safe: saat di-set, thread announce tahu bahwa ia harus berhenti

    event_berhenti = threading.Event()

    # Buat thread untuk loop announce, daemon=True agar thread otomatis mati ketika program utama selesai

    thread_announce = threading.Thread(target=loop_announce, args=(destination, event_berhenti, app_data), daemon=True)

    # Jalankan thread announce, mulai saat ini Node A mengumumkan dirinya setiap ANNOUNCE_INTERVAL detik

    thread_announce.start()

    # try/finally menjamin thread announce dihentikan walau terjadi error saat chat berlangsung

    try:

        # Loop input chat berjalan di thread utama, sementara pesan masuk ditangani callback Reticulum di thread lain

        sesi.jalankan_input()

    # finally selalu dijalankan, baik keluar normal maupun karena error

    finally:

        # Beri sinyal berhenti ke thread announce

        event_berhenti.set()

    # Pesan penutup agar pengguna tahu program berhenti dengan rapi

    cetak_warna("[*] Node A dihentikan.")

    # Kode 0 berarti keluar normal tanpa error

    sys.exit(0)


# Baris ini bernilai True hanya jika file dijalankan langsung (python node_a_server.py), bukan saat di-import

if __name__ == "__main__":

    # Panggil fungsi utama

    main()
