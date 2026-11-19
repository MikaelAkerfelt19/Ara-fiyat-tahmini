"""Testler her zaman sahte servisle çalışır."""

import os

os.environ["USE_MOCK"] = "1"

import pytest

import src.core.mock_service as ms


@pytest.fixture(autouse=True)
def temiz_gecmis() -> None:
    ms._HISTORY.clear()
