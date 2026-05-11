# Learnings & Challenges
 
Engineering diary — honest log of what failed, what worked, and why.
 
---
 
## Calibration
 
### Issue: RMS error > 1.0 px
- **Cause:** Checkerboard printed on non-flat / wrinkled paper
- **Fix:** Use rigid board, print on cardboard, avoid glare from lighting
 
### Issue: `findChessboardCorners` always returns False
- **Cause:** Lighting too harsh or too dark
- **Fix:** Use diffuse lighting, avoid direct light on board
 
### Note on fisheye model
- Use `cv2.fisheye.calibrate()` — NOT `cv2.calibrateCamera()`
- Fisheye uses Kannala-Brandt model: 4 distortion coefficients (k1, k2, k3, k4)
- Standard pinhole has 5 coefficients — incompatible with fisheye
 
---
 
## Environment (Jetson Nano)
 
### OpenCV installation
- Install opencv-contrib for fisheye support
- On Jetson, prefer: `pip3 install opencv-contrib-python`
- Or build from source for CUDA support
 
---
 
*Add new entries as you encounter issues during development*
