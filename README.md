# resectvol_dl
Automatically segment resective brain lacunas in MR images

ResectVol DL relies on the nnU-Net framework. Please install VERSION 1 in your Linux system to run ResectVol DL.

Weights can be downloaded from: https://drive.google.com/file/d/1DhhDo7TrbUtbDsrynj119cl64E0DQTM9/view?usp=drive_link

To install weights use the bash command (available after nnU-Net installation): nnUNet_install_pretrained_model_from_zip 

To run ResecVol DL, gather all your compressed nifti images (.nii.gz)  in a directory (eg: /media/study1/data/) and choose if you want to run only lacuna segmentation (-s), lacuna segmentation + region labeling (-sl), or lacuna segmentation + fast region labeling (less accurate) (-slf).

ResectVol DL first runs lacuna segmentation for all images, and then runs labeling.

Example calls:
./resectvol_dl.sh /media/study1/data/ /media/study1/output -s

./resectvol_dl.sh /media/study1/data/ /media/study1/output -sl

./resectvol_dl.sh /media/study1/data/ /media/study1/output -slf

Enjoy!
