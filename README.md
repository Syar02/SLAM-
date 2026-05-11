# fisheye-stereo-slam
 
> Pseudo-stereo Visual SLAM pipeline using a single fisheye camera on NVIDIA Jetson Nano.
 
**One fisheye lens → calibration → virtual left/right stereo pair → ORB-SLAM3**
 
![Status](https://img.shields.io/badge/status-in%20progress-yellow)
![Platform](https://img.shields.io/badge/platform-Jetson%20Nano-green)
![Language](https://img.shields.io/badge/language-Python%203-blue)
 
---
 
## Motivation
 
True stereo vision requires two physically separated cameras with a known baseline.
A fisheye camera wide FOV (≥160°) allows synthesizing two virtual "eyes" from a
single frame  the horizontal offset between crops acts as the virtual baseline.
 
Useful when:
- Only one camera is available on the robot
- Wide FOV is needed for navigation (indoor, corridor environments)
- Weight or mounting constraints prevent dual-camera setup
 
---
 
## Hardware
 
| Component | Spec |
|-----------|------|
| Main board | NVIDIA Jetson Nano 4GB |
| Camera | USB Fisheye, FOV ≥ 160° |
| OS | Ubuntu 20.04 (JetPack 4.6) |
 
---
 
## Requirements
 
```bash
pip3 install -r requirements.txt
```
 
---
 
## Usage
 
### Step 1 — Capture calibration frames
Print checkerboard (9×6, 25mm squares) on a flat rigid board.
```bash
python3 calibration/capture_calib.py --camera 0 --output kalibr_data/
```
Press `SPACE` to capture, `Q` to quit. Collect minimum 20 frames.
 
### Step 2 — Calibrate
```bash
python3 calibration/calibrate_webcam.py \
    --folder kalibr_data/ \
    --rows 6 --cols 9 --square 0.025
```
Target RMS: **< 0.5 px**. Acceptable: < 1.0 px.
 
### Step 3 — Verify
```bash
python3 calibration/cek_pose.py \
    --params kalibr_data/camera_params.yaml --camera 0
```
 
### Step 4 — Extract frames
```bash
python3 calibration/extract_frames.py --input video.mp4 --output frames/ --fps 5
```
 
### Step 5 — Report
```bash
python3 calibration/generate_report.py --params kalibr_data/camera_params.yaml
```
 
---
 
## Project structure
 
```
fisheye-stereo-slam/
├── calibration/
│   ├── capture_calib.py
│   ├── calibrate_webcam.py
│   ├── cek_pose.py
│   ├── extract_frames.py
│   └── generate_report.py
├── kalibr_data/               Calibration images + output YAML
├── docs/
│   └── learnings.md           Engineering diary
├── requirements.txt
├── LICENSE
└── README.md
```
 
 
## References
 
- [ORB-SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) — Campos et al., 2021
- [DSO](https://github.com/JakobEngel/dso) — Engel et al., 2018
- OpenCV fisheye model — Kannala & Brandt, 2006
 
---
 
*Tested on NVIDIA Jetson Nano · Bengkulu, Indonesia*
