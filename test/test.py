import os
import cv2 as cv
import csv
import numpy as np
from pathlib import Path
from mtcnn import MTCNN
import insightface

class FaceEmbeddingGenerator:
    def __init__(self, detector, dataset_path="src/dataset", csv_dir="data_csv"):
        self.detector = detector
        self.facenet = insightface.app.FaceAnalysis(name="buffalo_l")
        self.facenet.prepare(ctx_id=0)  # Dùng GPU. Đổi ctx_id=-1 nếu không có GPU.
        self.dataset_path = dataset_path
        self.csv_dir = csv_dir
        Path(self.csv_dir).mkdir(exist_ok=True)

        self.user_csv = os.path.join(self.csv_dir, "users.csv")
        self.image_csv = os.path.join(self.csv_dir, "images.csv")
        self.embedding_csv = os.path.join(self.csv_dir, "embeddings_arcface.csv")

    def generate_face_embeddings(self):
        try:
            num_folders, num_files = self.count_files()
            print(f"📂 Tìm thấy {num_files} ảnh trong {num_folders} thư mục.")

            is_new_user_file = not Path(self.user_csv).exists()
            is_new_image_file = not Path(self.image_csv).exists()
            is_new_embedding_file = not Path(self.embedding_csv).exists()

            with open(self.user_csv, mode="a", newline="", encoding="utf-8") as user_file, \
                 open(self.image_csv, mode="a", newline="", encoding="utf-8") as image_file, \
                 open(self.embedding_csv, mode="a", newline="", encoding="utf-8") as embedding_file:

                user_writer = csv.writer(user_file)
                image_writer = csv.writer(image_file)
                embedding_writer = csv.writer(embedding_file)

                if is_new_user_file:
                    user_writer.writerow(["id", "name"])
                if is_new_image_file:
                    image_writer.writerow(["id", "filename", "content_type", "file_size", "storage_path"])
                if is_new_embedding_file:
                    embedding_writer.writerow(["id", "vector", "user_id", "image_id"])

                user_id_counter = self.get_next_id(self.user_csv)
                image_id_counter = self.get_next_id(self.image_csv)
                embedding_id_counter = self.get_next_id(self.embedding_csv)

                for root, _, files in os.walk(self.dataset_path):
                    label = os.path.basename(root)
                    if not files:
                        continue

                    print(f"📂 Đọc thư mục: {label}")
                    user_writer.writerow([user_id_counter, label])
                    user_id = user_id_counter
                    user_id_counter += 1

                    count = 0
                    for file in files:
                        file_path = os.path.join(root, file)
                        print(f"  📄 Xử lý: {file_path}")

                        img_bgr = cv.imread(file_path)
                        if img_bgr is None:
                            print(f"⚠️ Lỗi đọc ảnh: {file_path}")
                            continue

                        img_rgb = cv.cvtColor(img_bgr, cv.COLOR_BGR2RGB)
                        faces = self.facenet.get(img_rgb)

                        if faces:
                            emb = faces[0].embedding
                            # Định dạng vector giữ nguyên kiểu "[0.1234, -0.5678, ...]"
                            vector_str = "[" + ", ".join(f"{v:.4f}" for v in emb) + "]"

                            image_writer.writerow([image_id_counter, file, "image/jpeg", os.path.getsize(file_path), file_path])
                            embedding_writer.writerow([embedding_id_counter, vector_str, user_id, image_id_counter])

                            image_id_counter += 1
                            embedding_id_counter += 1
                            count += 1

                            if count == 5:
                                break
                        else:
                            print(f"⚠️ Không phát hiện khuôn mặt trong ảnh: {file_path}")

            return "✅ Dữ liệu đã được lưu vào CSV thành công!"
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return "❌ Đã xảy ra lỗi!"

    def count_files(self):
        num_folders = sum(len(dirs) for _, dirs, _ in os.walk(self.dataset_path))
        num_files = sum(len(files) for _, _, files in os.walk(self.dataset_path))
        return num_folders, num_files

    def get_next_id(self, file_path):
        if not Path(file_path).exists():
            return 1
        with open(file_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)
            rows = list(reader)
        return 1 if not rows else int(rows[-1][0]) + 1

# Chạy thử
ll = FaceEmbeddingGenerator(detector=MTCNN())
ll.generate_face_embeddings()
