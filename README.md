# TRex-tutorials-data

This repository contains essential resources to help learn and apply animal tracking analysis using [`TRex`](https://trex.run/) and YOLO-based machine learning models.

## 📂 Repository Structure

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

## Description of content

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
  

## 🎥 Video tutorials for `TRex` tracking basics

Video tutorials covering TRex tracking basics are available on the [TRex YouTube Channel](https://www.youtube.com/@TRexTracker)

The original raw video files we used for tutorials are available [here](https://doi.org/10.17617/3.7F5MGE) and can be used to follow the tutorials step-by-step.


## 💻 Creating an annotation dataset and training a custom YOLO model 
1.	An example of how to do this on Roboflow can be found in the [Roboflow-annotations_and_YOLO-training_tutorial.pdf](https://github.com/albiangela/TRex-tutorials-data/blob/main/Roboflow-annotations_and_YOLO-training_tutorial.pdf) included in this repository.
   Alternative annotation software: [CVAT](https://www.cvat.ai/), [label-studio](https://labelstud.io/), [Labelbox](https://labelbox.com/), and more.
 
3.	Ultralytics Official Guide with notebooks to train models
The [official Ultralytics documentation](https://docs.ultralytics.com/integrations/jupyterlab/#what-are-the-key-features-of-jupyterlab-that-make-it-suitable-for-yolo11-projects) provides detailed instructions for training YOLO models in JupyterLab environments.

4.	Ultralytics HUB - a simple solution to model training 
For a streamlined, user-friendly experience, the [Ultralytics HUB](https://hub.ultralytics.com/home) allows you to upload your dataset and train a model through a simple interface or via a Google Colab notebook.

5.	Custom Training Google Colab Notebook
[Repo with Colab Notebook](https://github.com/albiangela/train-custom-YOLO-Colab) and helper utilities to fetch datasets, clean/relabel them, tile images, rebalance splits, and train YOLO models end to end.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/albiangela/train-custom-YOLO-Colab/blob/main/Train-custom-YOLO-model-example.ipynb)


7.	Local Training (Jupyter Notebook)
A local Jupyter notebook version of the training code is also available in the `model-training-code` folder. This version is ideal if you prefer working on your local machine or a specific computing environment.

Find even more suggestions on the [TRex website](https://trex.run/docs/model_training.html)

## 👩‍💻 Tutorial for TRex tracking data analysis 

This tutorial is developed in collaboration with the [movement package](https://github.com/neuroinformatics-unit/movement).

Use the following Google Colab notebook to analyze centroid tracking data from TRex:

- [Example notebook for TRex data analysis](https://colab.research.google.com/drive/1vvFPMWrHlLsnPOul8LdsmYqbmy-Y6sWp?usp=sharing).
  
This notebook is a guide for loading centroid trajectory data from background subtraction tracking, using [`TRex`](https://trex.run/).  
The goal is to transform raw `TRex` output into an `xarray.Dataset` using the [`movement`](https://movement.neuroinformatics.dev/index.html) library for data analysis and visualization.


Analysis Overview:

- Load `TRex` centroid output data
  
- Transform the data into a `movement`-compatible `xarray.Dataset`.
  
- Simple initial data visualization (to verify basic information)

This setup ensures efficient and structured analysis of animal tracking data, from initial tracking to advanced model training and analysis.

## 🔗 Reference Links Summary

| Topic | Link |
|-------|------|
| TRex Docs | https://trex.run/docs/ |
| YOLO Segmentation Format | https://docs.ultralytics.com/datasets/segment/ |
| YOLO Detection Format | https://docs.ultralytics.com/datasets/detect/ |
| Instance Segmentation Intro | https://blog.roboflow.com/instance-segmentation/ |
| Annotation and Training Intro | https://github.com/albiangela/TRex-tutorials-data/blob/main/Roboflow-annotations_and_YOLO-training_tutorial.pdf |
| Colab Notebook YOLO model training| https://colab.research.google.com/drive/1fk6Yj6iSKaP5CxlXav11n85f9-SBnGVb?usp=sharing |
| Training Guide | https://trex.run/docs/model_training.html |
| Example Data Tutorials| https://keeper.mpdl.mpg.de/d/12882cf6c0c14d7ca981/ |

