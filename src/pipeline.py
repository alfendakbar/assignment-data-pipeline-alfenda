"""
Data Pipeline Automobile (Versi PESERTA)

Isi bagian TODO. Setelah lengkap, jalankan dengan:

python src/pipeline.py

Input: automobileEDA_dirty_training.csv
Output: automobileEDA_processed.csv
"""
from __future__ import annotations
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def load_data(filepath: str) -> pd.DataFrame:
    """Baca CSV lokal ke DataFrame."""
    df = pd.read_csv(filepath)
    print(f"[load] {filepath} -> {len(df)} baris")
    return df


def inspect_data(df: pd.DataFrame) -> None:
    """Pemeriksaan kondisi awal dataset."""
    print(df.head())
    print(f"[inspect] {df.shape[0]} baris x {df.shape[1]} kolom")
    print(f"[inspect] kolom: {list(df.columns)}")
    print(df.dtypes)
    print(df.isna().sum())
    print(f"[inspect] duplicate: {df.duplicated().sum()}")
    for col in ["make", "aspiration", "num-of-doors", "body-style", "drive-wheels",
                "engine-location", "engine-type", "num-of-cylinders", "fuel-system",
                "horsepower-binned"]:
        print(f"[inspect] unik {col}: {sorted(df[col].dropna().unique())}")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Missing values + duplicates + format + noisy values."""
    before = len(df)
    missing_before = int(df.isna().sum().sum())

    # Duplicates
    dup = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Format konsistensi
    for col in ["make", "aspiration", "num-of-doors", "body-style", "drive-wheels",
                "engine-location", "engine-type", "num-of-cylinders", "fuel-system",
                "horsepower-binned"]:
        df[col] = df[col].str.lower().str.strip()
    tgl = df["transaction_date"].astype(str).str.strip()
    df["transaction_date"] = (
        pd.to_datetime(tgl.where(tgl.str.contains("/")), format="%d/%m/%Y", errors="coerce")
        .combine_first(pd.to_datetime(tgl.where(tgl.str.match(r"^\d{4}-")), format="%Y-%m-%d", errors="coerce"))
        .combine_first(pd.to_datetime(tgl.where(tgl.str.match(r"^\d{2}-[A-Za-z]{3}-")), format="%d-%b-%Y", errors="coerce"))
        .combine_first(pd.to_datetime(tgl.where(tgl.str.match(r"^\d{2}-\d{2}-")), format="%m-%d-%Y", errors="coerce"))
    )

    # Missing values
    df = df.dropna(subset=["make", "price"])
    df["num-of-doors"] = df["num-of-doors"].fillna(df["num-of-doors"].mode()[0])
    df["stroke"] = df["stroke"].fillna(df["stroke"].median())
    df["horsepower"] = df["horsepower"].fillna(df["horsepower"].median())
    df["horsepower-binned"] = df["horsepower-binned"].fillna(
        pd.cut(df["horsepower"], bins=[0, 100, 150, df["horsepower"].max() + 1],
               labels=["low", "medium", "high"]).astype(str)
    )
    df["transaction_date"] = df["transaction_date"].ffill()

    # Buang noisy values (harga <= 0, horsepower <= 0)
    mask_bad = (
        (df["price"] <= 0)
        | (df["horsepower"] <= 0)
    )
    df = df[~mask_bad].copy()

    print(f"[clean] {before} -> {len(df)} baris ({before - len(df)} dibuang)")
    print(f"[clean] duplicate dihapus: {dup}")
    print(f"[clean] missing values: {missing_before} -> {int(df.isna().sum().sum())}")
    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Scaling numerik + one-hot encoding kategori."""
    # MinMax scaling
    scaler = MinMaxScaler()
    df[["price_raw", "horsepower_raw"]] = df[["price", "horsepower"]]
    df[["price", "normalized-losses", "wheel-base", "height", "curb-weight",
        "engine-size", "bore", "stroke", "compression-ratio", "horsepower",
        "peak-rpm", "city-mpg", "highway-mpg", "city-L/100km"]] = scaler.fit_transform(
        df[["price", "normalized-losses", "wheel-base", "height", "curb-weight",
            "engine-size", "bore", "stroke", "compression-ratio", "horsepower",
            "peak-rpm", "city-mpg", "highway-mpg", "city-L/100km"]]
    )

    # One-hot encoding
    df = pd.get_dummies(
        df,
        columns=["make", "aspiration", "num-of-doors", "body-style", "drive-wheels",
                 "engine-location", "engine-type", "num-of-cylinders", "fuel-system",
                 "horsepower-binned"],
        dtype=int,
    )

    print(f"[transform] {df.shape[1]} kolom setelah transformasi")
    return df


def save_data(df: pd.DataFrame, filepath: str) -> None:
    """Persistensi hasil ke CSV."""
    df.to_csv(filepath, index=False)
    print(f"[save] {filepath}")


def main() -> None:
    df = load_data("./data/raw/automobileEDA_dirty_training.csv")
    inspect_data(df)
    df = clean_data(df)
    df = transform_data(df)
    save_data(df, "./data/processed/automobileEDA_processed.csv")
    print("Pipeline selesai ✓")


if __name__ == "__main__":
    main()
