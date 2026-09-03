"""
Pos Nol — lapisan akses data
==============================
Semua query ke database jalur ada di sini, terpisah dari tampilan (app.py)
supaya logikanya bisa dites sendiri tanpa menjalankan Streamlit.
"""
import sqlite3
import math
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "posnol_gunung.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def daftar_gunung():
    """Return list of dict: {id, nama, puncak_resmi_m, jalur: [{id, nama_jalur, jarak_total_m}]}"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, nama, puncak_resmi_m FROM gunung ORDER BY nama")
    gunung_rows = cur.fetchall()

    hasil = []
    for g in gunung_rows:
        cur.execute(
            "SELECT id, nama_jalur, jarak_total_m FROM jalur WHERE gunung_id=? ORDER BY nama_jalur",
            (g["id"],),
        )
        jalur_rows = cur.fetchall()
        hasil.append({
            "id": g["id"],
            "nama": g["nama"],
            "puncak_resmi_m": g["puncak_resmi_m"],
            "jalur": [dict(j) for j in jalur_rows],
        })
    conn.close()
    return hasil


def ambil_pos(jalur_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT nama, lat, lon, elevasi_m, jarak_dari_basecamp_m, "
        "COALESCE(ada_air, 0) AS ada_air "
        "FROM pos WHERE jalur_id=? AND COALESCE(tampilkan, 1)=1 ORDER BY urutan",
        (jalur_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def ambil_profil(jalur_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT lat, lon, elevasi_m FROM profil_elevasi WHERE jalur_id=? ORDER BY urutan",
        (jalur_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def ambil_jalur_lengkap(jalur_id):
    """Info jalur + gunung induknya."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT j.id, j.nama_jalur, j.jarak_total_m, j.catatan_sumber, j.file_gpx_asal, "
        "g.nama AS nama_gunung, g.puncak_resmi_m "
        "FROM jalur j JOIN gunung g ON g.id = j.gunung_id WHERE j.id=?",
        (jalur_id,),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def log_pembersihan():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT pesan FROM log_pembersihan ORDER BY id")
    rows = [r["pesan"] for r in cur.fetchall()]
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Perhitungan turunan (segmen antar-pos, elevation gain per segmen, dsb)
# ---------------------------------------------------------------------------

def segmen_antar_pos(pos_list):
    """Dari list pos (sudah terurut jarak), hitung jarak & gain per segmen.
    Return list of dict: {dari, ke, jarak_segmen_m, gain_segmen_m, elevasi_ke_m}"""
    out = []
    for i in range(1, len(pos_list)):
        a, b = pos_list[i - 1], pos_list[i]
        out.append({
            "dari": a["nama"],
            "ke": b["nama"],
            "jarak_segmen_m": b["jarak_dari_basecamp_m"] - a["jarak_dari_basecamp_m"],
            "gain_segmen_m": b["elevasi_m"] - a["elevasi_m"],
            "elevasi_ke_m": b["elevasi_m"],
        })
    return out


def estimasi_waktu_naismith(jarak_m, gain_m, faktor_tim=1.0, faktor_beban=1.0):
    """Aturan Naismith: 1 jam per 5km datar + 1 jam per 600m naik.
    faktor_tim & faktor_beban mengalikan hasil dasar (>1 = lebih lambat).
    Return (jam_dasar, jam_disesuaikan)."""
    jam_datar = jarak_m / 5000.0
    jam_naik = max(gain_m, 0) / 600.0
    jam_dasar = jam_datar + jam_naik
    jam_disesuaikan = jam_dasar * faktor_tim * faktor_beban
    return jam_dasar, jam_disesuaikan


def format_jam(jam_desimal):
    total_menit = round(jam_desimal * 60)
    j, m = divmod(total_menit, 60)
    return f"{j}j {m:02d}m"


def elevation_gain_total(pos_list):
    """Total elevation gain (hanya kenaikan, mengabaikan penurunan) sepanjang
    urutan pos yang tercatat. Dipakai untuk kalkulasi per-etape (tab Titik air,
    Estimasi waktu) yang memang butuh granularitas per-pos, bukan per-trackpoint."""
    gain = 0.0
    for i in range(1, len(pos_list)):
        d = pos_list[i]["elevasi_m"] - pos_list[i - 1]["elevasi_m"]
        if d > 0:
            gain += d
    return gain


def elevasi_tertinggi_dari_profil(profil):
    """Elevasi tertinggi sesungguhnya dari seluruh trackpoint GPX mentah,
    bukan hanya dari pos yang sudah dikurasi manual. Pos yang diberi nama
    (mis. 'Puncak') adalah titik yang dipilih manusia untuk representasi,
    dan tidak selalu persis sama dengan titik GPS tertinggi yang terekam."""
    if not profil:
        return None
    return max(p["elevasi_m"] for p in profil)


def elevation_gain_dari_profil(profil):
    """Total elevation gain dari seluruh trackpoint GPX mentah. Lebih akurat
    daripada elevation_gain_total(pos_list) karena menangkap naik-turun kecil
    di antara pos yang tidak tertangkap kalau hanya pakai titik pos."""
    if not profil or len(profil) < 2:
        return 0.0
    gain = 0.0
    for i in range(1, len(profil)):
        d = profil[i]["elevasi_m"] - profil[i - 1]["elevasi_m"]
        if d > 0:
            gain += d
    return gain


def tambah_jarak_kumulatif_profil(profil):
    """Tambahkan jarak kumulatif (km) ke tiap titik profil, dihitung dari
    koordinat berurutan, supaya grafik elevasi punya sumbu-x yang bermakna
    (jarak dari basecamp) alih-alih nomor index mentah."""
    if not profil:
        return profil
    out = [{**profil[0], "jarak_km": 0.0}]
    kumulatif = 0.0
    for i in range(1, len(profil)):
        a, b = profil[i - 1], profil[i]
        d = haversine(a["lat"], a["lon"], b["lat"], b["lon"])
        kumulatif += d
        out.append({**b, "jarak_km": round(kumulatif / 1000, 3)})
    return out


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))
