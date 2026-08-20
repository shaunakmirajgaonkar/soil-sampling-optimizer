
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="GroundWatch Local",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path("data/synthetic_subsidence_registry.csv")

REQUIRED_COLUMNS = ['record_id', 'zone_code', 'observation_date', 'satellite_subsidence_mm_year', 'subsidence_trend_score', 'groundwater_extraction_score', 'groundwater_level_change_m', 'construction_activity_score', 'building_density_score', 'soil_susceptibility_score', 'rainfall_30d_mm', 'rainfall_anomaly_score', 'drainage_condition_score', 'surface_load_score', 'historical_subsidence_score', 'monitoring_confidence_score', 'source_data_status', 'review_status']

# ---------- Theme ----------
st.markdown("""
<style>
.stApp {
    background: #f5f8fa;
    color: #172b34;
}
.block-container {
    max-width: 1500px;
    padding: 1.25rem 2rem 3rem;
}
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #dce6ea;
}
[data-testid="stSidebar"] * {
    color: #21343d !important;
}
.hero {
    background: linear-gradient(135deg, #ffffff 0%, #eef7f6 52%, #eef4fb 100%);
    border: 1px solid #d8e6e9;
    border-radius: 28px;
    padding: 30px 34px;
    margin-bottom: 18px;
    box-shadow: 0 14px 38px rgba(29, 58, 68, 0.07);
}
.hero h1 {
    color: #18353d;
    font-size: 2.55rem;
    letter-spacing: -0.045em;
    margin: 14px 0 8px;
}
.hero p {
    color: #566b73;
    line-height: 1.65;
}
.pill {
    display: inline-block;
    padding: 7px 12px;
    margin-right: 6px;
    border-radius: 999px;
    background: #e8f5f2;
    border: 1px solid #cce5df;
    color: #21655b;
    font-size: .72rem;
    font-weight: 800;
}
.card {
    background: #ffffff;
    border: 1px solid #dce7ea;
    border-radius: 20px;
    padding: 20px;
    margin: 12px 0;
    box-shadow: 0 7px 22px rgba(32, 61, 72, .045);
}
.info {
    background: #f0f7fb;
    border: 1px solid #d6e6ee;
    border-radius: 16px;
    padding: 15px;
    color: #385864;
}
.warn {
    background: #fff9eb;
    border: 1px solid #ead9a7;
    border-radius: 16px;
    padding: 15px;
    color: #67551f;
}
.danger {
    background: #fff4f1;
    border: 1px solid #ebcfc6;
    border-radius: 16px;
    padding: 15px;
    color: #6d382d;
}
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #dce7ea;
    border-radius: 18px;
    padding: 12px 16px;
}
h2, h3 {
    color: #1d3740 !important;
}
</style>
""", unsafe_allow_html=True)


def calculate_score(row):
    # Transparent local screening rules.
    subsidence = np.clip(float(row["satellite_subsidence_mm_year"]) / 40 * 100, 0, 100)

    factors = {
        "satellite": subsidence,
        "trend": float(row["subsidence_trend_score"]),
        "groundwater": float(row["groundwater_extraction_score"]),
        "construction": float(row["construction_activity_score"]),
        "density": float(row["building_density_score"]),
        "soil": float(row["soil_susceptibility_score"]),
        "rainfall": float(row["rainfall_anomaly_score"]),
        "surface_load": float(row["surface_load_score"]),
        "historical": float(row["historical_subsidence_score"]),
    }

    score = round(float(np.clip(
        0.20 * factors["satellite"]
        + 0.12 * factors["trend"]
        + 0.14 * factors["groundwater"]
        + 0.10 * factors["construction"]
        + 0.08 * factors["density"]
        + 0.12 * factors["soil"]
        + 0.07 * factors["rainfall"]
        + 0.05 * factors["surface_load"]
        + 0.12 * factors["historical"],
        0, 100
    )), 1)

    if score < 30:
        band = "Low Review"
    elif score < 55:
        band = "Moderate Review"
    elif score < 75:
        band = "High Review"
    else:
        band = "Critical Review"

    reasons = []
    if factors["satellite"] >= 70:
        reasons.append("elevated satellite-derived subsidence signal")
    if factors["groundwater"] >= 70:
        reasons.append("high groundwater-extraction signal")
    if factors["construction"] >= 70:
        reasons.append("high construction-activity signal")
    if factors["soil"] >= 70:
        reasons.append("susceptible soil signal")
    if factors["historical"] >= 70:
        reasons.append("strong historical-subsidence signal")
    if factors["rainfall"] >= 70:
        reasons.append("elevated rainfall-anomaly signal")
    if factors["density"] >= 75:
        reasons.append("high building-density context")

    explanation = "; ".join(reasons) if reasons else "No strong contributing signal under the local screening rules."

    return score, band, explanation


# ---------- Load and validate ----------
try:
    df = pd.read_csv(DATA_PATH)
except Exception as exc:
    st.error(f"Unable to load the local registry: {exc}")
    st.stop()

missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.stop()

scored = df.apply(calculate_score, axis=1, result_type="expand")
scored.columns = ["subsidence_risk_score", "review_band", "factor_explanation"]
df = pd.concat([df.reset_index(drop=True), scored], axis=1)


# ---------- Navigation ----------
st.sidebar.markdown("## 🌍 GroundWatch Local")
st.sidebar.caption("Land-subsidence early-warning screening")

page = st.sidebar.radio(
    "Workspace",
    [
        "Ground Stability Command Center",
        "Zone Explorer",
        "Subsidence Drivers",
        "Record Review",
        "Local Data Lab",
        "Responsible Use",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("100% local processing")
st.sidebar.caption("No external APIs")
st.sidebar.caption("Synthetic or authorized records only")


# ---------- Hero ----------
st.markdown("""
<div class="hero">
    <span class="pill">LOCAL-FIRST</span>
    <span class="pill">GEOHAZARD SCREENING</span>
    <span class="pill">EXPLAINABLE</span>
    <span class="pill">HUMAN REVIEW</span>
    <h1>🌍 GroundWatch Local</h1>
    <p>
        <b>Land Subsidence Early-Warning Mapper</b> — screen locally supplied
        geographic records for potential ground-sinking signals using
        satellite measurements, groundwater extraction, construction activity,
        soil susceptibility, rainfall, surface loading, and historical trends.
    </p>
    <p>
        Results are screening signals, not confirmed ground movement,
        engineering findings, property-safety determinations, or predictions
        of future subsidence.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------- Pages ----------
if page == "Ground Stability Command Center":
    a, b, c, d, e = st.columns(5)
    a.metric("Zones monitored", len(df))
    b.metric("Average score", f"{df['subsidence_risk_score'].mean():.0f}/100")
    c.metric("High / Critical", int((df["subsidence_risk_score"] >= 55).sum()))
    d.metric("High groundwater signal", int((df["groundwater_extraction_score"] >= 70).sum()))
    e.metric("High soil susceptibility", int((df["soil_susceptibility_score"] >= 70).sum()))

    left, right = st.columns(2)

    with left:
        q = (
            df.groupby("zone_code", as_index=False)["subsidence_risk_score"]
            .mean()
            .sort_values("subsidence_risk_score", ascending=False)
        )
        fig = px.bar(
            q,
            x="zone_code",
            y="subsidence_risk_score",
            title="Subsidence screening score by zone",
        )
        fig.update_layout(template="plotly_white", height=370)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.scatter(
            df,
            x="satellite_subsidence_mm_year",
            y="subsidence_risk_score",
            size="groundwater_extraction_score",
            color="review_band",
            hover_name="zone_code",
            title="Observed subsidence signal vs screening score",
        )
        fig.update_layout(template="plotly_white", height=370)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="warn"><b>Interpretation:</b> Higher scores indicate a combination of '
        'local ground-movement and contributing-condition signals. They do not establish '
        'that a zone is unsafe or that future ground sinking will occur.</div>',
        unsafe_allow_html=True,
    )

    display_cols = [
        "record_id", "zone_code", "satellite_subsidence_mm_year",
        "groundwater_extraction_score", "construction_activity_score",
        "soil_susceptibility_score", "rainfall_anomaly_score",
        "subsidence_risk_score", "review_band",
    ]
    st.dataframe(
        df[display_cols].sort_values("subsidence_risk_score", ascending=False),
        use_container_width=True,
        hide_index=True,
    )


elif page == "Zone Explorer":
    st.subheader("🗺️ Zone stability explorer")

    zone = st.selectbox(
        "Select zone",
        ["All zones"] + sorted(df["zone_code"].astype(str).unique()),
    )
    view = df if zone == "All zones" else df[df["zone_code"] == zone]

    a, b, c = st.columns(3)
    a.metric("Records", len(view))
    b.metric("Mean screening score", f"{view['subsidence_risk_score'].mean():.0f}/100")
    b.metric if False else None
    c.metric("Mean satellite signal", f"{view['satellite_subsidence_mm_year'].mean():.1f} mm/yr")

    fig = px.scatter(
        view,
        x="groundwater_extraction_score",
        y="satellite_subsidence_mm_year",
        size="construction_activity_score",
        color="review_band",
        hover_name="zone_code",
        title="Groundwater extraction vs observed subsidence",
    )
    fig.update_layout(template="plotly_white", height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        view[
            [
                "record_id", "zone_code", "satellite_subsidence_mm_year",
                "groundwater_level_change_m", "construction_activity_score",
                "soil_susceptibility_score", "historical_subsidence_score",
                "subsidence_risk_score", "review_band",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


elif page == "Subsidence Drivers":
    st.subheader("📊 Potential contributing-condition signals")

    signal_cols = [
        "subsidence_trend_score",
        "groundwater_extraction_score",
        "construction_activity_score",
        "building_density_score",
        "soil_susceptibility_score",
        "rainfall_anomaly_score",
        "surface_load_score",
        "historical_subsidence_score",
    ]

    means = df[signal_cols].mean().reset_index()
    means.columns = ["signal", "mean_score"]

    fig = px.bar(
        means,
        x="signal",
        y="mean_score",
        title="Average contributing-condition signals",
    )
    fig.update_layout(template="plotly_white", height=430, xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.scatter(
        df,
        x="soil_susceptibility_score",
        y="subsidence_risk_score",
        size="rainfall_anomaly_score",
        color="review_band",
        hover_name="zone_code",
        title="Soil susceptibility vs screening score",
    )
    fig.update_layout(template="plotly_white", height=430)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="info"><b>Assessment approach:</b> Compare independent '
        'measurements and contextual factors. Engineering or geotechnical '
        'assessment may require validated remote-sensing products, field '
        'measurements, groundwater data, soil investigations, and local '
        'engineering review.</div>',
        unsafe_allow_html=True,
    )


elif page == "Record Review":
    st.subheader("📋 Zone record review")

    selected = st.selectbox("Select record", df["record_id"].astype(str).tolist())
    r = df[df["record_id"].astype(str) == selected].iloc[0]

    a, b, c, d = st.columns(4)
    a.metric("Screening score", f"{r['subsidence_risk_score']:.0f}/100")
    b.metric("Review band", r["review_band"])
    c.metric("Satellite signal", f"{r['satellite_subsidence_mm_year']:.1f} mm/yr")
    d.metric("Groundwater signal", f"{r['groundwater_extraction_score']:.0f}/100")

    st.markdown(
        '<div class="danger"><b>Safety boundary:</b> This screening record '
        'must not be interpreted as an engineering safety assessment, a finding '
        'of structural danger, or a prediction of imminent ground failure.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(f"**Zone:** {r['zone_code']}  •  **Observation date:** {r['observation_date']}")
    st.write(
        f"**Subsidence:** {r['satellite_subsidence_mm_year']:.1f} mm/yr  •  "
        f"**Groundwater extraction:** {r['groundwater_extraction_score']}/100  •  "
        f"**Construction:** {r['construction_activity_score']}/100"
    )
    st.write(
        f"**Soil susceptibility:** {r['soil_susceptibility_score']}/100  •  "
        f"**Historical signal:** {r['historical_subsidence_score']}/100  •  "
        f"**Rainfall anomaly:** {r['rainfall_anomaly_score']}/100"
    )
    st.write(f"**Factor explanation:** {r['factor_explanation']}")
    st.markdown("</div>", unsafe_allow_html=True)


elif page == "Local Data Lab":
    st.subheader("📂 CSV validation and local replacement")
    st.write("CSV files are processed locally and validated before replacement.")

    st.code(", ".join(REQUIRED_COLUMNS), language="text")

    uploaded = st.file_uploader(
        "Replace local land-subsidence registry",
        type=["csv"],
    )

    if uploaded:
        try:
            new_df = pd.read_csv(uploaded)
            missing = [c for c in REQUIRED_COLUMNS if c not in new_df.columns]

            if missing:
                st.error("Missing required columns: " + ", ".join(missing))
            elif new_df.empty:
                st.error("The uploaded CSV contains no records.")
            else:
                new_df.to_csv(DATA_PATH, index=False)
                st.success(f"Validated and loaded {len(new_df):,} records.")
                st.rerun()

        except Exception as exc:
            st.error(f"CSV validation failed: {exc}")

    st.markdown("### Current local registry")
    st.dataframe(
        df[REQUIRED_COLUMNS],
        use_container_width=True,
        hide_index=True,
    )

    export = df.drop(columns=["factor_explanation"], errors="ignore").to_csv(index=False).encode()
    st.download_button(
        "Download scored subsidence registry",
        export,
        "land_subsidence_scored.csv",
        "text/csv",
    )


else:
    st.subheader("🛡️ Responsible use")

    st.markdown("""
    <div class="card">
    <h3>Early-warning screening, not engineering certification</h3>
    <ul>
        <li>Use synthetic or authorized geographic and infrastructure records only.</li>
        <li>Do not interpret the score as proof that a building, road, or property is unsafe.</li>
        <li>Do not use the platform alone for evacuation, construction approval, property valuation, or emergency decisions.</li>
        <li>Validate remote-sensing signals against appropriate ground, groundwater, and geotechnical information.</li>
        <li>Use qualified geotechnical, civil-engineering, hydrological, and public-safety professionals for consequential decisions.</li>
        <li>Avoid publishing sensitive infrastructure or private-property information unnecessarily.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption(
    "GroundWatch Local • 100% local processing • No external APIs • "
    "Land-subsidence decision support"
)
