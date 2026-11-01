"""Random-effects Bayesian model selection over driving-input families (Fig. 4C-F, Table S5).

For each group x modality x condition, the variational RFX-BMS of Stephan et al.
(2009) (SPM12 spm_BMS.m) is applied to the participants' log evidences (free
energies) of the four models. Model-level prior counts are set so that each input
family has a total prior count alpha_0 = 1 (0.5 per model, i.e. SPM's family
"F-unity" prior). Then, for family k:

    g_nk    = sum of participant n's posterior model responsibilities over the A0 and
              A1 variants of family k (marginalising over the FEF-V1 factor)
    alpha_k = alpha_0 + sum_n g_nk                    (Dirichlet posterior)
    PP_k    = mean_n g_nk                             (plotted in Fig. 4C-F)
    EP_k    = P(r_k > r_j | data)                     (exceedance probability)

Outputs (OUTPUT_DIR/dcm/):
    table_S5_family_bms.csv       group-level summary
    participant_family_gnk.csv    participant-level g_nk (Data S1)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import digamma

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from dcm import models  # noqa: E402

FAMILY_LABEL = {"sensory": "Sensory-input", "FEF": "FEF-input"}


def spm_bms(lme, alpha0, tol=1e-3, max_iter=10_000):
    """Variational RFX-BMS (spm_BMS.m). lme: participants x models. Returns alpha, g."""
    alpha = alpha0.astype(float).copy()
    for _ in range(max_iter):
        log_u = lme + digamma(alpha) - digamma(alpha.sum())
        log_u -= log_u.mean(axis=1, keepdims=True)
        log_u = np.sign(log_u) * np.minimum(500, np.abs(log_u))
        u = np.exp(log_u)
        g = u / u.sum(axis=1, keepdims=True)
        prev, alpha = alpha, alpha0 + g.sum(axis=0)
        if np.linalg.norm(alpha - prev) < tol:
            break
    return alpha, g


def main():
    F = pd.read_csv(config.OUTPUT_DIR / "dcm" / "free_energy.csv")
    model_names = [f"{i}_{a}" for i, a in models.MODELS]
    family_of = np.array([i for i, _ in models.MODELS])
    families = models.INPUT_FAMILIES
    alpha0 = np.array([1.0 / np.sum(family_of == f) for f in family_of])

    summary, participants = [], []
    for (group, modality, condition), df in F.groupby(["group", "modality", "condition"]):
        df = df.assign(model=df["input"] + "_" + df["connection"])
        lme = df.pivot(index="subject", columns="model", values="F")[model_names]
        alpha_m, g_m = spm_bms(lme.to_numpy(), alpha0)

        g = np.column_stack([g_m[:, family_of == f].sum(axis=1) for f in families])
        alpha = np.array([alpha_m[family_of == f].sum() for f in families])
        # Exceedance probability for two families: P(r_1 > 0.5), r_1 ~ Beta(alpha_1, alpha_2)
        ep = np.array([stats.beta.sf(0.5, alpha[0], alpha[1]), stats.beta.sf(0.5, alpha[1], alpha[0])])
        pp = g.mean(axis=0)
        winner = int(np.argmax(alpha))

        for n, subject in enumerate(lme.index):
            for k, fam in enumerate(families):
                participants.append({"group": group, "modality": modality, "condition": condition,
                                     "participant": config.LABELS[subject], "family": FAMILY_LABEL[fam],
                                     "g_nk": g[n, k]})
        summary.append({
            "group": group, "modality": modality, "condition": condition,
            "sensory_mean_PP": pp[0], "FEF_mean_PP": pp[1],
            "sensory_alpha": alpha[0], "FEF_alpha": alpha[1],
            "winner": FAMILY_LABEL[families[winner]], "EP_winner": ep[winner],
            "n_favoring_winner": f"{int((g[:, winner] > 0.5).sum())}/{len(g)}",
        })

    table = pd.DataFrame(summary)
    table.to_csv(config.out("dcm", "table_S5_family_bms.csv"), index=False)
    pd.DataFrame(participants).to_csv(config.out("dcm", "participant_family_gnk.csv"), index=False)
    print(table.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
