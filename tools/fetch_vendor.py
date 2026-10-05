"""Fetch pinned frontend assets so visitors never contact a third-party CDN."""
from pathlib import Path
from urllib.request import urlopen

DESTINATION = Path(__file__).resolve().parents[1] / "app" / "static" / "vendor"
ASSETS = {
    "bootstrap.min.css": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css",
    "bootstrap-icons.min.css": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css",
    "fonts/bootstrap-icons.woff2": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/fonts/bootstrap-icons.woff2",
    "fonts/bootstrap-icons.woff": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/fonts/bootstrap-icons.woff",
    "chart.umd.min.js": "https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js",
    "licenses/bootstrap.txt": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/LICENSE",
    "licenses/bootstrap-icons.txt": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/LICENSE",
    "licenses/chartjs.txt": "https://cdn.jsdelivr.net/npm/chart.js@4.5.1/LICENSE.md",
}

if __name__ == "__main__":
    for filename, url in ASSETS.items():
        target = DESTINATION / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(url, timeout=30) as response:
            target.write_bytes(response.read())
        print(f"Downloaded {filename}")
