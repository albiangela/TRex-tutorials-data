.. include:: names.rst

.. _install:

Installation and Workshop Setup
===============================

This page covers everything you need to do **before the workshop**: install
|trex|, download the example videos, and (optionally) bookmark the analysis
notebooks you'll use afterwards.

.. epigraph::

   **Heads up:** please install |trex| and download the example dataset *before*
   the workshop starts — installation can take a few minutes and the dataset is
   a couple of GB. If you don't get to it in time, we'll bring a hard drive with
   all the videos.

Install TRex
------------

|trex| is distributed through `conda-forge`-style channels, so installation is
the same on Windows, macOS, and Linux.

1. **Install Miniforge.** Download and install Miniforge from
   `conda-forge.org/miniforge <https://conda-forge.org/miniforge/>`_. This gives
   you the ``conda`` package manager preconfigured to use the ``conda-forge``
   channel.

   .. NOTE::

      **What is a terminal, and how do I open the Miniforge one?**

      A terminal (or command-line interface) is a text window for typing
      commands to your computer.

      - **Windows:** open the **Miniforge Prompt** (or **Miniforge PowerShell
        Prompt**) from the Start menu.
      - **macOS / Linux:** open your normal terminal app (Terminal.app, iTerm2,
        GNOME Terminal, ...). Miniforge's installer will offer to set up
        ``conda`` automatically; if you skipped that, follow the activation
        instructions printed at the end of the installer.

2. **Create a TRex environment.** In the terminal, run:

   .. code-block:: bash

      conda create -n track -c trexing trex

3. **Activate the environment.** Every time you open a new terminal and want
   to use |trex|, run:

   .. code-block:: bash

      conda activate track

4. **Launch TRex.** With the environment activated:

   .. code-block:: bash

      trex

That's it — you should now see the |trex| welcome screen. If anything goes
wrong, check the `TRex website <https://trex.run>`_ or the
`GitHub repository <https://github.com/mooch443/trex>`_ for support.

Download the workshop dataset
-----------------------------

We'll use a small set of example videos during the workshop. Please download
them ahead of time and save them somewhere you can find again on your laptop:

- `Example videos for multi-object tracking <https://doi.org/10.17617/3.7F5MGE>`_
  — multi-individual videos used in :doc:`tutorials` and
  :doc:`3-create-custom-model`.

You can also browse and watch the
`TRex YouTube channel <https://www.youtube.com/@TRexTracker>`_ in advance to
get a feel for the interface before the workshop.

After tracking: analysis resources
----------------------------------

Once you've tracked a video with |trex|, the exported data (npz / csv) is
straightforward to load and analyze in Python. We've prepared notebooks and
example code to get you started:

- `TRex Analysis Notebooks on Colab <https://colab.research.google.com/drive/1vvFPMWrHlLsnPOul8LdsmYqbmy-Y6sWp?usp=sharing>`_
  — run them directly in your browser, no local setup required.
- `TRex-tutorials-data on GitHub <https://github.com/albiangela/TRex-tutorials-data>`_
  — example datasets, pre-trained YOLO models, a Colab notebook for training
  your own model, and the source for these tutorials.
