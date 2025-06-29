import cv2
import numpy as np
import time

# راه‌اندازی دوربین
cap = cv2.VideoCapture(0)
time.sleep(3)

# گرفتن چند فریم برای پس‌زمینه
bg_frames = []
print("[INFO] Capturing background...")

for i in range(60):
    ret, frame = cap.read()
    if not ret:
        continue
    frame = cv2.flip(frame, 1)
    bg_frames.append(frame)

background = np.median(np.array(bg_frames), axis=0).astype(np.uint8)
print("[INFO] Background captured.")

# رنگ جسم نامرئی (مثلاً شنل قرمز)
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

kernel = np.ones((3, 3), np.uint8)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # ساخت ماسک برای قرمز
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    # حذف نویز ماسک
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.GaussianBlur(mask, (7, 7), 0)

    # ماسک معکوس
    mask_inv = cv2.bitwise_not(mask)

    # جایگزینی ناحیه قرمز با پس‌زمینه
    part1 = cv2.bitwise_and(background, background, mask=mask)
    part2 = cv2.bitwise_and(frame, frame, mask=mask_inv)
    result = cv2.addWeighted(part1, 1, part2, 1, 0)

    # نمایش نتیجه
    cv2.imshow("Invisibility Cloak - Pro", result)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
