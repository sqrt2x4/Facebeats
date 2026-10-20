from picamera2 import Picamera2
import cv2
import os
import sys
import time

name = sys.argv[1]

dataset_path = f"dataset/{name}"
os.makedirs(dataset_path, exist_ok=True)

face_cascade = cv2.CascadeClassifier(
    "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
)

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

count = 0
MAX_IMAGES = 10

time.sleep(2)

while count < MAX_IMAGES:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        file_path = f"{dataset_path}/{count}.jpg"
        cv2.imwrite(file_path, face)

        print("Saved:", file_path)
        count += 1

    cv2.imshow("Capturing", frame)

    if cv2.waitKey(1) == 27:
        break

picam2.stop()
cv2.destroyAllWindows()