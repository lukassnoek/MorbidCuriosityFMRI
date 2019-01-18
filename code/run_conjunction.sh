#set the main feat-directory 
MAIN_DIR=../results/wholebrain.gfeat
C1_DIR=$MAIN_DIR/cope1.feat/stats
C2_DIR=$MAIN_DIR/cope1.feat/stats
#smoothness: no argument to calculate individual smoothness parameters

./easythresh_conj.sh $C1_DIR/zstat1.nii.gz $C2_DIR/zstat1.nii.gz $MAIN_DIR/mask.nii.gz 2.58 0.05 $MAIN_DIR/bg_image.nii.gz conjunction_cue-negpos_contrast-actpas
