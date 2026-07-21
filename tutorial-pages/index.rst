.. include:: names.rst

TRex Tutorials
==============

Welcome! |trex| is a versatile tracking software for analyzing the movement and
posture of animals (or any other moving objects) in video. These tutorials walk
you from your first project all the way through training your own detection
models, with a separate FAQ for the issues that come up most often along the way.

.. epigraph::

   **Coming to the workshop?** Please install |trex| and download the example
   dataset **before** the workshop starts — see `Installation and Workshop
   Setup <install.rst>`_. If this is your first time tracking anything, also
   skim `Introduction to Tracking with TRex <1-intro-detection-tracking.rst>`_
   so the vocabulary on day one is familiar.

You can watch the video versions on the
`TRex YouTube channel <https://www.youtube.com/@TRexTracker>`_, and find example
videos, models, and analysis notebooks on the
`TRex-tutorials-data GitHub repository <https://github.com/albiangela/TRex-tutorials-data>`_.

Before you start
----------------

- `Installation and Workshop Setup <install.rst>`_ — install |trex| with
  Miniforge (Windows, macOS, Linux), download the workshop dataset, and
  bookmark the analysis notebooks for after tracking.

Get oriented
------------

Start here if this is your first time using |trex| or you want to make sure
your recording setup will give you tractable data.

- `Introduction to Tracking with TRex <1-intro-detection-tracking.rst>`_ —
  what tracking actually involves, what each stage of the |trex| workflow
  does, and the recording choices that matter most before you ever open the
  app.

Hands-on tutorials
------------------

Step-by-step walkthroughs using example videos you can download and follow
along with.

- `Tutorials <tutorials.rst>`_ — the main end-to-end tutorial: setting up a
  project, detecting and tracking individuals, tuning parameters, working
  with tracklets, correcting identities (manually and with Visual
  Identification), posture, and a second walkthrough using a YOLO pose model.
- `Creating an Annotation Dataset <2-create-annotations.rst>`_ — when the
  built-in detection isn't enough: choosing an annotation tool (including
  TRex's own built-in annotation window), collecting frames, and labeling
  them.
- `Training a Custom YOLO Model <3-create-custom-model.rst>`_ — training
  your own YOLO detection, segmentation, or pose model on the dataset you
  just annotated.

Reference and help
------------------

- `FAQ <4-FAQ.rst>`_ — common problems with tracking, identity assignment,
  and parameter tuning, with concrete things to try.

.. toctree::
   :hidden:
   :maxdepth: 2

   install
   1-intro-detection-tracking
   tutorials
   2-create-annotations
   3-create-custom-model
   4-FAQ
