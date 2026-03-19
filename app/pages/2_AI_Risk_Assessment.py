"""
Page 2 — AI-powered Environmental Risk Assessment.

Allows users to select a location, download a satellite image from
ESRI World Imagery, and run Ollama models to detect environmental danger.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on the path so main and app modules are importable
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from PIL import Image

from app.ai_workflow import run_pipeline

st.set_page_config(page_title="AI Risk Assessment | Project Okavango", layout="wide")

st.title("AI Environmental Risk Assessment")
st.markdown(
    "Select a location on Earth. A satellite image will be downloaded and "
    "analysed by AI models to determine whether the area shows signs of "
    "environmental danger."
)

# ---------------------------------------------------------------------------
# Sidebar — input controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Location Settings")
    lat = st.number_input(
        "Latitude", min_value=-90.0, max_value=90.0, value=0.0, step=0.1, format="%.4f"
    )
    lon = st.number_input(
        "Longitude", min_value=-180.0, max_value=180.0, value=0.0, step=0.1, format="%.4f"
    )
    zoom = st.slider("Zoom Level", min_value=5, max_value=17, value=10)
    st.caption("Higher zoom = more detail, smaller area covered.")

    st.divider()
    run_btn = st.button("Analyse Area", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------
if run_btn:
    config_path = str(ROOT / "models.yaml")
    images_dir = str(ROOT / "images")
    db_path = str(ROOT / "database" / "images.csv")

    with st.spinner("Running AI pipeline — this may take a couple of minutes..."):
        try:
            result = run_pipeline(
                lat=lat,
                lon=lon,
                zoom=zoom,
                config_path=config_path,
                images_dir=images_dir,
                db_path=db_path,
            )
        except Exception as e:
            st.error(f"Pipeline error: {e}")
            st.stop()

    if result.get("from_cache"):
        st.info("Result loaded from cache — this location was already analysed.")

    # -----------------------------------------------------------------------
    # Row 1: satellite image + image description side by side
    # -----------------------------------------------------------------------
    st.subheader("Satellite Image & Description")
    col_img, col_desc = st.columns(2)

    with col_img:
        img_path = Path(result["image_path"])
        if img_path.exists():
            st.image(
                str(img_path),
                caption=f"Lat: {lat}  |  Lon: {lon}  |  Zoom: {zoom}",
                use_container_width=True,
            )
        else:
            st.warning("Image file not found on disk.")

    with col_desc:
        st.markdown(f"**Vision model:** `{result['image_model']}`")
        st.write(result["image_description"])

    # -----------------------------------------------------------------------
    # Row 2: danger assessment
    # -----------------------------------------------------------------------
    st.subheader("Environmental Risk Assessment")
    st.markdown(f"**Assessment model:** `{result['text_model']}`")

    with st.expander("Full model response", expanded=True):
        import re
        # Re-format numbered items onto separate lines for readability
        formatted = re.sub(r"\s*(\d+)\.\s", r"\n\n\1. ", result["text_description"])
        # Put "Overall" summary on its own line too
        formatted = re.sub(r"\s*(Overall\b)", r"\n\n\1", formatted)
        st.markdown(formatted.strip())

    # Visual danger indicator
    danger_flag = str(result.get("danger", "N")).strip().upper()
    if danger_flag == "Y":
        st.error("ENVIRONMENTAL DANGER DETECTED", icon="🚨")
    else:
        st.success("No significant environmental danger detected", icon="✅")

    # -----------------------------------------------------------------------
    # Row 3: metadata
    # -----------------------------------------------------------------------
    with st.expander("Run details"):
        st.markdown(f"- **Timestamp:** {result.get('timestamp', 'N/A')}")
        st.markdown(f"- **Image saved at:** `{result.get('image_path', 'N/A')}`")
        st.markdown(f"- **Loaded from cache:** {result.get('from_cache', False)}")
