# Method notes

Summary of what the scripts implement, under the corresponding STAR Methods headings of
the manuscript (see the manuscript for the full description).

## Region of interest definition

Scripts: `config.py` (Glasser parcels), `atlas/make_v1_mask.py` (V1), `roi_utils.py` (masks).

RSA and DCM ROIs are defined in MNI152 space and are identical for all participants:

| ROI | Definition |
|-----|------------|
| FEF | Glasser 10 / 190 |
| A1/2 | Glasser A1 (24 / 204) |
| S1 | Glasser 3b (9 / 189) |
| IOG | Glasser V4 (6 / 186) |
| SOG | Glasser V3A (13 / 193) |
| IPS | Glasser IPS1, MIP, LIPv, LIPd, AIP and IP2 (both hemispheres) |
| V1 | varea 1 of the Benson et al. (2014) template, resampled to MNI152 |

Glasser labels 1–180 are the right hemisphere and 181–360 the left hemisphere.
Only voxels inside the participant- and run-specific fMRIPrep functional masks are
used. Because acquisition used partial-brain coverage, an ROI that lies entirely
outside the acquired slab is treated as missing (participant × modality combinations
excluded from the DCM are listed in `OUTPUT_DIR/dcm/excluded.csv`).

## RSA and DCM preprocessing (GLMsingle)

Script: `beta_estimation/run_glmsingle.py`.

Unsmoothed runs are fitted one at a time; each stimulation block is a trial; six
motion parameters are extra regressors; library-HRF betas (type B) are used.

## Representational similarity analysis

Scripts: `rsa/crossmodal_rsa.py`, `rsa/rsa_stats.py`.

Betas are averaged over blocks, then runs; OBT − PS maps for each modality are
resampled to a common 2-mm grid and correlated (Pearson) within each ROI over voxels
covered in every tactile and auditory run. Fisher z is used for inference
(two-tailed one-sample t-tests; means and 95% CIs back-transformed to r).

## Dynamic causal modeling — GLM characterization of the node set (Fig. S2, Table S6)

Script: `glm_characterization/roi_effect_size.py`.

For each participant and modality, voxel-wise Cohen's d (OBT > PS, pooled SD over
block betas) is averaged within each DCM node. Group means are tested against zero
with exploratory one-sample t-tests, Benjamini–Hochberg corrected across ROIs within
each modality × group.

## Dynamic causal modeling

Scripts: `dcm/extract_roi_timeseries.py`, `dcm/models.py`, `dcm/estimate_dcm.py`, `dcm/family_bms.py`.

Six nodes (V1, IPS, FEF, SOG, IOG and S1 or A1/2) with fixed bidirectional
connections V1–IOG, V1–SOG, IOG–IPS, SOG–IPS, IPS–FEF and sensory–IPS. Node time
series are parcel means of 6-mm smoothed data within the coverage mask. Four models
cross the driving input (sensory cortex vs FEF) with the absence/presence of a
bidirectional FEF–V1 connection. The input is the stimulus-block regressor; PS and
OBT runs are fitted separately (runs of one condition concatenated).

Models are specified and inverted with pydcm (`dcm/estimate_dcm.py`). pydcm does not
include the group-level BMS, so `dcm/family_bms.py` implements it as a direct port of
SPM12 `spm_BMS.m`.

Group inference uses variational RFX-BMS (Stephan et al., 2009) with a family prior of
α₀ = 1 per input family (0.5 per model); participant-level family probabilities g_nk
are summed over the A0/A1 variants, α_k = α₀ + Σₙ g_nk, and exceedance probabilities
are computed from the Dirichlet posterior.

## Response quantification and statistical analysis (phase-specified coherence)

Script: `coherence/coherence_stats.py`.

Coherence at the block frequency (1/30 Hz) was computed in mrVista following
Masuda et al. (2021, *Curr. Biol.* 31, 406–412) using the standard vistasoft coherence
analysis. `coherence/coherence_stats.py` computes the planned paired t-tests, the
2 × 2 mixed ANOVA (group × task) and FDR correction from the ROI-level values in
Data S1 (Table S3 and Results). The manuscript reports these statistics as computed
in MATLAB and IBM SPSS; the script implements the same tests in Python.
