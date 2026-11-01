# Overview

Analysis code for:

> Masuda Y, Watanabe R, Yamashita A, Terao M, Iida M, Kinjo T, Tohma A, Horiguchi H,
> Matsumoto K, Nakano T, Nakadomari S, Wandell BA, Amano K.
> *Cross-modal V1 Signals in Human Early Blindness Depend on Task, not Stimulus.*
> (submitted to *Current Biology*).

The repository contains the custom scripts for the representational similarity
analysis (RSA), dynamic causal modeling (DCM) family comparison, GLM-based
characterisation of the DCM nodes, statistical analysis of phase-specified coherence,
and figure generation. Section, figure and table numbers refer to the manuscript.

## Data

No data are included. Raw and minimally processed MRI data of the blind participants
are available on request (see *Data and code availability* in the manuscript).
ROI-level numerical source data are provided with the paper as Data S1.

Participants are EB1–EB6 (`sub-032`–`sub-037`) and C1–C6 (`sub-007`–`sub-012`).
BIDS task labels are `tactilepvclosed`, `tactileobtclosed`, `audiopvclosed` and
`audioobtclosed` (PS = passive sensing, OBT = one-back task; "pv" in the file names
denotes PS). Each run has 100 volumes (TR = 3 s) with ten 15-s stimulation blocks
alternating with 15-s rest.

## Upstream processing (not part of this repository)

* fMRIPrep 24.0.0 (MNI152NLin2009cAsym, 2 mm) and FreeSurfer.
* mrVista/vistasoft for the phase-specified coherence (Fig. 1, Fig. S1 and the values in Data S1).

## Analyses and code

Each analysis in the manuscript (STAR Methods heading in the first column) and the
scripts that implement it, in the order they are run.

| Analysis (STAR Methods) | Manuscript items | Scripts |
|---|---|---|
| Region of interest definition (V1 for RSA/DCM) | — | `atlas/make_v1_mask.py` |
| RSA and DCM preprocessing (GLMsingle betas) | input to Fig. 3, Fig. S2 | `beta_estimation/run_glmsingle.py` |
| Representational similarity analysis | Fig. 3, Table S4 | `rsa/crossmodal_rsa.py` → `rsa/rsa_stats.py` |
| Dynamic causal modeling | Fig. 4C–F, Table S5 | `dcm/extract_roi_timeseries.py` → `dcm/models.py` / `dcm/estimate_dcm.py` → `dcm/family_bms.py` |
| Dynamic causal modeling — GLM characterization of the node set | Fig. S2, Table S6 | `glm_characterization/roi_effect_size.py` |
| Response quantification / Quantification and statistical analysis (phase-specified coherence) | Fig. 2, Table S3, coherence statistics in the Results | `coherence/coherence_stats.py` |
| Figures | Figs. 2, 3, 4C–F, S2 | `figures/make_figures.py` |

Not regenerated here: Fig. 1 and Fig. S1 (surface coherence maps and time courses,
produced in mrVista), the coherence values themselves (computed in mrVista; provided in
Data S1), and the schematics in Fig. 4A–B.

## Shared and third-party code

| Path | Contents |
|---|---|
| `config.py` | Paths, participants, task labels, block design, ROI definitions (Glasser parcels) |
| `roi_utils.py` | ROI and fMRIPrep coverage masks on any MNI152 grid |
| `io_utils.py` | Reads CSV files or a sheet of the Data S1 workbook |
| `third_party/pydcm/` | pydcm (GPL-3.0) with local fixes, see [third_party.md](third_party.md) |

What each step computes is summarised in [methods.md](methods.md), which follows the
same headings.

## Contact

Yoichiro Masuda (ymasuda@jikei.ac.jp) — lead contact.
Code: Ryutaro Watanabe, The University of Tokyo.
