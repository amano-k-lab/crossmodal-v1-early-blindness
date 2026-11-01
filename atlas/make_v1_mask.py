"""Build the V1 mask used for the RSA and DCM analyses.

V1 is taken from the retinotopic template of Benson et al. (2014) on the fsaverage
surface, exported to the fsaverage volume (e.g. with neuropythy:
``python -m neuropythy atlas fsaverage --volume-export``), which yields
benson14_varea.mgz / benson14_angle.mgz / benson14_eccen.mgz.

A voxel belongs to V1 when varea == 1 and it has a defined polar angle and
eccentricity. The mask is in fsaverage (MNI305-aligned) space; downstream scripts
resample it to each MNI152 functional grid with nearest-neighbour interpolation.
The same mask is used for every participant.
"""
import sys
from pathlib import Path

import nibabel as nib
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402


def main():
    varea = nib.load(config.BENSON_DIR / "benson14_varea.mgz")
    angle = nib.load(config.BENSON_DIR / "benson14_angle.mgz").get_fdata()
    eccen = nib.load(config.BENSON_DIR / "benson14_eccen.mgz").get_fdata()

    v1 = (varea.get_fdata() == 1) & (angle != 0) & (eccen != 0)
    img = nib.Nifti1Image(v1.astype(np.int16), varea.affine)
    config.V1_MASK.parent.mkdir(parents=True, exist_ok=True)
    nib.save(img, config.V1_MASK)
    print(f"V1 mask: {int(v1.sum())} voxels -> {config.V1_MASK}")


if __name__ == "__main__":
    main()
