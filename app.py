from __future__ import annotations

import os

import streamlit as st

from src.csv_handler import baca_csv
from src.saw_processor import hitung_saw


LABEL_KRITERIA = [
    'C1 (Harga)',
    'C2 (Jarak)',
    'C3 (Fasilitas)',
    'C4 (Kebersihan)',
    'C5 (Keamanan)',
]
BOBOT = [0.2, 0.2, 0.2, 0.2, 0.2]
JENIS_KRITERIA = ['cost', 'benefit', 'cost', 'cost', 'cost']
CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'respon_gform.csv')


def buat_subset_kriteria(data_kos: list[dict], indeks_terpilih: list[int]) -> tuple[list[dict], list[str], list[float], list[str]]:
    """Membentuk data dan konfigurasi baru berdasarkan kriteria yang dipilih."""
    labels = [LABEL_KRITERIA[i] for i in indeks_terpilih]
    bobot = [BOBOT[i] for i in indeks_terpilih]
    jenis = [JENIS_KRITERIA[i] for i in indeks_terpilih]

    total_bobot = sum(bobot)
    if total_bobot == 0:
        raise ValueError('Total bobot subset bernilai 0.')

    bobot_ternormalisasi = [nilai / total_bobot for nilai in bobot]

    data_subset = []
    for kos in data_kos:
        data_subset.append({
            'nama': kos['nama'],
            'alamat': kos['alamat'],
            'kriteria': [kos['kriteria'][i] for i in indeks_terpilih],
        })

    return data_subset, labels, bobot_ternormalisasi, jenis


def format_tabel_konfigurasi(labels: list[str], bobot: list[float], jenis: list[str]) -> list[dict]:
    return [
        {
            'Kriteria': labels[i],
            'Bobot': round(bobot[i], 4),
            'Jenis': jenis[i],
        }
        for i in range(len(labels))
    ]


def format_tabel_alternatif(data_kos: list[dict]) -> list[dict]:
    return [
        {
            'No': i + 1,
            'Nama Kos': kos['nama'],
            'Alamat': kos['alamat'],
        }
        for i, kos in enumerate(data_kos)
    ]


def format_tabel_matriks(data_kos: list[dict], matriks: list[list[float | int]], labels: list[str]) -> list[dict]:
    rows = []
    for i, kos in enumerate(data_kos):
        row = {'Alternatif': kos['nama']}
        for j, label in enumerate(labels):
            row[label] = matriks[i][j]
        rows.append(row)
    return rows


def format_tabel_ranking(ranking: list[dict]) -> list[dict]:
    return [
        {
            'Rank': i + 1,
            'Nama Kos': item['nama'],
            'Skor (V)': item['skor_v'],
            'Alamat': item['alamat'],
        }
        for i, item in enumerate(ranking)
    ]


st.set_page_config(
    page_title='SPK Kos Purbalingga - SAW',
    page_icon='🏠',
    layout='wide',
)

st.title('Sistem Pendukung Keputusan Pemilihan Rumah Kos di Purbalingga')
st.caption('Metode Simple Additive Weighting dengan pilihan satu atau beberapa kriteria.')

with st.sidebar:
    st.header('Pilih Kriteria')
    selected_indices = st.multiselect(
        'Kriteria yang dipakai',
        options=list(range(len(LABEL_KRITERIA))),
        format_func=lambda index: LABEL_KRITERIA[index],
        default=list(range(len(LABEL_KRITERIA))),
    )
    proses = st.button('Proses SAW', use_container_width=True)

try:
    data_kos_awal = baca_csv(CSV_PATH)
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()
except ValueError as e:
    st.error(str(e))
    st.stop()

if not selected_indices:
    st.warning('Pilih minimal satu kriteria untuk menjalankan SAW.')
    st.stop()

if not proses:
    st.info('Pilih kriteria di sidebar lalu tekan Proses SAW.')
    st.stop()

try:
    data_kos, labels_aktif, bobot_aktif, jenis_aktif = buat_subset_kriteria(data_kos_awal, selected_indices)
    hasil = hitung_saw(data_kos, bobot_aktif, jenis_aktif)
except ValueError as e:
    st.error(str(e))
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric('Alternatif awal', len(data_kos_awal))
col2.metric('Alternatif dipakai', len(data_kos))
col3.metric('Jumlah kriteria aktif', len(labels_aktif))

st.subheader('Konfigurasi Kriteria Aktif')
st.table(format_tabel_konfigurasi(labels_aktif, bobot_aktif, jenis_aktif))

st.subheader('Data Alternatif')
st.table(format_tabel_alternatif(data_kos))

st.subheader('Hasil Perangkingan')
st.table(format_tabel_ranking(hasil['ranking']))

st.subheader('Matriks Keputusan Awal (X)')
st.table(format_tabel_matriks(data_kos, hasil['matriks_x'], labels_aktif))

st.subheader('Matriks Ternormalisasi (R)')
st.table(format_tabel_matriks(data_kos, hasil['matriks_r'], labels_aktif))

if hasil['ranking']:
    terbaik = hasil['ranking'][0]
    st.success(f"Rekomendasi terbaik: {terbaik['nama']} dengan skor {terbaik['skor_v']:.4f}")
    st.write(f"Alamat: {terbaik['alamat']}")
