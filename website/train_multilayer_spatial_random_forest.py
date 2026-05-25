from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter
from rasterio.enums import Resampling
from rasterio.warp import reproject
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


TARGET_DIR = Path("public/raster")
FEATURE_DIR = Path("Raster/suitability")
TARGET_RASTER = TARGET_DIR / "final_suitability_ml.tif"
OUTPUT_DIR = TARGET_DIR
OUTPUT_RASTER = OUTPUT_DIR / "final_suitability_ml_spatial_rf_continuous.tif"
HISTOGRAM_PNG = OUTPUT_DIR / "rf_continuous_prediction_histogram.png"
MAP_PNG = OUTPUT_DIR / "rf_continuous_predicted_map.png"
FEATURE_IMPORTANCE_PNG = OUTPUT_DIR / "rf_feature_importance.png"

SMOOTH_SIGMA = 1.2
ENABLE_OVERSAMPLING = True
MIN_CLASS_FRACTION = 0.03
FORCE_QUANTILE_3CLASS_IF_IMBALANCED = True
HIGH_CLASS_PROB_BOOST = 1.35

FEATURE_RASTERS = [
    ("roads_suitability", FEATURE_DIR / "roads_suitability.tif"),
    ("water_suitability", FEATURE_DIR / "water_suitability.tif"),
    ("lulc_suitability", FEATURE_DIR / "lulc_suitability.tif"),
    ("builtup_suit", FEATURE_DIR / "builtup_suit.tif"),
    ("industrial_suit", FEATURE_DIR / "industrial_suit.tif"),
    ("hospital_suit", FEATURE_DIR / "hospital_suit.tif"),
    ("school_suit", FEATURE_DIR / "school_suit.tif"),
    ("railway_suit", FEATURE_DIR / "railway_suit.tif"),
]


def load_raster(path: Path):
    with rasterio.open(path) as src:
        array = src.read(1)
        profile = src.profile
        nodata = src.nodata
    return array, profile, nodata


def align_raster_to_target(source_path: Path, target_profile):
    """Reproject a raster onto the target grid using nearest-neighbor resampling."""
    with rasterio.open(source_path) as src:
        source = src.read(1)

        if src.nodata is not None:
            destination = np.full(
                (target_profile["height"], target_profile["width"]),
                src.nodata,
                dtype=source.dtype,
            )
        else:
            destination = np.zeros(
                (target_profile["height"], target_profile["width"]),
                dtype=source.dtype,
            )

        reproject(
            source=source,
            destination=destination,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=target_profile["transform"],
            dst_crs=target_profile["crs"],
            src_nodata=src.nodata,
            dst_nodata=src.nodata,
            resampling=Resampling.nearest,
        )

    return destination, src.nodata


def is_valid_layer(array, nodata):
    if nodata is None:
        if np.issubdtype(array.dtype, np.floating):
            return np.isfinite(array)
        return np.ones(array.shape, dtype=bool)

    if np.issubdtype(array.dtype, np.floating) and np.isnan(nodata):
        return np.isfinite(array)

    return array != nodata


def build_dataset(target_path: Path):
    target_array, profile, target_nodata = load_raster(target_path)

    valid_mask = is_valid_layer(target_array, target_nodata)
    valid_mask &= target_array > 0

    height, width = target_array.shape
    split_col = int(width * 0.6)

    train_mask = np.zeros_like(valid_mask, dtype=bool)
    test_mask = np.zeros_like(valid_mask, dtype=bool)
    train_mask[:, :split_col] = True
    test_mask[:, split_col:] = True
    train_mask &= valid_mask
    test_mask &= valid_mask

    feature_arrays = []
    for feature_name, feature_path in FEATURE_RASTERS:
        if not feature_path.exists():
            raise FileNotFoundError(
                f"Missing feature raster: {feature_name} -> {feature_path}")

        aligned, nodata = align_raster_to_target(feature_path, profile)
        feature_arrays.append(aligned)
        valid_mask &= is_valid_layer(aligned, nodata)

    # Refresh spatial masks after removing invalid feature pixels.
    train_mask &= valid_mask
    test_mask &= valid_mask

    # Flatten target raster and features only for valid pixels.
    y_raw = target_array[valid_mask].astype(np.float32)
    x_all = np.column_stack([feature[valid_mask].astype(
        np.float32) for feature in feature_arrays])

    valid_flat = valid_mask.reshape(-1)
    train_flat = train_mask.reshape(-1)[valid_flat]
    test_flat = test_mask.reshape(-1)[valid_flat]
    valid_indices = np.flatnonzero(valid_flat)
    train_indices = valid_indices[train_flat]
    test_indices = valid_indices[test_flat]

    x_train = x_all[train_flat]
    y_train_raw = y_raw[train_flat]
    x_test = x_all[test_flat]
    y_test_raw = y_raw[test_flat]

    thresholds = {
        "split_col": split_col,
        "width": width,
        "height": height,
        "feature_names": [name for name, _ in FEATURE_RASTERS],
    }

    return (
        x_train,
        y_train_raw,
        x_test,
        y_test_raw,
        y_raw,
        valid_mask,
        valid_indices,
        profile,
        feature_arrays,
        thresholds,
    )


def save_prediction(prediction_valid, valid_mask, profile, out_path: Path):
    nodata_value = -9999.0
    pred_full = np.full(valid_mask.shape, nodata_value, dtype=np.float32)
    pred_full[valid_mask] = prediction_valid.astype(np.float32)

    out_profile = profile.copy()
    out_profile.update(dtype=rasterio.float32, count=1,
                       compress="lzw", nodata=nodata_value)

    with rasterio.open(out_path, "w", **out_profile) as dst:
        dst.write(pred_full, 1)


def save_histogram(score_values, out_path: Path):
    plt.figure(figsize=(6, 4))
    plt.hist(
        score_values,
        bins=40,
        color="#2A9D8F",
        edgecolor="white",
        alpha=0.9,
    )
    plt.title("Predicted Continuous Suitability Distribution")
    plt.xlabel("Suitability Score")
    plt.ylabel("Pixel Count")
    plt.grid(axis="y", alpha=0.2)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)


def save_feature_importance(model, feature_names, out_path: Path):
    importances = model.feature_importances_
    order = np.argsort(importances)[::-1]

    plt.figure(figsize=(8, 5))
    plt.barh([feature_names[i] for i in order],
             importances[order], color="#4C78A8")
    plt.title("Feature Importance")
    plt.xlabel("Importance")
    plt.gca().invert_yaxis()
    plt.grid(axis="x", alpha=0.2)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)

    print("\nFeature Importance:")
    for index in order:
        print(f"{feature_names[index]:20s}: {importances[index]:.4f}")


def fit_minmax_scaler(x_train):
    feature_min = x_train.min(axis=0)
    feature_max = x_train.max(axis=0)
    denom = feature_max - feature_min
    denom[denom == 0] = 1.0
    return feature_min, denom


def apply_minmax_scaler(x, feature_min, denom):
    return (x - feature_min) / denom


def oversample_minority_classes(x_train, y_train, random_state=42):
    rng = np.random.default_rng(random_state)
    classes, counts = np.unique(y_train, return_counts=True)
    target_count = counts.max()

    x_parts = []
    y_parts = []

    for cls, count in zip(classes, counts):
        cls_idx = np.flatnonzero(y_train == cls)
        if count < target_count:
            extra_idx = rng.choice(cls_idx, size=(
                target_count - count), replace=True)
            final_idx = np.concatenate([cls_idx, extra_idx])
        else:
            final_idx = cls_idx

        x_parts.append(x_train[final_idx])
        y_parts.append(y_train[final_idx])

    x_balanced = np.vstack(x_parts)
    y_balanced = np.concatenate(y_parts)

    # Shuffle after oversampling to avoid class blocks during fitting.
    order = rng.permutation(len(y_balanced))
    return x_balanced[order], y_balanced[order]


def quantile_three_class_labels(values):
    # Rank-based tercile split to force all 3 classes when data are highly imbalanced.
    n = len(values)
    order = np.argsort(values, kind="mergesort")
    labels = np.empty(n, dtype=np.int32)

    first = n // 3
    second = (2 * n) // 3

    labels[order[:first]] = 1
    labels[order[first:second]] = 2
    labels[order[second:]] = 3
    return labels


def ensure_three_classes(y_raw):
    y_int = y_raw.astype(np.int32)
    classes, counts = np.unique(y_int, return_counts=True)
    total = counts.sum()

    print("Original target unique values:", list(
        zip(classes.tolist(), counts.tolist())))

    class_count_map = {int(c): int(n) for c, n in zip(classes, counts)}
    c1 = class_count_map.get(1, 0)
    c2 = class_count_map.get(2, 0)
    c3 = class_count_map.get(3, 0)

    min_required = int(total * MIN_CLASS_FRACTION)
    needs_reclass = (
        FORCE_QUANTILE_3CLASS_IF_IMBALANCED
        and (c1 == 0 or c2 == 0 or c3 < min_required)
    )

    if needs_reclass:
        print(
            "Target classes are missing/imbalanced for class-3 learning; "
            "applying quantile-based 3-class relabeling (33/33/33)."
        )
        y_fixed = quantile_three_class_labels(y_raw)
    else:
        y_fixed = y_int

    fixed_classes, fixed_counts = np.unique(y_fixed, return_counts=True)
    print("Model target class distribution:", list(
        zip(fixed_classes.tolist(), fixed_counts.tolist())))

    return y_fixed


def predict_proba_score_in_chunks(
    model,
    feature_arrays,
    flat_indices,
    feature_min,
    denom,
    chunk_size=250_000,
):
    score = np.zeros(len(flat_indices), dtype=np.float32)

    feature_flats = [feature.reshape(-1) for feature in feature_arrays]
    classes = model.classes_.astype(np.int32)

    for start in range(0, len(flat_indices), chunk_size):
        chunk_indices = flat_indices[start:start + chunk_size]
        x_chunk = np.column_stack([feature_flat[chunk_indices]
                                  for feature_flat in feature_flats])
        x_chunk = apply_minmax_scaler(
            x_chunk.astype(np.float32), feature_min, denom)
        proba = model.predict_proba(x_chunk)

        # Always build a 3-class probability table [P1, P2, P3].
        p_all = np.zeros((len(chunk_indices), 3), dtype=np.float32)
        for i, cls in enumerate(classes):
            if 1 <= cls <= 3:
                p_all[:, cls - 1] = proba[:, i]

        if HIGH_CLASS_PROB_BOOST > 1.0:
            p_all[:, 2] *= HIGH_CLASS_PROB_BOOST
            denom_p = p_all.sum(axis=1, keepdims=True)
            denom_p[denom_p == 0] = 1.0
            p_all = p_all / denom_p

        class_values = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        score[start:start + len(chunk_indices)] = p_all @ class_values

    return score


def gaussian_smooth_with_mask(image, sigma):
    valid = np.isfinite(image).astype(np.float32)
    filled = np.nan_to_num(image, nan=0.0).astype(np.float32)

    smooth_sum = gaussian_filter(filled, sigma=sigma)
    smooth_weight = gaussian_filter(valid, sigma=sigma)

    smoothed = np.full(image.shape, np.nan, dtype=np.float32)
    non_zero = smooth_weight > 1e-6
    smoothed[non_zero] = smooth_sum[non_zero] / smooth_weight[non_zero]
    smoothed = np.clip(smoothed, 1.0, 3.0)

    return smoothed


def main():
    if not TARGET_RASTER.exists():
        raise FileNotFoundError(f"Target raster not found: {TARGET_RASTER}")

    (
        x_train,
        y_train_raw,
        x_test,
        y_test_raw,
        y_raw,
        valid_mask,
        valid_indices,
        profile,
        feature_arrays,
        split_info,
    ) = build_dataset(TARGET_RASTER)

    y_all = ensure_three_classes(y_raw)
    # Re-split labels after potential relabeling.
    valid_flat = valid_mask.reshape(-1)
    train_mask = np.zeros(valid_mask.shape, dtype=bool)
    test_mask = np.zeros(valid_mask.shape, dtype=bool)
    train_mask[:, :split_info["split_col"]] = True
    test_mask[:, split_info["split_col"]:] = True
    train_mask &= valid_mask
    test_mask &= valid_mask
    train_flat = train_mask.reshape(-1)[valid_flat]
    test_flat = test_mask.reshape(-1)[valid_flat]

    y_train = y_all[train_flat]
    y_test = y_all[test_flat]

    feature_min, denom = fit_minmax_scaler(x_train.astype(np.float32))
    x_train_scaled = apply_minmax_scaler(
        x_train.astype(np.float32), feature_min, denom)
    x_test_scaled = apply_minmax_scaler(
        x_test.astype(np.float32), feature_min, denom)

    if ENABLE_OVERSAMPLING:
        x_train_scaled, y_train = oversample_minority_classes(
            x_train_scaled, y_train, random_state=42)

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(x_train_scaled, y_train)

    y_pred = model.predict(x_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Training samples: {len(x_train):,}")
    print(f"Testing samples:  {len(x_test):,}")
    print(
        f"Spatial split column: {split_info['split_col']} / {split_info['width']}")
    print("Normalization: min-max scaling applied per feature (0 to 1)")
    print(f"Oversampling enabled: {ENABLE_OVERSAMPLING}")
    print(f"High-class probability boost: {HIGH_CLASS_PROB_BOOST}")
    print("Class distribution used for model:",
          np.unique(y_all, return_counts=True))
    print(f"Accuracy: {accuracy:.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred, labels=[1, 2, 3]))
    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            y_pred,
            labels=[1, 2, 3],
            target_names=["Low", "Medium", "High"],
            digits=4,
            zero_division=0,
        )
    )

    print("\nClass mapping:")
    print("1 = Low suitability")
    print("2 = Medium suitability")
    print("3 = High suitability")

    # Predict continuous suitability score for all valid pixels using class probabilities.
    continuous_valid = predict_proba_score_in_chunks(
        model,
        feature_arrays,
        valid_indices,
        feature_min,
        denom,
    )

    continuous_image = np.full(valid_mask.shape, np.nan, dtype=np.float32)
    continuous_image[valid_mask] = continuous_valid
    smoothed_image = gaussian_smooth_with_mask(
        continuous_image, sigma=SMOOTH_SIGMA)

    # Normalize output to strict 1..3 range.
    smoothed_valid = smoothed_image[valid_mask]
    min_v = np.nanmin(smoothed_valid)
    max_v = np.nanmax(smoothed_valid)
    if max_v > min_v:
        smoothed_valid = 1.0 + 2.0 * (smoothed_valid - min_v) / (max_v - min_v)
    else:
        smoothed_valid = np.full_like(smoothed_valid, 2.0)

    smoothed_image[valid_mask] = smoothed_valid

    vis_classes = np.digitize(smoothed_valid, bins=[
                              1.6667, 2.3333], right=False) + 1
    print("Predicted map class distribution (after scaling):",
          np.unique(vis_classes, return_counts=True))

    save_prediction(smoothed_valid, valid_mask, profile, OUTPUT_RASTER)
    print(f"\nSaved predicted raster: {OUTPUT_RASTER}")

    save_histogram(smoothed_valid, HISTOGRAM_PNG)
    print(f"Saved histogram: {HISTOGRAM_PNG}")

    save_feature_importance(
        model, split_info["feature_names"], FEATURE_IMPORTANCE_PNG)
    print(f"Saved feature importance plot: {FEATURE_IMPORTANCE_PNG}")

    plt.figure(figsize=(8, 7))
    im = plt.imshow(smoothed_image, cmap="RdYlGn", vmin=1,
                    vmax=3, interpolation="bilinear")
    # Draw district boundary from the valid raster mask for clear map extent.
    plt.contour(valid_mask.astype(np.uint8), levels=[
                0.5], colors="black", linewidths=1.2)
    plt.title("Predicted Continuous Suitability Map (ML)")
    cbar = plt.colorbar(im, ticks=[1, 2, 3])
    cbar.set_label("Suitability")
    cbar.ax.set_yticklabels(["Low", "Medium", "High"])
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(MAP_PNG, dpi=150)
    print(f"Saved predicted map: {MAP_PNG}")
    plt.show()


if __name__ == "__main__":
    main()
