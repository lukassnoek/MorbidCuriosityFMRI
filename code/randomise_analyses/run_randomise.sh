DES_DIR=../../results/design
RAND_DIR=../../results/randomise
ROI_DIR=../../results/ROIs

for mask in IFG_bin Striatum_bin; do

    for contrast in desc_posneg desc_neg desc_pos stim_neg stim_pos desc_negpos stim_negpos stim_posneg; do
        echo "Running contrast $contrast with mask $mask"
        randomise -i $RAND_DIR/$contrast.nii.gz -o $RAND_DIR/$contrast/$mask/$mask -d $DES_DIR/grouplevel.mat -t $DES_DIR/grouplevel.con -e $DES_DIR/grouplevel.grp -x -T -n 5000 -m $ROI_DIR/$mask.nii.gz
    done
done 
