"""
saw_processor.py
================
Modul inti algoritma perhitungan Simple Additive Weighting (SAW).
Memproses normalisasi matriks keputusan dan perangkingan alternatif.
"""

from __future__ import annotations


def hitung_saw(
    data_kos: list[dict],
    bobot: list[float],
    jenis_kriteria: list[str],
) -> dict:
    """
    Menghitung perangkingan alternatif menggunakan metode SAW.

    Parameter:
        data_kos (list[dict]): Data kos hasil parsing CSV.
            Setiap elemen: {'nama': str, 'alamat': str, 'kriteria': [int...]}
        bobot (list[float]): Array bobot untuk setiap kriteria.
            Contoh: [0.2, 0.2, 0.2, 0.2, 0.2]
        jenis_kriteria (list[str]): Array jenis atribut ('cost' atau 'benefit').
            Contoh: ['cost', 'benefit', 'cost', 'cost', 'cost']

    Returns:
        dict: Dictionary berisi:
            - 'matriks_x': Matriks keputusan awal (list of list)
            - 'matriks_r': Matriks ternormalisasi (list of list)
            - 'ranking': List hasil perangkingan (sorted descending)
                Setiap elemen: {'nama': str, 'alamat': str, 'skor_v': float}

    Raises:
        ValueError: Jika jumlah bobot/jenis tidak sesuai jumlah kriteria.
    """

    jumlah_alternatif = len(data_kos)
    jumlah_kriteria = len(bobot)

    # =========================================================================
    # Validasi Input
    # =========================================================================
    if len(jenis_kriteria) != jumlah_kriteria:
        raise ValueError(
            f"[ERROR] Jumlah jenis kriteria ({len(jenis_kriteria)}) "
            f"tidak sama dengan jumlah bobot ({jumlah_kriteria})."
        )

    for i, kos in enumerate(data_kos):
        if len(kos['kriteria']) != jumlah_kriteria:
            raise ValueError(
                f"[ERROR] Jumlah kriteria pada '{kos['nama']}' "
                f"({len(kos['kriteria'])}) tidak sesuai dengan "
                f"jumlah bobot ({jumlah_kriteria})."
            )

    # Validasi total bobot (harus mendekati 1.0)
    total_bobot = sum(bobot)
    if abs(total_bobot - 1.0) > 0.001:
        raise ValueError(
            f"[ERROR] Total bobot ({total_bobot:.4f}) tidak sama dengan 1.0."
        )

    for jenis in jenis_kriteria:
        if jenis not in ('cost', 'benefit'):
            raise ValueError(
                f"[ERROR] Jenis kriteria '{jenis}' tidak valid. "
                f"Gunakan 'cost' atau 'benefit'."
            )

    # =========================================================================
    # LANGKAH 1: Bangun Matriks Keputusan (X)
    # =========================================================================
    matriks_x = [kos['kriteria'][:] for kos in data_kos]

    # =========================================================================
    # LANGKAH 2: Hitung Nilai Min & Max Setiap Kolom Kriteria
    # =========================================================================
    min_per_kolom = []
    max_per_kolom = []

    for j in range(jumlah_kriteria):
        kolom_j = [matriks_x[i][j] for i in range(jumlah_alternatif)]
        min_per_kolom.append(min(kolom_j))
        max_per_kolom.append(max(kolom_j))

    # =========================================================================
    # LANGKAH 3: Normalisasi Matriks (R)
    #   - Benefit: R_ij = X_ij / Max(X_j)
    #   - Cost   : R_ij = Min(X_j) / X_ij
    # =========================================================================
    matriks_r = []

    for i in range(jumlah_alternatif):
        baris_r = []
        for j in range(jumlah_kriteria):
            x_ij = matriks_x[i][j]

            if jenis_kriteria[j] == 'benefit':
                r_ij = x_ij / max_per_kolom[j]
            else:  # cost
                r_ij = min_per_kolom[j] / x_ij

            baris_r.append(round(r_ij, 4))
        matriks_r.append(baris_r)

    # =========================================================================
    # LANGKAH 4: Hitung Nilai Preferensi (V) & Perangkingan
    #   V_i = Σ (W_j * R_ij)
    # =========================================================================
    hasil_ranking = []

    for i in range(jumlah_alternatif):
        skor_v = 0.0
        for j in range(jumlah_kriteria):
            skor_v += bobot[j] * matriks_r[i][j]

        hasil_ranking.append({
            'nama': data_kos[i]['nama'],
            'alamat': data_kos[i]['alamat'],
            'skor_v': round(skor_v, 4),
        })

    # Urutkan descending berdasarkan skor_v
    hasil_ranking.sort(key=lambda x: x['skor_v'], reverse=True)

    return {
        'matriks_x': matriks_x,
        'matriks_r': matriks_r,
        'ranking': hasil_ranking,
    }
