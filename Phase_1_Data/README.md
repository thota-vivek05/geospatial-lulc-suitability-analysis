# Phase 1 — Data Collection and Preparation

This phase contains the foundational datasets used for the Geospatial LULC Suitability Mapping project.  
The data includes administrative boundaries, satellite imagery, and thematic vector layers used for preprocessing, NDVI analysis, land use classification, and suitability analysis.

---

# Objectives

- Collect and organize geospatial datasets
- Prepare study area boundary data
- Acquire and preprocess satellite imagery
- Extract thematic vector layers for analysis
- Prepare spatial datasets for GIS workflows

---

# Study Area

The project focuses on the Medchal–Malkajgiri region, Telangana, India.

---

# Folder Structure

## Boundary_Data/

Contains administrative and cleaned boundary datasets used to clip and preprocess raster and vector layers.

### Important Files

- `Medchal_Malkajgiri_Boundary.geojson`
- `Medchal_Malkajgiri_Boundary_clean_32644.shp`

### Purpose

- Define study area extent
- Raster clipping
- Coordinate system standardization
- Spatial masking

---

## Satellite_Image/

Contains georeferenced and clipped satellite imagery used for remote sensing analysis.

### Important Files

- `LISSIII_Medchal_GeoRef.tif`
- `LISSIII_Medchal_GeoRef_Clipped.tif`

### Purpose

- NDVI generation
- Land Use Land Cover (LULC) classification
- Raster analysis
- Machine learning workflows

### Satellite Information

- Sensor: IRS LISS III
- Image Type: Multispectral Raster
- Coordinate System: UTM Zone 44N (EPSG:32644)

---

## vectors/

Contains clipped vector layers used for thematic and proximity analysis.

### Example Layers

- Roads
- Water bodies
- Transportation networks

### Purpose

- Spatial analysis
- Proximity calculations
- Suitability factor generation

---

## vector_boundary/

Contains thematic KML layers extracted and prepared for geospatial analysis.

### Included Layers

- Roads
- Railways
- Water bodies
- Built-up areas
- Vegetation
- Schools
- Hospitals
- Industrial zones
- Points of Interest (POI)

### Purpose

These datasets were used for:

- LULC analysis
- Spatial factor generation
- Infrastructure mapping
- Suitability modeling

---

# Software and Tools Used

- QGIS
- Python
- GDAL
- Rasterio
- GeoPandas

---

# Coordinate Reference System (CRS)

Most processed datasets use:

EPSG:32644 — WGS 84 / UTM Zone 44N

---

# Data Processing Workflow

1. Data collection
2. Boundary cleaning
3. Coordinate reprojection
4. Satellite image clipping
5. Vector extraction
6. Layer organization
7. Preparation for preprocessing and analysis

---

# Notes

- Temporary GIS metadata files (`.qmd`, `.aux.xml`) were excluded from this repository.
- Large raw datasets and downloaded archives were removed to maintain repository efficiency.
- This repository contains only the processed and essential datasets required for reproducibility and demonstration.

---

# Next Phase

The prepared datasets from this phase are used in:

- Phase 2 — Preprocessing
- Phase 3 — NDVI Analysis
- Phase 4 — LULC Classification
- Phase 5 — Machine Learning Suitability Analysis
