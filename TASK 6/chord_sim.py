# Simulasi Chord (m = 5, ruang identifier 0..31) untuk memverifikasi jawaban soal 1 Tugas-6.
# Aturan (Tanenbaum & van Steen, Distributed Systems):
#   succ(k)        = node aktif pertama dengan id >= k, berputar melewati 0
#   FT_p[i]        = succ((p + 2^(i-1)) mod 2^m), i = 1..m
#   lookup(p, k)   : jika k di (p, FT_p[1]] kembalikan FT_p[1]; selain itu teruskan ke FT_p[j]
#                    dengan FT_p[j] <= k < FT_p[j+1] (berputar), atau FT_p[m] jika k melewati semuanya.
import sys

M = 5
N = 2 ** M
NODES = [1, 4, 7, 12, 15, 19, 20, 27]      # node aktif hasil pembacaan gambar (lingkaran tebal)


def succ(k, nodes):
    k %= N
    for n in sorted(nodes):
        if n >= k:
            return n
    return min(nodes)                       # berputar melewati 0


def finger_table(p, nodes):
    return [(i, (p + 2 ** (i - 1)) % N, succ(p + 2 ** (i - 1), nodes)) for i in range(1, M + 1)]


def in_open(x, a, b):
    """x di interval terbuka (a, b) pada ring."""
    a, b, x = a % N, b % N, x % N
    return (a < x < b) if a < b else (x > a or x < b)


def in_half(x, a, b):
    """x di interval (a, b] pada ring."""
    return in_open(x, a, b) or (x % N) == (b % N)


def lookup(p, k, nodes):
    """Mengembalikan (node penanggung jawab, daftar node yang dikunjungi, daftar langkah)."""
    path, steps = [p], []
    cur = p
    for _ in range(4 * M):
        ft = [e[2] for e in finger_table(cur, nodes)]
        if k % N == cur:
            steps.append((cur, "k = id node ini", cur))
            return cur, path, steps
        if in_half(k, cur, ft[0]):
            steps.append((cur, f"{cur} < {k} <= FT[1] = {ft[0]}", ft[0]))
            if path[-1] != ft[0]:
                path.append(ft[0])
            return ft[0], path, steps
        nxt = ft[0]
        for j in range(M - 1, -1, -1):      # finger terjauh yang belum melewati k
            if in_open(ft[j], cur, k):
                nxt = ft[j]
                break
        steps.append((cur, f"teruskan ke FT[{ft.index(nxt) + 1 if nxt in ft else '?'}] = {nxt}", nxt))
        path.append(nxt)
        cur = nxt
    raise RuntimeError("lookup tidak berhenti")


def main():
    ok = True

    def cek(nama, kondisi, info=""):
        nonlocal ok
        print(("LULUS  " if kondisi else "GAGAL  ") + nama + (f"  [{info}]" if info else ""))
        ok = ok and kondisi

    print("Node aktif:", NODES, "\n")
    for p in (1, 12, 20, 27):
        print(f"Finger table node {p}:")
        for i, start, s in finger_table(p, NODES):
            raw = p + 2 ** (i - 1)
            mod = f" mod 32 = {start}" if raw >= N else ""
            print(f"  i={i}  {p}+2^{i-1} = {raw}{mod}  -> succ = {s}")
        print()

    exp = {
        1: [4, 4, 7, 12, 19],
        12: [15, 15, 19, 20, 1],
        20: [27, 27, 27, 1, 4],
        27: [1, 1, 1, 4, 12],
    }
    for p, e in exp.items():
        cek(f"Finger table node {p} = {e}", [x[2] for x in finger_table(p, NODES)] == e)

    owner, path, steps = lookup(1, 26, NODES)
    print("\nLookup key 26 dari node 1:")
    for cur, alasan, nxt in steps:
        print(f"  di node {cur}: {alasan} -> {nxt}")
    print("  jalur:", " -> ".join(map(str, path)), "| penanggung jawab:", owner, "\n")
    cek("Lookup 26 dari node 1: jalur 1 -> 19 -> 20 -> 27", path == [1, 19, 20, 27])
    cek("Penanggung jawab key 26 = 27", owner == 27 == succ(26, NODES))

    # Uji menyeluruh: semua node awal x semua key
    # Catatan: jika key milik node awal sendiri (key di (predecessor, p]), node awal tidak mengenal predecessor-
    # nya,
    # sehingga lookup berkeliling ring dan kembali ke node awal. Itu perilaku Chord yang normal, bukan galat.
    salah_hasil, salah_jalur, kembali, maks = 0, 0, 0, 0
    for p in NODES:
        for k in range(N):
            o, pt, _ = lookup(p, k, NODES)
            if o != succ(k, NODES):
                salah_hasil += 1
            tanpa_ujung = pt[:-1] if (len(pt) > 1 and pt[-1] == p) else pt
            if any(x not in NODES for x in pt) or len(set(tanpa_ujung)) != len(tanpa_ujung):
                salah_jalur += 1
            if len(pt) > 1 and pt[-1] == p:
                kembali += 1
                if succ(k, NODES) != p:
                    salah_jalur += 1          # kembali ke node awal hanya sah bila node awal pemiliknya
            maks = max(maks, len(pt) - 1)
    cek(f"Semua {len(NODES) * N} kombinasi (node awal, key): hasil = succ(k)",
        salah_hasil == 0, f"salah={salah_hasil}")
    cek("Jalur hanya melewati node aktif tanpa pengulangan", salah_jalur == 0, f"salah={salah_jalur}")
    cek("Kembali ke node awal hanya terjadi bila node awal pemilik key", kembali == 24, f"kasus={kembali}")
    cek("Jumlah lompatan maksimum <= m = 5", maks <= M, f"maksimum={maks}")

    # Sensitivitas: jika node 19 ternyata bukan node aktif
    alt = [n for n in NODES if n != 19]
    print("\nJika node 19 BUKAN node aktif (hanya untuk perbandingan):")
    for p in (1, 12, 20, 27):
        print(f"  FT node {p}:", [x[2] for x in finger_table(p, alt)])
    o2, p2, _ = lookup(1, 26, alt)
    print("  lookup 26 dari node 1:", " -> ".join(map(str, p2)), "| penanggung jawab:", o2)

    print("\nHASIL AKHIR:", "SEMUA LULUS" if ok else "ADA YANG GAGAL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
