import os

if os.getenv("USE_MOCK", "0") == "1":
    from src.core import mock_service as service
else:
    from src.core import service

__all__ = ["service"]
