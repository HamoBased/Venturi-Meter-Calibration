# Venturi Meter Calibration — OpenFOAM + Streamlit

Internship project: CFD simulation of a venturi meter in OpenFOAM, with a
Streamlit-based calibration tool for predicting pressure drop from flow rate.

## Project structure
- `openfoam-case/` — the OpenFOAM case (mesh, physics setup, boundary conditions)
- `ui/` — the Streamlit calibration tool (app.py)

## Setup: running the OpenFOAM simulation
```bash
cd openfoam-case
blockMesh
checkMesh
foamRun
```

## Setup: running the calibration UI
```bash
cd ui
pip install -r requirements.txt
streamlit run app.py
```

## Status
- [x] Mesh generation (axisymmetric wedge)
- [x] Physics setup (water, k-epsilon turbulence)
- [x] Calibration data (4 flow rates, 0.5-2.0 m/s)
- [x] Calibration UI (flow rate -> predicted pressure drop)
- [ ] Geometry parameter variation (throat ratio, converging/diverging angle)
- [ ] Validation against physical lab rig data

## Author
Ahmed Isameldin — UTM Wind Turbine Laboratory internship
