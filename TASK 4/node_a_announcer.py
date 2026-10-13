import time
import sys
import RNS

def main():
    reticulum = RNS.Reticulum()
    identity = RNS.Identity()
    destination = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        "assessment",
        "node_a"
    )

    print("==================================================")
    print("      NODE A - ANNOUNCER (RETICULUM NETWORK)      ")
    print("==================================================")
    print(f"Hash Identitas   : {identity.hexhash}")
    print(f"Hash Destination : {destination.hexhash}")
    print(f"Nama Terstruktur : assessment.node_a")
    print("==================================================\n")

    app_data = "Halo dari Node A! [Assessment Reticulum]".encode("utf-8")

    try:
        print("[+] Mengirimkan paket Announce ke jaringan...")
        destination.announce(app_data=app_data)
        print("[V] Announce berhasil dikirimkan!")
        print("[i] Menunggu jaringan memproses siaran...")
        time.sleep(3)
    except KeyboardInterrupt:
        print("\n[*] Program dihentikan oleh pengguna.")
        sys.exit(0)

if __name__ == "__main__":
    main()
