from spynoza.glm.workflows import create_modelgen_workflow
from spynoza.glm.FEAT.nodes import Custom_Level1design_Feat, Rename_feat_dir
from spynoza.utils import set_parameters_in_nodes, ConcatenateIterables
from nipype.pipeline import Node, MapNode, Workflow
from nipype.interfaces.io import SelectFiles
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.interfaces.io import DataSink
from nipype.interfaces.fsl.model import FEAT, L2Model, FLAMEO
import os.path as op
from glob import glob

base_dir = '/home/lsnoek1/MorbidCuriosityFMRI/data/bids/derivatives'
out_dir = op.join(base_dir, 'derivatives', 'firstlevel')
sub_ids = sorted([op.basename(f) for f in glob(op.join(base_dir, 'fmriprep', 'sub-???'))])

meta_wf = Workflow('firstlevel_spynoza')

input_node = Node(IdentityInterface(fields=['sub_id']), name='inputspec')
input_node.iterables = [('sub_id', sub_ids)]

select_files = Node(SelectFiles(templates={'func': '{sub_id}/func/*preproc.nii.gz',
                                           'func_mask': '{sub_id}/func/*brainmask.nii.gz',
                                           'T1': '{sub_id}/anat/*preproc.nii.gz',
                                           'events': '{sub_id}/func/all.tsv',
                                           'confounds': '{sub_id}/func/*confounds.tsv'}),
                                name='selectfiles')

select_files.inputs.base_directory = op.join(base_dir, 'fmriprep')
select_files.inputs.raise_on_empty = False
select_files.inputs.sort_filelist = True

meta_wf.connect(input_node, 'sub_id', select_files, 'sub_id')

modelgen_wf = create_modelgen_workflow(skip_specify_model=True)
modelgen_wf.inputs.inputspec.sort_by_onset = True
modelgen_wf.inputs.inputspec.TR = 2
modelgen_wf.inputs.inputspec.extend_motion_pars = False
modelgen_wf.inputs.inputspec.exclude = None
modelgen_wf.inputs.inputspec.hp_filter = 100
modelgen_wf.inputs.inputspec.which_confounds = ['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ']

meta_wf.connect(select_files, 'events', modelgen_wf, 'inputspec.events_file')
meta_wf.connect(select_files, 'confounds', modelgen_wf, 'inputspec.confound_file')
meta_wf.connect(select_files, 'func', modelgen_wf, 'inputspec.func_file')

feat_node = Node(interface=Custom_Level1design_Feat, name='feat')
feat_node.inputs.smoothing = 5
feat_node.inputs.temp_deriv = True

feat_node.inputs.registration = 'fmriprep'
feat_node.inputs.slicetiming = 'no'
feat_node.inputs.motion_correction = 0
feat_node.inputs.bet = True
feat_node.inputs.prewhitening = True
feat_node.inputs.motion_regression = False
feat_node.inputs.thresholding = 'uncorrected'
feat_node.inputs.hrf = 'doublegamma'
feat_node.inputs.open_feat_html = True
feat_node.inputs.highpass = 128
feat_node.inputs.contrasts = [
    ('desc_neg_yes', 'T', ['desc_neg_yes'], [1]),
    ('desc_pos_yes', 'T', ['desc_pos_yes'], [1]),
    ('stim_neg_yes', 'T', ['stim_neg_yes'], [1]),
    ('stim_pos_yes', 'T', ['stim_pos_yes'], [1]),
    ('desc_neg>pos', 'T', ['desc_neg_yes', 'desc_pos_yes'], [1, -1]),
    ('desc_pos>neg', 'T', ['desc_neg_yes', 'desc_pos_yes'], [-1, 1]),
    ('stim_neg>pos', 'T', ['stim_neg_yes', 'stim_pos_yes'], [1, -1]),
    ('stim_pos>neg', 'T', ['stim_neg_yes', 'stim_pos_yes'], [-1, 1])
]

meta_wf.connect(select_files, 'func', feat_node, 'func_file')
meta_wf.connect(modelgen_wf, 'outputspec.session_info', feat_node, 'session_info')
meta_wf.connect(input_node, 'sub_id', feat_node, 'output_dirname')
meta_wf.connect(select_files, 'func_mask', feat_node, 'mask')

run_feat_node = Node(FEAT(), name='run_feat')

meta_wf.connect(feat_node, 'feat_dir', run_feat_node, 'fsf_file')

datasink = Node(interface=DataSink(), name='datasink')
datasink.inputs.parameterization = False
datasink.inputs.base_directory = out_dir
meta_wf.connect(feat_node, 'confound_file', datasink, 'confound_file')
meta_wf.connect(feat_node, 'ev_files', datasink, 'ev_files')
meta_wf.connect(run_feat_node, 'feat_dir', datasink, 'firstlevel_FEAT')
meta_wf.connect(input_node, 'sub_id', datasink, 'container')

meta_wf.base_dir = op.join(base_dir, 'spynoza', 'workingdir')
meta_wf.run(plugin='MultiProc', plugin_args={'n_procs' : 15})
