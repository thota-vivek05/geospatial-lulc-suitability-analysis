# Phase 5 — Machine Learning Based Suitability Analysis

This phase focuses on geospatial suitability modeling using raster-based spatial factors, proximity analysis, and machine learning-assisted workflows.

---

# Objectives

- Generate suitability factors
- Prepare spatial ML inputs
- Perform raster suitability analysis
- Develop final suitability maps
- Support spatial decision-making

---

# Workflow

1. Raster factor preparation
2. Distance analysis
3. Raster standardization
4. Suitability factor generation
5. Weighted overlay analysis
6. Final suitability map generation
7. Machine learning integration

---

# Preprocessing Layers

The preprocessing layers were generated from spatial infrastructure and environmental datasets.

### Included Layers

- Roads raster
- Roads distance raster
- Water raster
- Water distance raster

These layers were used as spatial predictors for suitability modeling.

---

# Suitability Factors

The `suitability/` folder contains thematic suitability rasters generated from different spatial factors.

### Included Factors

- Built-up suitability
- Industrial suitability
- Railway suitability
- School suitability
- Hospital suitability
- Water suitability
- Roads suitability
- LULC suitability
- Housing suitability

---

# Final Output

## `Final_Suitability_Map.tif`

Final integrated suitability map generated using multiple spatial and thematic factors.

### Applications

- Urban planning
- Site selection
- Spatial decision support
- Infrastructure planning
- Land suitability assessment

---

# Techniques Used

- Raster Reclassification
- Euclidean Distance Analysis
- Weighted Overlay Analysis
- Spatial Multi-Criteria Evaluation
- GIS Raster Modeling

---

# Machine Learning Integration

Python-based workflows were used to support suitability prediction and raster analysis.

### Technologies Used

- Python
- Scikit-learn
- Rasterio
- GDAL
- NumPy

---

# Software Used

- QGIS
- Python
- GDAL
- Raster Calculator

---

# Notes

- Temporary metadata and intermediate files were excluded from this repository.
- Final processed outputs were retained for reproducibility and visualization.

---

# Project Outcome

The generated suitability maps demonstrate the integration of remote sensing, GIS, and machine learning techniques for spatial analysis and decision support applications.