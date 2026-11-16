from dataclasses import asdict, dataclass


@dataclass
class CarInput:
    """Arayüzün formdan topladığı araç bilgisi. `mileage` KİLOMETRE cinsindendir."""

    brand: str
    model: str
    year: int
    mileage: int  # kilometre (km)
    fuel_type: str
    transmission: str
    # İsteğe bağlı alanlar; bilinmiyorsa None
    condition: str | None = None
    cylinders: int | None = None
    drive: str | None = None
    body_type: str | None = None
    title_status: str | None = None
    seller_type: str | None = None  # "Galeri" / "Bireysel"; bilinmiyorsa None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Prediction:
    """Servisin döndürdüğü tahmin. price, low ve high TL cinsindendir."""

    price: float  # TL
    low: float | None  # olası aralığın alt sınırı, TL (yoksa None)
    high: float | None  # olası aralığın üst sınırı, TL (yoksa None)
    model_version: str
    currency: str = "TRY"
    usd_try: float | None = None  # tahminde kullanılan USD/TRY kuru
