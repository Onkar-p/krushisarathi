"""
train_yield_model.py
Trains a crop yield prediction model using synthetic agricultural data.
Uses features: Crop type, Soil type, Temperature, Rainfall, Humidity, pH, Nitrogen, Phosphorus, Potassium.
"""

import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder

MODEL_DIR = Path(r"E:\krushisarathi\models")
DATA_DIR = Path(r"E:\krushisarathi\data")
RANDOM_STATE = 42

# ─── Crop knowledge base ───────────────────────────────────────────────
# (crop, ideal_soil, ideal_temp_range, ideal_rain_range, ideal_ph_range, base_yield_tonnes_per_hectare)
CROP_PROFILES = [
    ("Rice",        "Clay",      (22, 32), (1000, 2000), (5.5, 6.5), 4.5),
    ("Wheat",       "Loamy",     (12, 25), (400, 800),   (6.0, 7.5), 3.5),
    ("Maize",       "Sandy Loam",(18, 27), (500, 800),   (5.8, 7.0), 5.0),
    ("Sugarcane",   "Loamy",     (25, 35), (1200, 2500), (6.0, 7.5), 70.0),
    ("Cotton",      "Black",     (25, 35), (600, 1000),  (6.0, 7.5), 2.0),
    ("Soybean",     "Loamy",     (20, 30), (500, 900),   (6.0, 7.0), 2.5),
    ("Potato",      "Sandy Loam",(15, 25), (500, 700),   (5.0, 6.5), 25.0),
    ("Tomato",      "Sandy Loam",(20, 30), (400, 600),   (6.0, 7.0), 35.0),
    ("Pepper",      "Loamy",     (20, 30), (500, 700),   (6.0, 7.0), 20.0),
    ("Groundnut",   "Sandy",     (25, 35), (500, 700),   (6.0, 6.5), 1.8),
    ("Mustard",     "Loamy",     (10, 25), (250, 500),   (6.0, 7.5), 1.2),
    ("Chickpea",    "Black",     (15, 30), (300, 500),   (6.0, 7.5), 1.5),
    ("Onion",       "Loamy",     (15, 25), (350, 550),   (6.0, 7.0), 20.0),
    ("Banana",      "Clay Loam", (25, 35), (1500, 2500), (6.0, 7.5), 40.0),
    ("Mango",       "Loamy",     (24, 36), (750, 2500),  (5.5, 7.5), 8.0),
]

SOIL_TYPES = ["Sandy", "Loamy", "Clay", "Black", "Red", "Sandy Loam", "Clay Loam", "Laterite"]


def generate_synthetic_data(n_samples: int = 5000) -> pd.DataFrame:
    """Generate realistic synthetic crop yield data."""
    np.random.seed(RANDOM_STATE)
    records = []

    for _ in range(n_samples):
        # Pick a random crop profile
        crop, ideal_soil, temp_range, rain_range, ph_range, base_yield = CROP_PROFILES[
            np.random.randint(len(CROP_PROFILES))
        ]

        # Randomly pick soil (sometimes ideal, sometimes not)
        if np.random.rand() < 0.5:
            soil = ideal_soil
        else:
            soil = SOIL_TYPES[np.random.randint(len(SOIL_TYPES))]

        # Generate environmental conditions with some randomness
        temp = np.random.uniform(temp_range[0] - 10, temp_range[1] + 10)
        rainfall = np.random.uniform(rain_range[0] * 0.3, rain_range[1] * 1.5)
        humidity = np.random.uniform(30, 95)
        ph = np.random.uniform(ph_range[0] - 2, ph_range[1] + 2)
        ph = np.clip(ph, 3.5, 9.5)

        # NPK values
        nitrogen = np.random.uniform(10, 140)
        phosphorus = np.random.uniform(5, 80)
        potassium = np.random.uniform(5, 80)

        # Calculate yield based on how close conditions are to ideal
        yield_factor = 1.0

        # Temperature factor
        ideal_temp = (temp_range[0] + temp_range[1]) / 2
        temp_dev = abs(temp - ideal_temp) / (temp_range[1] - temp_range[0])
        yield_factor *= max(0.2, 1 - 0.5 * temp_dev)

        # Rainfall factor
        ideal_rain = (rain_range[0] + rain_range[1]) / 2
        rain_dev = abs(rainfall - ideal_rain) / (rain_range[1] - rain_range[0])
        yield_factor *= max(0.15, 1 - 0.4 * rain_dev)

        # pH factor
        ideal_ph = (ph_range[0] + ph_range[1]) / 2
        ph_dev = abs(ph - ideal_ph) / (ph_range[1] - ph_range[0])
        yield_factor *= max(0.3, 1 - 0.4 * ph_dev)

        # Soil suitability
        soil_factor = 1.0 if soil == ideal_soil else np.random.uniform(0.5, 0.85)
        yield_factor *= soil_factor

        # Nutrient factor (simplified)
        nutrient_score = (min(nitrogen, 100) / 100 + min(phosphorus, 60) / 60 + min(potassium, 60) / 60) / 3
        yield_factor *= (0.5 + 0.5 * nutrient_score)

        # Final yield with noise
        crop_yield = base_yield * yield_factor * np.random.uniform(0.85, 1.15)
        crop_yield = max(0.1, crop_yield)

        records.append({
            "Crop": crop,
            "Soil_Type": soil,
            "Temperature_C": round(temp, 1),
            "Rainfall_mm": round(rainfall, 1),
            "Humidity_pct": round(humidity, 1),
            "pH": round(ph, 2),
            "Nitrogen_kg_per_ha": round(nitrogen, 1),
            "Phosphorus_kg_per_ha": round(phosphorus, 1),
            "Potassium_kg_per_ha": round(potassium, 1),
            "Yield_tonnes_per_ha": round(crop_yield, 2),
        })

    return pd.DataFrame(records)


def main():
    print("=" * 60)
    print("  Crop Yield Prediction - Model Training")
    print("=" * 60)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Generate data
    print("\n[1/5] Generating synthetic crop data...")
    df = generate_synthetic_data(5000)
    csv_path = DATA_DIR / "crop_yield_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"  Data saved to {csv_path}")
    print(f"  Shape: {df.shape}")
    print(f"\n  Sample:\n{df.head()}")

    # Encode categoricals
    print("\n[2/5] Encoding categorical features...")
    le_crop = LabelEncoder()
    le_soil = LabelEncoder()
    df["Crop_enc"] = le_crop.fit_transform(df["Crop"])
    df["Soil_enc"] = le_soil.fit_transform(df["Soil_Type"])

    feature_cols = [
        "Crop_enc", "Soil_enc", "Temperature_C", "Rainfall_mm",
        "Humidity_pct", "pH", "Nitrogen_kg_per_ha",
        "Phosphorus_kg_per_ha", "Potassium_kg_per_ha",
    ]
    X = df[feature_cols].values
    y = df["Yield_tonnes_per_ha"].values

    # Split
    print("\n[3/5] Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    # Train
    print("\n[4/5] Training Gradient Boosting Regressor...")
    model = GradientBoostingRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        min_samples_split=5,
        random_state=RANDOM_STATE,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\n{'=' * 60}")
    print(f"  MAE : {mae:.3f} tonnes/ha")
    print(f"  R²  : {r2:.4f}")
    print(f"{'=' * 60}")

    # Feature importance
    print("\n[5/5] Feature importances:")
    feature_names = [
        "Crop", "Soil", "Temperature", "Rainfall",
        "Humidity", "pH", "Nitrogen", "Phosphorus", "Potassium",
    ]
    for name, imp in sorted(
        zip(feature_names, model.feature_importances_), key=lambda x: -x[1]
    ):
        print(f"  {name:15s}: {imp:.4f}")

    # Save
    joblib.dump(model, MODEL_DIR / "yield_model.joblib")
    joblib.dump(le_crop, MODEL_DIR / "yield_crop_encoder.joblib")
    joblib.dump(le_soil, MODEL_DIR / "yield_soil_encoder.joblib")

    # Save metadata
    meta = {
        "crops": list(le_crop.classes_),
        "soils": list(le_soil.classes_),
        "feature_cols": feature_cols,
        "feature_names": feature_names,
    }
    joblib.dump(meta, MODEL_DIR / "yield_meta.joblib")

    print(f"\nModels saved to {MODEL_DIR}")
    print("Done!")


if __name__ == "__main__":
    main()
