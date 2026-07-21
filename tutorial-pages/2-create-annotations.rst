Creating an Annotation Dataset
=============================================

This guide covers the general steps for creating an annotation dataset for a custom detection/tracking model, and then walks through the tools annotation built into TRex in more detail.

1) Decide what model you want to train
--------------------------------------

Before creating an annotation dataset, decide which type of task you want to train.
At the moment, TRex supports **YOLO-based models** (Ultralytics), such as detection, segmentation, or pose.

Browse the supported tasks here: `Ultralytics YOLO Tasks <https://docs.ultralytics.com/tasks/>`_

.. tip::
   Your choice here affects how you annotate:

   - **Detection** → bounding boxes
   - **Segmentation** → polygons/masks
   - **Pose** → keypoints

2) Plan your dataset and choose videos
--------------------------------------

Pick videos that represent the full variability of your problem space.
The goal is to avoid training on a narrow "best-case" subset, but to show it the entire landscape of what you expect it to handle later on.

- Include different backgrounds, lighting, camera angles, and distances.
- Include easy and hard examples (small targets, partial visibility, motion blur, reflections, etc.).
- Try to cover all relevant environments and recording conditions.

3) Create an annotation dataset (extract frames + label)
--------------------------------------------------------

The first practical step is to create an annotation dataset. This means extracting a set of frames from your videos and drawing labels around the target(s) of interest.

Common annotation tools
^^^^^^^^^^^^^^^^^^^^^^^

- `Roboflow <https://roboflow.com/>`_ Fast and user-friendly.

.. note::
    Roboflow has a free version, but uploaded data becomes **public** (visible in the “Roboflow universe”). New accounts typically include **14 days of private projects**. `Roboflow Setup Guide <https://github.com/albiangela/TRex-tutorials-data/blob/main/Roboflow-annotations_and_YOLO-training_tutorial.pdf>`_

Alternatives - if you need the data to remain fully local:

- **CVAT** (local or self-hosted)
- **Label Studio** (local or self-hosted) - `tutorial <https://alexhang212.github.io/YOLO_Behaviour_Repo/annotation.html>`_
- **TRex** (built-in annotation) - annotate directly inside TRex while reviewing your video, then export the dataset as YOLO or COCO format.

Annotations in TRex have a slightly different workflow compared to the other tools. Below you'll see instructions that apply to many of these tools, also TRex, as well as some general advice. See `Annotating with TRex (UNDER DEVELOPMENT)`_ below for the full walkthrough the TRex-specific system.

Frame extraction recommendations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Extract ~25-30 frames per video** as a starting point.
- It can help to extract more than needed, then select frames to annotate roughly at random.
- Annotate frames from most videos (don't concentrate on just a few).

Annotation guidelines
^^^^^^^^^^^^^^^^^^^^^

- Label **all visible targets** in each frame (or all visible parts, if partially occluded).
- Make bounding boxes **tight** around the target with as little background as possible.
- Be consistent in how you treat partial visibility and edge-of-frame cases.

.. note::
   Consistency matters, the same visual scenario should be labeled the same way across the dataset.
   This reduces confusion for the model and usually improves performance.

4) Export the dataset in YOLO format
------------------------------------

Once annotation is complete, export your dataset in a YOLO-compatible format.
Most tools offer an export option for YOLO/Ultralytics.

- Keep a clear ``train/val/test`` split (usually 70%/20%/10% of the annotated dataset).
- Verify that labels align with images after export (spot-check a few samples).

Annotating with TRex (UNDER DEVELOPMENT)
-----------------------------------------

If you'd rather annotate directly inside TRex instead of using Roboflow, CVAT, or Label Studio, TRex has a built-in annotation window described below.

Install and open TRex
^^^^^^^^^^^^^^^^^^^^^^

See `Installation and Workshop Setup <install.rst>`_ to install and open TRex.

Start annotating in TRex
^^^^^^^^^^^^^^^^^^^^^^^^^

To get started with annotations, watch the example video tutorial first: `<https://keeper.mpdl.mpg.de/f/9a7d49aabe724e5aaf71/>`_

Parameters and shortcuts for annotations in TRex
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use these parameters and shortcuts to set up annotations and move through the video and annotated frames:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Action
     - Shortcut / Menu
   * - Show annotated frames in the timeline
     - **FOIs > Annotated** in the top-right menu
   * - Play or pause the video
     - **Space bar**
   * - Go to the next annotated frame
     - **M**
   * - Go to the previous annotated frame
     - **N**
   * - Add an annotation box
     - Hold **Ctrl** and click **4 points** with the left mouse button
   * - Move one frame at a time
     - **Left / Right arrow keys**
   * - Set detection type
     - Change ``detect_format`` depending on the type of annotation task you want to work with (object detection, segmentation, pose estimation, oriented bounding boxes, classification). See the `Ultralytics task documentation <https://docs.ultralytics.com/tasks>`_.
   * - Set annotation classes
     - Define ``detect_class`` with the classes you want to annotate, for example ``bug``, ``shark``, ``person``, or any other target class relevant to your project.

Save and export your annotations in TRex
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you have annotated your frames, save your work and export the dataset:

- **Menu > Save config**
- **Menu > Save state**
- **Menu > Export annotations** — annotations can be exported as **YOLO** or **COCO** format

Next steps
--------------------------------------

Once you have exported your annotation dataset, continue to `Creating a Custom Model <3-create-custom-model.rst>`_ to train a custom YOLO-based model on it.
