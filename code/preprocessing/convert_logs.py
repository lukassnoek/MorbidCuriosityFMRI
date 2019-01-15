import os
import os.path as op
from glob import glob
import pandas as pd

files = sorted(glob('../data/raw/*/*events.tsv'))
for f in files:
    df = pd.read_csv(f, sep='\t')
    df['onset'] = df['rel-onset-pulse'] / 1000
    df['trial_type'] = df['trial-type'][df['trial-type'] != 'resp']
    df['trial_type'] = ['dec' if 'dec' in t else t for t in df['trial_type']]
    df['trial_type'] = ['_'.join(t.split('_')[:-1]) if t != 'dec' else t for t in df['trial_type']]
    df['trial_type'] = ['_'.join(t.split('_')[:-1]) if len(t.split('_')) > 3 else t for t in df['trial_type']]
    df = df[df.trial_type.str.contains("resp") == False] 
    sub_name = f.split(op.sep)[2]
    out_dir = 'DATA/preproc/fmriprep/%s/func/all.tsv' % sub_name
    print("Writing to disk: %s" % out_dir)
    df[['trial_type', 'onset', 'weight', 'duration']].to_csv(out_dir, sep='\t', header=True, index=False)
