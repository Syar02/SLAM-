import cv2, glob, os
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

IMAGE_DIR    = "/home/syar/data/turtlebot/kalibr_data/images_webcam"
CHECKERBOARD = (8, 5)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

images  = sorted(glob.glob(os.path.join(IMAGE_DIR, "*.png")))
centers = []

for fname in images:
    img  = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK)
    if ret:
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        cx = np.mean(corners2[:,:,0])
        cy = np.mean(corners2[:,:,1])
        centers.append((cx, cy))

centers = np.array(centers)
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(centers[:,0], centers[:,1], c='red', s=60, alpha=0.7)
ax.set_xlim(0, 640); ax.set_ylim(480, 0)
ax.set_xlabel("X pixel"); ax.set_ylabel("Y pixel")
ax.set_title(f"Distribusi pusat checkerboard ({len(centers)} frame)\nIdeal: menyebar ke seluruh area frame")
ax.axhline(240, color='gray', linestyle='--', alpha=0.4)
ax.axvline(320, color='gray', linestyle='--', alpha=0.4)
# Bagi frame jadi 3x3 grid, hitung distribusi
grid_count = np.zeros((3,3), int)
for cx, cy in centers:
    col = min(int(cx / (640/3)), 2)
    row = min(int(cy / (480/3)), 2)
    grid_count[row, col] += 1
print("\nDistribusi per zona (3x3 grid):")
print(f"  {grid_count[0]}")
print(f"  {grid_count[1]}")
print(f"  {grid_count[2]}")
print("\nIdeal: setiap zona ada minimal 2-3 foto")
plt.tight_layout()
plt.savefig("/home/syar/pose_distribution.png")
plt.show()
print("\nGambar disimpan ke ~/pose_distribution.png")