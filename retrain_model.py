import os
import cv2
import numpy as np

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
labels = []

dataset_path = "dataset"

label_map = {}
current_label = 0

for user in sorted(os.listdir(dataset_path)):

    user_path = os.path.join(dataset_path, user)

    if not os.path.isdir(user_path):
        continue

    label_map[current_label] = user

    for img_name in sorted(os.listdir(user_path)):
        img_path = os.path.join(user_path, img_name)

        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            continue

        faces.append(img)
        labels.append(current_label)

    current_label += 1

if len(faces) == 0:
    print("No faces found. Skipping training.")
    exit()

recognizer.train(faces, np.array(labels))
recognizer.save("trainer.yml")

with open("labels.txt", "w") as f:
    for k, v in label_map.items():
        print(f"Label {k} -> {v}")
        f.write(f"{k},{v}\n")

print("✅ Training complete")