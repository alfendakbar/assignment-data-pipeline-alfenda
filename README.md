# Assignment Data Pipeline: Automobile

Pipeline Python untuk membersihkan dan mentransformasi dataset otomotif yang sengaja dibuat kotor (`automobileEDA_dirty_training.csv`), lalu menyimpannya sebagai `automobileEDA_processed.csv`. Satu kali `python src/pipeline.py` menjalankan semuanya: load, inspect, clean, transform, save.

## Dataset

Dataset berisi 205 mobil dengan 30 kolom: spesifikasi mesin dan bodi (`engine-size`, `horsepower`, `curb-weight`, `body-style`, dan lainnya), konsumsi bahan bakar, `price`, serta `transaction_date`. 

File yang tersedia:
- `automobileEDA_dirty_training.csv`: input pipeline, disimpan di `data/raw/`.
- `automobileEDA_processed.csv`: output hasil pipeline, tersimpan di `data/processed/`.

## Struktur folder

```
data-pipeline-assignment/
├── data/
│   ├── raw/automobileEDA_dirty_training.csv
│   └── processed/automobileEDA_processed.csv
├── src/pipeline.py
├── documentation/data-flow-diagram.png
├── README.md
└── requirements.txt
```

## Kondisi awal dataset

Hasil `inspect_data` pada data mentah:

- Ukuran: 205 baris x 30 kolom.
- Missing values (17 sel): `transaction_date` 2, `make` 2, `num-of-doors` 2, `stroke` 4, `horsepower` 3, `price` 3, `horsepower-binned` 1.
- Duplikat: 4 baris identik.
- Tipe data: `transaction_date` masih `object` (teks), padahal isinya tanggal.
- Kategori tidak konsisten: `make` (`ALFA-ROMERO`, `Audi`, `BMW`, serta `dodge  `, `mercury  `, `porsche  ` dengan spasi di belakang), `body-style` (`SEDAN`, `Sedan`), `drive-wheels` (`AWD`, `RWD`), `fuel-system` (`MPFI`, `Mpfi`).
- Format tanggal campur: `2025-01-01`, `02/01/2025`, `01-03-2025`, `04-Jan-2025`.
- Skala tidak seragam: `price` sampai 45.400, `peak-rpm` sampai 6.600, sedangkan `length` dan `width` sudah berada di 0 sampai 1.

## Cleaning

| Masalah | Kolom | Metode | Alasan |
|---|---|---|---|
| Duplikat | semua | `drop_duplicates` | 4 baris identik menggandakan bobot mobil yang sama. |
| Kategori tidak konsisten | `make`, `aspiration`, `num-of-doors`, `body-style`, `drive-wheels`, `engine-location`, `engine-type`, `num-of-cylinders`, `fuel-system`, `horsepower-binned` | `str.lower().str.strip()` | `Sedan` dan `SEDAN` akan menjadi dua kategori terpisah saat di-encode. |
| Format tanggal campur | `transaction_date` | Parse per format, lalu jadi `datetime` | Tanda `/` dibaca dd/mm/yyyy dan `-` berawalan bulan dibaca mm-dd-yyyy. Urutan hasilnya naik satu hari per baris, jadi pembacaan ini cocok. |
| `make` kosong | `make` | Baris dibuang | Merek tidak bisa ditebak dari kolom lain. |
| `price` kosong | `price` | Baris dibuang | `price` adalah target yang kemungkinan dipakai nanti, jadi nilai tebakan akan mengotori data. |
| `num-of-doors` kosong | `num-of-doors` | Diisi modus (`four`) | Kolom kategorikal, modus adalah pilihan paling aman. |
| `stroke`, `horsepower` kosong | `stroke`, `horsepower` | Diisi median (3,29 dan 95) | Distribusi `horsepower` punya outlier sampai 262, median tidak ikut tertarik. |
| `horsepower-binned` kosong | `horsepower-binned` | Diturunkan dari `horsepower` (batas 100 dan 150) | Kolom ini turunan dari `horsepower`, jadi bisa dihitung ulang. Batas 100 dan 150 saya tentukan sendiri. |
| `transaction_date` kosong | `transaction_date` | Isi dari baris sebelumnya (`ffill`) | Tanggal naik berurutan, jadi baris sebelumnya adalah perkiraan terdekat. |
| Nilai tidak wajar | `price`, `horsepower` | Buang jika `<= 0` | Aturan ini dibuat sendiri karena soal tidak menyebut batas. Pada data ini tidak ada baris yang terbuang oleh aturan tersebut. |

Jumlah data: 205 baris menjadi 197 baris. Delapan baris yang hilang terdiri dari 4 duplikat dan 4 baris tanpa `make` atau `price`. Missing values turun dari 17 sel menjadi 0.

## Transformasi

**Min-Max scaling** diterapkan ke 14 kolom numerik: `price`, `normalized-losses`, `wheel-base`, `height`, `curb-weight`, `engine-size`, `bore`, `stroke`, `compression-ratio`, `horsepower`, `peak-rpm`, `city-mpg`, `highway-mpg`, `city-L/100km`. Semuanya dipetakan ke rentang 0 sampai 1 supaya kolom dengan angka besar seperti `price` tidak mendominasi kolom kecil seperti `bore`. Sedangkan kolom `length` dan `width` tidak di-scale karena sudah berada di 0 sampai 1. `symboling`, `diesel`, dan `gas` dibiarkan karena berupa kode atau kolom biner.

**One-hot encoding** diterapkan ke 10 kolom kategorikal: `make`, `aspiration`, `num-of-doors`, `body-style`, `drive-wheels`, `engine-location`, `engine-type`, `num-of-cylinders`, `fuel-system`, `horsepower-binned`. Tidak ada urutan alami antar kategori ini, jadi one-hot lebih aman daripada label angka.

Kolom baru: `price_raw` dan `horsepower_raw` menyimpan nilai asli sebelum di-scale, supaya hasilnya bisa dibandingkan. Kolom kategorikal asli diganti kolom dummy, sehingga jumlah kolom akhir menjadi 83.

Contoh sebelum dan sesudah:

| Baris | price (asli) | price (scaled) | horsepower (asli) | horsepower (scaled) |
|---|---|---|---|---|
| 0 | 13.495 | 0,2080 | 111 | 0,2944 |
| 1 | 16.500 | 0,2826 | 111 | 0,2944 |
| 2 | 16.500 | 0,2826 | 154 | 0,4953 |
| 3 | 13.950 | 0,2193 | 102 | 0,2523 |

## Cara menjalankan

Install dependency:

```
pip install -r requirements.txt
```

Jalankan dari folder utama project (bukan dari dalam `src/`):

```
python src/pipeline.py
```

(Folder `data/processed/` harus sudah ada sebelum pipeline dijalankan).

## Alur ETL

- Extract: `load_data` membaca CSV dari `data/raw/`.
- Transform: `inspect_data`, `clean_data`, dan `transform_data` memeriksa, membersihkan, lalu mengubah data.
- Load: `save_data` menulis hasil ke `data/processed/automobileEDA_processed.csv`.

Diagram alur ada di `documentation/data-flow-diagram.png`.
