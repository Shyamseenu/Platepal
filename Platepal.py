import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Plate Pal",
    page_icon="🍽️",
    layout="wide",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
    }
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }
    .recipe-card {
        background: #fff;
        border-left: 4px solid #e07a5f;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .recipe-card h4 {
        font-family: 'Playfair Display', serif;
        color: #1a1a2e;
        font-size: 1.2rem;
        margin-bottom: 0.3rem;
    }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        margin-right: 5px;
        margin-bottom: 6px;
    }
    .badge-cal  { background: #fde8d8; color: #c0392b; }
    .badge-fat  { background: #fef9e7; color: #d68910; }
    .badge-carb { background: #eafaf1; color: #1e8449; }
    .badge-prot { background: #ebf5fb; color: #1a5276; }
    .badge-sim  { background: #f4ecf7; color: #7d3c98; }
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background: #e8f4f8;
        border-left: 4px solid #3498db;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Data loading (cached)
# ─────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file):
    """Load and validate the recipe dataset."""
    df = pd.read_csv(uploaded_file)
    required_cols = {'Name', 'Calories', 'FatContent', 'CarbohydrateContent',
                     'ProteinContent', 'RecipeInstructions'}
    missing = required_cols - set(df.columns)
    if missing:
        st.error(f"Dataset is missing columns: {missing}")
        st.stop()
    df = df.dropna(subset=list(required_cols))
    return df


# ─────────────────────────────────────────────
# Health-based filtering
# ─────────────────────────────────────────────
def apply_health_filters(df, sugar_level, blood_pressure):
    """
    Filter recipes based on medical indicators.
    - High sugar (≥126 mg/dL): restrict high-calorie and high-carb foods
    - High BP (≥130 mmHg): restrict high-fat and high-sodium foods (fat used as proxy)
    """
    filtered = df.copy()
    warnings = []

    if sugar_level >= 126:
        carb_threshold = filtered['CarbohydrateContent'].quantile(0.60)
        cal_threshold  = filtered['Calories'].quantile(0.60)
        filtered = filtered[
            (filtered['CarbohydrateContent'] <= carb_threshold) &
            (filtered['Calories'] <= cal_threshold)
        ]
        warnings.append("🩸 High sugar detected — high-carb and high-calorie recipes have been filtered out.")

    if blood_pressure >= 130:
        fat_threshold = filtered['FatContent'].quantile(0.60)
        filtered = filtered[filtered['FatContent'] <= fat_threshold]
        warnings.append("❤️ High blood pressure detected — high-fat recipes have been filtered out.")

    return filtered, warnings


# ─────────────────────────────────────────────
# Similarity calculation (FIX: normalize user
# values against dataset ranges, not themselves)
# ─────────────────────────────────────────────
def calculate_similarity(user_raw_values, df):
    """
    Normalise user inputs and dataset values using the SAME scale
    (dataset min/max), then compute cosine similarity.
    """
    nutrient_cols = ['Calories', 'FatContent', 'CarbohydrateContent', 'ProteinContent']
    data_values = df[nutrient_cols].copy()

    col_min = data_values.min()
    col_max = data_values.max()
    denom   = (col_max - col_min).replace(0, 1)   # avoid division by zero

    # Normalise dataset
    data_norm = (data_values - col_min) / denom

    # Normalise user values using SAME dataset scale (the critical fix)
    user_norm = [(val - col_min[col]) / denom[col]
                 for val, col in zip(user_raw_values, nutrient_cols)]
    user_norm = [max(0.0, min(1.0, v)) for v in user_norm]   # clamp to [0,1]

    similarity = cosine_similarity([user_norm], data_norm.values)
    result = df.copy()
    result['Similarity'] = similarity[0]
    return result


# ─────────────────────────────────────────────
# UI — Header
# ─────────────────────────────────────────────
st.markdown('<p class="main-title">🍽️ Plate Pal</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Where AI meets your Appetite</p>', unsafe_allow_html=True)
st.divider()


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("👤 Sign In")
    name = st.text_input("Your name")
    if st.button("Sign In", use_container_width=True):
        if name.strip():
            st.session_state.signed_in = True
            st.session_state.name = name.strip()
            st.success(f"Welcome, {name.strip()}! 👋")
        else:
            st.warning("Please enter your name.")

    if st.session_state.get("signed_in"):
        st.divider()
        st.header("📋 Your Profile")

        age = st.slider("Age", 1, 100, 30)
        sugar_level    = st.slider("Sugar Level (mg/dL)", 60, 500, 90,
                                   help="Normal fasting: 70–99 | Prediabetes: 100–125 | Diabetic: ≥126")
        blood_pressure = st.slider("Blood Pressure (mmHg)", 60, 200, 120,
                                   help="Normal: <120 | Elevated: 120–129 | High: ≥130")

        st.divider()
        st.subheader("🥗 Daily Nutrition Goals")
        calories      = st.slider("Calories (kcal)",  500,  5000, 2000)
        fat_content   = st.slider("Fat (g)",            1,   300,   70)
        carb_content  = st.slider("Carbohydrates (g)",  1,   600,  250)
        prot_content  = st.slider("Protein (g)",        1,   300,   50)

        st.divider()
        st.header("📂 Upload Dataset")
        uploaded_file = st.file_uploader(
            "Upload Recipe Dataset (.csv)",
            type=["csv"],
            help="CSV must contain: Name, Calories, FatContent, CarbohydrateContent, ProteinContent, RecipeInstructions"
        )
        n_results = st.slider("Number of recommendations", 3, 20, 5)

        get_recs = st.button("🔍 Get Recommendations", use_container_width=True, type="primary")


# ─────────────────────────────────────────────
# Main area
# ─────────────────────────────────────────────
if not st.session_state.get("signed_in"):
    st.markdown("""
    <div class="info-box">
        👈 Please <strong>sign in</strong> from the sidebar to get started.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Show user summary
col1, col2, col3, col4 = st.columns(4)
col1.metric("🔥 Calories",      f"{calories} kcal")
col2.metric("🥩 Protein",       f"{prot_content} g")
col3.metric("🍞 Carbohydrates", f"{carb_content} g")
col4.metric("🧈 Fat",           f"{fat_content} g")

# Medical indicators
if sugar_level >= 126:
    st.markdown('<div class="warning-box">⚠️ <strong>Elevated blood sugar</strong> detected. Recommendations will prioritise low-carb, low-calorie options.</div>', unsafe_allow_html=True)
if blood_pressure >= 130:
    st.markdown('<div class="warning-box">⚠️ <strong>Elevated blood pressure</strong> detected. Recommendations will prioritise low-fat options.</div>', unsafe_allow_html=True)

st.divider()

# Recommendations
if get_recs:
    if uploaded_file is None:
        st.error("📂 Please upload your Recipe Dataset CSV from the sidebar first.")
        st.stop()

    with st.spinner("Analysing recipes…"):
        data = load_data(uploaded_file)

        # Apply health-based filters
        filtered_data, health_warnings = apply_health_filters(data, sugar_level, blood_pressure)

        for w in health_warnings:
            st.info(w)

        if filtered_data.empty:
            st.error("No recipes matched your health filters. Try adjusting your inputs.")
            st.stop()

        # Calculate similarity
        user_raw = [calories, fat_content, carb_content, prot_content]
        results  = calculate_similarity(user_raw, filtered_data)
        top_n    = results.sort_values('Similarity', ascending=False).head(n_results)

    st.subheader(f"✨ Top {n_results} Recipes for {st.session_state.name}")

    for rank, (_, row) in enumerate(top_n.iterrows(), 1):
        sim_pct = round(row['Similarity'] * 100, 1)
        with st.container():
            st.markdown(f"""
            <div class="recipe-card">
                <h4>#{rank} &nbsp; {row['Name']}</h4>
                <span class="badge badge-cal">🔥 {round(row['Calories'])} kcal</span>
                <span class="badge badge-fat">🧈 Fat {round(row['FatContent'])}g</span>
                <span class="badge badge-carb">🍞 Carbs {round(row['CarbohydrateContent'])}g</span>
                <span class="badge badge-prot">🥩 Protein {round(row['ProteinContent'])}g</span>
                <span class="badge badge-sim">✅ {sim_pct}% match</span>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("📖 View Recipe Instructions"):
                st.write(row['RecipeInstructions'])

    # Download results
    st.divider()
    csv_out = top_n[['Name', 'Calories', 'FatContent', 'CarbohydrateContent',
                      'ProteinContent', 'Similarity', 'RecipeInstructions']].to_csv(index=False)
    st.download_button(
        label="⬇️ Download Recommendations as CSV",
        data=csv_out,
        file_name="plate_pal_recommendations.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    st.markdown("""
    <div class="info-box">
        👈 Fill in your profile in the sidebar, upload your recipe dataset, then click <strong>Get Recommendations</strong>.
    </div>
    """, unsafe_allow_html=True)
