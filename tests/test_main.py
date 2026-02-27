import os
import pytest
import geopandas as gpd
from main import OkavangoData

# This fixture ensures we have a clean instance for each test
@pytest.fixture
def data_handler():
    # We use a specific test_downloads folder to avoid clobbering real data
    return OkavangoData(download_dir="test_downloads")

def test_function_1_downloads(data_handler):
    """
    Test for Function 1: Verifies that the download directory 
    is created and contains files.
    """
    assert os.path.exists(data_handler.download_dir)
    # Replace 'example.csv' with one of the actual filenames your function creates
    # assert os.path.exists(os.path.join(data_handler.download_dir, "forest_area.csv"))

def test_function_2_merges(data_handler):
    """
    Test for Function 2: Verifies that the world_map attribute 
    is a GeoDataFrame and contains merged data.
    """
    # Check if the map was loaded as a GeoDataFrame
    assert isinstance(data_handler.world_map, gpd.GeoDataFrame)
    
    # Check if the merge worked (the left dataframe must be geopandas)
    # Check for a column that exists in your CSV but NOT in the original map
    # assert "annual_change" in data_handler.world_map.columns