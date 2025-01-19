import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Could not open video device")
else:
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Could not read frame")
            break

cap.release()
cv2.destroyAllWindows()
