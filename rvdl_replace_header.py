# -------------------------------------------------------------------------
# Function to replace header for predicted results from ResectVol DL
# -------------------------------------------------------------------------
# Usage example:
# Ex 1: 
# python /path/to/rvdl_replace_header.py /path/to/T1_anat_file.nii.gz \
#                       /path/to/Lacuna_pred.nii.gz 1
# Ex 2:
# python /path/to/rvdl_replace_header.py <path to folder with T1 anats> \
#                       <path to folder with lacuna predictions> 1
#                       
# -------------------------------------------------------------------------
# INPUTS
# 1) /path/to/T1_anat_file.nii.gz - full path to the T1 anatomical file; or
#                                   path to folder containing all T1s
#                                   (images with correct orientation)
# 2) /path/to/Lacuna_pred.nii.gz - full path to the lacuna prediction; or
#                                  path to folder containing all predictions
#                                  (images to be corrected)
# 3) Delete original lacuna file and keep the header corrected file only? 
#                           Options: 0 - keep both files (corrected file 
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
# University of Campinas, 2025
#
# Copyright (c) 2025
# Raphael Fernandes Casseb & Brunno Machado de Campos
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the distribution
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# =========================================================================

import nibabel as nib
import os
import sys

# ORGANIZE INPUTS
original_file = sys.argv[1]
pred_file     = sys.argv[2]
delete_pred   = int(sys.argv[3])


# RUN
if os.path.exists(original_file):
    
    # Folder with .nii.gz files
    if os.path.isdir(original_file): 
        
        # Rename inputs
        originals_dir = original_file
        preds_dir = pred_file
        
        # List files 
        orig_files = sorted([f for f in os.listdir(originals_dir) if f.endswith('.nii.gz')])
        pred_files = sorted([f for f in os.listdir(preds_dir) if f.endswith('.nii.gz')])
        
        # Replace header
        for i in range(len(orig_files)):
            hdr_info = nib.load(os.path.join(originals_dir, orig_files[i])).header
            hdr_info.set_data_dtype('uint8')
            
            pred_dat = nib.load(os.path.join(preds_dir, pred_files[i])).get_fdata()
            
            nib.save(nib.Nifti1Image(pred_dat, None, hdr_info), os.path.join(preds_dir, pred_files[i][:-7] + 'x.nii.gz'))
            
            # Replace file
            if delete_pred:
                os.remove(os.path.join(preds_dir, pred_files[i]))
                os.rename(os.path.join(preds_dir, pred_files[i][:-7] + 'x.nii.gz'), os.path.join(preds_dir, pred_files[i]))

    # Single file
    else:
        hdr_info = nib.load(original_file).header
        hdr_info.set_data_dtype('uint8')
    
        pred_dat = nib.load(pred_file).get_fdata()
        nib.save(nib.Nifti1Image(pred_dat, None, hdr_info), pred_file[:-7] + 'x.nii.gz')

        if delete_pred:
            os.remove(pred_file)
            os.rename(pred_file[:-7] + 'x.nii.gz', pred_file[:-7] + '.nii.gz')