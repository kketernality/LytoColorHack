import time
import math
import numpy as np
import cv2
from PIL import ImageGrab
import pyautogui

# Flag to control program to do auto-gaming
autoGaming = False
autoGamingMs = 200

# How many many milliseconds between two frames
frameMs = 33
maxNumDrawing = 100

# Create a flexible window to display
cv2.namedWindow('Window', cv2.WINDOW_NORMAL)
screen = np.asarray(ImageGrab.grab())

# Identify main screen resolution
if len(screen.shape) == 3:
    h, w, c = screen.shape
elif len(screen.shape) == 2:
    h, w = screen.shape
else:
    raise ValueError('Unknown screen resolution')

# Ratio of game screen over the left half screen
gameLeftRatio = 0.28
gameRightRatio = 0.28
gameTopRatio = 0.45
gameBottomRatio = 0.15

crop_x1 = int(gameLeftRatio * (w // 2))
crop_x2 = (w // 2) - int(gameRightRatio * (w // 2))
crop_y1 = int(gameTopRatio * h)
crop_y2 = h - int(gameBottomRatio * h)

# Ratio of display window over the crop region
displayRatio = 1.0
crop_w = abs(crop_x2 - crop_x1) + 1
crop_h = abs(crop_y2 - crop_y1) + 1
windowSize = (int(displayRatio * crop_w), int(displayRatio * crop_h))
cv2.resizeWindow('Window', windowSize)

maxRadius = int(crop_w / 3.5)
minRadius = int(crop_w / 20)

print("Crop window: [{}, {}], size: [{}, {}]".format(crop_x1, crop_y1, crop_w, crop_h))

# Variable for auto-gaming
lastAutoGameTime = time.time()

while True:
    beginTime = time.time()
    screen = np.asarray(ImageGrab.grab())

    screen = screen[crop_y1:crop_y2, crop_x1:crop_x2, :]
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

    # Using OpenCV to find circles in screen
    # CirclesRaw.shape -> (1, numCircles, 3)
    circlesRaw = cv2.HoughCircles(cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY),
                                  cv2.HOUGH_GRADIENT, 1.5, 8,
                                  param1=100, param2=80,
                                  minRadius=minRadius, maxRadius=maxRadius)

    # Restructure as Python list for easier manipulation
    if circlesRaw is not None:
        circles = [(x, y, radius) for (x, y, radius) in circlesRaw[0, :]]
    else:
        circles = []

    # Filter out partially out-of-boundary circles
    valids = []
    for idx, (x, y, radius) in enumerate(circles):
        out_of_boundary = (x - radius < 0)        \
                       or (x + radius >= crop_w)  \
                       or (y - radius < 0)        \
                       or (y + radius >= crop_h)
        valids.append(not out_of_boundary)
    circles = [circle for valid, circle in zip(valids, circles) if valid]

    # Non-max suppression on overlapped circles
    numCircles = len(circles)
    isSuppressed = [False] * numCircles
    for itsIdx in range(numCircles):
        if isSuppressed[itsIdx]:
            continue
        for otherIdx in range(itsIdx + 1, numCircles):
            if isSuppressed[otherIdx]:
                continue
            # Unpack values of its and other's circle
            it_x, it_y, it_radius = circles[itsIdx]
            other_x, other_y, other_radius = circles[otherIdx]
            # Distance between two circles
            distance = math.sqrt((it_x - other_x) ** 2 + (it_y - other_y) ** 2)
            # Adopt a very simple criteria for circle NMS
            if distance < 0.8 * max(it_radius, other_radius):
                if other_radius <= it_radius:
                    isSuppressed[otherIdx] = True
                else:
                    isSuppressed[itsIdx] = True
    circles = [circle for isSup, circle in zip(isSuppressed, circles) if not isSup]

    # Find out the color for each circle
    circleColors = []
    for (x, y, radius) in circles:
        # Coordinates of the inner rectangle inside the circle
        x1 = int(x - 0.5 * radius)
        x2 = int(x + 0.5 * radius)
        y1 = int(y - 0.5 * radius)
        y2 = int(y + 0.5 * radius)

        # Color of circle is the mean color of the rectangle
        color = screen[y1:y2, x1:x2, :].mean(axis=(0, 1))
        circleColors.append(color)

    # Find the circle with the most different color with the others
    circleDistances = []
    numCircles = len(circles)
    for itsIdx in range(numCircles):
        distanceSum = 0.0
        for otherIdx in range(numCircles):
            if itsIdx == otherIdx:
                continue
            itsColor = circleColors[itsIdx]
            otherColor = circleColors[otherIdx]
            distance = math.sqrt((itsColor[0] - otherColor[0]) ** 2 +
                                 (itsColor[1] - otherColor[1]) ** 2 +
                                 (itsColor[2] - otherColor[2]) ** 2)
            distanceSum += distance
        circleDistances.append(distanceSum)

    if numCircles > 0:
        maxIdx = np.argmax(circleDistances)
    else:
        maxIdx = -1

    # Draw all identified circle on the screen
    for idx, (x, y, radius) in enumerate(circles):
        if idx > maxNumDrawing:
            break

        if idx == maxIdx:
            # Fill the circle with white color
            cv2.circle(screen, (x, y), radius, (255, 255, 255), -1, 8, 0)
            # Draw the boundary of the circle
            cv2.circle(screen, (x, y), radius, (0, 0, 255), 2, 8, 0)
        else:
            # Draw the center point of the circle
            cv2.circle(screen, (x, y), 3, (15, 230, 15), -1, 8, 0)
            # Draw the boundary of the circle
            cv2.circle(screen, (x, y), radius, (15, 230, 15), 2, 8, 0)

    # Auto-gaming logic
    if autoGaming and maxIdx >= 0:
        currentTime = time.time()
        if 1000.0 * (currentTime - lastAutoGameTime) > autoGamingMs:
            max_x, max_y, _ = circles[maxIdx]
            prevMouse = pyautogui.position()
            pyautogui.click(x=(crop_x1 + max_x), y=(crop_y1 + max_y))
            pyautogui.moveTo(*prevMouse)
            # Stay focus/active on the OpenCV window for we will miss the
            # keyboard event if we don't focus on the window
            pyautogui.click(*prevMouse)
            lastAutoGameTime = time.time()

    # Processing time of this frame
    endTime = time.time()
    procMs = 1000.0 * (endTime - beginTime)
    waitMs = max(int(frameMs - procMs), 1)  # 0 means wait indefinitely

    # Display processing time of each frame
    cv2.putText(screen, '{:.2f} ms'.format(procMs),
                (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 1, cv2.LINE_AA)

    cv2.imshow('Window', screen)

    key = cv2.waitKey(waitMs)
    if key == 27:
        break
    elif key == ord('s'):
        if autoGaming:
            print('Stop auto-gaming')
            autoGaming = False
        else:
            print('Start auto-gaming')
            autoGaming = True

cv2.destroyAllWindows()
