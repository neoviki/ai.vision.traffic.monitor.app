# AI Traffic Monitor – Intelligent Traffic Monitoring with Object Detection and Counting

**AI Traffic Monitor** is a Convolutional Neural Network (CNN) based computer vision application that detects and counts traffic-related objects (such as cars, trucks, buses, and pedestrians) in images, videos, or live camera feeds, and displays the results in a tabular format.

It uses the YOLOv8 object detection model - a pretrained deep CNN by Ultralytics [1] - to analyze each frame and generate structured traffic object counts and visual overlays.

---

## Demo

![Demo](demo.gif)

---

## Features

* Detects traffic-related objects, including:
  - Person
  - Bicycle
  - Car
  - Motorcycle
  - Bus
  - Truck
  - Train
  - (and other common road objects)

* Keyboard shortcuts
  - `Esc` or `q`        : Quit the application gracefully
  - `Back to Menu`      : Switch between modes without restarting

---

## Installation

```bash
git clone https://github.com/neoviki/ai.vision.traffic.monitor.app
cd ai.traffic.monitor
chmod +x installer.sh;./installer.sh
```

To **uninstall**, run:

```bash
chmod +x uninstaller.sh;./uninstaller.sh
```

---

## Usage

### 1. Launch the Application

```bash
ai.traffic.monitor
```

### 2. Choose a Mode

| Mode               | Description                                       |
| ------------------ | ------------------------------------------------- |
| **Image Mode**     | Detect objects in a single image                  |
| **Video Mode**     | Process a video file frame-by-frame               |
| **Live Mode**      | Analyze webcam feed with periodic frame detection |

### 3. View Results

* Left side: Original input image/frame
* Right side: AI Processed output with bounding boxes
* Bottom: Object counter table
* Top-right: Current time and date

### 4. Key Controls

| Key / Button   | Action                              |
|----------------|-------------------------------------|
| `Esc` or `q`   | Quit application                    |
| `Space`        | Pause or resume video playback      |

---

## Tested Systems

| OS                      | Python Version | Dependencies                           | CPU                              | RAM    | 
|-------------------------|----------------|----------------------------------------|----------------------------------|--------|
| Ubuntu 24.04 LTS        | 3.12           | OpenCV, Pillow, Tkinter, YOLOv8        | Intel Core i7-1165G7 @ 2.80 GHz  | 16 GB  | 
---

## References

* [1] [Ultralytics YOLOv8 Documentation](https://docs.ultralytics.com/models/yolov8/)
* [2] [Ultralytics GitHub Repository](https://github.com/ultralytics/ultralytics)
* [3] Video by [German Korb](https://www.pexels.com/video/road-systems-in-montreal-canada-for-traffic-management-of-motor-vehicles-3727445/) on Pexels
* [4] Image by [TRANG NGUYEN](https://pixabay.com/users/thelegendreturn-24390146/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=6810885) from [Pixabay](https://pixabay.com/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=6810885)

---

**Developed using OpenCV, Tkinter, and YOLOv8**

