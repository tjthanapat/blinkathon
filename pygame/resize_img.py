import cv2
import matplotlib.pyplot as plt
import numpy as np
img = cv2.imread('pygame/car2.png', cv2.IMREAD_UNCHANGED)

scale_percent = 40 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
  
# resize image
resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

cv2.imwrite('pygame/newcar2.png', resized)