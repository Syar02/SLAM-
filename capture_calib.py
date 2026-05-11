import cv2
import os
import time
import numpy as np

# ─── Konfigurasi ──────────────────────────────────────────────────────────────
CAMERA_INDEX  = 0
WIDTH         = 640
HEIGHT        = 480
SAVE_DIR      = os.path.expanduser("/home/syar/data/turtlebot/kalibr_data/images_fisheye")
TARGET_FRAMES = 50        # lebih banyak untuk fisheye
CHECKERBOARD  = (8, 5)    # inner corners — sesuaikan dengan checkerboard kamu
MIN_INTERVAL  = 1.5       # detik minimum antar frame (hindari pose mirip)
# ─────────────────────────────────────────────────────────────────────────────

os.makedirs(SAVE_DIR, exist_ok=True)

# Hapus gambar lama jika ada
old_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.png')]
if old_files:
    print(f"  Menghapus {len(old_files)} gambar lama dari {SAVE_DIR}...")
    for f in old_files:
        os.remove(os.path.join(SAVE_DIR, f))

cap = cv2.VideoCapture(CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_AUTOFOCUS,    0)     # matikan autofocus
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)    # auto exposure boleh aktif

if not cap.isOpened():
    print(f"[ERROR] Kamera index {CAMERA_INDEX} tidak ditemukan.")
    exit(1)

# Warm up kamera
for _ in range(10):
    cap.read()

print("=" * 60)
print("  CAPTURE KALIBRASI KAMERA FISHEYE")
print("=" * 60)
print(f"  Resolusi  : {WIDTH}x{HEIGHT}")
print(f"  Simpan ke : {SAVE_DIR}")
print(f"  Target    : {TARGET_FRAMES} frame")
print("-" * 60)
print("  SPASI  = simpan (jika checkerboard terdeteksi)")
print("  S      = simpan paksa")
print("  Q      = keluar")
print("-" * 60)
print("  TIPS FISHEYE:")
print("  - Checkerboard HARUS terlihat DATAR (tempel di papan keras)")
print("  - Pastikan SELURUH checkerboard masuk frame")
print("  - Gerakkan PERLAHAN, jangan blur")
print("  - Variasikan: kiri, kanan, atas, bawah, miring 45 derajat")
print("=" * 60)

count       = 0
flash_timer = 0
last_save   = 0

# Kriteria subpix — lebih ketat untuk fisheye
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)

# Flag deteksi fisheye — lebih agresif
detect_flags = (
    cv2.CALIB_CB_ADAPTIVE_THRESH +
    cv2.CALIB_CB_NORMALIZE_IMAGE +
    cv2.CALIB_CB_FAST_CHECK
)

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Gagal baca frame.")
        break

    # Untuk fisheye: enhance contrast dulu agar deteksi lebih mudah
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_eq = cv2.equalizeHist(gray)   # equalize histogram

    display = frame.copy()

    # Coba deteksi di gray biasa dulu, fallback ke equalized
    found, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, detect_flags)
    if not found:
        found, corners = cv2.findChessboardCorners(gray_eq, CHECKERBOARD, detect_flags)

    now = time.time()
    cooldown_ok = (now - last_save) >= MIN_INTERVAL

    if found:
        # SubPix refinement dengan window kecil (cocok untuk fisheye distortion)
        corners2 = cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), criteria)
        cv2.drawChessboardCorners(display, CHECKERBOARD, corners2, found)

        if cooldown_ok:
            status_color = (0, 220, 0)
            status_text  = "TERDETEKSI — tekan SPASI untuk simpan"
        else:
            sisa = MIN_INTERVAL - (now - last_save)
            status_color = (0, 200, 200)
            status_text  = f"Tunggu {sisa:.1f}s sebelum simpan berikutnya..."
    else:
        status_color = (0, 100, 220)
        status_text  = "Arahkan ke checkerboard (pastikan seluruh board terlihat)"

    # Flash saat simpan
    if now - flash_timer < 0.2:
        cv2.rectangle(display, (0, 0), (WIDTH, HEIGHT), (255, 255, 255), 25)

    # Tampilkan preview gray equalized di sudut (bantu debug)
    mini = cv2.cvtColor(cv2.resize(gray_eq, (120, 90)), cv2.COLOR_GRAY2BGR)
    display[HEIGHT-95:HEIGHT-5, WIDTH-125:WIDTH-5] = mini
    cv2.putText(display, "enhanced",
                (WIDTH-122, HEIGHT-7), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180,180,180), 1)

    # Progress bar
    progress = int((count / TARGET_FRAMES) * (WIDTH - 20))
    cv2.rectangle(display, (10, HEIGHT-22), (WIDTH-10, HEIGHT-8),  (40, 40, 40), -1)
    cv2.rectangle(display, (10, HEIGHT-22), (10+progress, HEIGHT-8), (0, 200, 100), -1)

    # Status bar atas
    cv2.rectangle(display, (0, 0), (WIDTH, 36), (0, 0, 0), -1)
    cv2.putText(display, status_text,
                (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1, cv2.LINE_AA)

    # Counter
    cv2.rectangle(display, (0, HEIGHT-42), (WIDTH-130, HEIGHT-24), (0, 0, 0), -1)
    cv2.putText(display, f"Tersimpan: {count}/{TARGET_FRAMES}",
                (8, HEIGHT-28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)

    cv2.imshow("Fisheye Calibration Capture  |  SPASI=simpan  S=paksa  Q=keluar", display)

    key = cv2.waitKey(1) & 0xFF

    if key == ord(' '):
        if found and cooldown_ok:
            fname = os.path.join(SAVE_DIR, f"frame_{count:04d}.png")
            cv2.imwrite(fname, frame)   # simpan frame ASLI (bukan equalized)
            count      += 1
            flash_timer = now
            last_save   = now
            print(f"  [{count:02d}/{TARGET_FRAMES}] Disimpan: {fname}")
        elif not found:
            print("  [!] Checkerboard tidak terdeteksi")
        else:
            print("  [!] Terlalu cepat — tunggu sebentar")

    elif key == ord('s'):
        fname = os.path.join(SAVE_DIR, f"frame_{count:04d}.png")
        cv2.imwrite(fname, frame)
        count      += 1
        flash_timer = now
        last_save   = now
        print(f"  [{count:02d}/{TARGET_FRAMES}] Disimpan paksa: {fname}")

    elif key == ord('q'):
        break

    if count >= TARGET_FRAMES:
        print(f"\n[OK] Target {TARGET_FRAMES} frame tercapai!")
        break

cap.release()
cv2.destroyAllWindows()

print("\n" + "=" * 60)
print(f"  Total tersimpan : {count} frame")
print(f"  Lokasi          : {SAVE_DIR}")
print()
if count < 20:
    print("  [!] Kurang — ulangi dengan lebih banyak pose")
elif count < 35:
    print("  [OK] Cukup untuk kalibrasi dasar")
else:
    print("  [BAGUS] Jumlah ideal untuk kalibrasi fisheye akurat")
print()
print("  Langkah berikutnya:")
print("  Ganti IMAGE_DIR di calibrate_fisheye.py ke:")
print(f"  {SAVE_DIR}")
print("=" * 60)