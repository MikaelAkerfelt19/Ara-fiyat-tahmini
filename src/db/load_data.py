"""Ham CSV'yi temizleyip cars tablosuna yükler. Çalıştırma: python -m src.db.load_data"""

from contextlib import closing

import pandas as pd

from src.db.schema import connect, create_tables
from src.ml.config import FEATURES, RAW_TRAIN_PATH, TARGET
from src.ml.preprocess import clean, filter_train_rows


def main() -> None:
    raw = pd.read_csv(RAW_TRAIN_PATH)
    df = filter_train_rows(clean(raw))[["id", *FEATURES, TARGET]].copy()
    # Nullable Int64 sütunlar to_sql için float'a çevrilir (NaN -> NULL)
    for col in df.columns:
        if str(df[col].dtype) == "Int64":
            df[col] = df[col].astype("float64")
    with closing(connect()) as conn:
        create_tables(conn)
        df.to_sql("cars", conn, if_exists="replace", index=False)  # tekrar çalıştırılabilir
        conn.commit()
    print(f"cars tablosu yazıldı: {len(df)} satır ({len(raw) - len(df)} satır elendi)")


if __name__ == "__main__":
    main()
