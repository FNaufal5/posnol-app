@echo off
setlocal enabledelayedexpansion
title Pos Nol - Perencana Pendakian
cd /d "%~dp0"

echo ============================================
echo   POS NOL - Perencana Pendakian
echo ============================================
echo.

REM --- Cek Python tersedia -------------------------------------------------
where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python tidak ditemukan di komputer ini.
    echo.
    echo     Silakan pasang Python dulu dari https://python.org/downloads
    echo     Saat instalasi, PENTING: centang kotak "Add python.exe to PATH"
    echo     sebelum klik Install.
    echo.
    echo     Setelah Python terpasang, klik dua kali file ini lagi.
    echo.
    pause
    exit /b 1
)

echo [1/3] Python ditemukan.

REM --- Cek/pasang paket yang dibutuhkan ------------------------------------
echo [2/3] Memeriksa paket yang dibutuhkan...
python -c "import streamlit, pandas" >nul 2>nul
if errorlevel 1 (
    echo       Paket belum lengkap, memasang sekarang...
    echo       (hanya perlu sekali, sedikit lebih lama di percobaan pertama)
    python -m pip install --quiet -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [!] Pemasangan paket gagal. Periksa koneksi internet, lalu coba lagi.
        pause
        exit /b 1
    )
    echo       Paket berhasil dipasang.
) else (
    echo       Semua paket sudah tersedia.
)

echo [3/3] Menjalankan aplikasi...
echo.
echo       Jendela ini HARUS TETAP TERBUKA selama aplikasi dipakai.
echo       Tutup jendela ini untuk mematikan aplikasi.
echo.
echo       Browser akan terbuka otomatis dalam beberapa detik...
echo.

REM --- Jalankan Streamlit, browser dibuka otomatis oleh Streamlit sendiri --
python -m streamlit run app.py --server.headless false

pause
