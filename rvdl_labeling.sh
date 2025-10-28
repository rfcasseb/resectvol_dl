#!/bin/bash
roi_labeling() {
	# -------------------------------------------------------------------------
	# Main script to perform labeling of lacuna regions
	# -------------------------------------------------------------------------
	# Usage examples:
    # Slow good run - ~15 min (depends on system)
	# time bash rvdl_labeling.sh roi_labeling /path/to/Pos.nii.gz /path/to/Lacuna.nii.gz /path/to/rvdl_labeling.sh slow_good
	# Quick poor run - ~6 min (depends on system)
	# time bash rvdl_labeling.sh roi_labeling /path/to/Pos.nii.gz /path/to/Lacuna.nii.gz /path/to/rvdl_labeling.sh quick_dirty
	# -------------------------------------------------------------------------
	# INPUTS:
	# 1) /path/to/Pos.nii.gz - full path to postoperative image in nii.gz format
	# 2) /path/to/Lacuna.nii.gz - full path to lacuna mask images in nii.gz 
	#    format
	# 3) /path/to/rvdl_labeling.sh - full path to rvdl_labeling.sh (there 
	#    must be a folder named "labeling_template" at the same level
    #    of the rvdl_labeling.sh file, containing the DKT template)
	# 4) running mode - options: "quick_dirty" or "slow_good"

	# OUTPUTS:
	# 1) anat_descrip_<Lacuna>.txt - txt file containing the anatomical
	#    description or regions
	# 2) NL_ch2bet_DKT_res_in_native.nii.gz - non-linearly registered labeling 
	# 	 atlas (Desikan-Killiany-Tourville) in native space
	# 3) ROIs folder - contains all the lacuna regions that were estimated 
	# 	 saved as individual nii.gz files
	# -------------------------------------------------------------------------
	# To do:
	# - Try -x in ants registration


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
		
	in_house=0
	if [ $in_house -eq 1 ]; then
		CoresPerCase=15 
	else
		num_processors=$(nproc --all)
		CoresPerCase=$((num_processors - 2))
	fi
	del_extra=yes

	# ------------------------------------------------------------------
	# 0. LOAD INPUTS
	# ------------------------------------------------------------------
    code_dir=$(dirname "$3")
	brn_path=$(dirname "$1")
	brn_name=$(basename "$1")
	brn_name_core=$(basename "$brn_name" .nii.gz)
	lac_path=$(dirname "$2")
	lac_name=$(basename "$2")
	lac_name_core=$(basename "$lac_name" .nii.gz)
	run_mode="$4"
	
	if [[ $run_mode == "slow_good" ]]; then
		echo "Performing anatomical labeling of image $1"
		echo "This may take a while"
	elif [[ $run_mode == "quick_dirty" ]]; then
		echo "Performing anatomical labeling of image $1"
		echo "This may take a while"
	else
		echo "ERROR: please choose a running mode (\"slow_good\" or \"quick_dirty\"). See the \"Usage examples\" in function header"
		exit
	fi

	# Choose atlas ($code_dir/labeling_template/)
	atlas_brain=ch2bet
	atlas_labels=ch2bet_DKT_res
	

	
	# ------------------------------------------------------------------	
	# 1. BRAIN EXTRACTION
	# ------------------------------------------------------------------
    # 1.1. Apply lacuna mask to post file
	# (SPM12 NewSegment ignores 0 voxels)
	# ~ 5 s
    fslmaths $lac_path/$lac_name_core -mul -1 -add 1 -mul $brn_path/$brn_name_core $brn_path/"$brn_name_core"_masked
	gunzip $brn_path/"$brn_name_core"_masked.nii.gz
	
	# 1.2. Run SPM12 NewSegment
	# ~ 4 min 30 s
	python $code_dir/rvdl_tissue_seg.py $brn_path/"$brn_name_core"_masked.nii
	rm $brn_path/c3"$brn_name_core"_masked.nii
	rm $brn_path/c4"$brn_name_core"_masked.nii
	rm $brn_path/c5"$brn_name_core"_masked.nii
	rm $brn_path/m"$brn_name_core"_masked.nii
	rm $brn_path/"$brn_name_core"_masked_seg8.mat
	rm $brn_path/BiasField_"$brn_name_core"_masked.nii
	gzip $brn_path/"$brn_name_core"_masked.nii
	gzip $brn_path/c1"$brn_name_core"_masked.nii
	gzip $brn_path/c2"$brn_name_core"_masked.nii

	# 1.3. Threshold tissues and combine them to create brain mask
	fslmaths $brn_path/c1"$brn_name_core"_masked.nii.gz -thr .1 -bin $brn_path/bc1"$brn_name_core"_masked.nii.gz
	fslmaths $brn_path/c2"$brn_name_core"_masked.nii.gz -thr .1 -bin $brn_path/bc2"$brn_name_core"_masked.nii.gz
	fslmaths $brn_path/bc1"$brn_name_core"_masked.nii.gz -add $brn_path/bc2"$brn_name_core"_masked.nii.gz -bin $brn_path/brain_mask.nii.gz
	rm $brn_path/c1"$brn_name_core"_masked.nii.gz
	rm $brn_path/bc1"$brn_name_core"_masked.nii.gz
	rm $brn_path/c2"$brn_name_core"_masked.nii.gz
	rm $brn_path/bc2"$brn_name_core"_masked.nii.gz


	# ------------------------------------------------------------------	
	# 2. COMPLETE POST IMAGE WITH LACUNA MASK
	# ------------------------------------------------------------------
	# 2.1. Apply mask
	fslmaths $brn_path/"$brn_name_core"_masked.nii.gz -mul $brn_path/brain_mask.nii.gz $brn_path/"$brn_name_core"_brn_masked
	rm $brn_path/"$brn_name_core"_masked.nii.gz 

	# 2.2. Get mean
	mean_val=$(fslmeants -i $brn_path/"$brn_name_core"_brn_masked -m $brn_path/brain_mask.nii.gz)
	mean_val=$(echo "scale=0; ($mean_val+0.005)/1" | bc)
	rm $brn_path/brain_mask.nii.gz

	# 2.3. Fill out lacuna with mean
	fslmaths $lac_path/$lac_name_core -mul $mean_val -add $brn_path/"$brn_name_core"_brn_masked $brn_path/"$brn_name_core"_full
	rm $brn_path/"$brn_name_core"_brn_masked.nii.gz

	# ------------------------------------------------------------------	
	# 3. STEPS IN MNI SPACE
	# ------------------------------------------------------------------
	if [[ $run_mode == "slow_good" ]]; then
		# 3.1. LINEARLY register native to MNI template
		antsRegistrationSyN.sh -d 3 -n $CoresPerCase -f $code_dir/labeling_template/"$atlas_brain".nii.gz -m $brn_path/"$brn_name_core"_full.nii.gz -o $brn_path/L_"$brn_name_core"_ -t a
		# ~30s

		# 3.2. NON-LINEARLY register MNI template onto registerED NATIVE
		antsRegistrationSyN.sh -d 3 -n $CoresPerCase -f $brn_path/L_"$brn_name_core"_Warped.nii.gz -m $code_dir/labeling_template/"$atlas_brain".nii.gz -o $brn_path/NL_"$atlas_brain"_  -t b
		# ~6min30s

	elif [[ $run_mode == "quick_dirty" ]]; then
		# 3.1. LINEARLY register native to MNI template
		antsRegistrationSyNQuick.sh -d 3 -n $CoresPerCase -f $code_dir/labeling_template/"$atlas_brain".nii.gz -m $brn_path/"$brn_name_core"_full.nii.gz -o $brn_path/L_"$brn_name_core"_ -t a
		# ~10s

		# 3.2. NON-LINEARLY register MNI template onto registerED NATIVE
		antsRegistrationSyNQuick.sh -d 3 -n $CoresPerCase -f $brn_path/L_"$brn_name_core"_Warped.nii.gz -m $code_dir/labeling_template/"$atlas_brain".nii.gz -o $brn_path/NL_"$atlas_brain"_ -t b
		# ~45s

	fi
	
	# Remove residuals
	rm $brn_path/L_"$brn_name_core"_Warped.nii.gz
	rm $brn_path/L_"$brn_name_core"_0GenericAffine.mat
	rm $brn_path/L_"$brn_name_core"_InverseWarped.nii.gz
	rm $brn_path/NL_"$atlas_brain"_Warped.nii.gz
	rm $brn_path/NL_"$atlas_brain"_InverseWarped.nii.gz
	rm $brn_path/NL_"$atlas_brain"_1InverseWarp.nii.gz

	# 3.3. LINEARLY register MNI template onto native
	antsRegistrationSyN.sh -d 3 -n $CoresPerCase -f $brn_path/"$brn_name_core"_full.nii.gz -m $code_dir/labeling_template/"$atlas_brain".nii.gz -o $brn_path/L_"$atlas_brain"_in_native_ -t a
	# ~30s
	rm $brn_path/L_"$atlas_brain"_in_native_InverseWarped.nii.gz
	rm $brn_path/L_"$atlas_brain"_in_native_Warped.nii.gz

	# 3.4. Apply NON-linear transformation to labels, then LINEAR to 
	# bring to NATIVE 
	antsApplyTransforms -d 3 -e 0 \
		-i $code_dir/labeling_template/"$atlas_labels".nii.gz \
		-o $brn_path/NL_"$atlas_labels"_in_native.nii.gz \
		-n NearestNeighbor \
		-r $brn_path/"$brn_name_core"_full.nii.gz \
		-t $brn_path/L_"$atlas_brain"_in_native_0GenericAffine.mat \
		-t $brn_path/NL_"$atlas_brain"_1Warp.nii.gz \
		-t $brn_path/NL_"$atlas_brain"_0GenericAffine.mat

	# 3.5. Correct header
	fslcpgeom $brn_path/"$brn_name_core"_full.nii.gz $brn_path/NL_"$atlas_labels"_in_native.nii.gz
	# python rvdl_replace_header.py $brn_path/"$brn_name_core"_full.nii.gz $brn_path/NL_"$atlas_labels"_in_native.nii.gz 1

	# Remove residuals
	rm $brn_path/"$brn_name_core"_full.nii.gz
	rm $brn_path/NL_"$atlas_brain"_0GenericAffine.mat
	rm $brn_path/NL_"$atlas_brain"_1Warp.nii.gz
	rm $brn_path/L_"$atlas_brain"_in_native_0GenericAffine.mat

	
	# ------------------------------------------------------------------	
	# 4. Anatomical labeling
	# ------------------------------------------------------------------
	# 4.1. Create image with lacuna labels (binarize)
	fslmaths $lac_path/$lac_name_core -bin -mul $brn_path/NL_"$atlas_labels"_in_native $brn_path/"$lac_name_core"_labeled

	# 4.2. Create table and ROIs
	python $code_dir/rvdl_labeling_descrip.py $lac_path/"$lac_name_core".nii.gz $brn_path/"$lac_name_core"_labeled.nii.gz $brn_path/NL_"$atlas_labels"_in_native.nii.gz 0.5 1

	# 4.3. Delete extras
	if [[ $del_extra == "yes" ]]; then
		rm $brn_path/NL_"$atlas_labels"_in_native.nii.gz
	fi
	
}

"$@"