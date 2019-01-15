BASE_DIR=../../data/bids/derivatives/firstlevel
RANDOMISE_DIR=../../results/randomise

fslmerge -t $RANDOMISE_DIR/desc_neg $BASE_DIR/sub*.feat/reg_standard/stats/cope1.nii.gz
fslmerge -t $RANDOMISE_DIR/desc_pos $BASE_DIR/sub*.feat/reg_standard/stats/cope2.nii.gz
fslmerge -t $RANDOMISE_DIR/stim_neg $BASE_DIR/sub*.feat/reg_standard/stats/cope3.nii.gz
fslmerge -t $RANDOMISE_DIR/stim_pos $BASE_DIR/sub*.feat/reg_standard/stats/cope4.nii.gz
fslmerge -t $RANDOMISE_DIR/desc_negpos $BASE_DIR/sub*.feat/reg_standard/stats/cope5.nii.gz
fslmerge -t $RANDOMISE_DIR/desc_posneg $BASE_DIR/sub*.feat/reg_standard/stats/cope6.nii.gz
fslmerge -t $RANDOMISE_DIR/stim_negpos $BASE_DIR/sub*.feat/reg_standard/stats/cope7.nii.gz
fslmerge -t $RANDOMISE_DIR/stim_posneg $BASE_DIR/sub*.feat/reg_standard/stats/cope8.nii.gz


