# Phase 2 — Image Preprocessing and Georeferencing

This phase focuses on preprocessing multispectral satellite imagery for geospatial analysis and machine learning workflows.

---

# Objectives

- Perform image georeferencing
- Reproject raster datasets
- Create multiband raster stacks
- Prepare thematic vector layers
- Generate classified raster outputs

---

# Processing Workflow

1. Satellite image preparation
2. Ground Control Point (GCP) collection
3. Georeferencing
4. CRS reprojection to UTM Zone 44N
5. Raster stacking
6. Nearest-neighbor resampling
7. Thematic layer preparation
8. Initial LULC classification preparation

---

# Main Files

## Raster Data

### `LISSIII_Multiband.vrt`

Virtual raster stack combining multispectral bands.

### `LISSIII_Multiband_GeoReferenced_UTM_32644_NN_24.tif`

Final georeferenced and projected multispectral raster used for further analysis.

---

# Georeferencing

The `georef/` folder contains Ground Control Point (GCP) files used during manual georeferencing.

### Included Files

- `.points` files generated in QGIS Georeferencer

---

# Vector Layers

The `Vector/` folder contains thematic shapefiles used for spatial analysis.

### Included Layers

- Built-up areas
- Hospitals
- Industrial zones
- Railways
- Schools

These layers were used for:

- Proximity analysis
- Suitability modeling
- Spatial factor generation

---

# Classification

The `classification/` folder contains preliminary LULC classification outputs.

### Included Files

- `LULC_Medchal_ML.tif`

---

# Software Used

- QGIS
- GDAL
- SCP Plugin
- Python

---

# Coordinate Reference System

EPSG:32644 — WGS 84 / UTM Zone 44N

---

# Notes

- Intermediate temporary rasters and metadata files were excluded from this repository.
- Only essential preprocessing outputs required for reproducibility were retained.

---

# Next Phase

The outputs from this phase are used in:

- Phase 3 — NDVI Analysis
- Phase 4 — LULC Suitability Mapping
- Phase 5 — Machine Learning Analysis