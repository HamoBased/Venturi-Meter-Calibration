"""
Venturi Meter Calibration Tool
------------------------------
Stage 5 of the venturi meter project: a simple UI that takes a flow rate
input and returns the predicted pressure drop, based on the OpenFOAM
calibration data generated in Stage 4.

Run with:
    streamlit run app.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ---------------------------------------------------------------------------
# 1. Calibration data (from Stage 4 OpenFOAM simulations)
# ---------------------------------------------------------------------------

# Venturi geometry (matches system/blockMeshDict)
INLET_RADIUS_M = 0.05      # 50 mm
THROAT_RADIUS_M = 0.025    # 25 mm
INLET_AREA_M2 = np.pi * INLET_RADIUS_M ** 2  # 0.007854 m^2

# Simulated data points: inlet velocity (m/s) -> pressure drop (Pa)
VELOCITIES = np.array([0.5, 1.0, 1.5, 2.0])
DELTA_P = np.array([1497, 5949, 13308, 23553])
FLOW_RATES_LMIN = VELOCITIES * INLET_AREA_M2 * 60000  # L/min

CAL_MIN_LMIN = FLOW_RATES_LMIN.min()
CAL_MAX_LMIN = FLOW_RATES_LMIN.max()

# ---------------------------------------------------------------------------
# 2. Fit a Bernoulli-consistent calibration curve: dP = k * Q^2
#    (Bernoulli predicts dP proportional to V^2, and V is proportional to Q
#    for a fixed inlet area, so dP = k * Q^2 is the physically correct form.)
# ---------------------------------------------------------------------------

Q_M3S = FLOW_RATES_LMIN / 60000
K_FIT = np.sum(Q_M3S ** 2 * DELTA_P) / np.sum(Q_M3S ** 4)


def predict_delta_p(flow_rate_lmin: float) -> float:
    """Predict pressure drop (Pa) for a given flow rate (L/min)."""
    q_m3s = flow_rate_lmin / 60000
    return K_FIT * q_m3s ** 2


def flow_rate_to_velocity(flow_rate_lmin: float) -> float:
    """Convert flow rate (L/min) to inlet velocity (m/s)."""
    q_m3s = flow_rate_lmin / 60000
    return q_m3s / INLET_AREA_M2


# ---------------------------------------------------------------------------
# 3. Streamlit UI
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Venturi Meter Calibration", layout="centered")

st.title("Venturi meter calibration tool")
st.caption(
    "Predicts pressure drop across the venturi meter for a given flow rate, "
    "calibrated against OpenFOAM simulation data."
)

st.divider()

# --- Input ---
st.subheader("Flow rate input")

flow_rate = st.slider(
    "Flow rate (L/min)",
    min_value=50.0,
    max_value=1200.0,
    value=471.2,
    step=1.0,
)

col1, col2 = st.columns(2)
with col1:
    flow_rate_manual = st.number_input(
        "Or type an exact value (L/min)",
        min_value=0.0,
        max_value=5000.0,
        value=float(flow_rate),
        step=0.1,
    )
with col2:
    st.metric("Equivalent inlet velocity", f"{flow_rate_to_velocity(flow_rate_manual):.3f} m/s")

flow_rate_used = flow_rate_manual

if flow_rate_used < CAL_MIN_LMIN or flow_rate_used > CAL_MAX_LMIN:
    st.warning(
        f"This flow rate is outside the simulated calibration range "
        f"({CAL_MIN_LMIN:.1f}-{CAL_MAX_LMIN:.1f} L/min). The prediction below is "
        f"extrapolated from the Bernoulli-based fit, not directly validated by simulation."
    )

# --- Prediction ---
predicted_dp = predict_delta_p(flow_rate_used)

st.divider()
st.subheader("Predicted pressure drop")

pcol1, pcol2 = st.columns(2)
with pcol1:
    st.metric("Pressure drop (\u0394P)", f"{predicted_dp:,.0f} Pa")
with pcol2:
    st.metric("Pressure drop (\u0394P)", f"{predicted_dp / 1000:,.2f} kPa")

st.divider()

# --- Calibration curve plot ---
st.subheader("Calibration curve")

fig, ax = plt.subplots(figsize=(6.5, 4))

# smooth fitted curve
q_smooth = np.linspace(0, max(FLOW_RATES_LMIN.max(), flow_rate_used) * 1.15, 200)
dp_smooth = K_FIT * (q_smooth / 60000) ** 2
ax.plot(q_smooth, dp_smooth, color="#2a78d6", linewidth=2, label="Fitted curve (\u0394P \u221d Q\u00b2)")

# simulated data points
ax.scatter(FLOW_RATES_LMIN, DELTA_P, color="#1a1a19", zorder=5, s=45, label="OpenFOAM data points")

# user's prediction
ax.scatter(
    [flow_rate_used], [predicted_dp],
    color="#d95926", zorder=6, s=90, marker="D", label="Your input"
)
ax.annotate(
    f"{predicted_dp:,.0f} Pa",
    (flow_rate_used, predicted_dp),
    textcoords="offset points", xytext=(10, 5), fontsize=9, color="#d95926"
)

ax.set_xlabel("Flow rate (L/min)")
ax.set_ylabel("Pressure drop, \u0394P (Pa)")
ax.set_title("Venturi meter calibration curve")
ax.legend(loc="upper left", fontsize=9)
ax.grid(axis="y", color="#e1e0d9", linewidth=0.8)
ax.set_axisbelow(True)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

st.pyplot(fig)

st.divider()

# --- Reference data table ---
with st.expander("Simulated calibration data (OpenFOAM, Stage 4)"):
    df = pd.DataFrame({
        "Velocity (m/s)": VELOCITIES,
        "Flow rate (L/min)": FLOW_RATES_LMIN.round(1),
        "\u0394P (Pa)": DELTA_P,
    })
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.caption(
        f"Geometry: inlet radius = {INLET_RADIUS_M*1000:.0f} mm, "
        f"throat radius = {THROAT_RADIUS_M*1000:.0f} mm. "
        f"Fitted coefficient k = {K_FIT:,.2f} (from \u0394P = k \u00d7 Q\u00b2)."
    )

st.caption(
    "Note: geometry (throat ratio, converging/diverging angle) is fixed to the simulated "
    "case. Predicting for a different geometry would require re-running the OpenFOAM "
    "simulation for that configuration."
)
