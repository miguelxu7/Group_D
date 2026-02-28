"""
Main module for Project Okavango.

Contains the OkavangoData class that orchestrates downloading,
merging, and storing all environmental datasets used by the
Streamlit application.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import geopandas as gpd
import pandas as pd
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field

from app.download_data import download_required_datasets
from app.merge_data import merge_map_with_datasets


class OkavangoData(BaseModel):
    """
    Central data handler for Project Okavango.

    On initialisation the class:
      1. Downloads every required dataset (Function 1).
      2. Reads each raw CSV into a pandas DataFrame.
      3. Merges every dataset with the world map (Function 2).

    Attributes
    ----------
    download_dir : str
        Path to the directory where datasets are stored.
    datasets : Dict[str, pd.DataFrame]
        Raw CSV data keyed by dataset name.
    merged_maps : Dict[str, gpd.GeoDataFrame]
        GeoDataFrames resulting from merging each dataset
        with the Natural Earth world map.
    downloaded_files : List[Path]
        Paths returned by the download step.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    download_dir: str = "downloads"
    datasets: Dict[str, pd.DataFrame] = Field(default_factory=dict)
    merged_maps: Dict[str, gpd.GeoDataFrame] = Field(default_factory=dict)
    downloaded_files: List[Path] = Field(default_factory=list)

    def __init__(self, download_dir: str = "downloads", **kwargs) -> None:
        """
        Initialise OkavangoData.

        Parameters
        ----------
        download_dir : str, optional
            Directory for downloaded files (default: "downloads").
        """
        super().__init__(download_dir=download_dir, **kwargs)

        # Function 1 — download all datasets
        self.downloaded_files = self.fetch_all_data()

        # Read raw CSVs into DataFrames
        self._load_raw_datasets()

        # Function 2 — merge each dataset with the world map
        self.merged_maps = self.process_and_merge_data()

    def fetch_all_data(self) -> List[Path]:
        """
        Execute Function 1: download every required dataset.

        Returns
        -------
        List[Path]
            File paths of all downloaded (or already cached) datasets.
        """
        return download_required_datasets(downloads_dir=self.download_dir)

    def _load_raw_datasets(self) -> None:
        """
        Read each downloaded CSV into a pandas DataFrame and store
        them in the ``datasets`` dictionary.
        """
        csv_files: Dict[str, str] = {
            "annual_change_forest_area": "annual_change_forest_area.csv",
            "annual_deforestation": "annual_deforestation.csv",
            "terrestrial_protected_areas": "terrestrial_protected_areas.csv",
            "share_degraded_land": "share_degraded_land.csv",
            "red_list_index": "red_list_index.csv",
        }

        downloads_path = Path(self.download_dir)

        for name, filename in csv_files.items():
            filepath = downloads_path / filename
            if filepath.exists():
                self.datasets[name] = pd.read_csv(filepath)
            else:
                print(f"Warning: {filepath} not found, skipping.")

    def process_and_merge_data(self) -> Dict[str, gpd.GeoDataFrame]:
        """
        Execute Function 2: merge the world map with each OWID dataset.

        Returns
        -------
        Dict[str, gpd.GeoDataFrame]
            Merged GeoDataFrames keyed by dataset label.
        """
        return merge_map_with_datasets(downloads_dir=self.download_dir)


if __name__ == "__main__":
    data = OkavangoData()

    print("\n=== Raw datasets loaded ===")
    for name, df in data.datasets.items():
        print(f"  {name}: {df.shape[0]} rows, {df.shape[1]} columns")

    print("\n=== Merged maps ===")
    for name, gdf in data.merged_maps.items():
        merged_count = gdf["value"].notna().sum()
        print(f"  {name}: {len(gdf)} rows, {merged_count} countries with data")