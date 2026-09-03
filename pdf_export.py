"""
Pos Nol — pembuat PDF Surat Rencana Perjalanan
=================================================
Terpisah dari app.py supaya logika penyusunan PDF bisa diuji sendiri.
Menggabungkan seluruh data sesi (tim, menu, biaya, beban, waktu tempuh,
ceklis) menjadi satu dokumen siap cetak.
"""
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

WARNA_TINTA = colors.HexColor("#1B2A2C")
WARNA_SABANA = colors.HexColor("#5F7F42")
WARNA_ABU = colors.HexColor("#6E7C7A")
WARNA_GARIS = colors.HexColor("#CDD5C9")
WARNA_MERAH = colors.HexColor("#95291F")


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("JudulUtama", fontSize=20, leading=24, textColor=WARNA_TINTA,
                          fontName="Helvetica-Bold", spaceAfter=4))
    ss.add(ParagraphStyle("SubJudul", fontSize=11, leading=14, textColor=WARNA_ABU,
                          spaceAfter=14))
    ss.add(ParagraphStyle("Seksi", fontSize=13, leading=16, textColor=WARNA_TINTA,
                          fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6))
    ss.add(ParagraphStyle("Isi", fontSize=10, leading=14, textColor=WARNA_TINTA))
    ss.add(ParagraphStyle("IsiKecil", fontSize=9, leading=12, textColor=WARNA_ABU))
    ss.add(ParagraphStyle("Peringatan", fontSize=10, leading=13, textColor=WARNA_MERAH,
                          fontName="Helvetica-Bold"))
    return ss


def _tabel_standar(data_baris, lebar_kolom, header=True):
    t = Table(data_baris, colWidths=lebar_kolom)
    gaya = [
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), WARNA_TINTA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, WARNA_GARIS),
    ]
    if header:
        gaya += [
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("LINEBELOW", (0, 0), (-1, 0), 1, WARNA_TINTA),
            ("TEXTCOLOR", (0, 0), (-1, 0), WARNA_ABU),
        ]
    t.setStyle(TableStyle(gaya))
    return t


def buat_pdf_surat_rencana(konteks: dict) -> bytes:
    """
    konteks berisi seluruh data sesi yang dibutuhkan:
      nama_gunung, nama_jalur, jumlah_hari, jumlah_orang,
      ketua, kontak_ketua, pj_medis, navigator, sweeper, batas_lapor,
      jarak_km, elevation_gain_m, puncak_mdpl,
      estimasi_waktu_teks, gaya_jalan, gaya_beban,
      anggota (list of dict: nama, berat_kg, tingkat, catatan),
      menu (list of dict: hari, waktu, menu, kkal, berat_g),
      kategori_biaya (list of dict: kategori, orang, per_orang),
      beban_carrier (dict nama -> kg),
      pos_air (list of dict: nama, jarak_km),
      ceklis_belum (list of str -- nama barang yang BELUM dicentang, ringkas)
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
    )
    ss = _styles()
    story = []

    # --- Kop surat -----------------------------------------------------
    story.append(Paragraph("Surat Rencana Perjalanan", ss["JudulUtama"]))
    story.append(Paragraph(
        f"{konteks['nama_gunung']} via {konteks['nama_jalur']} &nbsp;·&nbsp; "
        f"{konteks['jumlah_hari']} hari &nbsp;·&nbsp; {konteks['jumlah_orang']} orang",
        ss["SubJudul"],
    ))
    story.append(HRFlowable(width="100%", thickness=1.2, color=WARNA_TINTA, spaceAfter=10))

    # --- Ringkasan jalur -------------------------------------------------
    story.append(Paragraph("Ringkasan jalur", ss["Seksi"]))
    ringkasan = [
        ["Puncak resmi", f"{konteks['puncak_mdpl']:,.0f} mdpl".replace(",", ".")],
        ["Jarak jalur", f"{konteks['jarak_km']:.2f} km"],
        ["Elevation gain", f"{konteks['elevation_gain_m']:.0f} m"],
        ["Estimasi waktu naik", konteks.get("estimasi_waktu_teks", "-")],
        ["Gaya jalan / beban asumsi", f"{konteks.get('gaya_jalan','-')} / {konteks.get('gaya_beban','-')}"],
    ]
    story.append(_tabel_standar(ringkasan, [6 * cm, 10 * cm], header=False))

    # --- Penanggung jawab -------------------------------------------------
    story.append(Paragraph("Penanggung jawab", ss["Seksi"]))
    pj = [
        ["Ketua tim", konteks.get("ketua") or "(belum diisi)"],
        ["Kontak ketua", konteks.get("kontak_ketua") or "(belum diisi)"],
        ["Penanggung jawab medis", konteks.get("pj_medis") or "(belum diisi)"],
        ["Navigator", konteks.get("navigator") or "(belum diisi)"],
        ["Sweeper", konteks.get("sweeper") or "(belum diisi)"],
    ]
    story.append(_tabel_standar(pj, [6 * cm, 10 * cm], header=False))

    # --- Batas waktu lapor -------------------------------------------------
    story.append(Paragraph("Batas waktu lapor", ss["Seksi"]))
    story.append(Paragraph(
        f"Bila tim belum kembali ke basecamp hingga <b>{konteks.get('batas_lapor') or '(belum diisi)'}</b>, "
        f"hubungi pengelola jalur setempat dan Basarnas (115).", ss["Isi"],
    ))

    # --- Anggota tim & catatan medis -------------------------------------------------
    anggota = konteks.get("anggota", [])
    if anggota:
        story.append(Paragraph("Anggota tim & catatan medis", ss["Seksi"]))
        baris = [["Nama", "Berat", "Status", "Catatan"]]
        for a in anggota:
            label = {"merah": "Perlu konsultasi", "kuning": "Perhatian", "hijau": "Normal"}[a["tingkat"]]
            catatan_singkat = " ".join(a["catatan"])[:180]
            baris.append([a["nama"], f"{a['berat_kg']} kg", label, Paragraph(catatan_singkat, ss["IsiKecil"])])
        story.append(_tabel_standar(baris, [3 * cm, 2 * cm, 2.5 * cm, 8.5 * cm]))

        merah = [a["nama"] for a in anggota if a["tingkat"] == "merah"]
        if merah:
            story.append(Spacer(1, 6))
            story.append(Paragraph(
                f"PERHATIAN: {', '.join(merah)} memerlukan perhatian khusus — "
                f"lihat catatan lengkap di aplikasi.",
                ss["Peringatan"],
            ))
    else:
        story.append(Paragraph("Anggota tim & catatan medis", ss["Seksi"]))
        story.append(Paragraph("Belum ada anggota terdaftar.", ss["IsiKecil"]))

    # --- Titik air -------------------------------------------------
    pos_air = konteks.get("pos_air", [])
    story.append(Paragraph("Titik air terverifikasi", ss["Seksi"]))
    if pos_air:
        baris = [["Pos", "Jarak dari basecamp"]]
        for p in pos_air:
            baris.append([p["nama"], f"{p['jarak_km']:.2f} km"])
        story.append(_tabel_standar(baris, [10 * cm, 6 * cm]))
    else:
        story.append(Paragraph(
            "Belum ada titik sumber air terverifikasi dalam database untuk jalur ini. "
            "Konfirmasi ke basecamp/pengelola sebelum berangkat.", ss["IsiKecil"],
        ))

    # --- Menu & logistik -------------------------------------------------
    menu = konteks.get("menu", [])
    if menu:
        story.append(Paragraph("Menu & logistik", ss["Seksi"]))
        baris = [["Hari", "Waktu", "Menu", "kkal/orang"]]
        for m in sorted(menu, key=lambda x: x["hari"]):
            baris.append([f"H{m['hari']}", m["waktu"], m["menu"], f"{m['kkal']}"])
        story.append(_tabel_standar(baris, [1.5 * cm, 2.5 * cm, 8.5 * cm, 3.5 * cm]))

    # --- Pembagian biaya -------------------------------------------------
    biaya = konteks.get("kategori_biaya", [])
    if biaya:
        story.append(Paragraph("Pembagian biaya", ss["Seksi"]))
        baris = [["Kategori", "Orang", "Per orang", "Subtotal"]]
        total = 0
        for k in biaya:
            subtotal = k["orang"] * k["per_orang"]
            total += subtotal
            baris.append([
                k["kategori"], str(k["orang"]),
                f"Rp {k['per_orang']:,.0f}".replace(",", "."),
                f"Rp {subtotal:,.0f}".replace(",", "."),
            ])
        story.append(_tabel_standar(baris, [5 * cm, 2 * cm, 4 * cm, 4.5 * cm]))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Total biaya: Rp {total:,.0f}</b>".replace(",", "."), ss["Isi"]))

    # --- Beban carrier -------------------------------------------------
    beban = konteks.get("beban_carrier", {})
    if beban and anggota:
        story.append(Paragraph("Beban carrier tim", ss["Seksi"]))
        baris = [["Nama", "Berat badan", "Carrier", "% berat badan"]]
        for a in anggota:
            bb = a["berat_kg"]
            bc = beban.get(a["nama"], 0)
            persen = bc / bb * 100 if bb else 0
            tanda = " (berat)" if persen >= 30 else ""
            baris.append([a["nama"], f"{bb} kg", f"{bc} kg", f"{persen:.0f}%{tanda}"])
        story.append(_tabel_standar(baris, [5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm]))

    # --- Ceklis barang yang belum siap -------------------------------------------------
    ceklis_belum = konteks.get("ceklis_belum", [])
    story.append(Paragraph("Status ceklis barang", ss["Seksi"]))
    if ceklis_belum:
        story.append(Paragraph(
            f"<b>{len(ceklis_belum)} item belum dicentang</b> pada saat surat ini dibuat:",
            ss["Isi"],
        ))
        teks_list = "<br/>".join(f"- {x}" for x in ceklis_belum[:20])
        story.append(Paragraph(teks_list, ss["IsiKecil"]))
        if len(ceklis_belum) > 20:
            story.append(Paragraph(f"...dan {len(ceklis_belum)-20} item lainnya.", ss["IsiKecil"]))
    else:
        story.append(Paragraph("Semua item ceklis sudah dicentang lengkap.", ss["Isi"]))

    # --- Tanda tangan -------------------------------------------------
    story.append(Spacer(1, 24))
    story.append(_tabel_standar(
        [["_________________________", "_________________________"],
         ["Ketua tim", "Petugas basecamp"]],
        [8 * cm, 8 * cm], header=False,
    ))

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Dokumen dibuat otomatis oleh Pos Nol. Bukan pengganti izin resmi pendakian — "
        "tetap lapor ke pos pendaftaran/basecamp sesuai prosedur pengelola jalur.",
        ss["IsiKecil"],
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()
