import { useEffect, useRef, useState } from "react";
import {
  GeoJSON,
  MapContainer,
  Marker,
  Popup,
  ScaleControl,
  TileLayer,
  useMap,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import parseGeoraster from "georaster";
import GeoRasterLayer from "georaster-layer-for-leaflet";
import proj4 from "proj4";
import "leaflet/dist/leaflet.css";

const MAP_CENTER = [17.44, 78.69];
const DEFAULT_ZOOM = 11;
const SUITABILITY_BOUNDS = [
  [17.358440573347714, 78.3501502662344],
  [17.712471495159793, 78.75709009450597],
];

const QGIS_SUITABILITY_VALUES = {
  low: 1.8,
  medium: 2.4,
  high: 2.900001,
};

const SUITABILITY_CLASS_LIMITS = {
  low: 2.1,
  medium: 2.5,
};

const SUITABILITY_COLOR = {
  low: "#C62828",
  medium: "#F9A825",
  high: "#2E7D32",
};

if (typeof window !== "undefined" && !window.proj4) {
  window.proj4 = proj4;
}

const layerConfig = {
  roads: {
    url: "/data/roads.geojson",
    style: { color: "#000000", weight: 2.2 },
  },
  waterBodies: {
    url: "/data/water_poly.geojson",
    style: {
      color: "#1d4ed8",
      fillColor: "#2563eb",
      fillOpacity: 0.35,
      weight: 1,
    },
  },
  industrial: {
    url: "/data/industrial.geojson",
    style: {
      color: "#7e22ce",
      fillColor: "#a855f7",
      fillOpacity: 0.35,
      weight: 1,
    },
  },
  hospitals: {
    url: "/data/hospitals.geojson",
    style: {
      color: "#dc2626",
      fillColor: "#ef4444",
      fillOpacity: 0.8,
      weight: 1,
      radius: 5,
    },
  },
  schools: {
    url: "/data/schools.geojson",
    style: {
      color: "#16a34a",
      fillColor: "#22c55e",
      fillOpacity: 0.8,
      weight: 1,
      radius: 5,
    },
  },
  railway: {
    url: "/data/railway.geojson",
    style: { color: "#111827", weight: 2, dashArray: "8 6" },
  },
};

const hospitalIcon = L.divIcon({
  className: "poi-icon hospital-icon",
  html: "<span>+</span>",
  iconSize: [22, 22],
  iconAnchor: [11, 11],
});

const schoolIcon = L.divIcon({
  className: "poi-icon school-icon",
  html: "<span>S</span>",
  iconSize: [22, 22],
  iconAnchor: [11, 11],
});

const searchIcon = L.divIcon({
  className: "poi-icon search-icon",
  html: "<span>*</span>",
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

const suitabilityAdvice = {
  high: "Recommended for housing",
  medium: "Conditionally suitable",
  low: "Least suitable for housing",
};

const suitabilityReason = {
  high: "Near roads and schools, away from industrial areas, with balanced vegetation.",
  medium:
    "Moderate access to services with some constraints from surrounding factors.",
  low: "Limited accessibility and/or higher proximity to constraints like industry.",
};

function classifySuitability(value) {
  if (!Number.isFinite(value) || value < -1e20) {
    return null;
  }

  if (value < SUITABILITY_CLASS_LIMITS.low) {
    return "low";
  }

  if (value < SUITABILITY_CLASS_LIMITS.medium) {
    return "medium";
  }

  return "high";
}

function sampleSuitabilityAtLatLng(georaster, latlng) {
  if (!georaster || !latlng) {
    return null;
  }

  const width = georaster.width;
  const height = georaster.height;
  const xmin = georaster.xmin;
  const xmax = georaster.xmax;
  const ymin = georaster.ymin;
  const ymax = georaster.ymax;

  if (
    latlng.lng < xmin ||
    latlng.lng > xmax ||
    latlng.lat < ymin ||
    latlng.lat > ymax
  ) {
    return null;
  }

  const xRatio = (latlng.lng - xmin) / (xmax - xmin);
  const yRatio = (ymax - latlng.lat) / (ymax - ymin);

  const col = Math.max(0, Math.min(width - 1, Math.floor(xRatio * width)));
  const row = Math.max(0, Math.min(height - 1, Math.floor(yRatio * height)));

  const rasterBand = georaster.values?.[0];
  if (!rasterBand || !rasterBand[row]) {
    return null;
  }

  const rawValue = rasterBand[row][col];
  return classifySuitability(rawValue);
}

function SuitabilityClassLayer({
  enabled,
  suitabilityFilter,
  onRasterReady,
  onLoadingChange,
}) {
  const map = useMap();
  const georasterRef = useRef(null);
  const rasterLayerRef = useRef(null);

  useEffect(() => {
    let cancelled = false;

    const clearLayer = () => {
      if (rasterLayerRef.current && map.hasLayer(rasterLayerRef.current)) {
        map.removeLayer(rasterLayerRef.current);
      }
      rasterLayerRef.current = null;
    };

    if (!enabled) {
      clearLayer();
      return () => {
        cancelled = true;
      };
    }

    const renderSuitability = async () => {
      try {
        onLoadingChange?.(true);

        if (!georasterRef.current) {
          const response = await fetch("/raster/final_suitability.tif");
          if (!response.ok) {
            throw new Error("Failed to fetch final_suitability.tif");
          }
          const arrayBuffer = await response.arrayBuffer();
          georasterRef.current = await parseGeoraster(arrayBuffer);
          onRasterReady?.(georasterRef.current);
        }

        if (cancelled || !georasterRef.current) {
          return;
        }

        clearLayer();
        const selectedClass = suitabilityFilter || null;

        rasterLayerRef.current = new GeoRasterLayer({
          georaster: georasterRef.current,
          opacity: 0.45,
          resolution: 512,
          resampleMethod: "bilinear",
          mask: "/data/boundary.geojson",
          mask_srs: "EPSG:4326",
          mask_strategy: "outside",
          pixelValuesToColorFn: (values) => {
            const rawValue = values?.[0];
            const className = classifySuitability(rawValue);

            if (!className) {
              return null;
            }

            if (selectedClass && className !== selectedClass) {
              return null;
            }

            return SUITABILITY_COLOR[className];
          },
        });

        if (!cancelled && rasterLayerRef.current) {
          rasterLayerRef.current.addTo(map);
        }
      } catch (error) {
        clearLayer();
        console.warn(
          "GeoTIFF suitability render failed, using PNG fallback.",
          error,
        );
      } finally {
        onLoadingChange?.(false);
      }
    };

    renderSuitability();

    return () => {
      cancelled = true;
      clearLayer();
    };
  }, [enabled, map, suitabilityFilter, onRasterReady, onLoadingChange]);

  return null;
}

function SuitabilityInteraction({ enabled, georasterData }) {
  const [clickedPoint, setClickedPoint] = useState(null);
  const [clickedClass, setClickedClass] = useState(null);

  useMapEvents({
    click(event) {
      if (!enabled || !georasterData) {
        setClickedPoint(null);
        setClickedClass(null);
        return;
      }

      const className = sampleSuitabilityAtLatLng(georasterData, event.latlng);
      if (!className) {
        setClickedPoint(null);
        setClickedClass(null);
        return;
      }

      setClickedPoint(event.latlng);
      setClickedClass(className);
    },
  });

  if (!clickedPoint || !clickedClass) {
    return null;
  }

  return (
    <Popup position={[clickedPoint.lat, clickedPoint.lng]}>
      <strong>Suitability: {clickedClass.toUpperCase()}</strong>
      <br />
      {suitabilityAdvice[clickedClass]}
      <br />
      <strong>Reason:</strong> {suitabilityReason[clickedClass]}
    </Popup>
  );
}

function CoordinatesDisplay() {
  const [coords, setCoords] = useState(null);

  useMapEvents({
    mousemove(event) {
      setCoords(event.latlng);
    },
    mouseout() {
      setCoords(null);
    },
  });

  return (
    <div className="coordinates-display">
      {coords
        ? `Lat: ${coords.lat.toFixed(5)} | Lon: ${coords.lng.toFixed(5)}`
        : "Lat: -- | Lon: --"}
    </div>
  );
}

function ResetViewController({ resetToken }) {
  const map = useMap();

  useEffect(() => {
    if (resetToken == null) {
      return;
    }

    map.fitBounds(SUITABILITY_BOUNDS, {
      animate: true,
      padding: [20, 20],
    });
  }, [map, resetToken]);

  return null;
}

function SearchTargetMarker({ searchTarget }) {
  const map = useMap();

  useEffect(() => {
    if (!searchTarget) {
      return;
    }

    map.flyTo([searchTarget.lat, searchTarget.lon], 14, {
      animate: true,
    });
  }, [map, searchTarget]);

  if (!searchTarget) {
    return null;
  }

  return (
    <Marker position={[searchTarget.lat, searchTarget.lon]} icon={searchIcon}>
      <Popup>{searchTarget.name || "Searched location"}</Popup>
    </Marker>
  );
}

function DistrictBoundaryLayer({ data }) {
  if (!data) {
    return null;
  }

  return (
    <GeoJSON
      data={data}
      style={{
        color: "#000000",
        weight: 2.5,
        opacity: 0.8,
        fillOpacity: 0,
      }}
    />
  );
}

function MapComponent({
  layerVisibility,
  suitabilityFilter,
  resetToken,
  searchTarget,
}) {
  const [layerData, setLayerData] = useState({});
  const [boundaryData, setBoundaryData] = useState(null);
  const [georasterData, setGeorasterData] = useState(null);
  const [suitabilityLoading, setSuitabilityLoading] = useState(false);
  const loadingRef = useRef({});

  useEffect(() => {
    let cancelled = false;

    const loadBoundary = async () => {
      try {
        const response = await fetch("/data/boundary.geojson");
        if (!response.ok) {
          return;
        }

        const data = await response.json();
        if (!cancelled) {
          setBoundaryData(data);
        }
      } catch {
        // Keep map usable if boundary loading fails.
      }
    };

    loadBoundary();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    const keysToLoad = Object.keys(layerConfig).filter(
      (key) =>
        layerVisibility[key] && !layerData[key] && !loadingRef.current[key],
    );

    if (keysToLoad.length === 0) {
      return () => {
        cancelled = true;
      };
    }

    const loadEnabledLayers = async () => {
      const nextData = {};

      await Promise.all(
        keysToLoad.map(async (key) => {
          loadingRef.current[key] = true;
          try {
            const response = await fetch(layerConfig[key].url);
            if (!response.ok) {
              console.warn("Failed to load " + key + ": " + response.status);
              nextData[key] = null;
            } else {
              nextData[key] = await response.json();
            }
          } catch (err) {
            console.warn("Error loading " + key + ":", err);
            nextData[key] = null;
          } finally {
            loadingRef.current[key] = false;
          }
        }),
      );

      if (!cancelled && Object.keys(nextData).length > 0) {
        setLayerData((prev) => ({ ...prev, ...nextData }));
      }
    };

    loadEnabledLayers();

    return () => {
      cancelled = true;
    };
  }, [layerVisibility, layerData]);

  const renderLayer = (key) => {
    const data = layerData[key];
    const styleConfig = layerConfig[key].style;

    if (!data || !layerVisibility[key]) {
      return null;
    }

    return (
      <GeoJSON
        key={key}
        data={data}
        style={styleConfig}
        onEachFeature={(feature, layer) => {
          const name =
            feature?.properties?.name ||
            feature?.properties?.Name ||
            feature?.properties?.NAME ||
            "Feature";
          layer.bindPopup(name);
        }}
        pointToLayer={(_, latlng) =>
          key === "hospitals"
            ? L.marker(latlng, { icon: hospitalIcon })
            : key === "schools"
              ? L.marker(latlng, { icon: schoolIcon })
              : L.circleMarker(latlng, {
                  color: styleConfig.color,
                  fillColor: styleConfig.fillColor,
                  fillOpacity: styleConfig.fillOpacity,
                  radius: styleConfig.radius || 4,
                  weight: styleConfig.weight || 1,
                })
        }
      />
    );
  };

  return (
    <MapContainer
      center={MAP_CENTER}
      zoom={DEFAULT_ZOOM}
      className="leaflet-map"
      style={{ width: "100%", height: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <SuitabilityClassLayer
        enabled={layerVisibility.suitability}
        suitabilityFilter={suitabilityFilter}
        onRasterReady={setGeorasterData}
        onLoadingChange={setSuitabilityLoading}
      />
      <DistrictBoundaryLayer data={boundaryData} />
      <SuitabilityInteraction
        enabled={layerVisibility.suitability}
        georasterData={georasterData}
      />
      <ResetViewController resetToken={resetToken} />
      <SearchTargetMarker searchTarget={searchTarget} />
      <ScaleControl position="bottomright" />
      <CoordinatesDisplay />
      {Object.keys(layerConfig).map((key) => renderLayer(key))}
      {suitabilityLoading ? (
        <div className="map-loading-overlay">Loading suitability data...</div>
      ) : null}
    </MapContainer>
  );
}

export default MapComponent;
