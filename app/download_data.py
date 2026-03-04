from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import time
import requests

print("download_data.py is running")

@dataclass(frozen=True)
class DatasetSpec:
    """Represents a dataset to download."""
    filename: str
    url: str


class DownloadError(RuntimeError):
    """Raised when a dataset cannot be downloaded."""
    pass


def _download_file(url: str, destination: Path, timeout: int = 60, retries: int = 3) -> None:
    """
    Download a file from a URL with retry logic.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)

    last_exception: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, stream=True, timeout=timeout) as response:
                response.raise_for_status()

                with destination.open("wb") as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)

            print(f"Downloaded: {destination.name}")
            return

        except Exception as e:
            last_exception = e
            print(f"Retry {attempt}/{retries} for {destination.name}...")
            time.sleep(min(2 ** attempt, 8))

    raise DownloadError(f"Failed to download {url}") from last_exception


def download_required_datasets(
    downloads_dir: str | Path = "downloads",
    force: bool = False
) -> list[Path]:
    """
    Function 1:
    Downloads all required datasets into the downloads directory.

    Parameters
    ----------
    downloads_dir : str | Path
        Directory where datasets will be stored.
    force : bool
        If True, re-download files even if they already exist.

    Returns
    -------
    list[Path]
        List of file paths downloaded or already present.
    """

    downloads_path = Path(downloads_dir)

    datasets = [
        DatasetSpec(
            filename="annual_change_forest_area.csv",
            url="https://ourworldindata.org/grapher/annual-change-forest-area.csv",
        ),
        DatasetSpec(
            filename="annual_deforestation.csv",
            url="https://ourworldindata.org/grapher/annual-deforestation.csv",
        ),
        DatasetSpec(
            filename="terrestrial_protected_areas.csv",
            url="https://ourworldindata.org/grapher/terrestrial-protected-areas.csv",
        ),
        DatasetSpec(
            filename="share_degraded_land.csv",
            url="https://ourworldindata.org/grapher/share-degraded-land.csv",
        ),
        DatasetSpec(
            filename="red_list_index.csv",
            url="https://ourworldindata.org/grapher/red-list-index.csv",
        ),
        DatasetSpec(
            filename="ne_110m_admin_0_countries.zip",
            url="https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip",
        ),
    ]

    downloaded_files: list[Path] = []

    for dataset in datasets:
        destination = downloads_path / dataset.filename

        if destination.exists() and not force:
            print(f"Already exists: {destination.name}")
            downloaded_files.append(destination)
            continue

        _download_file(dataset.url, destination)
        downloaded_files.append(destination)

    return downloaded_files


if __name__ == "__main__":
    files = download_required_datasets()
    print("\nAll datasets ready:")
    for file in files:
        print(f" - {file}")