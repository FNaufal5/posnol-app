# Pos Nol — cara pakai

## Sekali klik

1. Pastikan semua file dalam folder ini ada di satu tempat yang sama, misalnya:
   `C:\Users\Farhan Adiyatma\Elektif - PosNol`
2. Klik dua kali **`Buka_PosNol.bat`**
3. Jendela hitam (command prompt) akan muncul dan bekerja sebentar —
   di percobaan **pertama kali**, ini akan memasang beberapa paket Python
   (butuh koneksi internet, sekitar 1-2 menit). Di percobaan berikutnya
   akan langsung cepat.
4. Browser akan terbuka otomatis ke aplikasi Pos Nol.
5. Untuk menutup aplikasi: tutup jendela command prompt hitam tadi.
   Menutup tab browser saja TIDAK mematikan aplikasinya.

## Kalau muncul pesan "Python tidak ditemukan"

Artinya komputer belum punya Python. Langkahnya:

1. Buka https://python.org/downloads dan unduh Python versi terbaru
2. Jalankan installer-nya
3. **PENTING**: di layar pertama installer, ada kotak centang
   **"Add python.exe to PATH"** — centang ini SEBELUM klik Install.
   Ini yang paling sering terlewat dan bikin error.
4. Setelah instalasi selesai, klik dua kali `Buka_PosNol.bat` lagi

## Struktur folder

```
Elektif - PosNol/
├── Buka_PosNol.bat      <- klik dua kali file ini
├── app.py                (tampilan & logika aplikasi)
├── data.py               (akses ke database)
├── pdf_export.py         (pembuat PDF surat rencana perjalanan)
├── posnol_gunung.db      (data jalur: Argopuro, Butak x2, Raung)
├── requirements.txt      (daftar paket yang dibutuhkan)
└── .streamlit/
    └── config.toml       (paksa tema terang — jangan dihapus/diedit)
```

Jangan memindahkan file apa pun keluar dari folder ini secara terpisah —
semuanya, termasuk folder `.streamlit`, harus tetap berada di satu folder
yang sama supaya `Buka_PosNol.bat` bisa menemukannya dan tema terang
konsisten tampil di semua sistem/browser.

## Menambah gunung/jalur baru nanti

Kalau database `posnol_gunung.db` diganti dengan versi yang berisi lebih
banyak gunung, aplikasi otomatis membaca daftar terbaru — tidak perlu
mengubah `app.py` maupun `Buka_PosNol.bat`.
