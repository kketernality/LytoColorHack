# LytoColorHack

LytoColorHack is a simple project for fun. 

Use it to automatically play Lyto Different Color Game to beat your pitty friends. :D

## Demostration

[![Auto-Gaming Hack for Lyto Different Color Game](https://img.youtube.com/vi/z-moUBR4lsY/0.jpg)](https://www.youtube.com/watch?v=z-moUBR4lsY "Auto-Gaming Hack for Lyto Different Color Game")

Click the above thumbnail to see demo video on Youtube.  

## Test Environment

This code was developed and tested on the following environment.

* Windows 10 :: 64-bit
* Python 3.6.1 :: Anaconda 4.4.0 (64-bit)

## Dependencies

Python package required for this project can be easily installed via pip:

```
pip install numpy
pip install opencv-python
pip install pillow 
pip install pyautogui
```
## Usage

Open the game and place the browser on the left to fill the left half screen as the demo video shows.

Press `s` to tell the program the game had started and begin auto-gaming.

## Methodology

* Take a screenshot of the left half screen.
* Indentify the circles in the screenshot using Hough in OpenCV.
* Post-process circles: 
  1. Boundary check
  2. Non-max suppression
* Identify the circle with the most different color from the others.
* If auto-gaming is on, simulate mouse to click the circle we identified.
* Display the result on a separate window.
