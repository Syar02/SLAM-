import cv2
import os

# --- KONFIGURASI ---
# Pastikan nama file sesuai dengan yang baru saja kamu rekam
video_path = '/home/syar/my_video-2.mkv'  
output_folder = '/home/syar/data/turtlebot/datasets/my_dataset/data/images4'
# ------------------

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Hapus isi folder lama agar tidak tercampur
import shutil
for filename in os.listdir(output_folder):
    file_path = os.path.join(output_folder, filename)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f'Gagal menghapus {file_path}: {e}')

vidcap = cv2.VideoCapture(video_path)
success, image = vidcap.read()
count = 0

print("Memulai ekstraksi frame...")

while success:
    # Simpan sebagai .jpg (DSO sangat menyukai format ini)
    filename = os.path.join(output_folder, f"frame_{count:05d}.jpg")
    cv2.imwrite(filename, image)     
    success, image = vidcap.read()
    if count % 100 == 0:
        print(f'Sudah mengekstrak {count} gambar...')
    count += 1

print(f"Selesai! {count} gambar tersimpan di {output_folder}")