import os
import geopandas as gpd
import pandas as pd
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any

class OkavangoData(BaseModel):
    # Allow arbitrary types for geopandas and pandas objects
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    download_dir: str = "downloads"
    datasets: Dict[str, pd.DataFrame] = {}
    world_map: gpd.GeoDataFrame = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Phase 2 Requirement: During __init__, both functions are executed
        self._ensure_dir_exists()
        self.fetch_all_data()
        self.process_and_merge_data()

    def _ensure_dir_exists(self) -> None:
        """Creates the downloads directory if it doesn't exist."""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def fetch_all_data(self) -> None:
        """
        Function 1 logic: Downloads required datasets.
        """
        # Paste your friend's Function 1 logic here
        # Example: data.to_csv(f"{self.download_dir}/forest_area.csv")
        pass

    def process_and_merge_data(self) -> None:
        """
        Function 2 logic: Merges map with datasets.
        The left dataframe MUST be the geopandas dataframe.
        """
        # Load the map
        self.world_map = gpd.read_file("ne_110m_admin_0_countries.zip")
        
        # Paste your friend's Function 2 logic here to merge
        # Ensure self.world_map is updated with the merged data
        pass

print("hello")