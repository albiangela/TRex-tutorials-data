Creating Annotations with TRex
=============================================

This guide explains how to install TRex, open it, and use it to annotate frames for a custom detection/tracking model.

1) Install TRex
--------------------------------------

First, install **Miniforge**, which is needed to create the TRex environment.

Download Miniforge here: `<https://conda-forge.org/download/>`_

Then open a terminal:

- **Windows:** search for and open **Miniforge Prompt**
- **macOS/Linux:** open **Terminal**

Create a new TRex environment:

.. code-block:: bash

   conda create -n beta -c trex-beta trex

When asked to proceed, type ``y`` and press **Enter**.

For the full installation documentation, see the `TRex installation documentation <https://trex.run/docs/install.html>`_.

2) Open TRex
--------------------------------------

Activate the TRex environment:

.. code-block:: bash

   conda activate beta

Start TRex:

.. code-block:: bash

   trex

3) Decide what model you want to train
--------------------------------------

Before creating an annotation dataset, decide which type of task you want to train.
At the moment, TRex supports **YOLO-based models** (Ultralytics), such as detection, segmentation, or pose.

Browse the supported tasks here: `Ultralytics YOLO Tasks <https://docs.ultralytics.com/tasks/>`_

.. tip::
   Your choice here affects how you annotate:

   - **Detection** → bounding boxes
   - **Segmentation** → polygons/masks
   - **Pose** → keypoints

4) Plan your dataset and choose videos
--------------------------------------

Pick videos that represent the full variability of what you want the model to handle.
The goal is to avoid training on a narrow "best-case" subset.

- Include different backgrounds, lighting, camera angles, and distances.
- Include easy and hard examples (small targets, partial visibility, motion blur, reflections, etc.).
- Try to cover all relevant environments and recording conditions.

5) Create an annotation dataset (extract frames + label)
--------------------------------------------------------

The first practical step is to create an annotation dataset. This means:
extracting a set of frames from your videos and drawing labels around the target(s) of interest.

Common annotation tools
^^^^^^^^^^^^^^^^^^^^^^^

- `Roboflow <https://roboflow.com/>`_ Fast and user-friendly.

.. note::
    Roboflow has a free version, but uploaded data becomes **public** (visible in the “Roboflow universe”). New accounts typically include **14 days of private projects**. `Roboflow Setup Guide <https://github.com/albiangela/TRex-tutorials-data/blob/main/Roboflow-annotations_and_YOLO-training_tutorial.pdf>`_

Alternatives - if you need the data to remain fully local:

- **CVAT** (local or self-hosted)
- **Label Studio** (local or self-hosted) - `tutorial <https://alexhang212.github.io/YOLO_Behaviour_Repo/annotation.html>`_
- **TRex** (built-in annotation) - annotate directly inside TRex while reviewing your video, then export the dataset as YOLO or COCO format (see the sections below).

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

6) Start annotating in TRex
--------------------------------------

To get started with annotations, watch the example video tutorial first: `<https://keeper.mpdl.mpg.de/f/9a7d49aabe724e5aaf71/>`_

7) Parameters and shortcuts for annotations in TRex
----------------------------------------------------

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

8) Save and export your annotations
--------------------------------------

Once you have annotated your frames, save your work and export the dataset:

- **Menu > Save config**
- **Menu > Save state**
- **Menu > Export annotations** — annotations can be exported as **YOLO** or **COCO** format

Next steps
--------------------------------------

Once you have exported your annotation dataset, continue to `Creating a Custom Model <3-create-custom-model.rst>`_ to train a custom YOLO-based model on it.
