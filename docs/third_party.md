# Third-party code

`third_party/pydcm` is pydcm (https://github.com/tmdemelo/pydcm, commit `1b4d7eb`),
a Python port of SPM12 r7487 DCM, distributed under GPL-3.0 (see
`third_party/pydcm/LICENSE`). It is used for model specification and inversion; the
random-effects BMS (`spm_BMS.m`) is not part of pydcm and is ported in
`dcm/family_bms.py`.

Local changes are listed in `third_party/pydcm/LOCAL_MODIFICATIONS.diff`:

* Python 3 / NumPy compatibility fixes in `spm_diff`, `spm_cat`, `spm_dx`,
  `spm_bireduce` and `spm_Ce`.
* The Gauss–Newton update in `spm_nlsi_GN`.
* Use of the unmodified A matrix for the prior covariance in `spm_dcm_fmri_priors`.
