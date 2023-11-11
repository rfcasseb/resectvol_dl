#!/bin/bash
# -------------------------------------------------------------------------
# Script to run ResectVol DL analysis (segmentation and labeling)
# MUST BE RUN FROM WITHIN FOLDER path/to/resectvoldl
# -------------------------------------------------------------------------
# =========================================================================
# Raphael Fernandes Casseb & Brunno Machado de Campos
# University of Campinas, 2023
#
# Copyright (c) 2023
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
	

# 1. help
# -------------------------------------------------------------------------
function help {
   echo
   echo "Usage: ./resectvol_dl.sh <folder_path> <output_folder_path> [-s|-sl|-slf]"
   echo
   echo "  <folder_path> : Path to the folder containing the nifti file(s) in .nii.gz format"
   echo "  <output_folder_path> : Path to a folder where results will be saved"
   echo "  -s           : Run lacuna segmentation only"
   echo "  -sl          : Run lacuna segmentation + slow and better ROI labeling"
   echo "  -slf         : Run lacuna segmentation + fast and worse ROI labeling"
}



# 2. Check if the user has provided the correct number of arguments
# -------------------------------------------------------------------------
if [ $# -lt 2 ]; then
   echo "Error: Missing arguments"
   help
   exit 1
fi



# 3. Parse the command line arguments
# -------------------------------------------------------------------------
folder_path=$1
output_folder_path=$2
option=$3



# 4. Check inputs
# -------------------------------------------------------------------------
# Check if folder exists
if [ ! -d "$folder_path" ]; then
   echo "Error: Folder not found"
   help
   exit 1
fi

# Check if output folder exists
if [ ! -d "$output_folder_path" ]; then
   echo "Error: Folder not found"
   help
   exit 1
fi

# Check if the folder contains any nifti files in .nii.gz format
nifti_files=$(find "$folder_path" -type f -name "*.nii.gz")
if [ -z "$nifti_files" ]; then
   echo "Error: No nifti files in .nii.gz format found in the folder"
   help
   exit 1
fi



# 5. Adjust file names to run prediction
# -------------------------------------------------------------------------
# Rename
for file in $nifti_files; do
   if [[ "$file" != *_0000.nii.gz ]]; then
      mv "$file" "${file%.nii.gz}_0000.nii.gz"
   fi
done

# Update names
nifti_files=$(find "$folder_path" -type f -name "*.nii.gz")



# 6. Run options
# -------------------------------------------------------------------------
if [ "$option" == "-s" ]; then
   # 6.1. Run lacuna segmentation only
   # ---------------------------------
   nnUNet_predict -i "$folder_path" -o "$output_folder_path" -tr nnUNetTrainerV2 -ctr nnUNetTrainerV2CascadeFullRes -m 3d_fullres -p nnUNetPlansv2.1 -t Task510_tp_etp2
   rm $output_folder_path/plans.pkl
   rm $output_folder_path/postprocessing.json


elif [ "$option" == "-sl" ]; then
   # 6.2.1. Run lacuna segmentation
   # ------------------------------
   nnUNet_predict -i "$folder_path" -o "$output_folder_path" -tr nnUNetTrainerV2 -ctr nnUNetTrainerV2CascadeFullRes -m 3d_fullres -p nnUNetPlansv2.1 -t Task510_tp_etp2
   rm $output_folder_path/plans.pkl
   rm $output_folder_path/postprocessing.json

   # 6.2.2. ROI labeling
   # -------------------
   # Necessary files
   lac_files=($output_folder_path/*.nii.gz)
   postop_files=($folder_path/*.nii.gz)

   # Create folders with the files
   for i in "${!lac_files[@]}"; do
      lac_file_name=$(basename -- "${lac_files[$i]}")
      dir_name="${lac_file_name%.nii.gz}"
      mkdir $output_folder_path/$dir_name
      
      # Move lacuna file to sbj output folder
      mv "${lac_files[$i]}" $output_folder_path/$dir_name/"$dir_name"_lac.nii.gz
      lac_file=$output_folder_path/$dir_name/"$dir_name"_lac.nii.gz
      
      # Copy postop file to sbj output folder
      for i in "${!postop_files[@]}"; do

         # Remove the _0000 suffix from postop file to find right folder
         postop_file_name=$(basename -- "${postop_files[$i]}")
         if [[ "$postop_file_name" == *_0000.nii.gz ]]; then
            postop_file_name="${postop_file_name%_0000.nii.gz}"
         else
            postop_file_name="${postop_file_name%.nii.gz}"
         fi

         # Compare file name with folder name (should match)
         if [[ $postop_file_name == $dir_name ]]; then
            cp ${postop_files[$i]} $output_folder_path/$dir_name/"$postop_file_name".nii.gz
            postop_file=$output_folder_path/$dir_name/"$postop_file_name".nii.gz
         fi
      done

      # Run labeling
      bash rvdl_labeling.sh roi_labeling $postop_file $lac_file $PWD/rvdl_labeling.sh slow_good

   done   

   

elif [ "$option" == "-slf" ]; then
   # 6.3.1. Run lacuna segmentation
   # ------------------------------
   nnUNet_predict -i "$folder_path" -o "$output_folder_path" -tr nnUNetTrainerV2 -ctr nnUNetTrainerV2CascadeFullRes -m 3d_fullres -p nnUNetPlansv2.1 -t Task510_tp_etp2
   rm $output_folder_path/plans.pkl
   rm $output_folder_path/postprocessing.json

   # 6.3.2. ROI labeling
   # -------------------
   # Necessary files
   lac_files=($output_folder_path/*.nii.gz)
   postop_files=($folder_path/*.nii.gz)

   # Create folders with the files
   for i in "${!lac_files[@]}"; do
      lac_file_name=$(basename -- "${lac_files[$i]}")
      dir_name="${lac_file_name%.nii.gz}"
      mkdir $output_folder_path/$dir_name
      
      # Move lacuna file to sbj output folder
      mv "${lac_files[$i]}" $output_folder_path/$dir_name/"$dir_name"_lac.nii.gz
      lac_file=$output_folder_path/$dir_name/"$dir_name"_lac.nii.gz
      
      # Copy postop file to sbj output folder
      for i in "${!postop_files[@]}"; do

         # Remove the _0000 suffix from postop file to find right folder
         postop_file_name=$(basename -- "${postop_files[$i]}")
         if [[ "$postop_file_name" == *_0000.nii.gz ]]; then
            postop_file_name="${postop_file_name%_0000.nii.gz}"
         else
            postop_file_name="${postop_file_name%.nii.gz}"
         fi

         # Compare file name with folder name (should match)
         if [[ $postop_file_name == $dir_name ]]; then
            cp ${postop_files[$i]} $output_folder_path/$dir_name/"$postop_file_name".nii.gz
            postop_file=$output_folder_path/$dir_name/"$postop_file_name".nii.gz
         fi
      done

      # Run labeling
      bash rvdl_labeling.sh roi_labeling $postop_file $lac_file $PWD/rvdl_labeling.sh quick_dirty

   done



else
   # 6.4. Catch wrong options
   # ------------------------
   # Rename the files back to their original names
   for file in $nifti_files; do
      if [[ "$file" == *_0000.nii.gz ]]; then
         mv "$file" "${file%_0000.nii.gz}.nii.gz"
      fi
   done
   echo "Error: Invalid option"
   help
   exit 1

fi # Run options



# 7. Rename the files back to their original names
# -------------------------------------------------------------------------
for file in $nifti_files; do
    if [[ "$file" == *_0000.nii.gz ]]; then
        mv "$file" "${file%_0000.nii.gz}.nii.gz"
    fi
done







# # -------------------------------------------------------------------------
# # MAIN
# # -------------------------------------------------------------------------
# # Loop through options
# while getopts ":hn:" option; do
#    case $option in
#       h) # display Help
#          help
#          exit;;
#       s) # Run segmentation
#          pos_file=$OPTARG;;
#      \?) # Invalid option
#          echo "Error: Invalid option"
#          exit;;
#    esac
# done