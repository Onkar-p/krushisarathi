"""
train_disease_model.py
Trains a crop disease classification model on the PlantVillage dataset.
Uses HOG + Color Histogram features with a Random Forest classifier.
"""

import os
import sys
import numpy as np
import joblib
from pathlib import Path
from PIL import Image
from skimage.feature import hog, local_binary_pattern
from skimage.color import rgb2gray, rgb2hsv
from skimage.transform import resize
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

# Configuration
DATASET_DIR = Path(r"E:\krushisarathi\PlantVillage")
MODEL_DIR = Path(r"E:\krushisarathi\models")
IMG_SIZE = (64, 64)
MAX_IMAGES_PER_CLASS = 500  # Use more images for better accuracy
RANDOM_STATE = 42


def extract_features(image_path: str) -> np.ndarray | None:
    """Extract combined HOG + Color Histogram + texture features from a single image."""
    try:
        img = Image.open(image_path).convert("RGB")
        img_array = np.array(img)
        img_resized = resize(img_array, (*IMG_SIZE, 3), anti_aliasing=True)

        # 1. HOG features (shape/texture)
        img_gray = rgb2gray(img_resized)
        hog_features = hog(
            img_gray,
            orientations=9,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            block_norm="L2-Hys",
        )

        # 2. Color histogram features (RGB channels)
        color_features = []
        for channel in range(3):
            hist, _ = np.histogram(img_resized[:, :, channel], bins=32, range=(0, 1))
            hist = hist.astype(float) / (hist.sum() + 1e-7)  # Normalize
            color_features.extend(hist)

        # 3. HSV color histogram (captures disease-specific colors better)
        img_hsv = rgb2hsv(img_resized)
        for channel in range(3):
            hist, _ = np.histogram(img_hsv[:, :, channel], bins=32, range=(0, 1))
            hist = hist.astype(float) / (hist.sum() + 1e-7)
            color_features.extend(hist)

        # 4. Statistical features (mean, std per channel)
        stats_features = []
        for channel in range(3):
            stats_features.append(np.mean(img_resized[:, :, channel]))
            stats_features.append(np.std(img_resized[:, :, channel]))
        for channel in range(3):
            stats_features.append(np.mean(img_hsv[:, :, channel]))
            stats_features.append(np.std(img_hsv[:, :, channel]))

        # Combine all features
        all_features = np.concatenate([
            hog_features,
            np.array(color_features),
            np.array(stats_features),
        ])

        return all_features
    except Exception as e:
        print(f"  [SKIP] Error processing {image_path}: {e}")
        return None


def load_dataset():
    """Load images from PlantVillage folders and extract features."""
    features = []
    labels = []

    # Get class directories (skip the nested PlantVillage subfolder)
    class_dirs = [
        d
        for d in sorted(DATASET_DIR.iterdir())
        if d.is_dir() and d.name != "PlantVillage"
    ]

    print(f"Found {len(class_dirs)} classes:\n")
    for cls_dir in class_dirs:
        image_files = [
            f for f in cls_dir.iterdir() if f.suffix.upper() in (".JPG", ".JPEG", ".PNG")
        ]
        # Limit images per class
        np.random.seed(RANDOM_STATE)
        if len(image_files) > MAX_IMAGES_PER_CLASS:
            indices = np.random.choice(len(image_files), MAX_IMAGES_PER_CLASS, replace=False)
            image_files = [image_files[i] for i in indices]

        print(f"  {cls_dir.name}: loading {len(image_files)} images...")

        count = 0
        for img_path in image_files:
            feat = extract_features(str(img_path))
            if feat is not None:
                features.append(feat)
                labels.append(cls_dir.name)
                count += 1
        print(f"    -> {count} images processed successfully")

    return np.array(features), np.array(labels)


def main():
    print("=" * 60)
    print("  PlantVillage Disease Detection - Model Training")
    print("  (HOG + Color Histograms + Statistics)")
    print("=" * 60)

    # Create model directory
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Load dataset
    print("\n[1/4] Loading dataset and extracting features...")
    X, y = load_dataset()
    print(f"\nTotal samples: {len(X)}, Feature dimension: {X.shape[1]}")

    # Encode labels
    print("\n[2/4] Encoding labels...")
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    print(f"Number of classes: {len(le.classes_)}")

    # Split data
    print("\n[3/4] Splitting into train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=RANDOM_STATE, stratify=y_encoded
    )
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # Train model — ExtraTreesClassifier often outperforms RF on image features
    print("\n[4/4] Training Extra Trees classifier (500 trees)...")
    clf = ExtraTreesClassifier(
        n_estimators=500,
        max_depth=None,  # Let trees grow fully
        min_samples_split=2,
        min_samples_leaf=1,
        n_jobs=-1,
        random_state=RANDOM_STATE,
        verbose=1,
    )
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n{'=' * 60}")
    print(f"  Test Accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")
    print(f"{'=' * 60}")
    print("\nClassification Report:")
    print(
        classification_report(
            y_test, y_pred, target_names=le.classes_, zero_division=0
        )
    )

    # Save model and label encoder
    model_path = MODEL_DIR / "disease_model.joblib"
    encoder_path = MODEL_DIR / "label_encoder.joblib"
    joblib.dump(clf, model_path)
    joblib.dump(le, encoder_path)
    print(f"\nModel saved to: {model_path}")
    print(f"Label encoder saved to: {encoder_path}")
    print("\nDone! You can now run the Streamlit app.")


if __name__ == "__main__":
    main()
