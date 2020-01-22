import cv2
from cv2 import ximgproc
import imutils
import numpy as np

from wireframe2code import driver


class Capture:

    def __init__(self, image):
        height, width, _ = image.shape
        if width > 500:
            image = imutils.resize(image, width=500)
        self.image = image

    def __preprocess(self):
        grayscaled = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        driver.show_image("Grayscaled", grayscaled)

        blurred = cv2.GaussianBlur(grayscaled, (5, 5), 0)
        driver.show_image("Blurred", blurred)

        thresholded = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)[1]
        driver.show_image("Thresholded", thresholded)

        dilated = cv2.dilate(thresholded, kernel=None, iterations=1)
        driver.show_image("Dilated", dilated)

        thinned = ximgproc.thinning(dilated, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)
        driver.show_image("Thinned", thinned)

        return dilated

    def contours(self):
        image = self.__preprocess()
        contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        return contours
