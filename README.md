# resectvol_dl
Automatically segment resective brain lacunas in MR images

ResectVol DL relies on the nnU-Net framework. Please install [nnU-Net VERSION 1](https://github.com/MIC-DKFZ/nnUNet/tree/nnunetv1) in your Linux system to run ResectVol DL. (To run region labeling, please also install [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation) and [ANTs](http://stnava.github.io/ANTs/))

Weights can be downloaded from [here](https://drive.google.com/file/d/1DhhDo7TrbUtbDsrynj119cl64E0DQTM9/view?usp=drive_link "weights") 

To install weights use the bash command (available after nnU-Net installation): nnUNet_install_pretrained_model_from_zip 

To run ResecVol DL, gather all your compressed nifti images (.nii.gz)  in a directory (eg: /media/study1/data/) and choose if you want to run only lacuna segmentation (-s), lacuna segmentation + region labeling (-sl), or lacuna segmentation + fast region labeling (less accurate) (-slf).

ResectVol DL first runs lacuna segmentation for all images, and then runs labeling.

Example calls:

	
  1) ./resectvol_dl.sh /media/study1/data/ /media/study1/output -s
        Input ex.: .../data/img1.nii.gz
	Outputs:   .../output/img1.nii.gz (lacuna mask)

 
  2) ./resectvol_dl.sh /media/study1/data/ /media/study1/output -sl
	Input ex.: .../data/img1.nii.gz
	Outputs:   .../output/img1/img1.nii.gz (original image)
		   .../output/img1/img1_lac.nii.gz (lacuna mask)
		   .../output/img1/anat_descrip_img_lac.txt (region labeling and volumetric information)
     		   .../output/img1/Lacuna_labeled.nii.gz (color coded labels)
     		   .../output/img1/NL_ch2bet_DKT_res_in_native.nii.gz (color coded brain)
		 

  3) ./resectvol_dl.sh /media/study1/data/ /media/study1/output -slf
     	Input ex.: .../data/img1.nii.gz
	Outputs:   .../output/img1/img1.nii.gz (original image)
		   .../output/img1/img1_lac.nii.gz (lacuna mask)
		   .../output/img1/anat_descrip_img_lac.txt (region labeling and volumetric information)
     		   .../output/img1/Lacuna_labeled.nii.gz (color coded labels)
     		   .../output/img1/NL_ch2bet_DKT_res_in_native.nii.gz (color coded brain)


NB: Lacuna segmentation is quite robust and rarely presents issues. On the other hand, labeling steps are more sensitive to image quality, which may cause errors in processing.


Two sample datasets can be downloaded from [here](https://drive.google.com/file/d/19Xgy-_ByZGXNYyP3QuGHCcIrwbRUBHHA/view?usp=drive_link "image samples").

Enjoy!
