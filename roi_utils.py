"""ROI masks on an arbitrary MNI152 voxel grid."""
from functools import lru_cache

import nibabel as nib
import numpy as np
from nilearn.image import resample_img

import config


def _resample_nearest(path, shape, affine_key):
    affine = np.array(affine_key).reshape(4, 4)
    img = resample_img(str(path), target_affine=affine, target_shape=shape,
                       interpolation="nearest")
    return np.asarray(img.dataobj)


@lru_cache(maxsize=8)
def _glasser_on_grid(shape, affine_key):
    return np.rint(_resample_nearest(config.GLASSER_ATLAS, shape, affine_key)).astype(int)


@lru_cache(maxsize=8)
def _v1_on_grid(shape, affine_key):
    return _resample_nearest(config.V1_MASK, shape, affine_key) > 0


def _key(img_or_shape_affine):
    if isinstance(img_or_shape_affine, tuple):
        shape, affine = img_or_shape_affine
    else:
        shape, affine = img_or_shape_affine.shape[:3], img_or_shape_affine.affine
    return tuple(int(s) for s in shape[:3]), tuple(np.round(np.asarray(affine), 6).ravel())


def glasser_labels(ref):
    """Glasser label volume on the grid of ``ref`` (image or (shape, affine))."""
    return _glasser_on_grid(*_key(ref))


def roi_mask(roi, ref):
    """Boolean mask of ``roi`` on the grid of ``ref``."""
    if roi == "V1":
        return _v1_on_grid(*_key(ref))
    return np.isin(glasser_labels(ref), config.GLASSER_ROIS[roi])


def coverage_mask(bold_file, ref=None):
    """fMRIPrep run-specific functional mask, optionally resampled to ``ref``."""
    mask_file = config.brain_mask_for(bold_file)
    if ref is None:
        return np.asarray(nib.load(mask_file).dataobj) > 0
    shape, affine = _key(ref)
    return _resample_nearest(mask_file, shape, affine) > 0
