from dataclasses import asdict, dataclass


@dataclass
class CarInput:
    """Arayüzün formdan topladığı araç bilgisi."""

    brand: str
    model: str
    year: int
    mileage: int
    fuel_type: str
    transmission: str
    # TODO(Hafta 1): DATA.md kesinleşince veri setindeki sütunlara göre güncelle

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Prediction:
    """Servisin döndürdüğü tahmin."""

    price: float
    low: float | None  # olası aralığın alt sınırı (yoksa None)
    high: float | None  # olası aralığın üst sınırı (yoksa None)
    model_version: str
