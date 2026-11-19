"""Servise tek giriş noktası. Backend henüz yoksa uygulama patlamaz.

Gerçek servis dosyaları (src/core/service.py, src/db, src/ml) bu çalışma
kopyasında bulunmadığında ``service`` None olur; arayüz bunu kontrol edip
kullanıcıya anlaşılır bir mesaj gösterir.
"""

try:
    from src.core.api import service
except ImportError:
    service = None

__all__ = ["service"]
