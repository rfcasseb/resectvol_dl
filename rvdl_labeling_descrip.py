# -------------------------------------------------------------------------
# Function that compares a brain mask to registered atlas to create the
# table with the volumetric data and save the independent ROIs
# PS: by default, regions with less than 5% resected volume are not
#     included in the table. Users can set "clean_res = 1" to include all
#     results.
# -------------------------------------------------------------------------
# Usage example:
# python /path/to/rvdl_labeling_descrip.py /path/to/Lacuna.nii.gz \
#                       /path/to/Lacuna_labeled.nii.gz \
#                       /path/to/NL_ch2bet_DKT_res_in_native.nii.gz 0.5 1
# -------------------------------------------------------------------------
# INPUTS
# 1) /path/to/Lacuna.nii.gz - full path to the image to be described
# 2) /path/to/NL_ch2bet_DKT_res_in_native.nii.gz - full path to the atlas
#    to be used as reference. There must be a label information file as 
#    described in the rvdl_labeling.sh file header.
# 3) Threshold to binarize Lacuna.nii.gz (in case it is not binary yet)
# 4) Save ROIs? Options: 1 - save rois as independent nii.gz files 
#                        0 - do not save ROIs

# OUPUTS:
# 1) anat_descrip_<Lacuna>.txt - txt file containing the anatomical
#    description or regions
# 2) ROIs folder - contains all the lacuna regions that were estimated 
# 	 saved as individual nii.gz files
# -------------------------------------------------------------------------
# To do: filter atlas indexes (check if they exist in both template and 
# normalized atlas)
# =========================================================================
# Raphael Fernandes Casseb & Brunno Machado de Campos
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

import os
import numpy as np
import nibabel as nib
from scipy.ndimage import label
import pandas as pd
from pathlib import Path
import sys


# ------------------------------------------------------------------
# 0. LOAD INPUTS
# ------------------------------------------------------------------
clear_small_resecs = False # do not include resections < 5% in table
rank_by_size = True
lac_img_path = sys.argv[1]
lac_lb_path = sys.argv[2]
atlas_path = sys.argv[3]
thresh = float(sys.argv[4]) # suggestion = 0.5
save_rois = sys.argv[5]

# Load atlas
code_dir, _ = os.path.split(Path( __file__ ).absolute())
atlas_info = os.path.join(code_dir, 'labeling_template/ch2bet_DKT_info.txt')
atlas_img = nib.load(atlas_path).get_fdata()
df = pd.read_csv(atlas_info, sep='\t', header=None)
index = df[0].values
labels = df[1].values
atlas_indx, atlas_voxls = np.unique(atlas_img, return_counts=True)

# Load info from img to be described
lac_img = nib.load(lac_img_path).get_fdata()
lac_img_hdr = nib.load(lac_img_path).header
vol_factor = np.prod(lac_img_hdr.get_zooms())

lac_lb_img = nib.load(lac_lb_path).get_fdata()
#lac_img_hdr = nib.load(lac_lb_path).header


# ------------------------------------------------------------------
# 1. INITIAL PROCESSING
# ------------------------------------------------------------------
# 1.1. Binarize image, if necessary
vals = np.unique(lac_img)
if len(vals) > 2:
    lac_img = (lac_img > thresh).astype(float)
elif vals[-1] != 1 or vals[0] != 0:
    lac_img = (lac_img > thresh).astype(float)

# 1.2. Tag unknown lacuna voxels with 999
unk_idx_img = np.logical_and(lac_lb_img==0, lac_img==1)
lac_lb_img[unk_idx_img] = 999

# 1.3. Number clusters
img_ccs, cluster_n = label(lac_img)

# 1.4. Create txt file to store results
img_path_tmp = Path(lac_img_path)
anat_path = img_path_tmp.parent
anat_name = os.path.splitext(img_path_tmp.stem)[0]
anat_ext = img_path_tmp.suffixes[0] + img_path_tmp.suffixes[1]
del img_path_tmp
out_file = os.path.join(anat_path, f'anat_descrip_{anat_name}.txt')


# 1.5. write header
with open(out_file, 'wt') as txt_f:
    txt_f.write('Results description\n')
    atlas_path_tmp = Path(atlas_path)
    atlas_name = os.path.splitext(atlas_path_tmp.stem)[0]
    atlas_ext = atlas_path_tmp.suffixes[0] + atlas_path_tmp.suffixes[1]
    txt_f.write(f'Atlas file name: {atlas_name}{atlas_ext}\n')
    txt_f.write(f'Result file name: {anat_name}{anat_ext}\n\n')


    # --------------------------------------------------------------
    # 2. LOOP OVER CLUSTERS AND REGIONS
    # --------------------------------------------------------------
    if save_rois:
        if os.path.exists(os.path.join(anat_path,'ROIs')) == False:
            os.mkdir(os.path.join(anat_path,'ROIs'))

    # 2.1. Loop over clusters
    cc_ind, cc_vxls = np.unique(img_ccs, return_counts=True) # binary img
    for cc in range(1, cluster_n + 1):

        # Total cluster volume
        txt_f.write(f'Cluster {cc_ind[cc]}:\n')
        txt_f.write(f'Volume: {cc_vxls[cc]} voxels ({cc_vxls[cc]*vol_factor:.2f} mm3)\n')
        
        # Do not describe clusters smaller than 3 voxels
        if cc_vxls[cc] < 4:
            txt_f.write(f'Cluster is too small to be described (less than 4 voxels).\n\n\n')
            continue

        # Header
        txt_f.write(f'ROI Index\tROI Name*\tResected vol (voxel)\tResected vol (mm3)\tResected %\n')

        # Select cluster
        cc_img = (img_ccs == cc).astype(float)
        cc_lbl_img = lac_lb_img*cc_img
        lb_indx, lb_vxls = np.unique(cc_lbl_img, return_counts=True) # labeled img
        lb_indx = lb_indx[1:]; lb_vxls = lb_vxls[1:] # Remove 0

        ROIs_info = pd.DataFrame(columns=['ROI Index', 'ROI Names', 'ROI Vol - img (vox)',
                                            'ROI Vol - img (mm3)', 'ROI Vol - resected (%)'])

        for rr in range(len(lb_indx)):

            # To avoid problems of empty tables
            if lb_indx[rr] == 999:
                resect_perc = 1
            else:
                resect_perc = lb_vxls[rr]/atlas_voxls[ atlas_indx == lb_indx[rr]]
            
            # Only include if resec perc >= 5%
            if clear_small_resecs:
                if resect_perc >= .05:
                    ROIs_info.loc[rr] = [lb_indx[rr], labels[index==lb_indx[rr]],
                                lb_vxls[rr], lb_vxls[rr]*vol_factor,
                                100*resect_perc]
                    
                    # Save ROIs
                    if save_rois:
                        roi_data = (atlas_img == lb_indx[rr]).astype(np.uint8)
                        new_img = nib.Nifti1Image(roi_data, affine=lac_img_hdr.get_sform())
                        roi_file = os.path.join(anat_path, 'ROIs', 'clstr_' + str(cc) + '_' 
                            + str(labels[index==lb_indx[rr]]).replace('[', '').replace(']','').replace('\'', '')
                            + '.nii.gz')
                        nib.save(new_img, roi_file)
                        del roi_data, new_img, roi_file

            # Include all resections
            else:                                      
                ROIs_info.loc[rr] = [lb_indx[rr], labels[index==lb_indx[rr]],
                                lb_vxls[rr], lb_vxls[rr]*vol_factor,
                                100*resect_perc]
                # Save ROIs
                if save_rois:
                    roi_data = (atlas_img == lb_indx[rr]).astype(np.uint8)
                    new_img = nib.Nifti1Image(roi_data, affine=lac_img_hdr.get_sform())
                    roi_file = os.path.join(anat_path, 'ROIs', 'clstr_' + str(cc) + '_' 
                        + str(labels[index==lb_indx[rr]]).replace('[', '').replace(']','').replace('\'', '') 
                        + '.nii.gz')
                    nib.save(new_img, roi_file)
                    del roi_data, new_img, roi_file
                    


        # Rank by size
        rank_by_size = True
        if rank_by_size:
            ROIs_info = ROIs_info.sort_values(by='ROI Vol - resected (%)', ascending=False)

        # Remove unnamed row to posteriorly add it at the end of the table
        unam_ind = ROIs_info.index.get_loc(ROIs_info[ROIs_info.iloc[:,0]==999].index[0])
        unam_row = ROIs_info.iloc[unam_ind]
        ROIs_info = ROIs_info[~(ROIs_info.iloc[:,0]==999)]
        
        # Write table to file
        for _, row in ROIs_info.iterrows():
            txt_f.write(f"{int(row['ROI Index'])}\t"
                        f"{str(row['ROI Names']).replace('[', '').replace(']','')}\t"
                        f"{int(row['ROI Vol - img (vox)'])}\t"
                        f"{row['ROI Vol - img (mm3)']:.2f}\t"
                        f"{int(row['ROI Vol - resected (%)']):.2f}\n")
        # Write unnamed to file
        txt_f.write(f"{int(unam_row['ROI Index'])}\t"
                        f"{str(unam_row['ROI Names']).replace('[', '').replace(']','')}\t"
                        f"{int(unam_row['ROI Vol - img (vox)'])}\t"
                        f"{unam_row['ROI Vol - img (mm3)']:.2f}\t"
                        f"---\n")
        txt_f.write('\n\n')

        del ROIs_info
    
    # Foot notes
    if clear_small_resecs == True:
        txt_f.write('OBS: Resections smaller than 5% of the ROI total volume are ommited.\n')
    txt_f.write(f'To see the complete list of ROIs, check the file .../resectvol_dl/labeling_template/ch2bet_DKT_info.nii.gz\n')
    txt_f.write(f'ROI Index: number codes from the reference atlas assigned to each ROI.\n')
    txt_f.write(f'ROI Name: obtained from the reference atlas.\n')
    txt_f.write(f'Resected vol (voxel): ROI resected volume (in voxels, NOT in mm3).\n')
    txt_f.write(f'Resected vol (mm3): ROI resected volume (in mm3).\n')
    txt_f.write(f'Resected %: ROI resected percentage.\n')
    txt_f.write(f'*Regions are labeled according to the DKT atlas (doi:10.3389/fnins.2012.00171). The ''Undetermined'' ROI corresponds to subarachnoid space, sulcus, and other unlabeled regions.\n')
    txt_f.write(f'PS: Clusters with less than 3 voxels are not described\n')