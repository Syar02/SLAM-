import cv2
import numpy as np
import glob
import os

# ─── Konfigurasi ──────────────────────────────────────────────────────────────
CHECKERBOARD = (8, 5)     # inner corners
SQUARE_SIZE  = 0.025      # meter
IMAGE_DIR    = os.path.expanduser("~/data/turtlebot/kalibr_data/images_webcam")
OUTPUT_DIR   = os.path.expanduser("~/data/turtlebot/kalibr_data")
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("  RE-CALIBRATION: WEBCAM PINHOLE (FIX K3)")
print("=" * 60)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)

objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

objpoints = [] 
imgpoints = [] 

images = sorted(glob.glob(os.path.join(IMAGE_DIR, "*.png")))
img_size = None
valid = 0

print(f"  Memproses {len(images)} gambar...")

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if img_size is None:
        img_size = (gray.shape[1], gray.shape[0])

    # Gunakan flag tambahan agar deteksi lebih ketat
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, 
        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FILTER_QUADS)

    if ret:
        objpoints.append(objp)
        # Window 11x11 untuk akurasi tinggi pada pinhole
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        valid += 1
        print(f"  [OK] {os.path.basename(fname)}")
    else:
        print(f"  [FAIL] {os.path.basename(fname)}")

if valid < 15:
    print(f"\n[ERROR] Hanya {valid} gambar valid. Hasil tidak akan akurat!")
    exit(1)

# ─── Bagian yang Diperbaiki (Menambahkan Flags) ──────────────────────────────
print("\n  Menghitung intrinsik (mengunci K3 agar RMS lebih kecil)...")

# CALIB_FIX_K3: Sangat penting untuk webcam murah agar distorsi tidak 'liar'
# CALIB_FIX_PRINCIPAL_POINT: Opsional, tapi kita biarkan dulu agar cx, cy bisa terhitung
flags = cv2.CALIB_FIX_K3 

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, img_size, None, None, flags=flags
)
# ─────────────────────────────────────────────────────────────────────────────

fx, fy = mtx[0, 0], mtx[1, 1]
cx, cy = mtx[0, 2], mtx[1, 2]
d = dist.ravel()
# Karena K3 difixed, nilainya akan menjadi 0 atau sangat stabil
k1, k2, p1, p2, k3 = d[0], d[1], d[2], d[3], d[4]

print("\n" + "=" * 60)
print(f"  RMS ERROR: {ret:.4f} px")
if ret > 0.7:
    print("  STATUS   : MASIH TINGGI. Disarankan foto ulang dengan papan kaku.")
else:
    print("  STATUS   : BAGUS. Siap digunakan.")
print("=" * 60)

# Generate YAML
yaml_content = f"""%YAML:1.0
---
Camera.type: "PinHole"

Camera.fx: {fx:.6f}
Camera.fy: {fy:.6f}
Camera.cx: {cx:.6f}
Camera.cy: {cy:.6f}

# Distortion parameters [k1, k2, p1, p2, k3]
Camera.k1: {k1:.8f}
Camera.k2: {k2:.8f}
Camera.p1: {p1:.8f}
Camera.p2: {p2:.8f}
Camera.k3: {k3:.8f}

Camera.width:  {img_size[0]}
Camera.height: {img_size[1]}
Camera.fps: 30.0
Camera.RGB: 1

ORBextractor.nFeatures: 1000
ORBextractor.scaleFactor: 1.2
ORBextractor.nLevels: 8
ORBextractor.iniThFAST: 20
ORBextractor.minThFAST: 7

Viewer.KeyFrameSize: 0.05
Viewer.KeyFrameLineWidth: 1
Viewer.GraphLineWidth: 0.9
Viewer.PointSize: 2
Viewer.CameraSize: 0.08
Viewer.CameraLineWidth: 3
Viewer.ViewpointX: 0
Viewer.ViewpointY: -0.7
Viewer.ViewpointZ: -1.8
Viewer.ViewpointF: 500
"""

yaml_path = os.path.join(OUTPUT_DIR, "webcam_pinhole.yaml")
with open(yaml_path, "w") as f:
    f.write(yaml_content)

print(f"  YAML disimpan di: {yaml_path}")