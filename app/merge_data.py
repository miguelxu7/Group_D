from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import pandas as pd


@dataclass(frozen=True)
class DatasetToMerge:
    """Spec for one OWID CSV that will be merged with the Natural Earth world map."""
    name: str          # label you can show in Streamlit
    csv_filename: str  # file inside downloads/


def _infer_value_column(df: pd.DataFrame) -> str:
    """
    OWID grapher CSVs usually have columns like: Entity, Code, Year, <value>.
    This function picks the value column automatically.
    """
    preferred_drop = {"Entity", "Code", "Year"}
    candidates = [c for c in df.columns if c not in preferred_drop]

    if not candidates:
        raise ValueError(f"Could not infer value column. Columns found: {list(df.columns)}")

    # In OWID grapher data, the value column is typically the last column
    return candidates[-1]


def _latest_per_country(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only the latest year per country (Code).
    This avoids multiple rows per country and makes mapping straightforward.
    """
    df = df.dropna(subset=["Code"])
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df.dropna(subset=["Year"])

    df = df.sort_values(["Code", "Year"])
    return df.groupby("Code", as_index=False).tail(1)


def merge_map_with_datasets(downloads_dir: str | Path = "downloads") -> dict[str, gpd.GeoDataFrame]:
    """
    Function 2 (required):
    Merges the Natural Earth world map with each OWID dataset.

    IMPORTANT:
    - Uses GeoPandas
    - Left dataframe is the GeoDataFrame (world map)
    - Returns multiple GeoDataFrames (one per dataset)
    """
    downloads_path = Path(downloads_dir)

    # 1) Load map (ZIP shapefile) as GeoDataFrame
    world_path = downloads_path / "ne_110m_admin_0_countries.zip"
    if not world_path.exists():
        raise FileNotFoundError(f"Map file not found: {world_path}. Run Function 1 first.")

    world = gpd.read_file(world_path)

    # Natural Earth ISO code column (usually ISO_A3). Some rows may contain '-99' as missing.
    if "ISO_A3" not in world.columns:
        raise ValueError(f"'ISO_A3' not found in Natural Earth data. Columns: {list(world.columns)}")

    world["ISO_A3"] = world["ISO_A3"].replace("-99", pd.NA)

    # 2) Define which OWID CSVs to merge (these match your Function 1 filenames)
    specs = [
        DatasetToMerge("Annual change in forest area (latest)", "annual_change_forest_area.csv"),
        DatasetToMerge("Annual deforestation (latest)", "annual_deforestation.csv"),
        DatasetToMerge("Terrestrial protected areas (latest)", "terrestrial_protected_areas.csv"),
        DatasetToMerge("Share degraded land (latest)", "share_degraded_land.csv"),
        DatasetToMerge("Red List Index (latest)", "red_list_index.csv"),
    ]

    merged_maps: dict[str, gpd.GeoDataFrame] = {}

    for spec in specs:
        csv_path = downloads_path / spec.csv_filename
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset not found: {csv_path}. Run Function 1 first.")

        df = pd.read_csv(csv_path)

        required = {"Entity", "Code", "Year"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{spec.csv_filename} missing columns {missing}. Found: {list(df.columns)}")

        value_col = _infer_value_column(df)

        # keep only needed columns and latest year per country
        latest = _latest_per_country(df[["Entity", "Code", "Year", value_col]].copy())

        # 3) Merge (LEFT must be the GeoDataFrame)
        merged = world.merge(
            latest,
            how="left",
            left_on="ISO_A3",
            right_on="Code",
        )

        # Rename the generic OWID value column to something consistent for plotting
        merged = merged.rename(columns={value_col: "value"})

        merged_maps[spec.name] = merged

    return merged_maps


if __name__ == "__main__":
    maps = merge_map_with_datasets()
    print("Merged datasets:")
    for name, gdf in maps.items():
        # how many countries got data merged?
        merged_count = gdf["value"].notna().sum()
        print(f"- {name}: rows={len(gdf)}, merged_values={merged_count}")