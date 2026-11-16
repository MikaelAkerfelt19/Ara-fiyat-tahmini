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
]
FEATURES = NUM_COLS + CAT_COLS
RANDOM_STATE = 42
RAW_TRAIN_PATH = "data/raw/train_data_v2.csv"
RAW_TEST_PATH = "data/raw/test_data_v2.csv"
MILE_TO_KM = 1.609344
MIN_PRICE_USD = 500

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
    "salvage": "Pert kayıtlı",
    "rebuilt": "Onarılmış pert",
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
# Türkiye piyasa fiyatları (Kaan, sahibinden/arabam.com, 16 Kasım 2026). Hepsi benzinli otomatik,
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
]
USE_MODEL_OVERRIDES = True  # referansı olan marka+model kendi katsayısını kullanır
