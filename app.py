"""
app.py — KrushiSarathi 🌾
A comprehensive web application for:
  Tab 1: Early Detection and Management of Crop Diseases & Pest Infestation
  Tab 2: Government Policies / Schemes for Farmers
  Tab 3: Crop Yield Prediction based on Soil Type & Weather Conditions

Run with:  streamlit run app.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from PIL import Image
from skimage.feature import hog
from skimage.color import rgb2gray
from skimage.transform import resize

from disease_info import DISEASE_INFO
from government_schemes import GOVERNMENT_SCHEMES

# ─── Configuration ─────────────────────────────────────────────────────
MODEL_DIR = Path(r"E:\krushisarathi\models")
IMG_SIZE = (64, 64)

# ─── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="KrushiSarathi — कृषि सारथी",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #2d6a4f 0%, #40916c 50%, #52b788 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 2.2rem; }
    .main-header p { margin: 0.3rem 0 0 0; font-size: 1.1rem; opacity: 0.9; }

    /* Cards */
    .info-card {
        background: #f8f9fa;
        border-left: 4px solid #2d6a4f;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }
    .warning-card {
        background: #fff3cd;
        border-left: 4px solid #e67e22;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }
    .success-card {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }
    .danger-card {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }

    /* Scheme card */
    .scheme-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: box-shadow 0.2s;
    }
    .scheme-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }

    /* Severity badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-none { background: #d4edda; color: #155724; }
    .badge-moderate { background: #fff3cd; color: #856404; }
    .badge-high { background: #f8d7da; color: #721c24; }
    .badge-veryhigh { background: #dc3545; color: white; }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    div[data-testid="stTabs"] button {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── Header ────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
        <h1>🌾 KrushiSarathi — कृषि सारथी</h1>
        <p>Early Detection & Management of Crop Diseases | Government Schemes | Crop Yield Prediction</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─── Helper: Load Models ──────────────────────────────────────────────
@st.cache_resource
def load_disease_model():
    """Load the trained disease classification model."""
    model_path = MODEL_DIR / "disease_model.joblib"
    encoder_path = MODEL_DIR / "label_encoder.joblib"
    if not model_path.exists() or not encoder_path.exists():
        return None, None
    return joblib.load(model_path), joblib.load(encoder_path)


@st.cache_resource
def load_yield_model():
    """Load the trained yield prediction model."""
    model_path = MODEL_DIR / "yield_model.joblib"
    crop_enc_path = MODEL_DIR / "yield_crop_encoder.joblib"
    soil_enc_path = MODEL_DIR / "yield_soil_encoder.joblib"
    meta_path = MODEL_DIR / "yield_meta.joblib"
    if not all(p.exists() for p in [model_path, crop_enc_path, soil_enc_path, meta_path]):
        return None, None, None, None
    return (
        joblib.load(model_path),
        joblib.load(crop_enc_path),
        joblib.load(soil_enc_path),
        joblib.load(meta_path),
    )


def extract_hog_features(image: Image.Image) -> np.ndarray:
    """Extract HOG + Color Histogram + Statistical features from a PIL image."""
    from skimage.color import rgb2hsv

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

    # 2. Color histogram features (RGB)
    color_features = []
    for channel in range(3):
        hist, _ = np.histogram(img_resized[:, :, channel], bins=32, range=(0, 1))
        hist = hist.astype(float) / (hist.sum() + 1e-7)
        color_features.extend(hist)

    # 3. HSV color histogram
    img_hsv = rgb2hsv(img_resized)
    for channel in range(3):
        hist, _ = np.histogram(img_hsv[:, :, channel], bins=32, range=(0, 1))
        hist = hist.astype(float) / (hist.sum() + 1e-7)
        color_features.extend(hist)

    # 4. Statistical features
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


def get_severity_badge(severity: str) -> str:
    """Return HTML badge based on severity level."""
    severity_lower = severity.lower()
    if "none" in severity_lower:
        return f'<span class="badge badge-none">✅ {severity}</span>'
    elif "very high" in severity_lower:
        return f'<span class="badge badge-veryhigh">🔴 {severity}</span>'
    elif "high" in severity_lower:
        return f'<span class="badge badge-high">🟠 {severity}</span>'
    else:
        return f'<span class="badge badge-moderate">🟡 {severity}</span>'


def format_class_name(class_name: str) -> str:
    """Make class names human-readable."""
    name = class_name.replace("__", " — ").replace("_", " ")
    return name


# ═══════════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs([
    "🔬 Disease Detection & Management",
    "🏛️ Government Schemes",
    "📊 Crop Yield Prediction",
])


# ═══════════════════════════════════════════════════════════════════════
#  TAB 1 — Disease Detection
# ═══════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 🔬 Early Detection & Management of Crop Diseases and Pest Infestation")
    st.markdown(
        "Upload an image of a **Pepper, Potato, or Tomato** leaf and our AI model will "
        "detect the disease and provide detailed management recommendations."
    )

    disease_model, label_encoder = load_disease_model()

    if disease_model is None:
        st.error(
            "⚠️ **Disease model not found!** Please run the training script first:\n\n"
            "```bash\npython train_disease_model.py\n```"
        )
    else:
        col_upload, col_result = st.columns([1, 1.5])

        with col_upload:
            st.markdown("### 📤 Upload Leaf Image")
            uploaded_file = st.file_uploader(
                "Choose a leaf image (JPG/PNG)",
                type=["jpg", "jpeg", "png"],
                key="disease_upload",
            )

            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_container_width=True)

                if st.button("🔍 Analyze Disease", type="primary", use_container_width=True):
                    with st.spinner("Extracting features and classifying..."):
                        features = extract_hog_features(image)
                        features = features.reshape(1, -1)

                        # Get prediction probabilities
                        proba = disease_model.predict_proba(features)[0]
                        pred_idx = np.argmax(proba)
                        pred_class = label_encoder.inverse_transform([pred_idx])[0]
                        confidence = proba[pred_idx] * 100

                        st.session_state["prediction"] = {
                            "class": pred_class,
                            "confidence": confidence,
                            "probabilities": proba,
                        }

        with col_result:
            if "prediction" in st.session_state:
                pred = st.session_state["prediction"]
                pred_class = pred["class"]
                confidence = pred["confidence"]

                st.markdown("### 📋 Diagnosis Result")

                # Get disease info
                info = DISEASE_INFO.get(pred_class, None)

                if info:
                    is_healthy = "healthy" in pred_class.lower()

                    # Result header
                    if is_healthy:
                        card_class = "success-card"
                        emoji = "✅"
                    elif "very high" in info["severity"].lower():
                        card_class = "danger-card"
                        emoji = "🚨"
                    else:
                        card_class = "warning-card"
                        emoji = "⚠️"

                    st.markdown(
                        f"""
                        <div class="{card_class}">
                            <h3>{emoji} {info['crop']} — {info['disease']}</h3>
                            <p>Confidence: <strong>{confidence:.1f}%</strong> &nbsp;&nbsp;
                            Severity: {get_severity_badge(info['severity'])}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Cause
                    st.markdown(f"**🔎 Cause:** {info['cause']}")

                    # Symptoms
                    st.markdown("**🩺 Symptoms:**")
                    for s in info["symptoms"]:
                        st.markdown(f"- {s}")

                    # Management
                    st.markdown("**💊 Management / Treatment:**")
                    for m in info["management"]:
                        st.markdown(f"- {m}")

                    # Confidence chart (top 5 predictions)
                    st.markdown("---")
                    st.markdown("**📊 Prediction Confidence (Top 5):**")
                    top_indices = np.argsort(pred["probabilities"])[::-1][:5]
                    chart_data = pd.DataFrame(
                        {
                            "Disease": [
                                format_class_name(label_encoder.inverse_transform([i])[0])
                                for i in top_indices
                            ],
                            "Confidence (%)": [pred["probabilities"][i] * 100 for i in top_indices],
                        }
                    )
                    fig = px.bar(
                        chart_data,
                        x="Confidence (%)",
                        y="Disease",
                        orientation="h",
                        color="Confidence (%)",
                        color_continuous_scale=["#ffcccc", "#28a745"],
                    )
                    fig.update_layout(
                        height=250,
                        margin=dict(l=0, r=0, t=10, b=0),
                        yaxis=dict(autorange="reversed"),
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Predicted class: **{format_class_name(pred_class)}** (confidence: {confidence:.1f}%)")
                    st.info("Detailed information not available for this class.")

    # Dataset overview
    st.markdown("---")
    with st.expander("📂 About the PlantVillage Dataset"):
        st.markdown(
            """
            This model is trained on the **PlantVillage** dataset containing leaf images of:
            - **Pepper (Bell):** Bacterial Spot, Healthy
            - **Potato:** Early Blight, Late Blight, Healthy
            - **Tomato:** Bacterial Spot, Early Blight, Late Blight, Leaf Mold,
              Septoria Leaf Spot, Spider Mites, Target Spot, Mosaic Virus,
              Yellow Leaf Curl Virus, Healthy

            **Total:** ~20,000+ labeled images across 15 classes.

            The model uses **HOG (Histogram of Oriented Gradients)** feature extraction
            with a **Random Forest** classifier.
            """
        )


# ═══════════════════════════════════════════════════════════════════════
#  TAB 2 — Government Schemes
# ═══════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 🏛️ Government Schemes & Policies for Farmers")
    st.markdown(
        "Explore government schemes designed to support Indian farmers. "
        "Filter by category and click on a scheme to see full details and how to apply."
    )

    # Category filter
    categories = sorted(set(s["category"] for s in GOVERNMENT_SCHEMES))
    col_filter, col_search = st.columns([1, 2])
    with col_filter:
        selected_category = st.selectbox(
            "Filter by Category",
            ["All Categories"] + categories,
        )
    with col_search:
        search_query = st.text_input("🔍 Search schemes", placeholder="e.g., insurance, credit, organic...")

    # Filter schemes
    filtered_schemes = GOVERNMENT_SCHEMES
    if selected_category != "All Categories":
        filtered_schemes = [s for s in filtered_schemes if s["category"] == selected_category]
    if search_query:
        query_lower = search_query.lower()
        filtered_schemes = [
            s for s in filtered_schemes
            if query_lower in s["name"].lower()
            or query_lower in s["description"].lower()
            or query_lower in s["category"].lower()
        ]

    st.markdown(f"**Showing {len(filtered_schemes)} scheme(s)**")

    # Display schemes
    for scheme in filtered_schemes:
        with st.expander(f"{scheme['icon']} **{scheme['name']}** — _{scheme['category']}_"):
            st.markdown(f"**Ministry:** {scheme['ministry']}")
            st.markdown(f"**Description:** {scheme['description']}")

            col_b, col_e = st.columns(2)
            with col_b:
                st.markdown("**✅ Key Benefits:**")
                for b in scheme["benefits"]:
                    st.markdown(f"- {b}")

            with col_e:
                st.markdown("**👤 Eligibility:**")
                for e in scheme["eligibility"]:
                    st.markdown(f"- {e}")

            st.markdown("**📝 How to Apply:**")
            for h in scheme["how_to_apply"]:
                st.markdown(f"- {h}")

            st.markdown(f"🔗 **Website:** [{scheme['website']}]({scheme['website']})")

    # Summary chart
    st.markdown("---")
    st.markdown("### 📊 Schemes by Category")
    cat_counts = pd.DataFrame(
        [{"Category": s["category"], "Count": 1} for s in GOVERNMENT_SCHEMES]
    ).groupby("Category").sum().reset_index()
    fig = px.pie(
        cat_counts,
        names="Category",
        values="Count",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4,
    )
    fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
#  TAB 3 — Yield Prediction
# ═══════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 📊 Crop Yield Prediction")
    st.markdown(
        "Predict expected crop yield (tonnes per hectare) based on soil type, "
        "weather conditions, and soil nutrient levels."
    )

    yield_model, crop_encoder, soil_encoder, yield_meta = load_yield_model()

    if yield_model is None:
        st.error(
            "⚠️ **Yield model not found!** Please run the training script first:\n\n"
            "```bash\npython train_yield_model.py\n```"
        )
    else:
        col_input, col_output = st.columns([1, 1.5])

        with col_input:
            st.markdown("### 🌾 Enter Crop & Conditions")

            crop = st.selectbox("Crop", yield_meta["crops"])
            soil = st.selectbox("Soil Type", yield_meta["soils"])

            st.markdown("#### 🌤️ Weather Conditions")
            c1, c2 = st.columns(2)
            with c1:
                temperature = st.slider("Temperature (°C)", 5.0, 45.0, 25.0, 0.5)
                rainfall = st.slider("Annual Rainfall (mm)", 100.0, 3000.0, 800.0, 50.0)
            with c2:
                humidity = st.slider("Humidity (%)", 20.0, 100.0, 65.0, 1.0)
                ph = st.slider("Soil pH", 3.5, 9.5, 6.5, 0.1)

            st.markdown("#### 🧪 Soil Nutrients (kg/ha)")
            n1, n2, n3 = st.columns(3)
            with n1:
                nitrogen = st.number_input("Nitrogen (N)", 10.0, 140.0, 60.0, 5.0)
            with n2:
                phosphorus = st.number_input("Phosphorus (P)", 5.0, 80.0, 35.0, 5.0)
            with n3:
                potassium = st.number_input("Potassium (K)", 5.0, 80.0, 35.0, 5.0)

            predict_btn = st.button("🔮 Predict Yield", type="primary", use_container_width=True)

        with col_output:
            if predict_btn:
                with st.spinner("Calculating yield prediction..."):
                    # Encode inputs
                    try:
                        crop_enc = crop_encoder.transform([crop])[0]
                        soil_enc = soil_encoder.transform([soil])[0]
                    except ValueError as e:
                        st.error(f"Encoding error: {e}")
                        st.stop()

                    features = np.array([[
                        crop_enc, soil_enc, temperature, rainfall,
                        humidity, ph, nitrogen, phosphorus, potassium,
                    ]])

                    predicted_yield = yield_model.predict(features)[0]
                    predicted_yield = max(0, predicted_yield)

                    st.markdown("### 📈 Prediction Result")

                    # Main metric
                    st.metric(
                        label=f"Predicted Yield for {crop}",
                        value=f"{predicted_yield:.2f} tonnes/ha",
                    )

                    # Gauge chart
                    fig_gauge = go.Figure(
                        go.Indicator(
                            mode="gauge+number",
                            value=predicted_yield,
                            title={"text": f"{crop} Yield (tonnes/ha)"},
                            gauge={
                                "axis": {"range": [0, max(80, predicted_yield * 1.5)]},
                                "bar": {"color": "#2d6a4f"},
                                "steps": [
                                    {"range": [0, predicted_yield * 0.5], "color": "#f8d7da"},
                                    {"range": [predicted_yield * 0.5, predicted_yield * 0.8], "color": "#fff3cd"},
                                    {"range": [predicted_yield * 0.8, max(80, predicted_yield * 1.5)], "color": "#d4edda"},
                                ],
                                "threshold": {
                                    "line": {"color": "red", "width": 4},
                                    "thickness": 0.75,
                                    "value": predicted_yield,
                                },
                            },
                        )
                    )
                    fig_gauge.update_layout(height=280, margin=dict(l=30, r=30, t=50, b=10))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                    # Input summary
                    st.markdown("**📋 Input Summary:**")
                    summary_df = pd.DataFrame(
                        {
                            "Parameter": [
                                "Crop", "Soil Type", "Temperature", "Rainfall",
                                "Humidity", "pH", "Nitrogen", "Phosphorus", "Potassium",
                            ],
                            "Value": [
                                crop, soil, f"{temperature}°C", f"{rainfall} mm",
                                f"{humidity}%", f"{ph}", f"{nitrogen} kg/ha",
                                f"{phosphorus} kg/ha", f"{potassium} kg/ha",
                            ],
                        }
                    )
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)

                    # Feature importance
                    st.markdown("**🔑 Feature Importance in Prediction:**")
                    feature_imp = pd.DataFrame(
                        {
                            "Feature": yield_meta["feature_names"],
                            "Importance": yield_model.feature_importances_,
                        }
                    ).sort_values("Importance", ascending=True)

                    fig_imp = px.bar(
                        feature_imp,
                        x="Importance",
                        y="Feature",
                        orientation="h",
                        color="Importance",
                        color_continuous_scale="Greens",
                    )
                    fig_imp.update_layout(
                        height=300,
                        margin=dict(l=0, r=0, t=10, b=0),
                        showlegend=False,
                    )
                    st.plotly_chart(fig_imp, use_container_width=True)

                    # Recommendations
                    st.markdown("---")
                    st.markdown("### 💡 Recommendations")
                    if ph < 5.5:
                        st.warning("🔸 Soil pH is **acidic**. Consider applying lime to raise pH.")
                    elif ph > 8.0:
                        st.warning("🔸 Soil pH is **alkaline**. Consider adding gypsum or sulfur.")
                    if nitrogen < 40:
                        st.info("🔹 Nitrogen levels are **low**. Apply urea or organic nitrogen sources.")
                    if phosphorus < 20:
                        st.info("🔹 Phosphorus is **low**. Apply DAP or SSP fertilizer.")
                    if potassium < 20:
                        st.info("🔹 Potassium is **low**. Apply MOP (Muriate of Potash).")
                    if rainfall < 400:
                        st.warning("🔸 Rainfall is **low**. Consider irrigation support — check PMKSY scheme in Government Schemes tab.")
                    if temperature > 38:
                        st.warning("🔸 Temperature is **very high**. Choose heat-tolerant varieties.")

        # Comparison tool
        st.markdown("---")
        with st.expander("📊 Compare Yield Across Soil Types"):
            if yield_model is not None:
                compare_crop = st.selectbox("Select crop for comparison", yield_meta["crops"], key="compare_crop")
                results = []
                for s in yield_meta["soils"]:
                    try:
                        c_enc = crop_encoder.transform([compare_crop])[0]
                        s_enc = soil_encoder.transform([s])[0]
                        feat = np.array([[c_enc, s_enc, 25.0, 800.0, 65.0, 6.5, 60.0, 35.0, 35.0]])
                        y_pred = yield_model.predict(feat)[0]
                        results.append({"Soil Type": s, "Predicted Yield (tonnes/ha)": round(max(0, y_pred), 2)})
                    except Exception:
                        pass
                if results:
                    comp_df = pd.DataFrame(results).sort_values("Predicted Yield (tonnes/ha)", ascending=False)
                    fig_comp = px.bar(
                        comp_df,
                        x="Soil Type",
                        y="Predicted Yield (tonnes/ha)",
                        color="Predicted Yield (tonnes/ha)",
                        color_continuous_scale="YlGn",
                        title=f"Yield of {compare_crop} across Soil Types (standard conditions)",
                    )
                    fig_comp.update_layout(height=350)
                    st.plotly_chart(fig_comp, use_container_width=True)


# ─── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 KrushiSarathi")
    st.markdown("*Your Agricultural Companion*")
    st.markdown("---")
    st.markdown(
        """
        ### 📖 How to Use

        **Tab 1 — Disease Detection**
        1. Upload a photo of a diseased leaf
        2. Click **Analyze Disease**
        3. View diagnosis, severity, and treatment

        **Tab 2 — Government Schemes**
        1. Browse or search agricultural schemes
        2. Check eligibility and benefits
        3. Follow the application steps

        **Tab 3 — Yield Prediction**
        1. Select crop and soil type
        2. Set weather and nutrient values
        3. Click **Predict Yield**
        """
    )
    st.markdown("---")
    st.markdown(
        """
        ### 🌱 Supported Crops

        **Disease Detection:**
        - 🫑 Pepper (Bell)
        - 🥔 Potato
        - 🍅 Tomato

        **Yield Prediction:**
        - Rice, Wheat, Maize
        - Sugarcane, Cotton, Soybean
        - Potato, Tomato, Pepper
        - Groundnut, Mustard, Chickpea
        - Onion, Banana, Mango
        """
    )
    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit & Scikit-learn")
