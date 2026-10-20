from picamera2 import Picamera2
import cv2

picam2 = Picamera2()

picam2.configure(
    picam2.create_preview_configuration(
        main={"size": (640, 480)}
    )
)

picam2.start()

while True:

    frame = picam2.capture_array()

    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) == 27:
        break

picam2.stop()
cv2.destroyAllWindows()