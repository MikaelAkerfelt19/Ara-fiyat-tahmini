"""Gerçek servis taslağı; GOREVLER_BACKEND.md B10 görevinde tamamlanacak."""

from src.core.schemas import CarInput, Prediction


def get_options() -> dict[str, list[str]]:
    raise NotImplementedError(
        "Henüz yazılmadı (GOREVLER_BACKEND.md, B10). Şimdilik USE_MOCK=1 kullanın."
    )


def get_models_for_brand(brand: str) -> list[str]:
    raise NotImplementedError(
        "Henüz yazılmadı (GOREVLER_BACKEND.md, B10). Şimdilik USE_MOCK=1 kullanın."
    )


def get_ranges() -> dict[str, tuple[float, float]]:
    raise NotImplementedError(
        "Henüz yazılmadı (GOREVLER_BACKEND.md, B10). Şimdilik USE_MOCK=1 kullanın."
    )


def predict(car: CarInput) -> Prediction:
    raise NotImplementedError(
        "Henüz yazılmadı (GOREVLER_BACKEND.md, B10). Şimdilik USE_MOCK=1 kullanın."
    )


def save_prediction(car: CarInput, pred: Prediction) -> None:
    raise NotImplementedError(
        "Henüz yazılmadı (GOREVLER_BACKEND.md, B10). Şimdilik USE_MOCK=1 kullanın."
    )


def get_history(limit: int = 20) -> list[dict]:
    raise NotImplementedError(
        "Henüz yazılmadı (GOREVLER_BACKEND.md, B10). Şimdilik USE_MOCK=1 kullanın."
    )


def get_model_info() -> dict:
    raise NotImplementedError(
        "Henüz yazılmadı (GOREVLER_BACKEND.md, B10). Şimdilik USE_MOCK=1 kullanın."
    )
