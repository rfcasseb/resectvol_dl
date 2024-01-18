# -------------------------------------------------------------------------
# Function to replace header for predicted results from ResectVol DL
# -------------------------------------------------------------------------
# Usage example:
# python /path/to/rvdl_replace_header.py /path/to/T1_anat_file.nii.gz \
#                       /path/to/Lacuna_pred.nii.gz 1 0
#                       
# -------------------------------------------------------------------------
# INPUTS
# 1) /path/to/T1_anat_file.nii.gz - full path to the T1 anatomical file; or
#                                   path to folder containing all T1s
# 2) /path/to/Lacuna_pred.nii.gz - full path to the lacuna prediction; or
#                                  path to folder containing all predictions
# 3) Single image correction? Options 0 - correct multiple images => original_file
#                                     and pred_file are the path to folders
#                                     containing files
#                                     1 - correct only one image => original_file
#                                     and pred_file are the path to one file
#                                     only
# 4) Delete predicted file? Options: 0 - keep both files (corrected file 
#                                        will have an 'x' suffix.
#                                    1 - replace the predicted file with 
#                                        mismatching header by the 
#                                        corrected predicted file (only 
#                                        available for single_img== 1);

# OUPUT:
# - Predicted file will be replaced by the corrected one; or 
# - A new file with the same name but added of the suffix 'x' will be 
#   created
# -------------------------------------------------------------------------
# =========================================================================
# Raphael Fernandes Casseb
# University of Campinas, 2023

import nibabel as nib
import os
import sys

# def nnunet_replace_header(original_file, pred_file, single_img, delete_pred):
# INPUTS
# single_img        (int)    1: correct only one image
#                            0: correct multiple images 
# delete_pred       (int)    1: replace the predicted file with mismatching header by the corrected
#                               predicted file (only available for single_img== 1);
#                            0: keep both files (corrected file will have an 'x' suffix.

# ORGANIZE INPUTS
original_file = sys.argv[1]
pred_file     = sys.argv[2]
single_img    = int(sys.argv[3])
delete_pred   = int(sys.argv[4])

if single_img == 0:
    originals_dir = original_file
    preds_dir = pred_file


# RUN
# Single image    
if single_img == 1:
    hdr_info = nib.load(original_file).header
    hdr_info.set_data_dtype('uint8')
    
    pred_dat = nib.load(pred_file).get_fdata()
    nib.save(nib.Nifti1Image(pred_dat, None, hdr_info), pred_file[:-7] + 'x.nii.gz')

    if delete_pred:
        os.remove(pred_file)
        os.rename(pred_file[:-7] + 'x.nii.gz', pred_file[:-7] + '.nii.gz')

# Multiple images
else:
    orig_files = [f for f in os.listdir(originals_dir) if f.endswith('.nii.gz')]
    pred_files = [f for f in os.listdir(preds_dir) if f.endswith('.nii.gz')]
    
    for i in range(len(orig_files)):
        hdr_info = nib.load(os.path.join(originals_dir, orig_files[i])).header
        hdr_info.set_data_dtype('uint8')
        
        pred_dat = nib.load(os.path.join(preds_dir, pred_files[i])).get_fdata()
        
        nib.save(nib.Nifti1Image(pred_dat, None, hdr_info), os.path.join(preds_dir, pred_files[i][:-7] + 'x.nii.gz'))
        
        # Replace file
        if delete_pred:
            os.remove(os.path.join(preds_dir, pred_files[i]))
            os.rename(os.path.join(preds_dir, pred_files[i][:-7] + 'x.nii.gz'), os.path.join(preds_dir, pred_files[i]))