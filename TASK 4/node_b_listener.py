import time
import sys
import RNS

class AssessmentAnnounceHandler:
    aspect_filter = "assessment.node_a"

    def received_announce(self, aspect_filter, announced_identity, announced_destination_hash, app_data, hop_count):
        print("\n==================================================")
        print("          [NODE B] ANNOUNCE DITERIMA!             ")
        print("==================================================")
        print(f"Filter Aspek Match  : {aspect_filter}")
        print(f"Destination Hash    : {RNS.prettyhexrep(announced_destination_hash)}")
        print(f"Hash Identitas      : {announced_identity.hexhash if announced_identity else 'Unknown'}")
        print(f"Jumlah Hop (Jarak)  : {hop_count} hop")
        
        if app_data:
            try:
                data_str = app_data.decode("utf-8")
                print(f"Data Tambahan (App Data): \"{data_str}\"")
            except Exception:
                print(f"Data Tambahan (Raw Bytes): {app_data.hex()}")
        else:
            print("Data Tambahan (App Data): <Kosong>")
            
        print("==================================================\n")

def main():
    reticulum = RNS.Reticulum()

    print("==================================================")
    print("      NODE B - ANNOUNCE LISTENER (RETICULUM)     ")
    print("==================================================")
    print("[+] Menginisialisasi listener Announce...")

    handler = AssessmentAnnounceHandler()
    RNS.Transport.register_announce_handler(handler)

    print(f"[+] Handler terdaftar untuk aspek: '{handler.aspect_filter}'")
    print("[+] Node B siap mendengarkan Announce dari Node A. Tekan Ctrl+C untuk keluar.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Program dihentikan oleh pengguna.")
        sys.exit(0)

if __name__ == "__main__":
    main()
