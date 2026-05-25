# Phase 3 — Spectral Indices Analysis

This phase focuses on generating and analyzing spectral indices derived from multispectral satellite imagery for vegetation, water, and built-up area assessment.

---

# Objectives

- Generate vegetation indices
- Analyze water bodies
- Identify built-up regions
- Improve land suitability analysis
- Prepare raster factors for machine learning

---

# Spectral Indices Generated

## NDVI — Normalized Difference Vegetation Index

Used for vegetation health and density analysis.

### Formula

NDVI = (NIR - Red) / (NIR + Red)

### Output

- `NDVI_Medchal.tif`

### Applications

- Vegetation monitoring
- Agricultural analysis
- Land cover assessment

---

## NDBI — Normalized Difference Built-up Index

Used for identifying urban and built-up areas.

### Formula

NDBI = (SWIR - NIR) / (SWIR + NIR)

### Output

- `NDBI_Medchal.tif`

### Applications

- Urban expansion analysis
- Built-up area extraction
- Infrastructure mapping

---

## NDWI — Normalized Difference Water Index

Used for detecting water bodies and moisture content.

### Formula

NDWI = (Green - NIR) / (Green + NIR)

### Output

- `NDWI_Medchal.tif`

### Applications

- Water body detection
- Hydrological analysis
- Surface water mapping

---

## SAVI — Soil Adjusted Vegetation Index

Used to reduce soil brightness effects in vegetation analysis.

### Formula

SAVI = ((NIR - Red) / (NIR + Red + L)) × (1 + L)

Where:
- L = Soil brightness correction factor

### Output

- `SAVI_Medchal.tif`

### Applications

- Sparse vegetation analysis
- Dryland vegetation mapping
- Agricultural monitoring

---

# Workflow

1. Multispectral raster preparation
2. Band extraction
3. Spectral index calculation
4. Raster normalization
5. Output generation
6. Visualization and interpretation

---

# Software and Tools Used

- QGIS
- Raster Calculator
- GDAL
- Python

---

# Applications in Project

The generated indices were later used for:

- LULC classification
- Suitability mapping
- Spatial factor generation
- Machine learning workflows

---

# Notes

- Final processed outputs were retained for reproducibility.
- Intermediate and duplicate rasters were removed to maintain repository efficiency.

---

# Next Phase

The outputs from this phase are used in:

- Phase 4 — LULC Suitability Mapping
- Phase 5 — Machine Learning Analysis