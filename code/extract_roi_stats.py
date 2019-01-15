import os.path as op
from skbold.postproc import extract_roi_info
from glob import glob

base_dir = 'results/univariate/FEAT.gfeat'
cope_paths = glob(op.join(base_dir, 'cope*.feat'))
for cope in cope_paths:
    for zstat in ['zstat1', 'zstat2']:
        stat_file = op.join(cope, 'thresh_%s.nii.gz' % zstat)
        extract_roi_info(stat_file, stat_name=zstat)