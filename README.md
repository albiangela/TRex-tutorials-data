# TRex-tutorial-data
This repository contains data used to follow TRex tutorials and learn tracking basics (https://trex.run/).

The original video files used for the tutorials and that can be used to follow video tutorials step-by-step can be found [here](https://doi.org/10.17617/3.7F5MGE)

The current folder structure is

```
├── TRex-tracking-output
│   ├── hexbugs
│   │   └── data
│   ├── locusts-5
│   │   └── data
│   └── multi-trials
│       └── data
├── YOLO-models
│   └── hexbugs-annotation-dataset
│       └── hexseg.v2i.yolov11
│           ├── test
│           │   ├── images
│           │   └── labels
│           ├── train
│           │   ├── images
│           │   └── labels
│           └── valid
│               ├── images
│               └── labels
├── dataset-info-files
└── model-training-code
```


Where:
- TRex-tracking-output: contains subfolders with per-individual tracking output files (.npz). These files can be used for further data analysis
- YOLO-models: contains two yolo models:
  - a 640px YOLO-pose model for locusts with 7 keypoints
  - a 1980px YOLO-segmentation model for hexbugs
- dataset-info-files: contains information on the data collection methods, description and acknowledgments
- model-training-code: contains a jupyter notebook with the commands to train a custom YOLO model (bounding box, keypoint, segmentation) and a .py file with useful functions to customize the code

## Tutorial to train a custom YOLO model
1.	Ultralytics Official Guide
The [official Ultralytics documentation](https://docs.ultralytics.com/integrations/jupyterlab/#what-are-the-key-features-of-jupyterlab-that-make-it-suitable-for-yolo11-projects) provides detailed instructions for training YOLO models in JupyterLab environments.

2.	Ultralytics HUB
For a streamlined, user-friendly experience, the [Ultralytics HUB](https://hub.ultralytics.com/home) allows you to upload your dataset and train a model through a simple interface or via a Google Colab notebook. More details can be found in the [Roboflow-annotations_and_YOLO-training_tutorial.pdf](https://github.com/albiangela/TRex-tutorials-data/blob/main/Roboflow-annotations_and_YOLO-training_tutorial.pdf) included in this repository.

3.	Custom Training Notebook
We have developed a [customizable Google Colab notebook](https://colab.research.google.com/drive/1mgATEXF9Q3uwyqn36zARJuN-SCao0vWY?usp=sharing) that allows you to:
	•	Adjust training parameters
	•	Add custom functions
	•	Extend functionality for your specific use case

4.	Local Training (Jupyter Notebook)
A local Jupyter notebook version of the training code is also available in the `model-training-code` folder. This version is ideal if you prefer working on your local machine or a specific computing environment.

## Tutorial for TRex tracking data analysis 
We are currently developing code to support TRex tracking data analysis using the [movement package](https://github.com/neuroinformatics-unit/movement)
An initial example Google Colab notebook can be found [here](https://colab.research.google.com/drive/1vvFPMWrHlLsnPOul8LdsmYqbmy-Y6sWp?usp=sharing)

