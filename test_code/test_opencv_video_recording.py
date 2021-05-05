# -*-coding: utf-8 -*-

import cv2

cap = cv2.VideoCapture(0)

width = int(cap.get(3))
height =  int(cap.get(4))

print(width)
print(height)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (width, height))

while True:
    ret, frame = cap.read()

    if ret:
        out.write(frame)

        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
out.release()
cv2.destroyAllWindows()