import LayerControl from "./LayerControl";
import SearchBar from "./SearchBar";
import { useState } from "react";

function Sidebar({
  layerVisibility,
  onLayerToggle,
  onSearchResult,
  suitabilityFilter,
  onSuitabilityChange,
  onZoomDistrict,
}) {
  const [showWhyPanel, setShowWhyPanel] = useState(false);
  const [showProjectInfo, setShowProjectInfo] = useState(false);

  return (
    <aside className="sidebar">
      <h1>Land Suitability Analysis Viewer</h1>
      <p className="subtitle">Medchal-Malkajgiri District, Telangana</p>

      <SearchBar onSearchResult={onSearchResult} />

      <section className="section-block">
        <h2>🗺 Map Tools</h2>
        <button type="button" className="reset-btn" onClick={onZoomDistrict}>
          Zoom to District
        </button>
      </section>

      <section className="section-block">
        <h2>📊 Suitability Filter</h2>
        <div className="suitability-buttons">
          {[
            { key: "high", label: "High suitability" },
            { key: "medium", label: "Medium suitability" },
            { key: "low", label: "Low suitability" },
          ].map((item) => (
            <button
              key={item.key}
              type="button"
              className={suitabilityFilter === item.key ? "active" : ""}
              onClick={() => onSuitabilityChange(item.key)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </section>

      <section className="section-block">
        <h2>🧠 Explainability</h2>
        <button
          type="button"
          className="reset-btn"
          onClick={() => setShowWhyPanel((prevState) => !prevState)}
        >
          Explain Suitability
        </button>
        {showWhyPanel ? (
          <div className="info-card">
            <p className="info-title">Why this area?</p>
            <p>High suitability because:</p>
            <ul>
              <li>Close to roads</li>
              <li>Near schools and hospitals</li>
              <li>Away from industrial zones</li>
              <li>Moderate vegetation support</li>
            </ul>
          </div>
        ) : null}

        <button
          type="button"
          className="reset-btn"
          onClick={() => setShowProjectInfo((prevState) => !prevState)}
        >
          Project Info
        </button>
        {showProjectInfo ? (
          <div className="info-card">
            <p className="info-title">Data Used</p>
            <ul>
              <li>LISS-III Satellite Imagery</li>
              <li>OpenStreetMap Data</li>
              <li>QGIS Analysis (NDVI, LULC, Proximity)</li>
            </ul>
          </div>
        ) : null}
      </section>

      <section className="section-block">
        <h2>🗺 Layers</h2>
        <LayerControl
          layerVisibility={layerVisibility}
          onLayerToggle={onLayerToggle}
        />
      </section>

      <section className="section-block legend-block">
        <h2>Legend</h2>
        <div className="legend-row">
          <span className="swatch high" />
          <span>Green: High suitability</span>
        </div>
        <div className="legend-row">
          <span className="swatch medium" />
          <span>Yellow: Medium suitability</span>
        </div>
        <div className="legend-row">
          <span className="swatch low" />
          <span>Red: Low suitability</span>
        </div>
      </section>
    </aside>
  );
}

export default Sidebar;
