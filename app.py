import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mars Rover Data Explorer", layout="wide")

# Load data
df = pd.read_csv("rover_images_sample.csv")
df["earth_date"] = pd.to_datetime(df["earth_date"])

# Title
st.title("🚀 Mars Rover Data Explorer")
st.write("Explore rover photos by rover, camera, and date.")

# Sidebar
st.sidebar.header("Filters")

rover = st.sidebar.selectbox("Select Rover", sorted(df["rover_name"].dropna().unique()))
camera = st.sidebar.selectbox("Select Camera", sorted(df["camera_name"].dropna().unique()))

min_date = df["earth_date"].min().date()
max_date = df["earth_date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Handle date input safely
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Filter data
filtered_df = df[
    (df["rover_name"] == rover) &
    (df["camera_name"] == camera) &
    (df["earth_date"] >= pd.to_datetime(start_date)) &
    (df["earth_date"] <= pd.to_datetime(end_date))
].copy()

# Summary metrics
st.subheader("📊 Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Total Photos", len(filtered_df))
col2.metric("Selected Rover", rover)
col3.metric("Selected Camera", camera)

st.divider()

# If no results
if filtered_df.empty:
    st.warning("No photos match these filters. Try a different rover, camera, or date range.")
else:
    # Charts
    left, right = st.columns(2)

    with left:
        st.subheader("Photos Over Time")
        photos_by_date = filtered_df.groupby("earth_date").size()
        st.line_chart(photos_by_date)

    with right:
        st.subheader("Photos by Camera")
        photos_by_camera = filtered_df["camera_name"].value_counts()
        st.bar_chart(photos_by_camera)

    st.divider()

    # Image gallery
    st.subheader("📸 Photo Gallery")

    show_images = st.checkbox("Show Mars Images", value=True)

    if show_images:
        max_images = st.slider("Number of images to display", 1, min(10, len(filtered_df)), min(4, len(filtered_df)))
        image_rows = filtered_df.head(max_images)

        gallery_cols = st.columns(2)
        for i, (_, row) in enumerate(image_rows.iterrows()):
            with gallery_cols[i % 2]:
                st.image(row["image_url"], caption=f"{row['rover_name']} - {row['camera_name']}", use_container_width=True)
                st.write(f"**Date:** {row['earth_date'].date()}")
                st.write(f"**Caption:** {row['caption']}")

    st.divider()

    # Raw data
    if st.checkbox("Show Raw Data"):
        st.dataframe(filtered_df, use_container_width=True)
