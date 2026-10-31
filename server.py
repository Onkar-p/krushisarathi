"""
server.py — KrushiSarathi Flask Backend
Provides REST API endpoints for:
  - Disease detection (image upload + classification)
  - Government schemes data
  - Crop yield prediction
"""

import os
import numpy as np
import joblib
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from PIL import Image
from skimage.feature import hog
from skimage.color import rgb2gray, rgb2hsv
from skimage.transform import resize

from disease_info import DISEASE_INFO
from government_schemes import GOVERNMENT_SCHEMES

# ─── Configuration ─────────────────────────────────────────────────────
MODEL_DIR = Path(r"E:\krushisarathi\models")
IMG_SIZE = (64, 64)

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)


# ─── Model Loading ─────────────────────────────────────────────────────
def load_disease_model():
    model_path = MODEL_DIR / "disease_model.joblib"
    encoder_path = MODEL_DIR / "label_encoder.joblib"
    if model_path.exists() and encoder_path.exists():
        return joblib.load(model_path), joblib.load(encoder_path)
    return None, None


def load_yield_model():
    model_path = MODEL_DIR / "yield_model.joblib"
    crop_enc_path = MODEL_DIR / "yield_crop_encoder.joblib"
    soil_enc_path = MODEL_DIR / "yield_soil_encoder.joblib"
    meta_path = MODEL_DIR / "yield_meta.joblib"
    if all(p.exists() for p in [model_path, crop_enc_path, soil_enc_path, meta_path]):
        return (
            joblib.load(model_path),
            joblib.load(crop_enc_path),
            joblib.load(soil_enc_path),
            joblib.load(meta_path),
        )
    return None, None, None, None


# Load models at startup
disease_model, label_encoder = load_disease_model()
yield_model, crop_encoder, soil_encoder, yield_meta = load_yield_model()


# ─── Feature Extraction ───────────────────────────────────────────────
def extract_features(image: Image.Image) -> np.ndarray:
    """Extract HOG + Color Histogram + Statistical features from a PIL Image."""
    img_array = np.array(image.convert("RGB"))
    img_resized = resize(img_array, (*IMG_SIZE, 3), anti_aliasing=True)

    # 1. HOG features
    img_gray = rgb2gray(img_resized)
    hog_features = hog(
        img_gray,
        orientations=9,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        block_norm="L2-Hys",
    )

    # 2. RGB color histogram
    color_features = []
    for ch in range(3):
        hist, _ = np.histogram(img_resized[:, :, ch], bins=32, range=(0, 1))
        hist = hist.astype(float) / (hist.sum() + 1e-7)
        color_features.extend(hist)

    # 3. HSV color histogram
    img_hsv = rgb2hsv(img_resized)
    for ch in range(3):
        hist, _ = np.histogram(img_hsv[:, :, ch], bins=32, range=(0, 1))
        hist = hist.astype(float) / (hist.sum() + 1e-7)
        color_features.extend(hist)

    # 4. Statistical features
    stats = []
    for ch in range(3):
        stats.append(np.mean(img_resized[:, :, ch]))
        stats.append(np.std(img_resized[:, :, ch]))
    for ch in range(3):
        stats.append(np.mean(img_hsv[:, :, ch]))
        stats.append(np.std(img_hsv[:, :, ch]))

    return np.concatenate([hog_features, np.array(color_features), np.array(stats)])


# ═══════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


# ─── Disease Detection API ─────────────────────────────────────────────
@app.route("/api/detect-disease", methods=["POST"])
def detect_disease():
    if disease_model is None or label_encoder is None:
        return jsonify({"error": "Disease model not loaded. Run train_disease_model.py first."}), 500

    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    try:
        image = Image.open(file.stream)
        features = extract_features(image).reshape(1, -1)

        proba = disease_model.predict_proba(features)[0]
        pred_idx = int(np.argmax(proba))
        pred_class = label_encoder.inverse_transform([pred_idx])[0]
        confidence = float(proba[pred_idx] * 100)

        # Top 5 predictions
        top5_idx = np.argsort(proba)[::-1][:5]
        top5 = []
        for i in top5_idx:
            cls_name = label_encoder.inverse_transform([int(i)])[0]
            top5.append({
                "class": cls_name,
                "display_name": cls_name.replace("__", " — ").replace("_", " "),
                "confidence": round(float(proba[i] * 100), 2),
            })

        # Disease info
        info = DISEASE_INFO.get(pred_class, {})

        return jsonify({
            "prediction": pred_class,
            "display_name": pred_class.replace("__", " — ").replace("_", " "),
            "confidence": round(confidence, 2),
            "top5": top5,
            "disease_info": info,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Government Schemes API ───────────────────────────────────────────
@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    category = request.args.get("category", "")
    search = request.args.get("search", "").lower()

    schemes = GOVERNMENT_SCHEMES
    if category:
        schemes = [s for s in schemes if s["category"] == category]
    if search:
        schemes = [
            s for s in schemes
            if search in s["name"].lower()
            or search in s["description"].lower()
            or search in s["category"].lower()
        ]

    categories = sorted(set(s["category"] for s in GOVERNMENT_SCHEMES))
    return jsonify({"schemes": schemes, "categories": categories})


# ─── Yield Prediction API ─────────────────────────────────────────────
@app.route("/api/predict-yield", methods=["POST"])
def predict_yield():
    if yield_model is None:
        return jsonify({"error": "Yield model not loaded. Run train_yield_model.py first."}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided."}), 400

    try:
        crop = data["crop"]
        soil = data["soil"]
        temperature = float(data["temperature"])
        rainfall = float(data["rainfall"])
        humidity = float(data["humidity"])
        ph = float(data["ph"])
        nitrogen = float(data["nitrogen"])
        phosphorus = float(data["phosphorus"])
        potassium = float(data["potassium"])

        crop_enc = crop_encoder.transform([crop])[0]
        soil_enc = soil_encoder.transform([soil])[0]

        features = np.array([[
            crop_enc, soil_enc, temperature, rainfall,
            humidity, ph, nitrogen, phosphorus, potassium,
        ]])

        predicted_yield = max(0, float(yield_model.predict(features)[0]))

        # Feature importances
        feature_names = yield_meta["feature_names"]
        importances = [
            {"feature": name, "importance": round(float(imp), 4)}
            for name, imp in zip(feature_names, yield_model.feature_importances_)
        ]
        importances.sort(key=lambda x: x["importance"], reverse=True)

        # Recommendations
        recommendations = []
        if ph < 5.5:
            recommendations.append({"type": "warning", "text": "Soil pH is acidic. Consider applying lime to raise pH."})
        elif ph > 8.0:
            recommendations.append({"type": "warning", "text": "Soil pH is alkaline. Consider adding gypsum or sulfur."})
        if nitrogen < 40:
            recommendations.append({"type": "info", "text": "Nitrogen levels are low. Apply urea or organic nitrogen sources."})
        if phosphorus < 20:
            recommendations.append({"type": "info", "text": "Phosphorus is low. Apply DAP or SSP fertilizer."})
        if potassium < 20:
            recommendations.append({"type": "info", "text": "Potassium is low. Apply MOP (Muriate of Potash)."})
        if rainfall < 400:
            recommendations.append({"type": "warning", "text": "Rainfall is low. Consider irrigation support — check PMKSY scheme."})
        if temperature > 38:
            recommendations.append({"type": "warning", "text": "Temperature is very high. Choose heat-tolerant varieties."})

        return jsonify({
            "predicted_yield": round(predicted_yield, 2),
            "crop": crop,
            "soil": soil,
            "importances": importances,
            "recommendations": recommendations,
        })
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Invalid value: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/yield-meta", methods=["GET"])
def get_yield_meta():
    if yield_meta is None:
        return jsonify({"error": "Yield model not loaded."}), 500
    return jsonify({
        "crops": yield_meta["crops"],
        "soils": yield_meta["soils"],
    })


@app.route("/api/compare-soils", methods=["POST"])
def compare_soils():
    if yield_model is None:
        return jsonify({"error": "Yield model not loaded."}), 500

    data = request.get_json()
    crop = data.get("crop", "Rice")

    results = []
    for soil in yield_meta["soils"]:
        try:
            c_enc = crop_encoder.transform([crop])[0]
            s_enc = soil_encoder.transform([soil])[0]
            feat = np.array([[c_enc, s_enc, 25.0, 800.0, 65.0, 6.5, 60.0, 35.0, 35.0]])
            y_pred = max(0, float(yield_model.predict(feat)[0]))
            results.append({"soil": soil, "yield": round(y_pred, 2)})
        except Exception:
            pass

    results.sort(key=lambda x: x["yield"], reverse=True)
    return jsonify({"crop": crop, "results": results})


# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n KrushiSarathi Server Starting...")
    print(f"   Disease model: {'Loaded' if disease_model else 'Not found'}")
    print(f"   Yield model:   {'Loaded' if yield_model else 'Not found'}")
    print(f"\n   Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
