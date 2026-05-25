from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# Class split controls for Low/Mid/High from input raster values.
# Lower LOW_CLASS_QUANTILE -> fewer red (Low) pixels.
LOW_CLASS_QUANTILE = 0.20
MID_CLASS_QUANTILE = 0.65


def load_raster(path: Path):
    with rasterio.open(path) as src:
        arr = src.read(1)
        profile = src.profile
        nodata = src.nodata
    return arr, profile, nodata


def build_dataset(target_path: Path):
    raster, profile, nodata = load_raster(target_path)

    valid_mask = np.ones(raster.shape, dtype=bool)
    if nodata is not None:
        valid_mask &= raster != nodata
    valid_mask &= raster > 0

    height, width = raster.shape
    split_col = int(width * 0.6)

    train_mask = np.zeros_like(valid_mask, dtype=bool)
    test_mask = np.zeros_like(valid_mask, dtype=bool)

    train_mask[:, :split_col] = True
    test_mask[:, split_col:] = True

    train_mask &= valid_mask
    test_mask &= valid_mask

    valid_values = raster[valid_mask].astype(np.float32)

    # Force 3 classes from final_suitability values:
    # 1 = Low, 2 = Mid, 3 = High
    q1, q2 = np.quantile(
        valid_values, [LOW_CLASS_QUANTILE, MID_CLASS_QUANTILE])
    y = np.digitize(valid_values, bins=[q1, q2], right=False) + 1

    x = valid_values.reshape(-1, 1)

    thresholds = (float(q1), float(q2))

    return x, y, raster, valid_mask, train_mask, test_mask, profile, thresholds


def save_prediction(prediction, valid_mask, profile, out_path: Path):
    pred_full = np.zeros(valid_mask.shape, dtype=np.uint8)
    pred_full[valid_mask] = prediction.astype(np.uint8)

    out_profile = profile.copy()
    out_profile.update(dtype=rasterio.uint8, count=1, compress="lzw", nodata=0)

    with rasterio.open(out_path, "w", **out_profile) as dst:
        dst.write(pred_full, 1)


def main():
    target_path = Path("public/raster/final_suitability_ml.tif")
    out_dir = target_path.parent

    x, y, raster, valid_mask, train_mask, test_mask, profile, thresholds = build_dataset(
        target_path)
    q1, q2 = thresholds

    valid_flat = valid_mask.reshape(-1)
    train_flat = train_mask.reshape(-1)[valid_flat]
    test_flat = test_mask.reshape(-1)[valid_flat]

    x_all = x
    y_all = y

    x_train = x_all[train_flat]
    y_train = y_all[train_flat]
    x_test = x_all[test_flat]
    y_test = y_all[test_flat]

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"Training samples: {len(x_train):,}")
    print(f"Testing samples:  {len(x_test):,}")
    print(
        f"Spatial split column: {int(raster.shape[1] * 0.6)} / {raster.shape[1]}")
    print(
        f"Class quantile split: low<{LOW_CLASS_QUANTILE:.2f}, mid<{MID_CLASS_QUANTILE:.2f}, high>=mid")
    print("Class distribution:", np.unique(y, return_counts=True))
    print(f"Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, labels=[
          1, 2, 3], target_names=["Low", "Mid", "High"], digits=4))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred, labels=[1, 2, 3]))

    print("\nClass mapping:")
    print("1 = Low suitability")
    print("2 = Mid suitability")
    print("3 = High suitability")
    print("\nClass value ranges from input raster:")
    print(f"Low (1):  value < {q1:.4f}")
    print(f"Mid (2):  {q1:.4f} <= value < {q2:.4f}")
    print(f"High (3): value >= {q2:.4f}")

    # Predict only the unseen test area; keep train area as original classes for comparison.
    full_pred = np.full_like(y_all, 0)
    full_pred[test_flat] = model.predict(x_test)
    full_pred[train_flat] = y_all[train_flat]

    out_tif = out_dir / "final_suitability_ml_rf_pred.tif"
    save_prediction(full_pred, valid_mask, profile, out_tif)
    print(f"\nSaved predicted raster: {out_tif}")

    plt.figure(figsize=(6, 4))
    plt.hist(y_pred, bins=np.arange(y_pred.min(),
             y_pred.max() + 2) - 0.5, edgecolor="black")
    plt.title("Predicted Suitability Distribution (Test Set)")
    plt.xlabel("Class")
    plt.ylabel("Pixel Count")
    plt.tight_layout()

    out_plot = out_dir / "rf_prediction_histogram.png"
    plt.savefig(out_plot, dpi=150)
    print(f"Saved histogram: {out_plot}")

    # Reshape prediction back to image and keep outside region transparent.
    pred_image = np.full(valid_mask.shape, np.nan)
    pred_image[valid_mask] = full_pred

    plt.figure(figsize=(6, 6))
    plt.imshow(pred_image, cmap="RdYlGn", vmin=1, vmax=3)
    plt.axvline(int(raster.shape[1] * 0.6),
                color="black", linestyle="--", linewidth=2)
    plt.title("Predicted Suitability Map (ML)")
    plt.colorbar()
    plt.axis("off")
    plt.tight_layout()

    out_map = out_dir / "rf_predicted_map.png"
    plt.savefig(out_map, dpi=150)
    print(f"Saved predicted map: {out_map}")
    plt.show()


if __name__ == "__main__":
    main()
