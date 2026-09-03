"""
Pos Nol — perencana pendakian
================================
streamlit run app.py

Alur:
  Halaman 1 (landing): pilih gunung & jalur saja.
  Setelah "Mulai rencana" ditekan -> masuk ke halaman fitur (6 tab).
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import data
import pdf_export

st.set_page_config(page_title="Pos Nol", page_icon="⛰️", layout="wide")

# ---------------------------------------------------------------------------
# Tema terang eksplisit (menimpa dark mode bawaan sistem/browser)
# ---------------------------------------------------------------------------
# Tema dasar terang diatur lewat .streamlit/config.toml (lebih andal daripada
# CSS override, karena bekerja di level engine bukan kalah-menang spesifisitas
# CSS melawan dark mode sistem). CSS di sini hanya untuk tipografi & aksen.
# ---------------------------------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Inter, sans-serif !important;
}
h1, h2, h3, h4 {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em;
    color: #1B2A2C !important;
}
p, span, label, div, li {
    font-size: 15px;
    line-height: 1.6;
}
div[data-testid="stMetricValue"] {
    font-weight: 700 !important;
    font-size: 26px !important;
    color: #1B2A2C !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    color: #5A6660 !important;
    font-weight: 500 !important;
}
[data-testid="stForm"] {
    background-color: #FFFFFF;
    border: 1px solid #CDD5C9 !important;
    border-radius: 8px;
    padding: 20px;
}
.stTabs [data-baseweb="tab"] {
    font-size: 15px;
    font-weight: 500;
}
.catatan-sumber {
    background-color: #E7EBE3; border-left: 3px solid #6E7C7A;
    padding: 12px 16px; border-radius: 0 6px 6px 0; font-size: 13px;
    line-height: 1.55; color: #333; margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# State awal
# ---------------------------------------------------------------------------
if "halaman" not in st.session_state:
    st.session_state.halaman = "landing"
if "anggota" not in st.session_state:
    st.session_state.anggota = []
if "menu" not in st.session_state:
    st.session_state.menu = []
if "kategori_biaya" not in st.session_state:
    st.session_state.kategori_biaya = []
if "beban_individu" not in st.session_state:
    st.session_state.beban_individu = []

daftar_gunung = data.daftar_gunung()

if not daftar_gunung:
    st.error("Database jalur belum berisi data.")
    st.stop()


def format_mdpl(nilai):
    return f"{nilai:,.0f} mdpl".replace(",", ".")


# ===========================================================================
# HALAMAN 1 — LANDING: pilih gunung & jalur saja
# ===========================================================================
if st.session_state.halaman == "landing":
    st.markdown("<br>", unsafe_allow_html=True)
    col_kiri, col_tengah, col_kanan = st.columns([1, 2, 1])
    with col_tengah:
        st.markdown(
            "<h1 style='text-align:center; font-size:52px; margin-bottom:0;'>⛰️ Pos Nol</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align:center; color:#6E7C7A; font-size:16px; margin-top:4px;'>"
            "Rencana sebelum langkah pertama</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        nama_gunung_list = [g["nama"] for g in daftar_gunung]
        pilih_gunung_nama = st.selectbox("Pilih gunung", nama_gunung_list, index=None,
                                          placeholder="Cari gunung…")

        if pilih_gunung_nama:
            gunung_terpilih = next(g for g in daftar_gunung if g["nama"] == pilih_gunung_nama)
            nama_jalur_list = [j["nama_jalur"] for j in gunung_terpilih["jalur"]]
            pilih_jalur_nama = st.radio("Pilih jalur", nama_jalur_list)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Mulai rencana →", type="primary", use_container_width=True):
                jalur_terpilih = next(
                    j for j in gunung_terpilih["jalur"] if j["nama_jalur"] == pilih_jalur_nama
                )
                st.session_state.gunung_id = gunung_terpilih["id"]
                st.session_state.jalur_id = jalur_terpilih["id"]
                st.session_state.halaman = "fitur"
                st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.caption(
            f"{len(daftar_gunung)} gunung · "
            f"{sum(len(g['jalur']) for g in daftar_gunung)} jalur · basis data dari tracklog GPX"
        )
    st.stop()

# ===========================================================================
# HALAMAN 2 — FITUR (6 tab)
# ===========================================================================

info_jalur = data.ambil_jalur_lengkap(st.session_state.jalur_id)
pos_list = data.ambil_pos(st.session_state.jalur_id)
profil = data.ambil_profil(st.session_state.jalur_id)
segmen = data.segmen_antar_pos(pos_list)
gain_total = data.elevation_gain_total(pos_list)

with st.sidebar:
    if st.button("← Ganti gunung / jalur"):
        st.session_state.halaman = "landing"
        st.rerun()

    st.title("⛰️ Pos Nol")
    st.caption(f"{info_jalur['nama_gunung']} · {info_jalur['nama_jalur']}")
    st.markdown("---")

    st.subheader("Tim")
    jumlah_hari = st.number_input("Jumlah hari", min_value=1, max_value=10, value=3)
    st.caption("Jumlah orang & data anggota diisi di tab **Skrining tim**.")
    jumlah_orang = max(len(st.session_state.anggota), 1)
    st.metric("Jumlah anggota terdaftar", len(st.session_state.anggota))

st.title(f"{info_jalur['nama_gunung']} via {info_jalur['nama_jalur']}")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Puncak (mdpl)", f"{info_jalur['puncak_resmi_m']:,.0f}".replace(",", "."))
col2.metric("Titik tertinggi (mdpl)", f"{data.elevasi_tertinggi_dari_profil(profil):,.0f}".replace(",", "."))
col3.metric("Jarak jalur (km)", f"{info_jalur['jarak_total_m']/1000:.2f}")
col4.metric("Elevation gain (m)", f"{gain_total:.0f}")
col5.metric("Jumlah pos", f"{len(pos_list)}")

st.subheader("Profil elevasi")
profil_dgn_jarak = data.tambah_jarak_kumulatif_profil(profil)
df_profil = pd.DataFrame(profil_dgn_jarak)

fig = px.line(
    df_profil, x="jarak_km", y="elevasi_m",
    labels={"jarak_km": "Jarak dari basecamp (km)", "elevasi_m": "Ketinggian (mdpl)"},
)
fig.update_traces(line_color="#5F7F42", hovertemplate="Jarak: %{x:.2f} km<br>Ketinggian: %{y:.0f} mdpl<extra></extra>")
fig.update_layout(
    height=260, margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="#F1F3EE", paper_bgcolor="#F1F3EE",
    font_color="#1B2A2C",
    xaxis=dict(gridcolor="#CDD5C9"), yaxis=dict(gridcolor="#CDD5C9"),
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Grafik menunjukkan seberapa tinggi dan seberapa jauh jalur ini dari basecamp — "
           "arahkan kursor ke garis untuk melihat ketinggian pada jarak tertentu.")

st.markdown("---")

tab1, tab2, tab3, tab8, tab4, tab5, tab7, tab6 = st.tabs([
    "🩺 Skrining tim", "💧 Titik air", "🍚 Menu & logistik",
    "🎒 Ceklis barang", "💰 Tim & biaya", "⏱️ Estimasi waktu",
    "🚑 P3K darurat", "📄 Surat rencana",
])

# ===========================================================================
# TAB 1 — SKRINING TIM
# ===========================================================================
with tab1:
    st.header("Skrining kelayakan sebelum berangkat")
    st.caption(
        "Tiap anggota mengisi sekali. Jawaban diolah jadi tiga tingkat perhatian, bukan izin "
        "atau larangan — keputusan tetap di tangan tim dan dokter yang memeriksa."
    )

    with st.form("form_skrining", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nama = c1.text_input("Nama anggota")
        berat_badan = c2.number_input("Berat badan (kg)", min_value=30, max_value=150, value=60)
        tinggi_badan = c3.number_input("Tinggi badan (cm)", min_value=140, max_value=200, value=165)
        umur = c1.number_input("Umur", min_value=15, max_value=70, value=22)

        st.markdown("**Kondisi kesehatan** (centang yang berlaku)")
        c4, c5 = st.columns(2)
        asma = c4.checkbox("Asma / gangguan napas")
        jantung = c5.checkbox("Riwayat jantung / hipertensi tak terkontrol")

        c6, c7 = st.columns(2)
        belum_3000 = c6.checkbox("Belum pernah naik di atas 3.000 mdpl")
        cedera_sendi = c7.checkbox("Riwayat cedera lutut / sendi")

        c8, c9 = st.columns(2)
        diabetes = c8.checkbox("Diabetes")
        hamil = c9.checkbox("Sedang hamil")

        submit = st.form_submit_button("Tambah ke tim")
        if submit and nama:
            catatan = []
            tingkat = "hijau"
            if asma:
                catatan.append("Asma — udara dingin & kering di ketinggian adalah pemicu bronkospasme umum. "
                                "Bawa inhaler cadangan, simpan di sleeping bag agar tidak dingin.")
                tingkat = "merah"
            if jantung:
                catatan.append("Riwayat jantung/hipertensi tak terkontrol — perlu konsultasi dokter sebelum berangkat.")
                tingkat = "merah"
            if diabetes:
                catatan.append("Diabetes — pantau gula darah, bawa camilan cepat saji untuk hipoglikemia.")
                if tingkat != "merah":
                    tingkat = "kuning"
            if hamil:
                catatan.append("Sedang hamil — pendakian gunung umumnya tidak disarankan pada kondisi ini; konsultasi wajib.")
                tingkat = "merah"
            if belum_3000:
                catatan.append(
                    f"Belum pernah di atas {format_mdpl(3000)}. Puncak jalur ini "
                    f"{format_mdpl(info_jalur['puncak_resmi_m'])} — pantau gejala pusing/mual saat mendekati puncak."
                )
                if tingkat == "hijau":
                    tingkat = "kuning"
            if cedera_sendi:
                catatan.append("Riwayat cedera lutut/sendi — perjalanan turun membebani sendi lebih berat dari naik. "
                                "Trekking pole dan pengurangan beban carrier disarankan.")
                if tingkat == "hijau":
                    tingkat = "kuning"
            if not catatan:
                catatan.append("Tidak ada catatan yang perlu penyesuaian rencana.")

            st.session_state.anggota.append({
                "nama": nama, "berat_kg": berat_badan, "tinggi_cm": tinggi_badan,
                "umur": umur, "tingkat": tingkat, "catatan": catatan,
            })
            st.rerun()

    warna = {"merah": "🔴", "kuning": "🟡", "hijau": "🟢"}
    label = {"merah": "Perlu konsultasi dokter", "kuning": "Perhatikan di lapangan", "hijau": "Tidak ada catatan"}

    if st.session_state.anggota:
        st.markdown(f"**{len(st.session_state.anggota)} anggota terdaftar**")
        for i, a in enumerate(st.session_state.anggota):
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 0.4])
                c1.markdown(f"**{a['nama']}** · {a['berat_kg']} kg · {a['tinggi_cm']} cm · {a['umur']} th")
                c2.markdown(f"{warna[a['tingkat']]} {label[a['tingkat']]}")
                if c3.button("🗑️", key=f"hapus_anggota_{i}"):
                    st.session_state.anggota.pop(i)
                    st.rerun()
                for c in a["catatan"]:
                    st.caption(c)

        if st.button("Kosongkan daftar tim"):
            st.session_state.anggota = []
            st.rerun()
    else:
        st.info("Belum ada anggota ditambahkan.")

    st.markdown(
        "<div class='catatan-sumber'>Pertanyaan diadaptasi dari <b>PAR-Q+</b> "
        "(Physical Activity Readiness Questionnaire for Everyone) ditambah butir khusus "
        "ketinggian dan dingin. Warburton DER, dkk. Health &amp; Fitness Journal of Canada, 2011.</div>",
        unsafe_allow_html=True,
    )

# ===========================================================================
# TAB 2 — TITIK AIR
# ===========================================================================
with tab2:
    st.header("Rencana air per etape")

    pos_air = [p for p in pos_list if p.get("ada_air")]

    if pos_air:
        st.success(f"{len(pos_air)} titik sumber air terverifikasi pada jalur ini:")
        df_air = pd.DataFrame(pos_air)
        df_air["jarak_km"] = (df_air["jarak_dari_basecamp_m"] / 1000).round(2)
        df_air["elevasi_m"] = df_air["elevasi_m"].round(0)
        st.dataframe(df_air[["nama", "jarak_km", "elevasi_m"]].rename(columns={
            "nama": "Pos", "jarak_km": "Jarak dari basecamp (km)", "elevasi_m": "Elevasi (m)"
        }), hide_index=True, use_container_width=True)
    else:
        st.warning("Belum ada titik sumber air terverifikasi untuk jalur ini dalam database. "
                   "Konfirmasi ke basecamp/pengelola jalur sebelum berangkat.")

    st.markdown("---")
    st.subheader("Kalkulator kebutuhan air")
    st.caption("Ini menghitung **total kebutuhan air tubuh** untuk seluruh perjalanan — "
               "belum memperhitungkan pengurangan dari isi ulang di titik air di atas.")

    c1, c2 = st.columns(2)
    with c1:
        estimasi_jam_default = round(sum(s["jarak_segmen_m"] for s in segmen) / 3000 + gain_total / 500, 1)
        jam_jalan_total = st.number_input(
            "Total jam jalan (naik+turun)", min_value=1.0, max_value=60.0,
            value=estimasi_jam_default, step=0.5,
        )
    with c2:
        suhu_panas = st.checkbox("Cuaca panas / tanjakan berat (tambah 20%)")

    air_per_orang = jam_jalan_total * 0.6 + 1.5 * jumlah_hari
    if suhu_panas:
        air_per_orang *= 1.2
    air_total = air_per_orang * jumlah_orang

    c1, c2, c3 = st.columns(3)
    c1.metric("Air per orang", f"{air_per_orang:.1f} L")
    c2.metric(f"Total untuk {jumlah_orang} orang", f"{air_total:.1f} L")
    c3.metric("Setara beban", f"{air_total:.1f} kg")

    st.markdown(
        "<div class='catatan-sumber'><b>Kebutuhan = 0,6 L per jam jalan + 1,5 L/hari</b> "
        "untuk masak &amp; minum di camp, naik 20% pada cuaca panas. "
        "Sawka MN, dkk. ACSM Position Stand. Med Sci Sports Exerc. 2007;39(2):377–90.</div>",
        unsafe_allow_html=True,
    )

# ===========================================================================
# TAB 3 — MENU & LOGISTIK
# ===========================================================================
with tab3:
    st.header("Menu dan belanja logistik")
    st.caption("Susun menu per waktu makan. Belum ada menu tersimpan — mulai dengan menambah di bawah.")

    with st.form("form_menu", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 3])
        hari_menu = c1.number_input("Hari", min_value=1, max_value=jumlah_hari, value=1)
        waktu_menu = c2.selectbox("Waktu", ["Pagi", "Siang", "Summit", "Malam"])
        nama_menu = c3.text_input("Menu")

        c4, c5, c6 = st.columns([1, 1, 2])
        kkal_menu = c4.number_input("kkal/orang", min_value=0, value=0)
        berat_menu = c5.number_input("Berat g/orang", min_value=0, value=0)
        c6.markdown(
            "<div style='padding-top:28px; font-size:13px;'>"
            "Cek kalori bahan makanan di "
            "<a href='https://www.fatsecret.co.id/kalori-gizi' target='_blank'>FatSecret Indonesia</a>"
            " atau <a href='https://nilaigizi.com' target='_blank'>NilaiGizi.com</a> (basis TKPI Kemenkes)."
            "</div>", unsafe_allow_html=True,
        )
        if st.form_submit_button("Tambah menu") and nama_menu:
            st.session_state.menu.append({
                "hari": hari_menu, "waktu": waktu_menu, "menu": nama_menu,
                "kkal": kkal_menu, "berat_g": berat_menu,
            })

    if st.session_state.menu:
        st.markdown(f"**{len(st.session_state.menu)} menu tersimpan**")
        menu_terurut = sorted(enumerate(st.session_state.menu), key=lambda x: x[1]["hari"])
        for idx_asli, m in menu_terurut:
            c1, c2, c3, c4, c5 = st.columns([0.6, 1, 3, 1, 1])
            c1.write(f"H{m['hari']}")
            c2.write(m["waktu"])
            c3.write(m["menu"])
            c4.write(f"{m['kkal']} kkal")
            if c5.button("🗑️ Hapus", key=f"hapus_menu_{idx_asli}"):
                st.session_state.menu.pop(idx_asli)
                st.rerun()

        if st.button("Kosongkan semua menu"):
            st.session_state.menu = []
            st.rerun()

        df_menu = pd.DataFrame(st.session_state.menu)
        kkal_per_hari = df_menu.groupby("hari")["kkal"].sum().mean()
        berat_total_orang = df_menu["berat_g"].sum() / 1000

        st.markdown("---")
        st.subheader("Kecukupan energi")

        if st.session_state.anggota:
            berat_rerata = sum(a["berat_kg"] for a in st.session_state.anggota) / len(st.session_state.anggota)
            tinggi_rerata = sum(a["tinggi_cm"] for a in st.session_state.anggota) / len(st.session_state.anggota)
            umur_rerata = sum(a["umur"] for a in st.session_state.anggota) / len(st.session_state.anggota)
            st.caption(
                f"Dihitung dari rerata {len(st.session_state.anggota)} anggota terdaftar di tab Skrining tim: "
                f"berat {berat_rerata:.0f} kg · tinggi {tinggi_rerata:.0f} cm · umur {umur_rerata:.0f} tahun."
            )
        else:
            st.warning("Belum ada anggota di tab Skrining tim — memakai nilai asumsi sementara. "
                       "Tambahkan anggota dulu supaya perhitungan ini akurat.")
            berat_rerata, tinggi_rerata, umur_rerata = 62, 165, 22

        bmr = 10 * berat_rerata + 6.25 * tinggi_rerata - 5 * umur_rerata + 5
        kebutuhan = bmr * 1.9

        c1, c2, c3 = st.columns(3)
        c1.metric("Kebutuhan hitungan", f"{kebutuhan:.0f} kkal/hari")
        c2.metric("Menu tersusun (rerata)", f"{kkal_per_hari:.0f} kkal/hari")
        selisih = kkal_per_hari - kebutuhan
        c3.metric("Selisih", f"{selisih:+.0f} kkal")

        if selisih < -200:
            st.error(f"⚠️ **Belum tercukupi** — menu kurang {abs(selisih):.0f} kkal/hari dari kebutuhan hitungan.")
        elif selisih < 0:
            st.warning(f"**Mendekati cukup** — menu kurang {abs(selisih):.0f} kkal/hari, masih dalam toleransi wajar.")
        else:
            st.success(f"✅ **Tercukupi** — menu melebihi kebutuhan hitungan sebesar {selisih:.0f} kkal/hari.")

        st.metric("Total berat makanan per orang", f"{berat_total_orang:.2f} kg")
    else:
        st.info("Belum ada menu ditambahkan.")

    st.markdown(
        "<div class='catatan-sumber'><b>Kebutuhan = BMR (Mifflin–St Jeor) × 1,9.</b> "
        "Belum memperhitungkan biaya energi tambahan dari menggendong beban carrier secara "
        "terpisah (Pandolf-Givoni-Goldman, 1977) — direncanakan pada versi berikutnya.</div>",
        unsafe_allow_html=True,
    )

# ===========================================================================
# TAB 4 — TIM & BIAYA
# ===========================================================================
with tab4:
    st.header("Pembagian biaya dan barang")
    st.caption("Belum ada kategori biaya tersimpan — mulai dengan menambah di bawah.")

    with st.form("form_biaya", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        kat = c1.text_input("Nama kategori")
        n_orang = c2.number_input("Jumlah orang", min_value=1, max_value=30, value=1)
        per_orang = c3.number_input("Biaya per orang (Rp)", min_value=0, value=0, step=10000)
        if st.form_submit_button("Tambah kategori") and kat:
            st.session_state.kategori_biaya.append({"kategori": kat, "orang": n_orang, "per_orang": per_orang})

    if st.session_state.kategori_biaya:
        st.markdown(f"**{len(st.session_state.kategori_biaya)} kategori tersimpan**")
        for i, k in enumerate(st.session_state.kategori_biaya):
            subtotal = k["orang"] * k["per_orang"]
            c1, c2, c3, c4, c5 = st.columns([2, 1, 1.4, 1.4, 1])
            c1.write(k["kategori"])
            c2.write(f"{k['orang']} orang")
            c3.write(f"Rp {k['per_orang']:,.0f}".replace(",", "."))
            c4.write(f"Rp {subtotal:,.0f}".replace(",", "."))
            if c5.button("🗑️ Hapus", key=f"hapus_biaya_{i}"):
                st.session_state.kategori_biaya.pop(i)
                st.rerun()

        if st.button("Kosongkan semua kategori biaya"):
            st.session_state.kategori_biaya = []
            st.rerun()

        df_biaya = pd.DataFrame(st.session_state.kategori_biaya)
        df_biaya["total"] = df_biaya["orang"] * df_biaya["per_orang"]

        c1, c2 = st.columns(2)
        c1.metric("Total orang tercatat", f"{df_biaya['orang'].sum()}")
        c2.metric("Total biaya", f"Rp {df_biaya['total'].sum():,.0f}".replace(",", "."))

        if df_biaya["orang"].sum() != jumlah_orang and st.session_state.anggota:
            st.warning(f"Jumlah orang di kategori biaya ({df_biaya['orang'].sum()}) tidak sama dengan "
                       f"jumlah anggota terdaftar ({jumlah_orang}).")
    else:
        st.info("Belum ada kategori biaya ditambahkan.")

    st.markdown("---")
    st.subheader("Beban carrier terhadap berat badan")
    st.caption("Beban di atas 30% berat badan meningkatkan risiko cedera pada pendaki rekreasional. "
               "Atur berat carrier tiap anggota yang sudah terdaftar di tab Skrining tim.")

    if st.session_state.anggota:
        if "beban_carrier" not in st.session_state:
            st.session_state.beban_carrier = {}

        total_beban_tim = 0.0
        for a in st.session_state.anggota:
            nama_a = a["nama"]
            if nama_a not in st.session_state.beban_carrier:
                st.session_state.beban_carrier[nama_a] = 0

            c1, c2, c3 = st.columns([2, 1.6, 2])
            c1.write(f"**{nama_a}** · {a['berat_kg']} kg")
            beban_baru = c2.number_input(
                "Carrier (kg)", min_value=0, max_value=40,
                value=st.session_state.beban_carrier[nama_a],
                key=f"beban_input_{nama_a}", label_visibility="collapsed",
            )
            st.session_state.beban_carrier[nama_a] = beban_baru
            total_beban_tim += beban_baru

            persen = beban_baru / a["berat_kg"] * 100 if a["berat_kg"] else 0
            if persen >= 30:
                tanda, ket = "🔴", "Berat — risiko cedera meningkat"
            elif persen >= 25:
                tanda, ket = "🟡", "Mendekati batas aman"
            elif beban_baru > 0:
                tanda, ket = "🟢", "Dalam batas aman"
            else:
                tanda, ket = "⚪", "Belum diisi"
            c3.markdown(f"{tanda} **{persen:.0f}%** — {ket}")

        st.caption("🟢 di bawah 25% berat badan · 🟡 25–29% mendekati batas · 🔴 30% ke atas dianggap berat")

        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.metric("Total beban carrier tim", f"{total_beban_tim:.0f} kg")
        c2.metric("Rerata per orang", f"{total_beban_tim/len(st.session_state.anggota):.1f} kg")

        berisiko = [a["nama"] for a in st.session_state.anggota
                    if a["berat_kg"] and st.session_state.beban_carrier.get(a["nama"], 0) / a["berat_kg"] >= 0.30]
        if berisiko:
            st.warning(f"⚠️ **{', '.join(berisiko)}** membawa beban ≥30% berat badan. "
                       "Pertimbangkan redistribusi ke anggota lain atau kurangi barang bawaan.")
    else:
        st.info("Belum ada anggota terdaftar. Tambahkan anggota di tab Skrining tim terlebih dahulu "
                "untuk mengisi beban carrier masing-masing.")

    st.markdown(
        "<div class='catatan-sumber'>Knapik JJ, Reynolds KL, Harman E. Soldier load carriage. "
        "Mil Med. 2004;169(1):45–56.</div>",
        unsafe_allow_html=True,
    )

# ===========================================================================
# TAB 5 — ESTIMASI WAKTU
# ===========================================================================
with tab5:
    st.header("Estimasi waktu tempuh")
    st.caption("Perkiraan rentang waktu dari basecamp sampai puncak.")

    c1, c2 = st.columns(2)
    with c1:
        gaya_jalan = st.radio(
            "Gaya jalan tim", ["Santai", "Sedang", "Cepat"], index=1, horizontal=True,
            help="Santai: sering berhenti foto/istirahat, cocok pemula. Sedang: ritme "
                 "stabil dengan istirahat singkat tiap 1 jam. Cepat: jarang berhenti, "
                 "tim berpengalaman dan fisik terlatih.",
        )
    with c2:
        gaya_beban = st.radio(
            "Beban bawaan", ["Ringan (< 12 kg)", "Sedang (12–18 kg)", "Berat (> 18 kg)"],
            index=1,
            help="Berat carrier rata-rata tim, di luar berat badan. Cek beban masing-masing "
                 "anggota di tab Tim & biaya.",
        )

    faktor_tim_map = {"Santai": 1.6, "Sedang": 1.3, "Cepat": 1.05}
    faktor_beban_map = {"Ringan (< 12 kg)": 1.0, "Sedang (12–18 kg)": 1.15, "Berat (> 18 kg)": 1.3}

    faktor_tim = faktor_tim_map[gaya_jalan]
    faktor_beban = faktor_beban_map[gaya_beban]

    jam_disesuaikan_total = 0.0
    for s in segmen:
        _, ja = data.estimasi_waktu_naismith(s["jarak_segmen_m"], max(s["gain_segmen_m"], 0), faktor_tim, faktor_beban)
        jam_disesuaikan_total += ja

    rentang_bawah = jam_disesuaikan_total * 0.9
    rentang_atas = jam_disesuaikan_total * 1.15

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align:center; padding:24px; background:#E7EBE3; border-radius:8px;'>"
        f"<div style='font-size:14px; color:#6E7C7A;'>Perkiraan waktu naik, basecamp → puncak</div>"
        f"<div style='font-size:40px; font-weight:600; color:#1B2A2C; margin-top:4px;'>"
        f"{data.format_jam(rentang_bawah)} – {data.format_jam(rentang_atas)}</div>"
        f"<div style='font-size:13px; color:#6E7C7A; margin-top:6px;'>"
        f"Gaya jalan {gaya_jalan.lower()} · beban {gaya_beban.lower()}</div>"
        f"</div>", unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Lihat rincian per segmen"):
        baris_waktu = []
        for s in segmen:
            _, ja = data.estimasi_waktu_naismith(s["jarak_segmen_m"], max(s["gain_segmen_m"], 0), faktor_tim, faktor_beban)
            baris_waktu.append({
                "Segmen": f"{s['dari']} → {s['ke']}",
                "Jarak (km)": round(s["jarak_segmen_m"] / 1000, 2),
                "Naik (m)": round(max(s["gain_segmen_m"], 0)),
                "Estimasi waktu": data.format_jam(ja),
            })
        st.dataframe(pd.DataFrame(baris_waktu), hide_index=True, use_container_width=True)

    with st.expander("Bagaimana angka ini dihitung?"):
        st.markdown(f"""
**Langkah 1 — waktu dasar per segmen (aturan Naismith, 1892):**
Setiap segmen antar-pos dihitung: 1 jam per 5 km jarak datar, ditambah 1 jam per 600 m
kenaikan elevasi. Ini kaidah lama yang dipakai luas di dunia pendakian, disusun untuk
**pendaki tunggal tanpa beban** — bukan tim dengan carrier.

**Langkah 2 — faktor penyesuaian gaya jalan & beban:**
Karena Naismith tidak memodelkan kecepatan tim atau berat bawaan, angka dasar itu dikalikan
dua faktor:

| Gaya jalan | Faktor | | Beban | Faktor |
|---|---|---|---|---|
| Santai | ×1,60 | | Ringan (< 12 kg) | ×1,00 |
| Sedang | ×1,30 | | Sedang (12–18 kg) | ×1,15 |
| Cepat | ×1,05 | | Berat (> 18 kg) | ×1,30 |

**Faktor-faktor ini adalah estimasi rekayasa berdasar pengalaman umum pendakian, bukan
angka hasil penelitian terkalibrasi.** Tidak ada studi yang secara spesifik mengukur
"gaya jalan santai/sedang/cepat" atau membuktikan angka 1,15/1,30 untuk kategori beban ini.
Faktor beban disusun mengacu pada prinsip umum di literatur soal beban gendongan
(Knapik dkk. 2004, lihat tab Tim & biaya) bahwa performa menurun seiring beban naik,
tapi angka pengali persisnya adalah pendekatan kami, bukan kutipan langsung dari studi
tersebut.

**Langkah 3 — kenapa rentangnya lebar (±dari titik tengah):**
Estimasi titik-tengah dikalikan 0,90 (batas bawah) dan 1,15 (batas atas). Rentang ini
sengaja **asimetris dan lebar** karena kondisi nyata di lapangan — cuaca, kondisi fisik
hari itu, keramaian jalur, istirahat tak terduga — bisa mengubah waktu tempuh signifikan,
dan kami tidak ingin memberi angka tunggal yang terasa presisi padahal tidak.
Anggap angka ini sebagai **kerangka perencanaan awal**, bukan jadwal pasti — selalu
sisakan waktu ekstra dan tanyakan estimasi lapangan terkini ke basecamp.
""")

    st.markdown(
        "<div class='catatan-sumber'>Dasar aturan dasar: Naismith W. Scottish Mountaineering "
        "Club Journal, 1892. Faktor penyesuaian tim &amp; beban: estimasi internal, belum "
        "divalidasi dengan data lapangan.</div>",
        unsafe_allow_html=True,
    )

# ===========================================================================
# TAB 6 — SURAT RENCANA
# ===========================================================================
with tab6:
    st.header("Surat rencana perjalanan")
    st.caption("Diambil otomatis dari seluruh tab di atas. Isi kolom di bawah, lalu unduh PDF lengkap.")

    c1, c2 = st.columns(2)
    ketua = c1.text_input("Ketua tim", key="srp_ketua")
    kontak_ketua = c1.text_input("Kontak ketua (HP)", key="srp_kontak")
    navigator = c1.text_input("Navigator", key="srp_navigator")
    pj_medis = c2.text_input("Penanggung jawab medis", key="srp_pj_medis")
    sweeper = c2.text_input("Sweeper", key="srp_sweeper")
    batas_lapor = c2.text_input("Batas waktu lapor (contoh: hari ke-3 pukul 18.00)", key="srp_batas_lapor")

    st.markdown("---")
    st.subheader("Ringkasan yang akan tercetak")

    # Hitung estimasi waktu memakai faktor default (Sedang/Sedang) untuk ringkasan surat,
    # agar tidak bergantung pada state slider yang mungkin belum dibuka di tab 5.
    jam_ringkasan = sum(
        data.estimasi_waktu_naismith(s["jarak_segmen_m"], max(s["gain_segmen_m"], 0), 1.3, 1.15)[1]
        for s in segmen
    )
    estimasi_teks = f"{data.format_jam(jam_ringkasan*0.9)} – {data.format_jam(jam_ringkasan*1.15)} (asumsi gaya sedang)"

    pos_air_srp = [p for p in pos_list if p.get("ada_air")]
    pos_air_untuk_pdf = [
        {"nama": p["nama"], "jarak_km": p["jarak_dari_basecamp_m"] / 1000} for p in pos_air_srp
    ]

    # Kumpulkan item ceklis yang belum dicentang, dengan label yang manusiawi
    label_ceklis = {
        "ceklis_tenda": "Tenda", "ceklis_flysheet": "Flysheet/terpal", "ceklis_matras_klp": "Matras kelompok",
        "ceklis_kompor": "Kompor+korek", "ceklis_gas": "Gas/bahan bakar", "ceklis_nesting": "Nesting",
        "ceklis_peta": "Peta/GPS", "ceklis_tali": "Tali webbing", "ceklis_trashbag": "Trashbag",
        "ceklis_p3k_utama": "P3K kelompok", "ceklis_emergency_blanket": "Emergency blanket",
        "ceklis_powerbank_klp": "Powerbank kelompok",
        "ceklis_p3k_nyeri": "Obat nyeri/demam", "ceklis_p3k_oralit": "Oralit", "ceklis_p3k_perban": "Perban/plester",
        "ceklis_p3k_antiseptik": "Antiseptik", "ceklis_p3k_mual": "Obat mual/diare", "ceklis_p3k_gunting": "Gunting/peniti",
        "ceklis_p3k_pribadi_khusus": "Obat pribadi khusus", "ceklis_p3k_oksigen": "Oksigen kecil",
        "ceklis_pribadi_jaket": "Jaket tebal", "ceklis_pribadi_baju_ganti": "Baju ganti",
        "ceklis_pribadi_sarung_tangan": "Sarung tangan", "ceklis_pribadi_kaos_kaki": "Kaos kaki cadangan",
        "ceklis_pribadi_buff": "Buff/masker leher", "ceklis_pribadi_ponco": "Jas hujan/ponco",
        "ceklis_pribadi_sleeping_bag": "Sleeping bag", "ceklis_pribadi_matras": "Matras pribadi",
        "ceklis_pribadi_carrier": "Carrier+raincover", "ceklis_pribadi_headlamp": "Headlamp",
        "ceklis_pribadi_botol_air": "Botol air", "ceklis_pribadi_trekking_pole": "Trekking pole",
        "ceklis_pribadi_obat": "Obat pribadi", "ceklis_pribadi_alat_makan": "Alat makan",
        "ceklis_pribadi_sunscreen": "Sunscreen/kacamata", "ceklis_pribadi_tisu": "Tisu/sabun",
        "ceklis_pribadi_kantong_plastik": "Kantong plastik", "ceklis_pribadi_kartu": "Kartu identitas/medis",
    }
    ceklis_belum = [label for key, label in label_ceklis.items() if not st.session_state.get(key, False)]

    with st.container(border=True):
        st.markdown("### Surat Rencana Perjalanan")
        st.write(f"**{info_jalur['nama_gunung']} via {info_jalur['nama_jalur']}** · "
                 f"{jumlah_hari} hari · {jumlah_orang} orang")
        st.write(f"- Ketua tim: {ketua or '_(belum diisi)_'} · {kontak_ketua or '_(belum diisi)_'}")
        st.write(f"- Penanggung jawab medis: {pj_medis or '_(belum diisi)_'}")
        st.write(f"- Navigator: {navigator or '_(belum diisi)_'} · Sweeper: {sweeper or '_(belum diisi)_'}")
        st.write(f"- Jarak jalur: {info_jalur['jarak_total_m']/1000:.2f} km, "
                 f"elevation gain {gain_total:.0f} m")
        st.write(f"- Estimasi waktu naik: {estimasi_teks}")
        st.write(f"- Batas waktu lapor: {batas_lapor or '_(belum diisi)_'}")
        st.write(f"- Titik air terverifikasi: {len(pos_air_srp)} pos")
        st.write(f"- Menu tersusun: {len(st.session_state.menu)} entri · "
                 f"Kategori biaya: {len(st.session_state.kategori_biaya)}")
        st.write(f"- Ceklis barang: {len(label_ceklis) - len(ceklis_belum)} dari {len(label_ceklis)} sudah dicentang")

        if st.session_state.anggota:
            merah = [a["nama"] for a in st.session_state.anggota if a["tingkat"] == "merah"]
            if merah:
                st.write(f"- **Catatan medis:** {', '.join(merah)} memerlukan perhatian khusus.")

    st.markdown("---")

    konteks_pdf = {
        "nama_gunung": info_jalur["nama_gunung"], "nama_jalur": info_jalur["nama_jalur"],
        "jumlah_hari": jumlah_hari, "jumlah_orang": jumlah_orang,
        "puncak_mdpl": info_jalur["puncak_resmi_m"],
        "jarak_km": info_jalur["jarak_total_m"] / 1000, "elevation_gain_m": gain_total,
        "estimasi_waktu_teks": estimasi_teks, "gaya_jalan": "Sedang", "gaya_beban": "Sedang (12–18 kg)",
        "ketua": ketua, "kontak_ketua": kontak_ketua, "pj_medis": pj_medis,
        "navigator": navigator, "sweeper": sweeper, "batas_lapor": batas_lapor,
        "anggota": st.session_state.anggota,
        "menu": st.session_state.menu,
        "kategori_biaya": st.session_state.kategori_biaya,
        "beban_carrier": st.session_state.get("beban_carrier", {}),
        "pos_air": pos_air_untuk_pdf,
        "ceklis_belum": ceklis_belum,
    }

    try:
        pdf_bytes = pdf_export.buat_pdf_surat_rencana(konteks_pdf)
        nama_file = f"Surat_Rencana_{info_jalur['nama_gunung']}_{info_jalur['nama_jalur']}.pdf".replace(" ", "_")
        st.download_button(
            "📄 Unduh Surat Rencana Perjalanan (PDF)",
            data=pdf_bytes, file_name=nama_file, mime="application/pdf",
            type="primary", use_container_width=True,
        )
    except Exception as e:
        st.error(f"Gagal membuat PDF: {e}")

# ===========================================================================
# TAB 7 — P3K DARURAT
# ===========================================================================
with tab7:
    st.header("Panduan pertolongan pertama")
    st.warning(
        "⚠️ Ini panduan awal, **bukan pengganti pelatihan P3K/wilderness first aid** dan "
        "bukan pengganti evakuasi medis. Pada kondisi serius, prioritaskan evakuasi turun "
        "dan hubungi Basarnas (115) atau layanan darurat setempat secepatnya."
    )

    kondisi = st.selectbox(
        "Pilih kondisi",
        ["Hipotermia", "Acute Mountain Sickness (AMS)", "Serangan jantung / nyeri dada",
         "Reaksi alergi berat (anafilaksis)", "Keseleo / cedera sendi", "Dehidrasi berat"],
    )

    if kondisi == "Hipotermia":
        st.subheader("🥶 Hipotermia")
        st.caption("Penyebab kematian pendaki paling umum di gunung Indonesia — jauh lebih "
                   "sering daripada AMS, karena suhu dingin + basah + angin di ketinggian sedang.")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Tanda ringan–sedang**")
            st.markdown("""
- Menggigil hebat
- Bicara tidak jelas, koordinasi menurun
- Kebingungan ringan, keputusan buruk
- Kulit pucat, dingin
""")
        with c2:
            st.markdown("**Tanda berat (bahaya)**")
            st.markdown("""
- Menggigil **berhenti** (tubuh kehabisan energi — tanda memburuk, bukan membaik)
- Kesadaran menurun, bicara mengigau
- Nadi & napas melambat
- Kaku otot, gerakan sangat lambat
""")

        st.markdown("**Penanganan segera**")
        st.markdown("""
1. **Pindahkan** dari angin/basah — cari perlindungan (tenda, flysheet) sesegera mungkin.
2. **Ganti pakaian basah** dengan yang kering. Bungkus dengan sleeping bag/emergency blanket.
3. **Hangatkan bertahap** — dekap tubuh (skin-to-skin jika perlu), beri minuman hangat manis
   **hanya jika sadar penuh dan bisa menelan**. Jangan beri alkohol.
4. **Jangan gosok/pijat anggota badan** yang dingin — bisa memicu aritmia jantung pada kasus berat.
5. Pada hipotermia berat: **tangani selembut mungkin**, hindari gerakan mendadak, dan evakuasi
   turun sesegera mungkin sambil terus menghangatkan.
""")
        st.markdown(
            "<div class='catatan-sumber'>Wilderness Medical Society Clinical Practice "
            "Guidelines for the Out-of-Hospital Evaluation and Treatment of Accidental "
            "Hypothermia.</div>", unsafe_allow_html=True,
        )

    elif kondisi == "Acute Mountain Sickness (AMS)":
        st.subheader("🏔️ Acute Mountain Sickness (AMS)")
        st.caption("Umumnya mulai muncul di atas 2.500 mdpl. Risiko HACE/HAPE (edema otak/paru "
                   "akibat ketinggian) jarang terjadi di bawah 3.500–4.000 mdpl, tapi tetap waspada.")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Gejala AMS ringan**")
            st.markdown("""
- Sakit kepala
- Mual, pusing
- Lelah tidak wajar
- Sulit tidur
""")
        with c2:
            st.markdown("**Tanda bahaya (HACE/HAPE)**")
            st.markdown("""
- Bingung, jalan sempoyongan (tidak bisa jalan garis lurus)
- Sesak napas **saat istirahat** (bukan hanya saat aktivitas)
- Batuk dengan dahak berbusa/kemerahan
- Kesadaran menurun
""")

        st.markdown("**Penanganan**")
        st.markdown("""
1. Gejala ringan: **berhenti naik**, istirahat di ketinggian yang sama sampai membaik. Jangan naik lebih tinggi.
2. Minum cukup, hindari alkohol dan obat tidur.
3. Bila tidak membaik atau memburuk dalam beberapa jam: **turun ke ketinggian lebih rendah** — ini penanganan paling efektif.
4. Tanda bahaya (HACE/HAPE): **turun segera**, ini kondisi darurat yang bisa fatal dalam hitungan jam.
""")
        st.markdown(
            "<div class='catatan-sumber'>Wilderness Medical Society Clinical Practice "
            "Guidelines for the Prevention and Treatment of Acute Altitude Illness.</div>",
            unsafe_allow_html=True,
        )

    elif kondisi == "Serangan jantung / nyeri dada":
        st.subheader("❤️ Serangan jantung / nyeri dada")

        st.markdown("**Tanda yang perlu diwaspadai**")
        st.markdown("""
- Nyeri/tertekan di dada, bisa menjalar ke lengan kiri, rahang, atau punggung
- Sesak napas, keringat dingin
- Mual, pusing
- Pada beberapa orang (terutama wanita/diabetes): gejala bisa lebih samar — cuma lelah ekstrem atau nyeri ulu hati
""")

        st.error("Ini kondisi darurat — waktu sangat menentukan.")
        st.markdown("**Penanganan segera**")
        st.markdown("""
1. **Hentikan aktivitas**, dudukkan/baringkan dalam posisi senyaman mungkin (biasanya setengah duduk).
2. Longgarkan pakaian ketat.
3. Bila orang tersebut punya obat jantung pribadi (contoh: nitrat), bantu sesuai instruksi dokter yang sudah diketahui sebelumnya.
4. **Segera evakuasi turun dan hubungi bantuan medis** — di gunung, ini berarti mengirim tim tercepat untuk mencari sinyal/pertolongan sambil satu orang tetap mendampingi.
5. Jika tidak sadar dan tidak bernapas normal: mulai RJP (kompresi dada) bila ada yang terlatih.
""")
        st.markdown(
            "<div class='catatan-sumber'>American Heart Association — Guidelines for CPR "
            "and Emergency Cardiovascular Care.</div>", unsafe_allow_html=True,
        )

    elif kondisi == "Reaksi alergi berat (anafilaksis)":
        st.subheader("⚠️ Reaksi alergi berat (anafilaksis)")

        st.markdown("**Tanda**")
        st.markdown("""
- Bengkak di wajah/bibir/lidah/tenggorokan
- Sesak napas, suara mengi/serak
- Ruam/gatal di seluruh tubuh, muncul cepat
- Pusing, tekanan darah turun drastis, bisa pingsan
- Biasanya muncul dalam menit setelah terpapar (sengatan serangga, makanan, obat tertentu)
""")

        st.error("Anafilaksis bisa mematikan dalam hitungan menit — jangan tunggu dan lihat dulu.")
        st.markdown("**Penanganan segera**")
        st.markdown("""
1. Jika korban membawa **auto-injector epinefrin (EpiPen)** pribadi, gunakan segera sesuai instruksi pada alat.
2. Baringkan dengan kaki diangkat sedikit lebih tinggi (kecuali sesak napas berat — posisi duduk lebih nyaman untuk pernapasan).
3. Longgarkan pakaian, awasi jalan napas terus-menerus.
4. Evakuasi turun secepatnya walau gejala membaik — reaksi bisa kambuh kembali dalam beberapa jam.
5. Jika henti napas/jantung: mulai RJP bila ada yang terlatih.
""")
        st.markdown(
            "<div class='catatan-sumber'>World Allergy Organization Anaphylaxis Guidelines.</div>",
            unsafe_allow_html=True,
        )

    elif kondisi == "Keseleo / cedera sendi":
        st.subheader("🦵 Keseleo / cedera sendi")

        st.markdown("**Penanganan (RICE, dimodifikasi untuk kondisi lapangan)**")
        st.markdown("""
1. **Rest** — hentikan aktivitas pada bagian yang cedera.
2. **Ice** — kompres dingin bila tersedia (air sungai dingin, bukan es batu di gunung); 15-20 menit,
   beri jeda, ulangi. Jangan tempel langsung tanpa alas ke kulit.
3. **Compression** — balut dengan perban elastis, tidak terlalu ketat (jari tetap harus bisa gerak & tidak kesemutan).
4. **Elevation** — posisikan bagian cedera lebih tinggi dari jantung bila memungkinkan.

**Kapan harus turun/evakuasi:**
- Tidak bisa menumpu berat badan sama sekali
- Bengkak sangat cepat & besar
- Bentuk sendi tampak berubah/tidak normal (dugaan dislokasi/patah)
""")

    elif kondisi == "Dehidrasi berat":
        st.subheader("💧 Dehidrasi berat")

        st.markdown("**Tanda**")
        st.markdown("""
- Sangat haus, mulut & bibir kering
- Urine sangat sedikit dan pekat/gelap
- Pusing, lemas, sakit kepala
- Pada kasus berat: kebingungan, jantung berdebar cepat, pingsan
""")
        st.markdown("**Penanganan**")
        st.markdown("""
1. Berhenti, istirahat di tempat teduh/terlindung.
2. Minum sedikit-sedikit tapi sering (bukan langsung banyak sekaligus) — air putih atau oralit bila ada.
3. Jika tersedia, tambahkan sedikit garam/oralit untuk mengganti elektrolit yang hilang lewat keringat.
4. Jika tidak membaik dalam 30-60 menit atau kondisi memburuk (bingung, tidak bisa minum sendiri): evakuasi turun.
""")

# ===========================================================================
# TAB 8 — CEKLIS BARANG
# ===========================================================================
with tab8:
    st.header("Ceklis barang bawaan")
    st.caption("Centang saat sudah dikemas — status tersimpan selama sesi ini berjalan.")

    sub_kelompok, sub_pribadi = st.tabs(["🏕️ Kelompok", "🎒 Pribadi"])

    with sub_kelompok:
        st.markdown("**Tempat tinggal & masak**")
        c1, c2 = st.columns(2)
        c1.checkbox("Tenda (cek jumlah pasak & frame lengkap)", key="ceklis_tenda")
        c1.checkbox("Flysheet / terpal", key="ceklis_flysheet")
        c1.checkbox("Matras kelompok cadangan", key="ceklis_matras_klp")
        c2.checkbox("Kompor + korek/pematik cadangan", key="ceklis_kompor")
        c2.checkbox("Gas / bahan bakar (lebih dari perkiraan)", key="ceklis_gas")
        c2.checkbox("Nesting / peralatan masak", key="ceklis_nesting")

        st.markdown("**Navigasi & keamanan tim**")
        c3, c4 = st.columns(2)
        c3.checkbox("Peta jalur / GPS cadangan", key="ceklis_peta")
        c3.checkbox("Tali webbing / tali serbaguna", key="ceklis_tali")
        c3.checkbox("Trashbag (sampah wajib dibawa turun)", key="ceklis_trashbag")
        c4.checkbox("P3K kelompok (lihat rincian di bawah)", key="ceklis_p3k_utama")
        c4.checkbox("Emergency blanket cadangan (minimal 1 per 2 orang)", key="ceklis_emergency_blanket")
        c4.checkbox("Powerbank / baterai cadangan kelompok", key="ceklis_powerbank_klp")

        st.markdown("**Isi kotak P3K kelompok (minimum disarankan)**")
        c5, c6 = st.columns(2)
        c5.checkbox("Obat pereda nyeri & demam", key="ceklis_p3k_nyeri")
        c5.checkbox("Oralit / garam elektrolit", key="ceklis_p3k_oralit")
        c5.checkbox("Perban elastis & plester luka", key="ceklis_p3k_perban")
        c5.checkbox("Antiseptik (povidon iodine/alkohol swab)", key="ceklis_p3k_antiseptik")
        c6.checkbox("Obat anti-mual & anti-diare", key="ceklis_p3k_mual")
        c6.checkbox("Gunting kecil & peniti", key="ceklis_p3k_gunting")
        c6.checkbox("Obat pribadi anggota berkebutuhan khusus (inhaler, dsb — lihat tab Skrining tim)", key="ceklis_p3k_pribadi_khusus")
        c6.checkbox("Tabung oksigen kecil (opsional, disarankan di atas 3.000 mdpl)", key="ceklis_p3k_oksigen")

        kelompok_keys = [k for k in st.session_state.keys() if k.startswith("ceklis_") and not k.startswith("ceklis_pribadi_")]

    with sub_pribadi:
        st.markdown("**Pakaian**")
        c1, c2 = st.columns(2)
        c1.checkbox("Jaket tebal / windproof", key="ceklis_pribadi_jaket")
        c1.checkbox("Baju & celana ganti (sesuai jumlah hari)", key="ceklis_pribadi_baju_ganti")
        c1.checkbox("Sarung tangan", key="ceklis_pribadi_sarung_tangan")
        c2.checkbox("Kaos kaki cadangan (minimal 2 pasang)", key="ceklis_pribadi_kaos_kaki")
        c2.checkbox("Buff / masker leher", key="ceklis_pribadi_buff")
        c2.checkbox("Jas hujan / ponco", key="ceklis_pribadi_ponco")

        st.markdown("**Tidur & bawaan**")
        c3, c4 = st.columns(2)
        c3.checkbox("Sleeping bag sesuai suhu ketinggian", key="ceklis_pribadi_sleeping_bag")
        c3.checkbox("Matras pribadi", key="ceklis_pribadi_matras")
        c3.checkbox("Carrier + rain cover", key="ceklis_pribadi_carrier")
        c4.checkbox("Headlamp/senter + baterai cadangan", key="ceklis_pribadi_headlamp")
        c4.checkbox("Botol air / hydration bladder", key="ceklis_pribadi_botol_air")
        c4.checkbox("Trekking pole (sangat disarankan untuk turun)", key="ceklis_pribadi_trekking_pole")

        st.markdown("**Pribadi lainnya**")
        c5, c6 = st.columns(2)
        c5.checkbox("Obat pribadi (sesuai kondisi di tab Skrining tim)", key="ceklis_pribadi_obat")
        c5.checkbox("Alat makan pribadi (sendok, piring, gelas)", key="ceklis_pribadi_alat_makan")
        c5.checkbox("Sunscreen & kacamata hitam", key="ceklis_pribadi_sunscreen")
        c6.checkbox("Tisu basah/kering & sabun secukupnya", key="ceklis_pribadi_tisu")
        c6.checkbox("Kantong plastik untuk sampah & baju kotor pribadi", key="ceklis_pribadi_kantong_plastik")
        c6.checkbox("Kartu identitas & kartu medis pribadi", key="ceklis_pribadi_kartu")

    # Progress ringkas dihitung dari semua key berawalan "ceklis_"
    semua_key_ceklis = [k for k in st.session_state.keys() if k.startswith("ceklis_")]
    if semua_key_ceklis:
        total = len(semua_key_ceklis)
        sudah = sum(1 for k in semua_key_ceklis if st.session_state[k])
        st.markdown("---")
        st.progress(sudah / total, text=f"{sudah} dari {total} barang sudah dicentang")

    st.markdown(
        "<div class='catatan-sumber'>Daftar disusun dari SOP umum pendakian gunung Indonesia "
        "dan pedoman keselamatan dasar. Sesuaikan dengan karakteristik jalur spesifik "
        "(ketersediaan air, suhu malam, aturan pengelola setempat).</div>",
        unsafe_allow_html=True,
    )
