"""Ekran görüntülerini gerçek servisle üretir.

Kullanım: .venv/bin/python scripts/screenshots.py
Sahte servisle üretmek için: USE_MOCK=1 .venv/bin/python scripts/screenshots.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "img"
PORT = 8512
URL = f"http://localhost:{PORT}"


def _sunucuyu_baslat() -> subprocess.Popen:
    env = dict(os.environ)  # USE_MOCK ayarlandıysa sahte servis kullanılır
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(ROOT / "app.py"),
            "--server.headless",
            "true",
            "--server.port",
            str(PORT),
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(60):
        try:
            with urllib.request.urlopen(URL, timeout=1) as response:
                if response.status == 200:
                    return proc
        except OSError:  # sunucu henüz ayakta değil
            time.sleep(0.5)
    proc.terminate()
    raise RuntimeError("Streamlit sunucusu başlamadı.")


def _sec(page, label: str, value: str) -> None:
    combo = page.get_by_role("combobox", name=label, exact=True)
    combo.click()
    combo.fill(value)
    page.get_by_role("option", name=value, exact=True).click()
    page.wait_for_timeout(700)


def _formu_doldur(page) -> None:
    _sec(page, "Marka", "Toyota")
    _sec(page, "Model", "Corolla")
    _sec(page, "Model yılı", "2015")
    _sec(page, "Kilometre", "100.000")
    _sec(page, "Yakıt", "Benzin")
    _sec(page, "Vites", "Otomatik")


def _tahmin_et(page) -> None:
    page.get_by_role("button", name="Fiyatı Tahmin Et").click()
    page.wait_for_selector("text=Tahmini fiyat", timeout=60_000)
    page.wait_for_selector("h2", timeout=60_000)
    page.wait_for_timeout(1500)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    proc = _sunucuyu_baslat()
    try:
        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(headless=True)

            page = browser.new_page(viewport={"width": 1200, "height": 1200})
            page.goto(URL)
            page.wait_for_selector('input[aria-label="Marka"]', timeout=30_000)
            page.screenshot(path=str(OUT / "bos_form.png"), full_page=True)
            page.close()

            page = browser.new_page(viewport={"width": 1200, "height": 1500})
            page.goto(URL)
            page.wait_for_selector('input[aria-label="Marka"]', timeout=30_000)
            _formu_doldur(page)
            _tahmin_et(page)
            page.screenshot(path=str(OUT / "sonuc.png"), full_page=True)

            page.get_by_text("Son tahminler", exact=True).click()
            page.wait_for_timeout(800)
            page.screenshot(path=str(OUT / "son_tahminler.png"), full_page=True)
            page.close()

            phone = browser.new_page(
                viewport={"width": 390, "height": 1200}, device_scale_factor=2
            )
            phone.goto(URL)
            phone.wait_for_selector('input[aria-label="Marka"]', timeout=30_000)
            _formu_doldur(phone)
            _tahmin_et(phone)
            phone.screenshot(path=str(OUT / "telefon.png"), full_page=True)
            phone.close()

            browser.close()
    finally:
        proc.terminate()
        proc.wait()

    print("Üretilenler:", ", ".join(p.name for p in sorted(OUT.glob("*.png"))))


if __name__ == "__main__":
    main()
