# ResectVol DL

Automatic segmentation and volumetric analysis of brain lacunae from T1-weighted MRI scans.
<br>Tested on resective surgery lacunae in patients with epilepsy and brain tumor.

---

## Features
<img src="lacuna_seg_ex.png" width="400">

- Automatic segmentation of brain lacunae using nnU-Net v2
- Optional region labeling (requires SPM12, ANTs, and FSL)
- Atlas-based volumetric description of resections

---

## 1. Installation
**SYSTEM REQUIREMENTS** <br>
- Linux system (tested on Ubuntu 20.04 and 22.04)
- GPU with at least 4GB VRAM available
- Python 3.10 (preferred; see note below) <br>
<br>

**INSTALLATION STEPS**<br>
**1) Create a virtual environment**<br>
We recommend using **Conda** to manage dependencies:
```bash
conda create -y -n resectvol_dl python=3.10
conda activate resectvol_dl
```
<br>

**2) Install nnU-Net ([Version 2](https://github.com/MIC-DKFZ/nnUNet))** <br>
You can install it directly via pip:
```bash
pip install nnunetv2
```
Note: `torch 2.9.0` causes slower inference (2x slower)
For optimal performance, install an older version of PyTorch before installing nnunetv2 (see **Performance Note** below).<br>
<br>

**3) Set nnU-Net directories**  <br>
Follow the [official nnU-Net instructions](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/set_environment_variables.md).
In short:
```bash
mkdir -p /tmp/nnunet/{nnUNet_raw,nnUNet_preprocessed,nnUNet_results}
export nnUNet_raw=/tmp/nnunet/nnUNet_raw
export nnUNet_preprocessed=/tmp/nnunet/nnUNet_preprocessed
export nnUNet_results=/tmp/nnunet/nnUNet_results
```
To make these persistent, add the `export` lines above to your `.~/bashrc` file.
<br><br>

**4) Download pretrained weights** <br>
 Dowload from [this link](https://drive.google.com/file/d/1uk7UDjOARlEwNSnxlO8nyQUM3ihTl5zM/view "ResectVol DL weights"). <br> 
Then install weights with nnU-Net's built in utility. Eg:
```bash
nnUNetv2_install_pretrained_model_from_zip /home/user/Downloads/resectvoldl_weights.zip
``` 
<br>

**5) Download ResecVol DL**
 Clone or download this repository and run predictions from inside the main folder:
Eg:
```bash
cd /home/user/study1/resectvol_dl
./resectvol_dl.sh /home/user/study1/data/ /home/user/study1/output/ -s

``` 
Two anonymized example datasets are available [here](https://drive.google.com/drive/folders/18y7ObOy5DYEpQ3fZw5tAxp7NHSUOVhT3 "image samples").
<br><br>

**6) (Optional) Install additional tools for region labeling:**
- [SPM12](https://www.fil.ion.ucl.ac.uk/spm/) (Matlab-based)
- [FSL](https://fsl.fmrib.ox.ac.uk/fsl/docs/install/index.html)
- [ANTs](https://github.com/ANTsX/ANTs).
<br><br>

---

### Performance Note:
PyTorch 2.9.0 introduces a regression in 3D convolutions that slows inference.<br>
To avoid this, install an [earlier PyTorch version](https://pytorch.org/get-started/previous-versions/)) before nnunetv2.<br>
Example setup (tested on Ubuntu 22.04, CUDA 11.5):
```bash
conda create -y -n resectvol_dl python=3.10
conda activate resectvol_dl
pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu118
pip install nnunetv2

``` 
Then [set up nnU-Net directories](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/set_environment_variables.md) and install [weights](https://drive.google.com/file/d/1uk7UDjOARlEwNSnxlO8nyQUM3ihTl5zM/view "ResectVol DL weights"):
```bash
mkdir -p /tmp/nnunet/{nnUNet_raw,nnUNet_preprocessed,nnUNet_results}
export nnUNet_raw=/tmp/nnunet/nnUNet_raw
export nnUNet_preprocessed=/tmp/nnunet/nnUNet_preprocessed
export nnUNet_results=/tmp/nnunet/nnUNet_results
nnUNetv2_install_pretrained_model_from_zip /home/user/Downloads/resectvoldl_weights.zip
```
Finally, run segmentation:
```bash
cd /home/user/study1/resectvol_dl
./resectvol_dl.sh /home/user/study1/data/ /home/user/study1/output/ -s

```

---

## 2. Usage
ResectVol DL performs lacuna segmentation for all images first and then (optionally) region labeling.

Example calls:

	
  ### 1) Segmentation only <br>
  ```bash
  ./resectvol_dl.sh   /media/study1/data/   /media/study1/output -s
  ```
**Input:**\
`.../data/img1.nii.gz` <br>
**Outputs:**\
`.../output/img1_lacuna.nii.gz` (lacuna mask)

 
  ### 2) Segmentation + Region labeling <br>
  ```bash
  ./resectvol_dl.sh   /media/study1/data/   /media/study1/output -sl
  ```
**Input:**\
`.../data/img1.nii.gz` <br>
**Outputs:**\
	`.../output/img1/img1_lacuna.nii.gz` (lacuna mask)\
  `.../output/img1/img1_lacuna_labeled.nii.gz` (color-coded labels)\
	`.../output/img1/anat_descrip_img1_lacuna.txt` (region labeling + volumetric info)\
	`.../output/img1/ROIs/` (folder with labeled ROIs in separate nifti files)

  ### 3) Segmentation + Quick region labeling <br>
  (Faster but lower registration accuracy)
  ```bash
  ./resectvol_dl.sh   /media/study1/data/   /media/study1/output -slf
  ```
**Input:**\
`.../data/img1.nii.gz` <br>
**Outputs:**\
  `.../output/img1/img1_lacuna.nii.gz` (lacuna mask)\
  `.../output/img1/img1_lacuna_labeled.nii.gz` (color-coded labels)\
	`.../output/img1/anat_descrip_img1_lacuna.txt` (region labeling + volumetric info)\
	`.../output/img1/ROIs/` (folder with labeled ROIs in separate nifti files)

---

## Notes: 
**Segmentation** is robust and typically error-free. On the other hand, **labeling** steps are more sensitive to image quality, which may cause errors in processing. In these cases, only the lacuna mask is generated.


Two example datasets are available [here](https://drive.google.com/drive/folders/18y7ObOy5DYEpQ3fZw5tAxp7NHSUOVhT3 "image samples").

---

## 3. Licensing:
ResectVol DL is released under the BSD 3-Clause License (see [license](https://github.com/rfcasseb/resectvol_dl?tab=BSD-3-Clause-1-ov-file "License")). <br>
This license applies only to the ResectVol DL code. <br> 
Users are responsible for complying with the licenses of nnU-Net, SPM12, ANTs, FSL, and any other required third-party software.

<!--
---
## Citation

If you use ResectVol DL in your research, please cite:

    [Casseb RF, de Campos BM, et al., 2025. ResectVol DL: Automated segmentation and volumetry of brain lacunas in epilepsy surgery patients. Journal TBD / medRxiv preprint]
-->

---
## Acknowledgments

Developed at the University of Campinas (UNICAMP), 2025.
