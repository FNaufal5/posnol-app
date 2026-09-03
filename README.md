# ⛰️ Pos Nol

**Rencana sebelum langkah pertama.**

Pos Nol adalah aplikasi perencana pendakian gunung untuk jalur-jalur di Indonesia. Dibangun dari tracklog GPX nyata (bukan data karangan), dengan fokus pada verifikasi data — jarak, elevasi, dan sumber air — sebelum dipakai untuk perencanaan yang menyangkut keselamatan.

🔗 **Coba aplikasinya:** [posnol-app.streamlit.app](https://posnol-app-vpjx44awueyb9rkive4gea.streamlit.app/)

---

## Fitur

- **Skrining kesehatan tim** — deteksi kondisi yang perlu perhatian khusus sebelum berangkat (asma, riwayat jantung, dll), diadaptasi dari PAR-Q+
- **Titik air** — sumber air per jalur, diverifikasi ke sumber eksternal, bukan ditebak dari nama pos
- **Menu & logistik** — hitung kecukupan kalori berbasis BMR (Mifflin–St Jeor) dari data tim yang terdaftar
- **Ceklis barang** — kelompok & pribadi, status tersimpan selama sesi berjalan
- **Tim & biaya** — pembagian biaya per kategori, dan cek beban carrier terhadap berat badan (ambang 30%, Knapik dkk. 2004)
- **Estimasi waktu tempuh** — berbasis aturan Naismith (1892), disesuaikan gaya jalan & beban
- **P3K darurat** — panduan hipotermia, AMS, serangan jantung, anafilaksis (bukan pengganti pelatihan/evakuasi medis)
- **Surat rencana perjalanan** — ringkasan otomatis dari semua data di atas, bisa diunduh sebagai PDF

## Jalur yang tersedia

Argopuro (Baderan–Bremi), Butak (Sirah Kencong & Tuyomerto), Raung (Kalibaru), Merbabu (Selo) — data diturunkan dari tracklog GPX komunitas, dikurasi manual, dan diverifikasi silang ke sumber pendakian lain.

## Stack

Python · Streamlit · SQLite · Plotly · ReportLab

## Menjalankan secara lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Keterbatasan yang jujur diakui

- Elevasi dan jarak diturunkan dari GPX komunitas, bukan survei resmi — ada perbedaan kecil antar sumber (dicatat di log pembersihan data internal)
- Faktor "gaya jalan" dan "beban" pada estimasi waktu adalah estimasi rekayasa, bukan hasil penelitian terkalibrasi
- Database SQLite di Streamlit Community Cloud bersifat baca-saja secara efektif — perubahan tidak tersimpan permanen lintas restart server
- Baru 5 dari rencana jalur yang dikurasi penuh; sisanya masih dalam antrean verifikasi manual

---

> ⚠️ **Bukan pengganti persiapan pendakian standar.** Selalu konfirmasi kondisi jalur terkini ke basecamp/pengelola resmi sebelum berangkat, dan jangan jadikan panduan P3K di aplikasi ini sebagai pengganti pelatihan pertolongan pertama atau evakuasi medis.

---

*README ini dibuat dengan bantuan AI (Claude, Anthropic).*
