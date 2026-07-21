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

5) Start annotating
--------------------------------------

To get started with annotations, watch the example video tutorial first: `<https://keeper.mpdl.mpg.de/f/9a7d49aabe724e5aaf71/>`_

6) Parameters and shortcuts for annotations in TRex
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

7) Save and export your annotations
--------------------------------------

Once you have annotated your frames, save your work and export the dataset:

- **Menu > Save config**
- **Menu > Save state**
- **Menu > Export annotations** — annotations can be exported as **YOLO** or **COCO** format

Next steps
--------------------------------------

Once you have exported your annotation dataset, continue to `Creating a Custom Model <3-create-custom-model.rst>`_ to train a custom YOLO-based model on it.
