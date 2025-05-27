# TRex-tutorial-data
This repository contains data used to follow TRex tutorials and learn tracking basics (https://trex.run/).

The original video files can be found [here](https://doi.org/10.17617/3.7F5MGE)

The current folder structure is

<pre>
```
├── TRex-tracking-output
│   ├── hexbugs
│   │   └── data
│   ├── locusts-15
│   │   └── data
│   ├── locusts-5
│   │   └── data
│   └── multi-trials
│       └── untitled folder
├── YOLO-models
└── dataset-info-files
```
</pre>


Where:
- TRex-tracking-output contains subfolders with per-individual tracking output files (.npz). These files can be used for further data analysis.
- YOLO-models contains two yolo models:
  - a 640px YOLO-pose model for locusts with 7 keypoints
  - a 640px YOLO-segmentation model for hexbugs
- dataset-info-files contains information on the data collection methods, description and acknowledgments.

The original video files are published [here](https://edmond.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.7F5MGE)

We are currently developing code to support TRex tracking data analysis using the [movement package](https://github.com/neuroinformatics-unit/movement)
An initial example Google Colab notebook can be found [here](https://colab.research.google.com/drive/1vvFPMWrHlLsnPOul8LdsmYqbmy-Y6sWp?usp=sharing)

