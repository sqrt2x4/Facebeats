import os
import cv2
import numpy as np

recognizer = cv2.face.LBPHFaceRecognizer_create()

dataset_path = "dataset"

faces = []
labels = []
label_map = {}
current_id = 0

for root, dirs, files in os.walk(dataset_path):

    for file in files:
        if file.endswith(".jpg") or file.endswith(".png"):

            path = os.path.join(root, file)

            label_name = os.path.basename(root)

            if label_name not in label_map:
                label_map[label_name] = current_id
                current_id += 1

            label_id = label_map[label_name]

            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

            if img is None:
                continue

            faces.append(img)
            labels.append(label_id)

if len(faces) == 0:
    print("❌ No training images found in dataset/")
    exit()

recognizer.train(faces, np.array(labels))

recognizer.save("trainer.yml")

with open("labels.txt", "w") as f:
    for name, id in label_map.items():
        f.write(f"{id},{name}\n")

print("✅ Training complete!")