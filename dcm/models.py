"""DCM model space (Figure 4A-B).

Six nodes: V1, IPS, FEF, SOG, IOG and the modality-specific primary sensory cortex
(S1 for tactile, A1/2 for auditory). Fixed intrinsic (bidirectional) connections,
shared by all models:

    V1 <-> IOG, V1 <-> SOG, IOG <-> IPS, SOG <-> IPS, IPS <-> FEF, sensory <-> IPS

(self-connections are always included by the SPM priors).

The model space crosses two factors, giving four models:
    driving input  : sensory cortex ("sensory")  vs  FEF ("FEF")
    FEF-V1 link    : absent ("A0")               vs  present, bidirectional ("A1")

The driving input is the stimulus-block regressor (15-s ON / 15-s OFF). No
modulatory (B) or nonlinear (D) effects are modelled; PS and OBT runs are fitted
separately.
"""
import numpy as np

# Node order matches the time-series columns written by extract_roi_timeseries.py.
V1, IPS, FEF, SOG, IOG, SENSORY = range(6)
N_NODES = 6

INTRINSIC = [(V1, IOG), (V1, SOG), (IOG, IPS), (SOG, IPS), (IPS, FEF), (SENSORY, IPS)]

INPUT_FAMILIES = ["sensory", "FEF"]
CONNECTION_FAMILIES = ["A0", "A1"]
MODELS = [(c, a) for c in INPUT_FAMILIES for a in CONNECTION_FAMILIES]


def a_matrix(connection):
    A = np.zeros((N_NODES, N_NODES))
    for i, j in INTRINSIC:
        A[i, j] = A[j, i] = 1
    if connection == "A1":
        A[FEF, V1] = A[V1, FEF] = 1
    return A


def c_matrix(driving_input):
    C = np.zeros((N_NODES, 1))
    C[SENSORY if driving_input == "sensory" else FEF, 0] = 1
    return C


def block_regressor(n_scans, tr):
    """Stimulus-block input sampled at the TR; each run starts with an ON block."""
    t = np.arange(n_scans) * tr
    return ((t % 30.0) < 15.0).astype(float)[:, None]


def dcm_structure(Y, driving_input, connection, tr):
    n_scans = Y.shape[0]
    return {
        "n": N_NODES,
        "v": n_scans,
        "a": a_matrix(connection),
        "b": np.zeros((N_NODES, N_NODES, 0)),
        "c": c_matrix(driving_input),
        "d": np.zeros((N_NODES, N_NODES, 0)),
        "U": {"u": block_regressor(n_scans, tr), "dt": tr, "name": ["stimulus"]},
        "Y": {"y": Y, "dt": tr, "X0": np.ones((n_scans, 1))},
        "options": {
            "two_state": 0, "stochastic": 0, "nonlinear": 0, "pdcm": 0,
            "centre": 0, "maxit": 128, "maxnodes": 10, "hE": 6, "hC": 1 / 128,
            "hidden": [],
        },
    }
