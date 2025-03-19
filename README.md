# People Tracking with YOLO and ByteTrack

This project tracks people using the YOLO algorithm, counting individuals who pass through a marked area. It can be applied to situations like counting people moving up and down stairs in a predefined area and tracking their paths.

# Demo

https://github.com/nguyenhoangtamm/People-Tracking/videos/predicition_output/count_in_zone/output.avi

## Table of Contents

-   [Description](#description)
-   [Working](#Working)
-   [Installation](#installation)
-   [Usage](#usage)
-   [Features](#features)
-   [Limitation](#Limitation)
-   [Bibliography](#Bibliography)

## Description

This project utilizes the YOLO (You Only Look Once) object detection algorithm combined with the ByteTrack multi-object tracking algorithm to monitor and count people passing through a marked area. It can be applied to scenarios such as counting individuals moving up and down stairs within a predefined zone and tracking their paths.

## Working:

1. **Read Video**:

    - The script starts by selecting a video file using the `choose_video` function. If no video is selected, the script exits.

2. **Load YOLO Model**:

    - The YOLO model is loaded from the specified path in the configuration file.

3. **Open Video**:

    - The selected video is opened using OpenCV's `VideoCapture`. The video dimensions and frame rate are retrieved.

4. **Select Region**:

    - The user is prompted to select a region of interest in the video by clicking on the video frame. The selected region is used to create a mask.

5. **Create Mask**:

    - A mask is created based on the selected region. This mask is used to determine if a detected person is within the region.

6. **Process Video Frames**:

    - The video frames are processed in a loop. For each frame:
        - The YOLO model detects objects in the frame.
        - The detected objects are tracked using ByteTrack.
        - If a detected person is within the selected region, their ID is noted, and their image is saved.

7. **Save Results**:

    - The processed video frames are saved to an output video file. Detected persons within the region are saved as images.

8. **Display Results**:
    - The processed video frames are displayed in a window. The script continues to process frames until the video ends or the user exits.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/nguyenhoangtamm/People-Tracking.git
    cd People-Tracking
    ```

2. Create and activate a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    source venv/bin/activate  # On macOS/Linux
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Prepare your input video or camera feed.
2. Update your path for video, mask, and out in config.json
3. Run the main tracking script:
    ```bash
    python main.py
    ```
4. View the results and counters in the console output or as specified in the configuration.
5. Your video is saved in videos/predicition_output/

## Features

-   Person detection using YOLO
-   Multi-object tracking with ByteTrack
-   Direction-based counting
-   Easy configuration and customization

## Limitation

-   The logic may need tuning as it sometimes misses counting a person.
-   Overlapping people can cause tracking issues.
-   Simultaneous movement of two people can result in missed counts; strategic camera placement is required.
-   Real-time processing requires a GPU.

## Bibliography

-   YOLO Model: [https://github.com/WongKinYiu/yolov9](https://github.com/WongKinYiu/yolov9)
-   ByteTrack Algorithm: [https://medium.com/tech-blogs-by-nest-digital/object-tracking-object-detection-tracking-using-bytetrack-0aafe924d292](https://medium.com/tech-blogs-by-nest-digital/object-tracking-object-detection-tracking-using-bytetrack-0aafe924d292)
-   Ultralytics: [https://docs.ultralytics.com/modes/track/](https://docs.ultralytics.com/modes/track/)
