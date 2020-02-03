from cv2 import cv2


def centroid(contour):
    """
    :return: the x and y coordinate of the center of a contour
    """
    moments = cv2.moments(contour)
    x = int(moments["m10"] / moments["m00"])
    y = int(moments["m01"] / moments["m00"])
    return x, y


def is_rectangle(contour):
    """
    Determines if the provided contour is a quadrangle.
    A contour is considered a quadrangle when:

    - It has four vertices.
    - Its area occupies a significant percentage of the minimum fitting rectangle for the contour.
      This percentage is specified through `minimum_area_ratio`.

    :return: boolean value indicating whether or not the provided contour is a quadrangle
    """
    perimeter = cv2.arcLength(contour, True)
    epsilon = 0.04 * perimeter
    approximate_curves = cv2.approxPolyDP(contour, epsilon, True)
    if len(approximate_curves) == 4:
        rectangle = cv2.minAreaRect(contour)
        ratio = abs(cv2.contourArea(contour)) / (rectangle[1][0] * rectangle[1][1])
        return ratio >= 0.85
    return False
