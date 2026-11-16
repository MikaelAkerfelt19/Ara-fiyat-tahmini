"""Ham CSV'leri temizleyip cars tablosuna yükler. Çalıştırma: python -m src.db.load_data"""

from contextlib import closing
from pathlib import Path

import pandas as pd

from src.db.schema import connect, create_tables
from src.ml.config import FEATURES, RAW_TRAIN_PATH, RAW_VEHICLES_PATH, TARGET
from src.ml.preprocess import clean, filter_report, filter_train_rows, unify_model_names

# vehicles.csv 1 GB; yalnızca gereken sütunlar okunur (description gibi ağır metinler okunmaz,
# satıcı tipi zaten seller_type sütunundan gelir). Bellek ve süre böylece çok azalır.
VEHICLES_COLS = [
    "id", "price", "year", "manufacturer", "condition", "cylinders", "fuel", "odometer",
    "title_status", "transmission", "drive", "type", "seller_type", "title",
    "odometer_broken", "odometer_rolled_over",
]  # fmt: skip


def _print_report(name: str, cleaned: pd.DataFrame) -> pd.DataFrame:
    """Kuralları uygular, her kuralın attığı satırı yazdırır, süzülmüş tabloyu döndürür."""
    print(f"\n{name}: {len(cleaned)} ilan, çöp temizliği (kural -> atılan satır)")
    for label, dropped in filter_report(cleaned):
        print(f"  {label}: {dropped}")
    kept = filter_train_rows(cleaned)
    print(f"  -> kalan: {len(kept)} satır")
    return kept


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame | None]:
    """(Kaggle, vehicles) temiz ve süzülmüş tablolarını döndürür; vehicles yoksa None."""
    kaggle_clean = clean(pd.read_csv(RAW_TRAIN_PATH))
    kaggle = _print_report("Kaggle", kaggle_clean).assign(source="kaggle")

    if not Path(RAW_VEHICLES_PATH).exists():
        print(f"\nUYARI: {RAW_VEHICLES_PATH} yok; yalnız Kaggle verisiyle devam ediliyor.")
        return kaggle, None

    raw = pd.read_csv(RAW_VEHICLES_PATH, usecols=VEHICLES_COLS, low_memory=False)
    vehicles = _print_report("vehicles", clean(raw.rename(columns={"id": "ID"})))

    # Sızıntı: aynı ilan iki sette de olabilir. Ölçümü Kaggle ilanlarında yaptığımız için
    # bu ilanlar vehicles'ta kalırsa model cevabı eğitimde görmüş olur. (başlık, fiyat) eşleşenleri
    # vehicles'tan çıkarırız. Eşleşme süzülmemiş tüm Kaggle ilanlarına bakar.
    pairs = kaggle_clean[["title", TARGET]].drop_duplicates()
    merged = vehicles.merge(pairs, on=["title", TARGET], how="left", indicator=True)
    vehicles = vehicles[(merged["_merge"] == "left_only").to_numpy()]
    print(f"  Kaggle ile çakışan ilanlar çıkarıldı (sızıntı) -> kalan: {len(vehicles)} satır")
    return kaggle, vehicles.assign(source="vehicles")


def main() -> None:
    kaggle, vehicles = load_frames()
    parts = [kaggle] if vehicles is None else [kaggle, vehicles]
    # title veritabanına yazılmaz; yalnızca sızıntı kontrolünde kullanıldı
    df = pd.concat(parts, ignore_index=True)[["id", *FEATURES, TARGET, "source"]].copy()
    # "3 Series" / "3SERIES", "4 Runner" / "4RUNNER" gibi yazım farkları tek ada indirilir;
    # böylece arayüz listesinde aynı model iki kez çıkmaz ve model örnekleri bölünmez.
    df = unify_model_names(df)
    # Nullable Int64 sütunlar to_sql için float'a çevrilir (NaN -> NULL)
    for col in df.columns:
        if str(df[col].dtype) == "Int64":
            df[col] = df[col].astype("float64")
    with closing(connect()) as conn:
        create_tables(conn)
        df.to_sql("cars", conn, if_exists="replace", index=False)  # tekrar çalıştırılabilir
        # İndeksler: arayüz marka ve marka+model sorgularını çok yapar; 300 bin satırda
        # indeks olmadan her seçim tabloyu baştan sona tarar.
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cars_brand ON cars (brand)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cars_brand_model ON cars (brand, model)")
        conn.commit()
    counts = df["source"].value_counts().to_dict()
    print(f"\ncars tablosu yazıldı: {len(df)} satır {counts}")


if __name__ == "__main__":
    main()
