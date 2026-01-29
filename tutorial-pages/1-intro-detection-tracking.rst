Introduction to Tracking with TRex
=============================================
If you are new to using TRex for object tracking, start here!
You probably have a specific use case in mind, videos to analyze, and objects to track. 
This guide will help you deciding on the best approach, whether you need to create a custom dataset, or not, and how to get started quickly.

The usual workfow is:

- Collect videos (Recording)
- Detect objects of interest in the videos (using a pre-trained model or background subtraction) (Detection)
- Track the detected objects across frames (Tracking)
- Analyze the tracking results (Analysis)

.. figure:: ./images/TRex-workflow.001.jpeg
   :alt: Short alt text
   :align: center
   :width: 60%

   The way to tracking: typical workflow.

1) Recording
--------------------------------------

Recording quality is the most important factor for good tracking data. 
We don't provide full recording support, but these guidelines help:

- Light: Use as much light as your system allows. If visible light is disruptive, consider infrared (IR) illumination.
- Camera: Dedicated computer-vision cameras (*e.g.*, Basler, Ximea) are ideal, but webcams, GoPros, DSLRs, or phones can work, depending on target size, speed, distance, and lighting.
- Settings help: Knowing aperture, frame rate, exposure time, and focus improves data quality. Frame rate for example is a trade-off: Higher fps captures fast motion but creates larger files.

Example: Walking locusts may be fine at ~10 fps, but you might miss a full jump. Choose fps based on the behaviors you need to resolve.

.. figure:: ./images/TRex-workflow.003b.jpeg
   :alt: Short alt text
   :align: center
   :width: 60%

   Recording fundamentals: ISO, aperture, shutter speed, and frame rate.

.. |DetectionBlue| raw:: html

   <span style="color:orange;">Detection</span>

2) Detection
--------------------------------------
After collecting a video, the next decision to take is how to detect your objects of interest (*e.g.* animals, robots, inanimate objects).
|DetectionBlue| means finding unidentified objects in each single frame of a video—the requirement for the next step: tracking them.


.. figure:: ./images/TRex-workflow.004.jpeg
   :alt: Short alt text
   :align: center
   :width: 60%

   Deteting objects of interest: the prerequisite for tracking.


In TRex, during the detection phase, the recorded video is converted into an optimized file format (.pv extension), which contains all necessary information for tracking.
There are multiple ways of detecting individuals. The most common are background subtraction and using a custom model.

.. raw:: html

   <div style="text-align:center;">
     <video controls playsinline width="640" src="_static/gif_detection_gui.mov"></video>
   </div>


For example if you have a static camera and a high contrast between the objects of interest and the background, background subtraction is a fast and easy way to detect objects.
If your video is more complex (moving camera, low contrast, changing background), a custom model is likely needed.

.. figure:: ./images/TRex-workflow.006.jpeg
   :alt: Short alt text
   :align: center
   :width: 60%

   Comparing two cases that require different methods: background subtraction vs. custom model.

In order to facilitate the decision, we provide a decision tree:

.. figure:: ./images/TRex-workflow.007.jpeg
   :alt: Short alt text
   :align: center
   :width: 60%

   Decision tree: choosing the right detection method.

Examples
=============================================

Here are three example videos showing different detection methods in TRex:


.. raw:: html

   <style>
     .video-slider {display:flex; gap:16px; overflow-x:auto; scroll-snap-type:x mandatory; padding:12px 0;}
     .video-slide  {min-width:340px; scroll-snap-align:start; position:relative;}
     .video-slide video {width:100%; height:200px; border-radius:8px; border:2px solid #ccc;}
     .fs-btn {position:absolute; top:8px; right:8px; padding:6px 8px; border:0; border-radius:6px;
              background:#111; color:#fff; font-size:12px; cursor:pointer; opacity:0.85;}
     .fs-btn:hover {opacity:1;}
   </style>

   <div class="video-slider">
     <div class="video-slide">
       <p><strong>Background subtraction</strong></p>
       <video controls playsinline src="_static/example_bsub_fish.mov"></video>
     </div>
     <div class="video-slide">
       <p><strong>Background subtraction and ML custom model</strong></p>
       <video controls playsinline src="_static/example_ml_loc.mov"></video>
     </div>
     <div class="video-slide">
       <p><strong>ML custom model</strong></p>
       <video controls playsinline src="_static/example_ml_shark.mov"></video>
     </div>
   </div>

   <script>
     document.querySelectorAll('.video-slide video').forEach((video) => {
       const btn = document.createElement('button');
       btn.className = 'fs-btn';
       btn.type = 'button';
       btn.textContent = 'Full screen';
       btn.addEventListener('click', () => {
         if (video.requestFullscreen) {
           video.requestFullscreen();
         } else if (video.webkitEnterFullscreen) {
           video.webkitEnterFullscreen(); // iOS Safari
         }
       });
       video.parentElement.appendChild(btn);
     });
   </script>

- `Background subtraction <https://raw.githubusercontent.com/albiangela/TRex-tutorials-data/main/tutorial-pages/_static/example_bsub_fish.mov>`__
- `Background subtraction + ML custom model <https://raw.githubusercontent.com/albiangela/TRex-tutorials-data/main/tutorial-pages/_static/example_ml_loc.mov>`__
- `ML custom model <https://raw.githubusercontent.com/albiangela/TRex-tutorials-data/main/tutorial-pages/_static/example_ml_shark.mov>`__


.. |Trackinggr| raw:: html

   <span style="color:green;">Tracking</span>

3) Tracking
--------------------------------------

Once the objects of interest are detected in each frame, the next step is to track them across frames.
|TRackinggr| means entities in one frame with entities in a future frame.


.. figure:: ./images/TRex-workflow.015.jpeg
   :alt: Short alt text
   :align: center
   :width: 60%

   Tracking: keep the identity of the detected dinosaurs across frames.