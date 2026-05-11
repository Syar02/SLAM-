#!/usr/bin/env python3
import cv2
import numpy as np
import glob
import os
import yaml

# ========== KONFIGURASI ==========
# Ubah sesuai pola chessboard Anda (jumlah sudut INTERNAL)
CHESSBOARD_ROWS = 6  # Jumlah baris kotak internal
CHESSBOARD_COLS = 9  # Jumlah kolom kotak internal
# Ukuran satu kotak dalam satuan dunia (misal cm). Tidak terlalu kritis untuk DSO asalkan konsisten.
SQUARE_SIZE = 2.5    
# Folder berisi gambar chessboard
IMAGE_FOLDER = "/home/syar/calib_images"
# =================================

def calibrate_camera():
    # Kriteria terminasi untuk algoritma corner refinement
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # Siapkan object points (3D points of real world chessboard corners)
    objp = np.zeros((CHESSBOARD_ROWS * CHESSBOARD_COLS, 3), np.float32)
    objp[:,:2] = np.mgrid[0:CHESSBOARD_COLS, 0:CHESSBOARD_ROWS].T.reshape(-1,2) * SQUARE_SIZE
    
    objpoints = [] # 3d points in real world space
    imgpoints = [] # 2d points in image plane
    
    images = glob.glob(os.path.join(IMAGE_FOLDER, '*.png')) + \
             glob.glob(os.path.join(IMAGE_FOLDER, '*.jpg'))
    
    print(f"Found {len(images)} images. Starting calibration...")
    
    for fname in images:
        img = cv2.imread(fname)
        if img is None:
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (CHESSBOARD_COLS, CHESSBOARD_ROWS), None)
        
        if ret == True:
            objpoints.append(objp)
            # Refine corner locations for sub-pixel accuracy
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)
            
            # Draw and display corners (opsional, untuk visualisasi)
            # cv2.drawChessboardCorners(img, (CHESSBOARD_COLS, CHESSBOARD_ROWS), corners2, ret)
            # cv2.imshow('img', img)
            # cv2.waitKey(100)
    
    cv2.destroyAllWindows()
    
    if len(objpoints) < 10:
        print(f"ERROR: Only {len(objpoints)} valid chessboard images found. Need at least 10-15.")
        print("Tips: Pastikan pencahayaan baik, chessboard tidak blur, dan variasi sudut cukup.")
        return
    
    # Perform camera calibration
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None)
    
    print("\n" + "="*60)
    print("CALIBRATION RESULTS")
    print("="*60)
    print(f"Reprojection Error: {ret:.4f} (semakin kecil semakin baik, ideal < 0.5)")
    print(f"\nCamera Matrix (Intrinsics):\n{mtx}")
    print(f"\nDistortion Coefficients:\n{dist.ravel()}")
    
    # Extract values for DSO camera.txt
    fx, fy = mtx[0,0], mtx[1,1]
    cx, cy = mtx[0,2], mtx[1,2]
    height, width = gray.shape[::-1]
    
    print("\n" + "-"*60)
    print("COPY-PASTE INI KE file camera.txt DSO:")
    print("-"*60)
    print(f"Pinhole {fx:.1f} {fy:.1f} {cx:.1f} {cy:.1f}")
    print(f"{width} {height}")
    print("-"*60)
    
    # Save results to YAML file for backup
    output_file = os.path.join(IMAGE_FOLDER, "calibration_results.yaml")
    data = {
        'camera_matrix': mtx.tolist(),
        'distortion_coefficients': dist.ravel().tolist(),
        'image_size': (width, height),
        'dso_format': f"Pinhole {fx:.1f} {fy:.1f} {cx:.1f} {cy:.1f}\n{width} {height}"
    }
    with open(output_file, 'w') as f:
        yaml.dump(data, f)
    print(f"\nDetailed results saved to: {output_file}")

if __name__ == "__main__":
    if not os.path.exists(IMAGE_FOLDER):
        print(f"ERROR: Folder {IMAGE_FOLDER} tidak ditemukan!")
        print(f"Silakan buat folder dan isi dengan gambar chessboard (.png/.jpg)")
    else:
        calibrate_camera()