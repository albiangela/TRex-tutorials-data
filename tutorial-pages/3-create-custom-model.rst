
Training a Custom YOLO Model
=============================================

This guide walks you through training a custom YOLO-based model on your own annotation dataset.

Before you start here, make sure you've created and exported an annotation dataset — see `Creating an Annotation Dataset <2-create-annotations.rst>`_.

1) Training a model
-------------------

After exporting your annotation dataset, you can train a custom YOLO-based model using Ultralytics.

- Training instructions:
  `Model Training Documentation <https://trex.run/docs/model_training.html>`_
- Custom Colab notebook (with extras like label changes and tiling):
  `Custom Training Colab Notebook <https://github.com/albiangela/train-custom-YOLO-Colab>`_

.. note::
   If your targets are small, tiling can help. You can tile images before annotation or tile annotated images before training (for example using the Colab notebook above). Be aware that this may produce subtle artifacts at the tile boundaries.
   In TRex, you can enable tiling during detection in the Detection configuration screen (make sure you also trained on tiles if you want to use the model with tiling based detection enabled).

2) Iterate
----------

Dataset building is iterative. After your first training run:

- Inspect mistakes (false positives/negatives) and add frames that represent those failure cases.
- Balance the dataset if one condition dominates (e.g., only one background or one viewpoint).
- Repeat: annotate → retrain → evaluate.

If anything is unclear or you run into issues during setup, annotation, or export, let us know.

Next steps
----------

If you run into tracking issues while using your model, check the `FAQ <4-FAQ.rst>`_.
