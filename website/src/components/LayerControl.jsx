const LAYER_LABELS = [
  {
    key: "roads",
    label: "Roads",
    description: "Used for accessibility analysis.",
  },
  {
    key: "waterBodies",
    label: "Water bodies",
    description: "Used to avoid flood-prone areas.",
  },
  {
    key: "industrial",
    label: "Industrial areas",
    description: "Avoided for housing due to pollution risk.",
  },
  {
    key: "hospitals",
    label: "Hospitals",
    description: "Indicates emergency service accessibility.",
  },
  {
    key: "schools",
    label: "Schools",
    description: "Represents educational service proximity.",
  },
  {
    key: "railway",
    label: "Railway",
    description: "Transport corridor used as a planning factor.",
  },
  {
    key: "suitability",
    label: "Final suitability map",
    description: "Combined output from weighted GIS criteria.",
  },
];

function LayerControl({ layerVisibility, onLayerToggle }) {
  return (
    <div className="layer-list">
      {LAYER_LABELS.map((layer) => (
        <label key={layer.key} className="layer-item">
          <input
            type="checkbox"
            checked={layerVisibility[layer.key]}
            onChange={() => onLayerToggle(layer.key)}
          />
          <span title={layer.description}>{layer.label}</span>
        </label>
      ))}
    </div>
  );
}

export default LayerControl;
