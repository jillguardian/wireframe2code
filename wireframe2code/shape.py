import cv2
import numpy as np


def find_center(contour):
    moments = cv2.moments(contour)
    x = int(moments["m10"] / moments["m00"])
    y = int(moments["m01"] / moments["m00"])
    return x, y


def find_vertices(contour):
    perimeter = cv2.arcLength(contour, True)
    approximate_curves = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
    return approximate_curves


def count_vertices(contour):
    vertices = find_vertices(contour)
    return len(vertices)


def bounding_rectangle(contours):
    contours = np.concatenate(contours)
    return cv2.boundingRect(contours)
