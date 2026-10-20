from picamera2 import Picamera2
import cv2

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

labels = {}

with open("labels.txt", "r") as f:
    for line in f:
        label, name = line.strip().split(",")
        labels[int(label)] = name

face_cascade = cv2.CascadeClassifier(
    "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
)

picam2 = Picamera2()

picam2.configure(
    picam2.create_preview_configuration(
        main={"size": (640, 480)}
    )
)
picam2.start()

recognized_name = None
candidate = None
hits = 0

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5
    )

    
    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        label, confidence = recognizer.predict(face)
        if confidence < 90:

            name = labels[label]

            if name == candidate:
                hits += 1
            else:
                candidate = name
                hits = 1

            print(name, confidence, hits)

            if hits >= 5:

                with open("current_user.txt", "w") as f:
                    f.write(name)

                print("✅ Recognized:", name)

                picam2.stop()
                cv2.destroyAllWindows()

                raise SystemExit

    # If a user was recognized and we broke the for-loop, break the while-loop too
    if recognized_name:
        break

    cv2.imshow("FaceBeats Recognition", frame)

    if cv2.waitKey(1) == 27:
        break

picam2.stop()
cv2.destroyAllWindows()