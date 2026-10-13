# time: berfungsi untuk time.sleep di loop utama agar CPU tidak terpakai penuh
import time
# sys: berfungsi untuk sys.exit() saat program dihentikan
import sys
# RNS: library Reticulum, di sini dibutuhkan untuk Reticulum(), Transport, dan prettyhexrep
import RNS


# Class ini adalah handler, yaitu objek yang dipanggil Reticulum setiap ada announce yang cocok
class AssessmentAnnounceHandler:
    # Atribut class bernama aspect_filter wajib ada, karena Transport membacanya untuk memilih announce
    # Nilainya sama dengan nama terstruktur di Node A, jadi hanya announce dari "assessment.node_a" yang diteruskan
    aspect_filter = "assessment.node_a"

    # Reticulum memanggil method ini dengan keyword argument, makanya nama parameter harus persis
    # destination_hash, announced_identity, dan app_data (self diisi otomatis oleh Python)
    def received_announce(self, destination_hash, announced_identity, app_data):
        # Jarak hop tidak dikirim sebagai parameter, jadi diambil dari tabel path milik Transport
        # hops_to menerima hash destination (bytes) dan mengembalikan jumlah hop
        hop_count = RNS.Transport.hops_to(destination_hash)

        print("\n" + "=" * 50)
        print("          [NODE B] ANNOUNCE DITERIMA!             ")
        print("=" * 50)
        # self.aspect_filter membaca atribut class di atas, jadi nilainya tidak ditulis ulang
        print(f"Filter Aspek Match  : {self.aspect_filter}")
        # destination_hash bertipe bytes, prettyhexrep mengubahnya jadi teks hex
        print(f"Destination Hash    : {RNS.prettyhexrep(destination_hash)}")
        # Pengecekan "if announced_identity" perlu, karena nilainya bisa None jika identity tidak ditemukan
        # Ekspresi "A if kondisi else B" adalah if-else dalam 1 baris
        identity_text = RNS.prettyhexrep(announced_identity.hash) if announced_identity else "Unknown"
        print(f"Hash Identitas      : {identity_text}")

        # PATHFINDER_M adalah batas hop maksimum, nilai ini keluar jika path belum diketahui
        # Maka dari itu dicek dulu sebelum dicetak sebagai angka
        if hop_count == RNS.Transport.PATHFINDER_M:
            print("Jumlah Hop (Jarak)  : tidak diketahui")
        else:
            print(f"Jumlah Hop (Jarak)  : {hop_count} hop")

        # app_data bisa None jika pengirim tidak menyertakan data, jadi dicek lebih dulu
        if app_data:
            # try-except dipakai karena belum tentu app_data berisi teks utf-8, bisa saja bytes biasa
            try:
                # decode kebalikan dari encode di Node A, mengubah bytes kembali menjadi string
                data_str = app_data.decode("utf-8")
                print(f"Data Tambahan (App Data): \"{data_str}\"")
            # Exception menangkap semua error decode, jadi program tidak crash
            except Exception:
                # .hex() mengubah bytes menjadi teks hex, sebagai cadangan jika bukan teks
                print(f"Data Tambahan (Raw Bytes): {app_data.hex()}")
        else:
            print("Data Tambahan (App Data): <Kosong>")

        print("=" * 50 + "\n")


def main():
    # Inisialisasi stack Reticulum, wajib sebelum register handler
    reticulum = RNS.Reticulum()

    print("=" * 50)
    print("      NODE B - ANNOUNCE LISTENER (RETICULUM)     ")
    print("=" * 50)
    print("[+] Menginisialisasi listener Announce...")

    # Membuat objek dari class handler, objek inilah yang didaftarkan ke Reticulum
    handler = AssessmentAnnounceHandler()
    # register_announce_handler mendaftarkan objek handler, jadi tiap announce yang cocok dengan
    # aspect_filter akan memanggil handler.received_announce secara otomatis
    RNS.Transport.register_announce_handler(handler)

    print(f"[+] Handler terdaftar untuk aspek: '{handler.aspect_filter}'")
    print("[+] Node B siap mendengarkan Announce dari Node A. Tekan Ctrl+C untuk keluar.\n")

    try:
        # Loop tanpa akhir agar program tetap running, karena handler dipanggil di thread milik Reticulum
        while True:
            # sleep 1 detik supaya loop tidak memakan CPU
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Program dihentikan oleh pengguna.")
        sys.exit(0)


if __name__ == "__main__":
    main()
