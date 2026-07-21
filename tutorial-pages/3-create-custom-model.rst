
How to Create a Custom Dataset for a ML Model
=============================================

This guide walks you through dataset creation (frame selection + annotation) and training a custom YOLO-based model.

1) Decide what model you want to train
--------------------------------------

Before creating an annotation dataset, decide which type of task you want to train.
At the moment, we support **YOLO-based models** (Ultralytics), such as detection, segmentation, or pose.

Browse the supported tasks here:
`Ultralytics YOLO Tasks <https://docs.ultralytics.com/tasks/>`_

.. tip::
   Your choice here affects how you annotate:

   - **Detection** → bounding boxes
   - **Segmentation** → polygons/masks
   - **Pose** → keypoints

2) Plan your dataset and choose videos
--------------------------------------

Pick videos that represent the full variability of what you want the model to handle.
The goal is to avoid training on a narrow “best-case” subset.

- Include different backgrounds, lighting, camera angles, and distances.
- Include easy and hard examples (small targets, partial visibility, motion blur, reflections, etc.).
- Try to cover all relevant environments and recording conditions.

To create your annotation dataset (choosing an annotation tool, extracting frames, and labeling them), see `Creating Annotations with TRex <2-create-annotations.rst>`_.

3) Export the dataset in YOLO format
------------------------------------

Once annotation is complete, export your dataset in a YOLO-compatible format.
Most tools offer an export option for YOLO/Ultralytics.

- Keep a clear ``train/val/test`` split (usually 70%/20%/10% of the annotated dataset).
- Verify that labels align with images after export (spot-check a few samples).

4) Training a model
-------------------

After exporting, you can train a custom YOLO-based model using Ultralytics.

- Training instructions:
  `Model Training Documentation <https://trex.run/docs/model_training.html>`_
- Custom Colab notebook (with extras like label changes and tiling):
  `Custom Training Colab Notebook <https://github.com/albiangela/train-custom-YOLO-Colab>`_

.. note::
   If your targets are small, tiling can help. You can tile images before annotation or tile annotated images before training (for example using the Colab notebook above).
   In TRex, you can enable tiling during detection, if you trained a tiled model.

5) Iterate
----------

Dataset building is iterative. After your first training run:

- Inspect mistakes (false positives/negatives) and add frames that represent those failure cases.
- Balance the dataset if one condition dominates (e.g., only one background or one viewpoint).
- Repeat: annotate → retrain → evaluate.

If anything is unclear or you run into issues during setup, annotation, or export, let us know.

Next steps
----------

If you run into tracking issues while using your model, check the `FAQ <4-FAQ.rst>`_.
