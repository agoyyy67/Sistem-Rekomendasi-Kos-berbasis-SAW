"""
main.py
=======
Entry point Sistem Pendukung Keputusan (SPK)
Pemilihan Rumah Kos di Purbalingga - Metode SAW.

Eksekusi: python main.py
"""

from __future__ import annotations

import os
import sys

from src.csv_handler import baca_csv
from src.saw_processor import hitung_saw


# =============================================================================
# KONFIGURASI KRITERIA
# =============================================================================
LABEL_KRITERIA = ['C1 (Harga)', 'C2 (Jarak)', 'C3 (Fasilitas)', 'C4 (Kebersihan)', 'C5 (Keamanan)']
BOBOT = [0.2, 0.2, 0.2, 0.2, 0.2]
JENIS_KRITERIA = ['cost', 'benefit', 'cost', 'cost', 'cost']

# Path file CSV
CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'respon_gform.csv')


# =============================================================================
# FUNGSI-FUNGSI TAMPILAN CLI
# =============================================================================

def cetak_garis(panjang: int = 90):
    """Mencetak garis pemisah."""
    print('=' * panjang)


def cetak_header():
    """Mencetak header program."""
    cetak_garis(90)
    print('  SISTEM PENDUKUNG KEPUTUSAN (SPK)')
    print('  PEMILIHAN RUMAH KOS DI PURBALINGGA')
    print('  Metode: Simple Additive Weighting (SAW)')
    cetak_garis(90)
    print()


def cetak_konfigurasi():
    """Mencetak konfigurasi kriteria yang digunakan."""
    print('[KONFIGURASI KRITERIA]')
    print('-' * 70)
    print(f'  {"Kriteria":<20} {"Bobot":<10} {"Jenis"}')
    print('-' * 70)
    for i in range(len(LABEL_KRITERIA)):
        print(f'  {LABEL_KRITERIA[i]:<20} {BOBOT[i]:<10} {JENIS_KRITERIA[i]}')
    print(f'  {"-"*20} {"-"*10} {"-"*10}')
    print(f'  {"Total Bobot:":<20} {sum(BOBOT):<10}')
    print()


def cetak_data_alternatif(data_kos: list[dict]):
    """Mencetak daftar alternatif yang dianalisis."""
    print(f'[DATA ALTERNATIF] Total: {len(data_kos)} kos')
    print('-' * 90)
    print(f'  {"No":<4} {"Nama Kos":<22} {"Alamat"}')
    print('-' * 90)
    for i, kos in enumerate(data_kos, start=1):
        print(f'  {i:<4} {kos["nama"]:<22} {kos["alamat"]}')
    print()


def cetak_matriks_x(data_kos: list[dict], matriks_x: list[list[int]]):
    """Mencetak Matriks Keputusan Awal (X)."""
    print('[MATRIKS KEPUTUSAN AWAL (X)]')
    print('-' * 90)

    # Header kolom
    header = f'  {"Alternatif":<22}'
    for label in LABEL_KRITERIA:
        header += f' {label:>15}'
    print(header)
    print('-' * 90)

    # Data matriks
    for i, kos in enumerate(data_kos):
        baris = f'  {kos["nama"]:<22}'
        for j in range(len(LABEL_KRITERIA)):
            baris += f' {matriks_x[i][j]:>15}'
        print(baris)
    print()


def cetak_matriks_r(data_kos: list[dict], matriks_r: list[list[float]]):
    """Mencetak Matriks Ternormalisasi (R)."""
    print('[MATRIKS TERNORMALISASI (R)]')
    print('-' * 90)

    # Header kolom
    header = f'  {"Alternatif":<22}'
    for label in LABEL_KRITERIA:
        header += f' {label:>15}'
    print(header)
    print('-' * 90)

    # Data matriks
    for i, kos in enumerate(data_kos):
        baris = f'  {kos["nama"]:<22}'
        for j in range(len(LABEL_KRITERIA)):
            baris += f' {matriks_r[i][j]:>15.4f}'
        print(baris)
    print()


def cetak_ranking(ranking: list[dict]):
    """Mencetak hasil perangkingan akhir."""
    print('[HASIL REKOMENDASI PERANGKINGAN]')
    cetak_garis(90)
    print(f'  {"Rank":<6} {"Nama Kos":<22} {"Skor (V)":>10}   {"Alamat"}')
    cetak_garis(90)

    for peringkat, item in enumerate(ranking, start=1):
        penanda = ' << TERBAIK' if peringkat == 1 else ''
        print(
            f'  {peringkat:<6} '
            f'{item["nama"]:<22} '
            f'{item["skor_v"]:>10.4f}   '
            f'{item["alamat"]}'
            f'{penanda}'
        )

    cetak_garis(90)
    print()
    print(f'  >> REKOMENDASI TERBAIK: {ranking[0]["nama"]}')
    print(f'     Alamat : {ranking[0]["alamat"]}')
    print(f'     Skor V : {ranking[0]["skor_v"]:.4f}')
    print()


# =============================================================================
# MAIN PROGRAM
# =============================================================================

def main():
    """Fungsi utama program SPK SAW."""
    cetak_header()

    # ----- TAHAP 1: Baca & Parsing CSV -----
    try:
        print('[TAHAP 1] Membaca data dari CSV...')
        data_kos = baca_csv(CSV_PATH)
        print(f'          [OK] Berhasil memuat {len(data_kos)} data kos.\n')
    except FileNotFoundError as e:
        print(f'\n{e}')
        sys.exit(1)
    except ValueError as e:
        print(f'\n{e}')
        sys.exit(1)

    # ----- TAHAP 2: Tampilkan Konfigurasi -----
    cetak_konfigurasi()
    cetak_data_alternatif(data_kos)

    # ----- TAHAP 3: Proses Algoritma SAW -----
    try:
        print('[TAHAP 2] Memproses algoritma SAW...')
        hasil = hitung_saw(data_kos, BOBOT, JENIS_KRITERIA)
        print('          [OK] Perhitungan selesai.\n')
    except ValueError as e:
        print(f'\n{e}')
        sys.exit(1)

    # ----- TAHAP 4: Tampilkan Hasil -----
    cetak_matriks_x(data_kos, hasil['matriks_x'])
    cetak_matriks_r(data_kos, hasil['matriks_r'])
    cetak_ranking(hasil['ranking'])

    print('Program selesai. Terima kasih telah menggunakan SPK SAW Kos Purbalingga.')
    cetak_garis(90)


if __name__ == '__main__':
    main()
