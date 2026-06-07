"""
csv_handler.py
==============
Modul untuk membaca dan parsing file CSV hasil unduh Google Form.
Menggunakan library bawaan Python (csv.DictReader) tanpa library eksternal.
"""

from __future__ import annotations

import csv
import os


def baca_csv(filepath: str) -> list[dict]:
    """
    Membaca file CSV dan melakukan parsing data kos.

    Parameter:
        filepath (str): Path relatif/absolut ke file CSV.

    Returns:
        list[dict]: List berisi dictionary data setiap kos dengan format:
            {
                'nama': str,
                'alamat': str,
                'kriteria': [int, int, int, int, int]
            }
            Urutan kriteria:
                C1 = Harga Sewa (cost)
                C2 = Jarak/Lokasi (benefit)
                C3 = Fasilitas (cost)
                C4 = Kebersihan (cost)
                C5 = Keamanan (cost)

    Raises:
        FileNotFoundError: Jika file CSV tidak ditemukan.
        ValueError: Jika terjadi kesalahan parsing data.
    """

    # Validasi keberadaan file
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"[ERROR] File CSV tidak ditemukan: '{filepath}'\n"
            f"        Pastikan file sudah diunduh dari Google Form dan "
            f"diletakkan di folder 'data/'."
        )

    data_kos = []

    with open(filepath, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        # Validasi kolom yang dibutuhkan
        kolom_wajib = [
            'Nama Rumah Kos',
            'Alamat Lengkap Kos',
            'Harga Sewa Kos per Tahun',
            'Kondisi Jarak / Lokasi Kos',
            'Kelengkapan Fasilitas Kos',
            'Tingkat Kebersihan Lingkungan Kos',
            'Tingkat Keamanan Kos',
        ]

        if reader.fieldnames is None:
            raise ValueError("[ERROR] File CSV kosong atau tidak memiliki header.")

        for kolom in kolom_wajib:
            if kolom not in reader.fieldnames:
                raise ValueError(
                    f"[ERROR] Kolom '{kolom}' tidak ditemukan di file CSV.\n"
                    f"        Kolom yang tersedia: {reader.fieldnames}"
                )

        for nomor_baris, row in enumerate(reader, start=2):
            try:
                nama = row['Nama Rumah Kos'].strip()
                alamat = row['Alamat Lengkap Kos'].strip()

                # =============================================================
                # Parsing kolom 'Harga Sewa Kos per Tahun'
                # Format: "1 - Kurang dari Rp 3.000.000"
                #          ^ Ambil karakter pertama sebagai skor integer
                # =============================================================
                raw_harga = row['Harga Sewa Kos per Tahun'].strip()
                skor_harga = int(raw_harga[0])

                # Parsing kolom kriteria numerik lainnya (sudah berupa integer)
                skor_jarak = int(row['Kondisi Jarak / Lokasi Kos'].strip())
                skor_fasilitas = int(row['Kelengkapan Fasilitas Kos'].strip())
                skor_kebersihan = int(row['Tingkat Kebersihan Lingkungan Kos'].strip())
                skor_keamanan = int(row['Tingkat Keamanan Kos'].strip())

                data_kos.append({
                    'nama': nama,
                    'alamat': alamat,
                    'kriteria': [
                        skor_harga,       # C1: Harga Sewa
                        skor_jarak,       # C2: Jarak/Lokasi
                        skor_fasilitas,   # C3: Fasilitas
                        skor_kebersihan,  # C4: Kebersihan
                        skor_keamanan,    # C5: Keamanan
                    ]
                })

            except (ValueError, IndexError) as e:
                raise ValueError(
                    f"[ERROR] Gagal parsing data pada baris ke-{nomor_baris}: {e}\n"
                    f"        Data baris: {row}"
                )

    if not data_kos:
        raise ValueError("[ERROR] File CSV tidak memiliki data (hanya header).")

    return data_kos
