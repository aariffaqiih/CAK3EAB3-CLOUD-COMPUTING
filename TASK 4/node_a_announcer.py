# import time: modul bawaan Python, berfungsi untuk delay (time.sleep) agar loop tidak berjalan tanpa jeda
import time
# import sys: modul bawaan Python, dibutuhkan untuk sys.exit() agar program keluar dengan rapi saat Ctrl+C
import sys
# import os: modul bawaan Python, dibutuhkan untuk mengecek apakah file identity sudah ada di disk (os.path.isfile)
import os
# import RNS: library Reticulum Network Stack, semua fungsi jaringan (Identity, Destination, Transport) ada di sini
import RNS

# Konstanta ditulis huruf besar sebagai kebiasaan Python untuk nilai yang tidak diubah ketika program berjalan
# Path file tempat identity disimpan, karena itu hash identity tidak berubah setiap program di-run
IDENTITY_PATH = "node_a_identity"
# Jeda antar announce dalam detik, announce berulang bertujuan agar Node B yang telat dijalankan tetap menerima pesan
ANNOUNCE_INTERVAL = 30


# def main(): membungkus semua logika dalam satu fungsi
def main():
    # RNS.Reticulum() menginisialisasi stack Reticulum (membaca config, menyalakan interface)
    # Variabel reticulum disimpan supaya objeknya tetap hidup selama program berjalan
    reticulum = RNS.Reticulum()

    # Variabel identity dibuat None dulu sebagai penanda belum ada identity yang berhasil dimuat
    identity = None
    # os.path.isfile mengembalikan True jika file identity sudah pernah dibuat di run sebelumnya
    if os.path.isfile(IDENTITY_PATH):
        # from_file membaca key dari file, hasilnya objek Identity yang sama dengan run sebelumnya
        identity = RNS.Identity.from_file(IDENTITY_PATH)
    # Jika file belum ada atau gagal dibaca, identity masih None, maka buat yang baru
    if identity is None:
        # RNS.Identity() membuat pasangan key kriptografi baru (publik dan privat)
        identity = RNS.Identity()
        # to_file menyimpan key ke disk, jadi run berikutnya memakai identity yang sama
        identity.to_file(IDENTITY_PATH)

    # RNS.Destination adalah alamat yang bisa dituju di jaringan Reticulum, dibuat dari identity + nama aspek
    destination = RNS.Destination(
        # Argumen 1: identity pemilik destination, dari sini hash destination dihitung
        identity,
        # Argumen 2: IN berarti destination ini menerima trafik masuk (milik node lokal), kebalikannya OUT untuk tujuan di node lain
        RNS.Destination.IN,
        # Argumen 3: SINGLE berarti destination terenkripsi untuk 1 identity, dipilih karena announce butuh identity pemilik
        RNS.Destination.SINGLE,
        # Argumen 4: app_name, bagian pertama nama terstruktur
        "assessment",
        # Argumen 5: aspek, bagian berikutnya, jadi nama lengkapnya "assessment.node_a" (sama dengan aspect_filter di Node B)
        "node_a"
    )

    print("=" * 50)
    print("      NODE A - ANNOUNCER (RETICULUM NETWORK)      ")
    print("=" * 50)
    # prettyhexrep mengubah bytes hash menjadi teks hex yang enak dibaca, dibungkus tanda < >
    # identity.hash adalah bytes hash dari identity, tidak bisa di-print mentah karena berupa bytes
    print(f"Hash Identitas   : {RNS.prettyhexrep(identity.hash)}")
    # destination.hash adalah alamat destination, nilai inilah yang akan terlihat di Node B
    print(f"Hash Destination : {RNS.prettyhexrep(destination.hash)}")
    print("Nama Terstruktur : assessment.node_a")
    print("=" * 50 + "\n")

    # String Python menyimpan teks unicode, tapi paket jaringan hanya menerima bytes
    # .encode("utf-8") mengubah string menjadi bytes, makanya app_data harus melewati langkah ini
    app_data = "Halo dari Node A! [Assessment Reticulum]".encode("utf-8")

    # try dipakai untuk menangkap KeyboardInterrupt (Ctrl+C), jadi program berhenti dengan pesan rapi, bukan traceback
    try:
        # while True membuat loop tanpa akhir, karena Node A harus tetap running agar koneksi ke jaringan tidak putus
        while True:
            print("[+] Mengirimkan paket Announce ke jaringan...")
            # announce() memberi tahu keberadaan destination beserta public key identity ke semua interface
            # Parameter app_data bertipe bytes, isinya ikut terbawa dan dibaca oleh Node B
            destination.announce(app_data=app_data)
            print("[V] Announce berhasil dikirimkan!")
            print(f"[i] Announce berikutnya dalam {ANNOUNCE_INTERVAL} detik. Tekan Ctrl+C untuk keluar.")
            # sleep menahan program selama 30 detik, jadi announce tidak membanjiri jaringan
            time.sleep(ANNOUNCE_INTERVAL)
    # except KeyboardInterrupt jalan jika pengguna menekan Ctrl+C
    except KeyboardInterrupt:
        print("\n[*] Program dihentikan oleh pengguna.")
        # sys.exit(0): kode 0 berarti keluar normal tanpa error
        sys.exit(0)


# Baris ini bernilai True hanya jika file di-run langsung, bukan di-import dari file lain
# Jadi main() tidak berjalan otomatis ketika file ini di-import
if __name__ == "__main__":
    main()
