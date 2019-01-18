import numpy as np
import nibabel as nib
import os.path as op
import pandas as pd
from glob import glob
from scipy import ndimage
from nilearn.datasets import fetch_atlas_harvard_oxford, load_mni152_template
from nilearn.image import coord_transform


def extract_roi_info(statfile, stat_name=None, out_dir=None, unilateral=True,
                     minimum_nr_of_vox=20, stat_threshold=None):

    """
    Extracts information per ROI for a given statistics-file.
    Reads in a thresholded (!) statistics-file (such as a thresholded z- or
    t-stat from a FSL first-level directory) and calculates for a set of ROIs
    the number of significant voxels included and its maximum value
    (+ coordinates). Saves a csv-file in the same directory as the
    statistics-file. Assumes that the statistics file is in MNI152 2mm space.

    Parameters
    ----------
    statfile : str
        Absolute path to statistics-file (nifti) that needs to be evaluated.
    stat_name : str
        Name for the contrast/stat-file that is being analyzed
    out_dir : str
        Path to output-directory
    unilateral : bool
        Whether to use unilateral masks
    minimum_nr_of_vox : int
        Minimum cluster size (i.e. clusters with fewer voxels than this number
        are discarded; also, ROIs containing fewer voxels than this will not
        be listed on the CSV.
    stat_threshold : int or float
        If the stat-file contains uncorrected data, stat_threshold can be used
        to set a lower bound.
    
    Returns
    -------
    df : Dataframe
        Dataframe corresponding to the written csv-file.
    """

    data = nib.load(statfile).get_data()
    
    if stat_threshold is not None:
        data[data < stat_threshold] = 0

    if stat_name is None:
        stat_name = op.basename(statfile).split('.')[0]

    mni_affine = load_mni152_template().affine
    sign_mask = np.ones(shape=data.shape)
    sign_mask[data < 0] = -1

    if unilateral:
        cort_rois = fetch_atlas_harvard_oxford('cort-maxprob-thr0-2mm', symmetric_split=True)
        subc_rois = fetch_atlas_harvard_oxford('sub-maxprob-thr0-2mm', symmetric_split=True)
    else:
        cort_rois = fetch_atlas_harvard_oxford('cort-maxprob-thr0-2mm', symmetric_split=False)
        subc_rois = fetch_atlas_harvard_oxford('sub-maxprob-thr0-2mm', symmetric_split=False)

    IGNORE_ROIS = ['Cerebral White Matter', 'Cerebral Cortex', 'Background', 'Ventricle',
                   'Ventrical']
    
    # Start clustering of data
    clustered_data, _ = ndimage.label(data > 0, structure=np.ones((3, 3, 3)))
    cluster_ids, cluster_sizes = np.unique(clustered_data.ravel(), return_counts=True)
    cluster_ids = cluster_ids[cluster_sizes.argsort()[::-1]][1:]

    if len(cluster_ids) == 0:
        print("Found 0 clusters!")
        return

    stats_dfs = []
    for i, cluster_id in enumerate(cluster_ids):  # largest to smallest
        cluster_idx = clustered_data == cluster_id
        cluster_max = data[cluster_idx].max()
        cluster_size = cluster_idx.sum()

        tmp = np.zeros(data.shape)
        tmp[cluster_idx] = data[cluster_idx] == cluster_max

        # in case of multiple voxels with same stat / weight
        if np.sum(tmp == 1) > 1:
            X, Y, Z = [coord[0] for coord in np.where(tmp == 1)]
        else:
            X, Y, Z = np.where(tmp == 1)

        # convert to MNI-coordinates
        X, Y, Z = coord_transform(X, Y, Z, mni_affine)

        stats_dict = {
                'Region': [],
                'K': [],
                'Max.': []
        }

        for atlas in [cort_rois, subc_rois]:

            atlas_map = atlas['maps'].get_data()
            labels = atlas['labels']

            for ii, roi in enumerate(labels):

                if any(roi2ignore in roi for roi2ignore in IGNORE_ROIS):
                    continue

                roi_idx = atlas_map == ii
                overlap_idx = np.logical_and(cluster_idx, roi_idx)
                n_vox_per_roi = overlap_idx.sum()

                if n_vox_per_roi > minimum_nr_of_vox:
                    max_stat = data[overlap_idx].max()
                    stats_dict['Region'].append(roi)
                    stats_dict['K'].append(n_vox_per_roi)
                    stats_dict['Max.'].append(max_stat)

        stats_df = pd.DataFrame(stats_dict)
        stats_df = stats_df.sort_values(by='K', ascending=False, axis=0)
        
        for col in ['Cluster nr.', 'Cluster size', 'Cluster max.', 'X', 'Y', 'Z']:
            stats_df[col] = np.nan

        stats_df.loc[stats_df.index[0], 'Cluster nr.'] = i+1
        stats_df.loc[stats_df.index[0], 'Cluster size'] = cluster_size
        stats_df.loc[stats_df.index[0], 'Cluster max.'] = cluster_max
        stats_df.loc[stats_df.index[0], 'X'] = X
        stats_df.loc[stats_df.index[0], 'Y'] = Y
        stats_df.loc[stats_df.index[0], 'Z'] = Z

        stats_df = stats_df.append(pd.Series([np.nan]), ignore_index=True)
        stats_dfs.append(stats_df)

    stats_df = pd.concat(stats_dfs, sort=True, axis=0).drop(0, axis=1)
    
    # Order columns
    stats_df = stats_df[['Cluster nr.', 'Cluster size', 'Cluster max.', 'X', 'Y', 'Z',
                         'Region', 'K', 'Max.']]

    if out_dir is None:
        out_dir = op.dirname(statfile)
    
    out_fn = op.join(out_dir, '%s_atlas_table.tsv' % stat_name)
    stats_df.to_csv(out_fn, sep='\t', index=False)
    
    return stats_df
                    

if __name__ == '__main__':

    base_dir = '../results/FEAT.gfeat'

    for cope in glob(op.join(base_dir, 'cope*.feat')):

        for zstat in glob(op.join(cope, 'thresh_zstat*.nii.gz')):
            
            extract_roi_info(
                statfile=zstat,
                stat_name=op.basename(zstat).split('.')[0],
                unilateral=True,
                minimum_nr_of_vox=20,
                stat_threshold=None
            )
