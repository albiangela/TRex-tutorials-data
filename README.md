# TRex-tutorials-data

This repository contains:

1. data obtained with [`TRex`](https://trex.run/) tutorials that can be used for tutorials on [tracking data analysis](#tutorial-for-trex-tracking-data-analysis) 

2. Two trained YOLO models that can be used following the which [tracking video tutorials](https://www.youtube.com/@TRexTracker)

3. Code for training custom YOLO models (bounding box, keypoints, segmentation) (see below: [Tutorial to train a custom YOLO model](#tutorial-to-train-a-custom-yolo-model)).


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

- **`TRex-tracking-output/`**  
  Contains subfolders with per-individual tracking output files (`.npz`). These can be used for further data analysis (see below: [Tutorial for TRex tracking data analysis](#tutorial-for-trex-tracking-data-analysis)).

- **`YOLO-models/`**  
  Includes two trained YOLO models:  
  &nbsp;&nbsp;&nbsp;&nbsp;• A **640px YOLO-pose model** for locusts (7 keypoints)  
  &nbsp;&nbsp;&nbsp;&nbsp;• A **1980px YOLO-segmentation model** for hexbugs

- **`dataset-info-files/`**  
  Documentation on data collection methods, dataset descriptions, and acknowledgments.

- **`model-training-code/`**  
  A Jupyter notebook for training custom YOLO models (bounding box, keypoints, segmentation), along with a Python script containing helper functions to customize the training process (see below: [Tutorial to train a custom YOLO model](#tutorial-to-train-a-custom-yolo-model)).
  

## 🎥 Video tutorials to learn `TRex` tracking basics

🎥 Video tutorials are available on the [TRex YouTube channel](https://www.youtube.com/@TRexTracker)

The original video files used for the tutorials and that can be used to follow video tutorials step-by-step can be found [here](https://doi.org/10.17617/3.7F5MGE)


## 💻 Tutorial to train a custom YOLO model
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

## 👩‍💻 Tutorial for TRex tracking data analysis 
We are currently developing code to support TRex tracking data analysis using the [movement package](https://github.com/neuroinformatics-unit/movement).

An initial example Google Colab notebook can be found [here](https://colab.research.google.com/drive/1vvFPMWrHlLsnPOul8LdsmYqbmy-Y6sWp?usp=sharing). 
This notebook is a guide for loading centroid trajectory data from background subtraction tracking, using [`TRex`](https://trex.run/).  
The goal is to transform raw `TRex` output into an `xarray.Dataset` using the [`movement`](https://movement.neuroinformatics.dev/index.html) library for data analysis and visualization.

Summary of steps:
- Load `TRex` centroid output data
- Transform the data into a `movement`-compatible `xarray.Dataset`.
- Simple initial data visualization (to verify basic information)

We will use a set of helper functions (part of this notebook and related scripts) to:
- Safely load `.npz` files from TRex.
- Validate the structure of the data.
- Convert it into an `xarray.Dataset` for use with `movement`.


