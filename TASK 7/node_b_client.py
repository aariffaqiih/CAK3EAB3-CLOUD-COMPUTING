# argparse: modul bawaan Python, dipakai untuk membaca hash tujuan dan opsi lain dari command line secara terstruktur

import argparse

# sys: modul bawaan Python, dipakai untuk sys.exit() dengan kode status error jika koneksi gagal

import sys

# time: modul bawaan Python, dipakai untuk time.sleep (jeda polling) dan time.time (menghitung batas waktu)

import time

# RNS: library Reticulum Network Stack, dipakai untuk Reticulum(), Transport, Identity.recall, Destination, dan Link

import RNS

# Impor nama-nama dari modul chat_common (satu file bersama) agar konstanta dan logika tidak ditulis ulang di dua node

from chat_common import (

    # Nama aplikasi untuk nama terstruktur destination, harus sama dengan Node A

    APP_NAME,

    # Aspek pertama nama terstruktur ("chat"), harus sama dengan Node A

    ASPECT_CHAT,

    # Aspek kedua nama terstruktur (berisi NIM), harus sama dengan Node A

    ASPECT_NIM,

    # Batas waktu menunggu path ke Node A

    BATAS_WAKTU_PATH,

    # Batas waktu menunggu link aktif

    BATAS_WAKTU_LINK,

    # Nama lengkap dipakai di pesan sapaan otomatis

    NAMA_LENGKAP,

    # NIM dipakai di pesan sapaan otomatis

    NIM,

    # Kelas dipakai di pesan sapaan otomatis

    KELAS,

    # Class yang menyimpan status dan logika sesi chat

    SesiChat,

    # Fungsi untuk mencetak banner berisi identitas mahasiswa

    cetak_banner,

    # Fungsi untuk mencetak teks dengan warna favorit

    cetak_warna,

)

# Label tampilan Node B, muncul sebagai nama pengirim di sisi Node A

LABEL_NODE = "Node B"


# Fungsi untuk memvalidasi dan mengubah hash heksadesimal dari command line menjadi bytes

def ubah_hash_hex(hash_hex):

    # TRUNCATED_HASHLENGTH dalam bit, dibagi 8 menjadi byte, dikali 2 menjadi jumlah karakter heksadesimal yang valid

    panjang_hex = (RNS.Reticulum.TRUNCATED_HASHLENGTH // 8) * 2

    # Tolak input yang panjangnya salah sebelum mencoba mengubahnya

    if len(hash_hex) != panjang_hex:

        # ValueError dipilih karena masalahnya ada pada nilai input, pesan menyebut panjang yang diharapkan

        raise ValueError(f"panjang hash harus {panjang_hex} karakter heksadesimal, bukan {len(hash_hex)}")

    # bytes.fromhex mengubah teks heksadesimal menjadi bytes, dan melempar ValueError sendiri jika ada karakter non-hex

    return bytes.fromhex(hash_hex)


# Fungsi untuk menunggu sampai kondisi terpenuhi atau batas waktu habis, dipakai untuk path dan link

def tunggu(kondisi, batas_detik):

    # Hitung kapan batas waktu berakhir dalam detik epoch

    batas = time.time() + batas_detik

    # Ulangi selama kondisi belum terpenuhi dan batas waktu belum lewat

    while not kondisi() and time.time() < batas:

        # Jeda 0.1 detik agar loop tidak memakan CPU penuh

        time.sleep(0.1)

    # Kembalikan hasil akhir kondisi: True jika terpenuhi, False jika batas waktu habis

    return kondisi()


# Fungsi utama membungkus seluruh logika program agar tidak ada variabel global berserakan

def main():

    # ArgumentParser membuat parser command line, description tampil saat pengguna menjalankan --help

    parser = argparse.ArgumentParser(description="Node B - chat Reticulum (klien)")

    # Argumen posisional wajib: hash destination Node A yang ditampilkan Node A saat dijalankan

    parser.add_argument("destination", help="hash destination Node A (heksadesimal)")

    # --config opsional: folder konfigurasi Reticulum alternatif, None berarti memakai folder bawaan (~/.reticulum)

    parser.add_argument("--config", default=None, help="path folder konfigurasi Reticulum alternatif")

    # parse_args membaca sys.argv dan mengisi objek args, jika ada opsi salah maka program berhenti dengan pesan error

    args = parser.parse_args()

    # try dipakai agar input hash yang salah menghasilkan pesan error rapi, bukan traceback

    try:

        # Ubah hash heksadesimal menjadi bytes, dilakukan sebelum menyalakan Reticulum supaya input salah gagal lebih cepat

        hash_tujuan = ubah_hash_hex(args.destination)

    # ValueError dilempar oleh ubah_hash_hex baik karena panjang salah maupun karakter non-hex

    except ValueError as error:

        # parser.error mencetak pesan penggunaan lalu keluar dengan kode 2, praktik standar untuk argumen CLI yang tidak valid

        parser.error(f"hash destination tidak valid: {error}")

    # Inisialisasi stack Reticulum (membaca config, menyalakan interface), wajib dilakukan sebelum memakai Transport

    # Variabel reticulum disimpan supaya objeknya tetap hidup selama program berjalan

    reticulum = RNS.Reticulum(args.config)

    # Tampilkan banner berisi nama, NIM, kelas, dan warna favorit

    cetak_banner("NODE B - CHAT CLIENT (RETICULUM)")

    # Cek apakah jalur (path) ke destination Node A sudah diketahui, misalnya dari announce yang pernah diterima

    if not RNS.Transport.has_path(hash_tujuan):

        # Beri tahu pengguna bahwa pencarian path dimulai

        cetak_warna("[+] Path belum diketahui, meminta path ke jaringan...")

        # request_path meminta jaringan memberi tahu jalur ke destination ini

        RNS.Transport.request_path(hash_tujuan)

        # Tunggu sampai path ditemukan, tetapi tidak selamanya (ada BATAS_WAKTU_PATH)

        if not tunggu(lambda: RNS.Transport.has_path(hash_tujuan), BATAS_WAKTU_PATH):

            # Tampilkan pesan gagal beserta saran pemecahan yang paling mungkin

            cetak_warna(f"[X] Path tidak ditemukan dalam {BATAS_WAKTU_PATH} detik. Pastikan Node A sedang berjalan dan hash benar.")

            # Kode 1 berarti keluar karena error

            sys.exit(1)

    # Ambil identity (public key) Node A dari data announce yang tersimpan, hasilnya None jika tidak dikenal

    identity_tujuan = RNS.Identity.recall(hash_tujuan)

    # Tanpa identity Node A, destination tidak bisa dibuat karena enkripsi butuh public key-nya

    if identity_tujuan is None:

        # Tampilkan pesan gagal yang spesifik

        cetak_warna("[X] Identity Node A tidak dikenal. Coba jalankan ulang setelah Node A mengirim announce.")

        # Kode 1 berarti keluar karena error

        sys.exit(1)

    # Destination OUT mewakili tujuan di node lain (kebalikan IN di Node A), dibuat dari identity dan nama terstruktur yang sama

    destination = RNS.Destination(

        # Argumen 1: identity milik Node A (hasil recall)

        identity_tujuan,

        # Argumen 2: OUT berarti destination ini adalah tujuan di node lain

        RNS.Destination.OUT,

        # Argumen 3: SINGLE, harus sama dengan yang dipakai Node A

        RNS.Destination.SINGLE,

        # Argumen 4: app_name, harus sama persis dengan Node A

        APP_NAME,

        # Argumen 5: aspek pertama, harus sama persis dengan Node A

        ASPECT_CHAT,

        # Argumen 6: aspek kedua (NIM), harus sama persis dengan Node A, jika beda maka hash tidak akan cocok

        ASPECT_NIM,

    )

    # Buat objek sesi chat, keluar_saat_tutup=True karena Node B tidak berguna jika Node A memutus link

    sesi = SesiChat(LABEL_NODE, keluar_saat_tutup=True)

    # Informasikan bahwa pembuatan link dimulai

    cetak_warna("[+] Membuat link ke Node A...")

    # RNS.Link membuat link terenkripsi ke destination, handshake berjalan di latar belakang (tidak memblokir)

    link = RNS.Link(destination)

    # Pasang callback paket masuk dan link tertutup sekarang juga, agar kegagalan saat handshake pun tertangani

    sesi.pasang_callback(link)

    # Saat handshake selesai dan link aktif, Reticulum memanggil sesi.link_terhubung

    link.set_link_established_callback(sesi.link_terhubung)

    # Tunggu sampai link aktif (sesi.link terisi) atau gagal (sesi.berjalan menjadi False) atau waktu habis

    tunggu(lambda: sesi.link is not None or not sesi.berjalan, BATAS_WAKTU_LINK)

    # Jika sesi.link masih None berarti link tidak pernah aktif

    if sesi.link is None:

        # Tampilkan pesan gagal beserta penyebab yang mungkin

        cetak_warna("[X] Link gagal dibuat (waktu habis atau ditolak). Pastikan Node A masih berjalan.")

        # Kode 1 berarti keluar karena error

        sys.exit(1)

    # Kirim sapaan otomatis berisi identitas mahasiswa, sekaligus bukti bahwa komunikasi Node B ke Node A bekerja

    sesi.kirim(f"Halo, saya {LABEL_NODE} - {NAMA_LENGKAP} ({NIM}, {KELAS})")

    # Mulai loop input chat di thread utama, pesan masuk ditangani callback Reticulum di thread lain

    sesi.jalankan_input()

    # Pesan penutup agar pengguna tahu program berhenti dengan rapi

    cetak_warna("[*] Node B dihentikan.")

    # Kode 0 berarti keluar normal tanpa error

    sys.exit(0)


# Baris ini bernilai True hanya jika file dijalankan langsung (python node_b_client.py ...), bukan saat di-import

if __name__ == "__main__":

    # Panggil fungsi utama

    main()
