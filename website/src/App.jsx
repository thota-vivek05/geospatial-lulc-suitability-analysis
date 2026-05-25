import { useState } from "react";
import MapComponent from "./components/MapComponent";
import Sidebar from "./components/Sidebar";

const DEFAULT_LAYER_VISIBILITY = {
  roads: false,
  waterBodies: false,
  industrial: false,
  hospitals: false,
  schools: false,
  railway: false,
  suitability: false,
};

function App() {
  const [layerVisibility, setLayerVisibility] = useState(
    DEFAULT_LAYER_VISIBILITY,
  );
  const [searchTarget, setSearchTarget] = useState(null);
  const [suitabilityFilter, setSuitabilityFilter] = useState("high");
  const [resetToken, setResetToken] = useState(0);

  const handleLayerToggle = (layerKey) => {
    setLayerVisibility((prev) => ({
      ...prev,
      [layerKey]: !prev[layerKey],
    }));
  };

  return (
    <div className="app-layout">
      <Sidebar
        layerVisibility={layerVisibility}
        onLayerToggle={handleLayerToggle}
        onSearchResult={setSearchTarget}
        suitabilityFilter={suitabilityFilter}
        onSuitabilityChange={setSuitabilityFilter}
        onZoomDistrict={() => setResetToken((prev) => prev + 1)}
      />
      <main className="map-panel">
        <div className="map-title">
          Land Suitability Map - Medchal-Malkajgiri
        </div>
        <MapComponent
          layerVisibility={layerVisibility}
          searchTarget={searchTarget}
          suitabilityFilter={suitabilityFilter}
          resetToken={resetToken}
        />
      </main>
    </div>
  );
}

export default App;
