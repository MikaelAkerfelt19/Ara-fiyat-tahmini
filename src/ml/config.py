"""Eğitim ve temizlik için ortak ayarlar."""

TARGET = "price"  # USD
NUM_COLS = ["year", "mileage", "cylinders"]
CAT_COLS = [
    "brand",
    "model",
    "fuel_type",
    "transmission",
    "condition",
    "drive",
    "body_type",
    "title_status",
    "seller_type",  # "Galeri" / "Bireysel"
]
FEATURES = NUM_COLS + CAT_COLS
RANDOM_STATE = 42
RAW_TRAIN_PATH = "data/raw/train_data_v2.csv"
RAW_TEST_PATH = "data/raw/test_data_v2.csv"
# İkinci, büyük veri seti (295 bin Craigslist ilanı). Dosya yoksa sistem yalnız Kaggle ile çalışır.
RAW_VEHICLES_PATH = "data/raw/vehicles.csv"
MILE_TO_KM = 1.609344
# 1.000 $ altı ilanlar çoğunlukla gerçek fiyat değil: peşinat, "ara" ilanı, tek haneli fiyatlar.
MIN_PRICE_USD = 1_000
# 250.000 $ üstü ilanlar büyük olasılıkla girdi hatası (fazladan sıfır); sıradan araç değil.
MAX_PRICE_USD = 250_000
# Metinde bu kalıplardan biri geçen ilan "Galeri" sayılır. vehicles.csv'de gerçek etiket
# (dealer/owner) olduğundan kalıp oraya karşı sınandı: ilanların %86'sını doğru bildi.
DEALER_PATTERN = r"\bdealer|financ|credit|stock\s*#|stock number|warrant|offered by|carfax"
# Kaggle ilanları eğitimde 5 kat ağırlık alır: asıl hedef bizim yarışma verisi,
# model ona daha çok uysun. Ölçüm: 5 katlı CV MAE 6139 $ -> 4345 $ (R² 0,485 -> 0,792).
KAGGLE_WEIGHT = 5.0
# Arayüzdeki model listesinde yer alması için bir modelin en az bu kadar ilanı olmalı.
MIN_MODEL_LISTINGS = 20

# Görünen marka adları
CANONICAL_BRANDS = [
    "Acura", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", "Buick", "BYD",
    "Cadillac", "Chery", "Chevrolet", "Chrysler", "Citroen", "Dacia", "Datsun", "Dodge",
    "Ferrari", "Fiat", "Ford", "Freightliner", "Genesis", "GMC", "Hino", "Honda", "Hummer",
    "Hyundai", "Infiniti", "International", "Isuzu", "Jaguar", "Jeep", "Kia", "Lamborghini",
    "Land Rover", "Lexus", "Lincoln", "Maserati", "Mazda", "McLaren", "Mercedes-Benz",
    "Mercury", "MG", "Mini", "Mitsubishi", "Nissan", "Oldsmobile", "Opel", "Peugeot",
    "Plymouth", "Pontiac", "Porsche", "Ram", "Renault", "Rolls-Royce", "Saab", "Saturn",
    "Scion", "Seat", "Skoda", "Smart", "Studebaker", "Subaru", "Suzuki", "Tesla", "Togg",
    "Toyota", "Triumph", "Volkswagen", "Volvo", "Willys",
]  # fmt: skip

# Küçük harf TAM eşleşme -> görünen ad.
# Chery ile Chevrolet farklı markalardır; bu yüzden yalnızca tam kelime eşleşmesi kullanılır.
BRAND_ALIASES = {
    "chevy": "Chevrolet",
    "vw": "Volkswagen",
    "mercedes": "Mercedes-Benz",
    "mercedes benz": "Mercedes-Benz",
    "infinity": "Infiniti",
    "catilac": "Cadillac",
    "landrover": "Land Rover",
    "rover": "Land Rover",  # vehicles.csv manufacturer değeri
    "rolls royce": "Rolls-Royce",
}

# Ham değer (küçük harf) -> Türkçe etiket
FUEL_LABELS = {
    "gas": "Benzin",
    "diesel": "Dizel",
    "hybrid": "Hibrit",
    "electric": "Elektrik",
    "other": "Diğer",
}
TRANSMISSION_LABELS = {"automatic": "Otomatik", "manual": "Manuel", "other": "Diğer"}
CONDITION_LABELS = {
    "new": "Sıfır",
    "like new": "Sıfır gibi",
    "excellent": "Çok iyi",
    "good": "İyi",
    "fair": "Orta",
    "salvage": "Hasarlı",
}
DRIVE_LABELS = {"fwd": "Önden çekiş", "rwd": "Arkadan itiş", "4wd": "4x4"}
BODY_LABELS = {
    "suv": "SUV",
    "sedan": "Sedan",
    "pickup": "Pikap",
    "truck": "Kamyonet",
    "hatchback": "Hatchback",
    "coupe": "Coupe",
    "convertible": "Cabrio",
    "van": "Van",
    "minivan": "Minivan",
    "wagon": "Station wagon",
    "bus": "Minibüs",
    "offroad": "Arazi",
    "other": "Diğer",
}
TITLE_STATUS_LABELS = {
    "clean": "Temiz",
    "salvage": "Ağır hasarlı",
    "rebuilt": "Ağır hasarlı (onarılmış)",
    "lien": "Rehinli",
    "missing": "Belgesiz",
    "parts only": "Parça için",
}

# ---------- Türkiye uyarlaması ----------
# Model ABD verisiyle USD tahmin eder; marka segmenti katsayı seçmek için kullanılır.
PREMIUM_BRANDS = {
    "Acura", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", "Cadillac", "Ferrari",
    "Genesis", "Infiniti", "Jaguar", "Lamborghini", "Land Rover", "Lexus", "Lincoln",
    "Maserati", "McLaren", "Mercedes-Benz", "Porsche", "Rolls-Royce", "Volvo",
}  # fmt: skip
SUV_BODY_TYPES = {"SUV", "Pikap", "Kamyonet", "Arazi"}
# Türkiye piyasa fiyatları (Kaan, 16 Kasım 2026): sahibinden.com ortalama fiyatları,
# galeri+bireysel karışık (seller_type bilinmiyor sayılır). Hepsi benzinli otomatik,
# temiz ruhsat; Tesla elektrikli.
REFERENCE_CARS = [  # (brand, model, year, km, fuel_type, body_type, fiyat_TL)
    ("Honda", "Civic", 2017, 200_000, "Benzin", "Sedan", 1_250_000),
    ("Toyota", "Corolla", 2011, 235_000, "Benzin", "Sedan", 800_000),
    ("Honda", "Accord", 2013, 175_000, "Benzin", "Sedan", 900_000),
    ("Toyota", "RAV4", 2015, 165_000, "Benzin", "SUV", 1_250_000),
    ("Jeep", "Wrangler", 2019, 70_000, "Benzin", "SUV", 4_200_000),
    ("BMW", "X5", 2020, 150_000, "Benzin", "SUV", 3_750_000),
    ("Porsche", "Cayenne", 2014, 190_000, "Benzin", "SUV", 4_150_000),
    ("Tesla", "Model 3", 2021, 130_000, "Elektrik", "Sedan", 2_200_000),
    # Düşük km'li örnekler (Kaan, 16 Kasım 2026)
    ("Honda", "Civic", 2020, 80_000, "Benzin", "Sedan", 1_750_000),
    ("Toyota", "Corolla", 2019, 100_000, "Benzin", "Sedan", 1_400_000),
    ("Toyota", "RAV4", 2021, 60_000, "Benzin", "SUV", 4_100_000),
    ("Mercedes-Benz", "C200", 2018, 90_000, "Benzin", "Sedan", 2_750_000),
]
# Yumuşak km çarpanının yükseldiği aralık. Modelin ABD fiyat kırılması bu aralıkta ölçüldü
# (120k-140k arasında tahmin yaklaşık x0,71 düşüyor); Türkiye'de böyle bir kırılma yok.
KM_RAMP = (120_000, 140_000)
KM_GRID_STEP = 1_000  # km zarfı ızgara adımı (localization.tl_price)
# Kırılma x km çarpanı en fazla 0,98 olur; böylece km arttıkça TL fiyat asla yükselmez.
MONOTONIC_MARGIN = 0.98
# Türkiye'de onarılmış araç da ağır hasar kayıtlı sayılır; iki etiket aynı kuralı alır.
HEAVY_DAMAGE_STATUSES = {"Ağır hasarlı", "Ağır hasarlı (onarılmış)"}
# Kaan'ın kararı (16 Kasım 2026): ağır hasarlı araç Türkiye'de %35 daha ucuz.
HEAVY_DAMAGE_DISCOUNT = 0.35
USE_MODEL_OVERRIDES = True  # referansı olan marka+model kendi katsayısını kullanır
