import os
from pathlib import Path

import pytest
import geopandas as gpd

from main import OkavangoData


TEST_DOWNLOADS = os.path.join(os.path.dirname(__file__), "test_downloads")


@pytest.fixture
def data_handler():
    """Create an OkavangoData instance using the test downloads folder."""
    return OkavangoData(download_dir=TEST_DOWNLOADS)


def test_function_1_downloads(data_handler):
    """
    Test for Function 1: Verifies that the download directory
    is created and contains all expected files.
    """
    assert os.path.exists(data_handler.download_dir)

    expected_files = [
        "annual_change_forest_area.csv",
        "annual_deforestation.csv",
        "terrestrial_protected_areas.csv",
        "share_degraded_land.csv",
        "red_list_index.csv",
        "ne_110m_admin_0_countries.zip",
    ]
    for filename in expected_files:
        filepath = Path(data_handler.download_dir) / filename
        assert filepath.exists(), f"Missing expected file: {filename}"


def test_function_2_merges(data_handler):
    """
    Test for Function 2: Verifies that merged_maps contains
    GeoDataFrames with the expected 'value' column from the merge.
    """
    assert len(data_handler.merged_maps) > 0, "No merged maps were created"

    for name, gdf in data_handler.merged_maps.items():
        assert isinstance(gdf, gpd.GeoDataFrame), f"{name} is not a GeoDataFrame"
        assert "value" in gdf.columns, f"{name} is missing the 'value' column"
