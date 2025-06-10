# TRex-tutorial-data
This repository contains data used to follow TRex tutorials and learn tracking basics (https://trex.run/).

The original video files used for the tutorials and that can be used to follow video tutorials step-by-step can be found [here](https://doi.org/10.17617/3.7F5MGE)

The current folder structure is

```
├── TRex-tracking-output
│   ├── hexbugs
│   │   └── data
│   ├── locusts-15
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
- TRex-tracking-output: contains subfolders with per-individual tracking output files (.npz). These files can be used for further data analysis.
- YOLO-models: contains two yolo models:
  - a 640px YOLO-pose model for locusts with 7 keypoints
  - a 1980px YOLO-segmentation model for hexbugs
- dataset-info-files: contains information on the data collection methods, description and acknowledgments.
- model-training-code: contains a jupyter notebook with the commands to train a custom YOLO model (bounding box, keypoint, segmentation). 

## Tutorial to train a custom YOLO model
An example Google Colab notebook to train a custom YOLO model can be found [here](https://colab.research.google.com/drive/1mgATEXF9Q3uwyqn36zARJuN-SCao0vWY?usp=sharing).

## Tutorial for TRex tracking data analysis 
We are currently developing code to support TRex tracking data analysis using the [movement package](https://github.com/neuroinformatics-unit/movement).
An initial example Google Colab notebook can be found [here](https://colab.research.google.com/drive/1vvFPMWrHlLsnPOul8LdsmYqbmy-Y6sWp?usp=sharing)

