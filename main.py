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
    cetak_konfigurasi_kriteria(LABEL_KRITERIA, BOBOT, JENIS_KRITERIA)


def cetak_konfigurasi_kriteria(labels: list[str], bobot: list[float], jenis: list[str]):
    """Mencetak konfigurasi kriteria berdasarkan daftar yang diberikan."""
    print('[KONFIGURASI KRITERIA]')
    print('-' * 70)
    print(f'  {"Kriteria":<20} {"Bobot":<10} {"Jenis"}')
    print('-' * 70)
    for i in range(len(labels)):
        print(f'  {labels[i]:<20} {bobot[i]:<10} {jenis[i]}')
    print(f'  {"-"*20} {"-"*10} {"-"*10}')
    print(f'  {"Total Bobot:":<20} {sum(bobot):<10}')
    print()


def cetak_menu_kriteria():
    """Mencetak menu pilihan kriteria untuk user."""
    print('[PILIH KRITERIA]')
    print('-' * 70)
    for i, label in enumerate(LABEL_KRITERIA, start=1):
        print(f'  {i}. {label} ({JENIS_KRITERIA[i - 1]})')
    print('  all. Semua kriteria')
    print('-' * 70)
    print('  Contoh input: 1 atau 1,3,5 atau all')
    print()


def baca_pilihan_kriteria() -> list[int]:
    """Membaca pilihan kriteria dari user dan mengembalikan indeks terpilih."""
    while True:
        pilihan = input('Masukkan pilihan kriteria: ').strip().lower()

        if pilihan in ('', 'all'):
            return list(range(len(LABEL_KRITERIA)))

        try:
            indeks_terpilih = []
            for item in pilihan.split(','):
                nomor = int(item.strip())
                if nomor < 1 or nomor > len(LABEL_KRITERIA):
                    raise ValueError
                if nomor - 1 not in indeks_terpilih:
                    indeks_terpilih.append(nomor - 1)

            if not indeks_terpilih:
                raise ValueError

            return indeks_terpilih
        except ValueError:
            print('  Input tidak valid. Gunakan angka 1-5, pisahkan dengan koma, atau ketik all.')


def buat_subset_kriteria(data_kos: list[dict], indeks_terpilih: list[int]) -> tuple[list[dict], list[str], list[float], list[str]]:
    """Membentuk data dan konfigurasi baru berdasarkan kriteria yang dipilih."""
    labels = [LABEL_KRITERIA[i] for i in indeks_terpilih]
    bobot = [BOBOT[i] for i in indeks_terpilih]
    jenis = [JENIS_KRITERIA[i] for i in indeks_terpilih]

    total_bobot = sum(bobot)
    if total_bobot == 0:
        raise ValueError('[ERROR] Total bobot subset bernilai 0.')

    bobot_ternormalisasi = [nilai / total_bobot for nilai in bobot]

    data_subset = []
    for kos in data_kos:
        data_subset.append({
            'nama': kos['nama'],
            'alamat': kos['alamat'],
            'kriteria': [kos['kriteria'][i] for i in indeks_terpilih],
        })

    return data_subset, labels, bobot_ternormalisasi, jenis


def cetak_data_alternatif(data_kos: list[dict]):
    """Mencetak daftar alternatif yang dianalisis."""
    print(f'[DATA ALTERNATIF] Total: {len(data_kos)} kos')
    print('-' * 90)
    print(f'  {"No":<4} {"Nama Kos":<22} {"Alamat"}')
    print('-' * 90)
    for i, kos in enumerate(data_kos, start=1):
        print(f'  {i:<4} {kos["nama"]:<22} {kos["alamat"]}')
    print()


def cetak_matriks_x(data_kos: list[dict], matriks_x: list[list[int]], labels: list[str]):
    """Mencetak Matriks Keputusan Awal (X)."""
    print('[MATRIKS KEPUTUSAN AWAL (X)]')
    print('-' * 90)

    # Header kolom
    header = f'  {"Alternatif":<22}'
    for label in labels:
        header += f' {label:>15}'
    print(header)
    print('-' * 90)

    # Data matriks
    for i, kos in enumerate(data_kos):
        baris = f'  {kos["nama"]:<22}'
        for j in range(len(labels)):
            baris += f' {matriks_x[i][j]:>15}'
        print(baris)
    print()


def cetak_matriks_r(data_kos: list[dict], matriks_r: list[list[float]], labels: list[str]):
    """Mencetak Matriks Ternormalisasi (R)."""
    print('[MATRIKS TERNORMALISASI (R)]')
    print('-' * 90)

    # Header kolom
    header = f'  {"Alternatif":<22}'
    for label in labels:
        header += f' {label:>15}'
    print(header)
    print('-' * 90)

    # Data matriks
    for i, kos in enumerate(data_kos):
        baris = f'  {kos["nama"]:<22}'
        for j in range(len(labels)):
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
    cetak_data_alternatif(data_kos)

    cetak_menu_kriteria()
    indeks_terpilih = baca_pilihan_kriteria()

    try:
        data_kos, labels_aktif, bobot_aktif, jenis_aktif = buat_subset_kriteria(data_kos, indeks_terpilih)
    except ValueError as e:
        print(f'\n{e}')
        sys.exit(1)

    cetak_konfigurasi_kriteria(labels_aktif, bobot_aktif, jenis_aktif)
    cetak_data_alternatif(data_kos)

    # ----- TAHAP 3: Proses Algoritma SAW -----
    try:
        print('[TAHAP 2] Memproses algoritma SAW...')
        hasil = hitung_saw(data_kos, bobot_aktif, jenis_aktif)
        print('          [OK] Perhitungan selesai.\n')
    except ValueError as e:
        print(f'\n{e}')
        sys.exit(1)

    # ----- TAHAP 4: Tampilkan Hasil -----
    cetak_matriks_x(data_kos, hasil['matriks_x'], labels_aktif)
    cetak_matriks_r(data_kos, hasil['matriks_r'], labels_aktif)
    cetak_ranking(hasil['ranking'])

    print('Program selesai. Terima kasih telah menggunakan SPK SAW Kos Purbalingga.')
    cetak_garis(90)


if __name__ == '__main__':
    main()
