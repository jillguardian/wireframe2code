from cv2 import cv2


def is_quadrangle(contour):
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


def centroid(contour):
    """
    :return: the x and y coordinate of the center of a contour
    """
    moments = cv2.moments(contour)
    x = int(moments["m10"] / moments["m00"])
    y = int(moments["m01"] / moments["m00"])
    return x, y


def intersection(rectangle_one, rectangle_two):
    x = max(rectangle_one[0], rectangle_two[0])
    y = max(rectangle_one[1], rectangle_two[1])
    w = min(rectangle_one[0] + rectangle_one[2], rectangle_two[0] + rectangle_two[2]) - x
    h = min(rectangle_one[1] + rectangle_one[3], rectangle_two[1] + rectangle_two[3]) - y
    if w < 0 or h < 0:
        return 0, 0, 0, 0
    return x, y, w, h


def union(rectangle_one, rectangle_two):
    x = min(rectangle_one[0], rectangle_two[0])
    y = min(rectangle_one[1], rectangle_two[1])
    w = max(rectangle_one[0] + rectangle_one[2], rectangle_two[0] + rectangle_two[2]) - x
    h = max(rectangle_one[1] + rectangle_one[3], rectangle_two[1] + rectangle_two[3]) - y
    return x, y, w, h


def is_aligned_horizontally(rectangle_one, rectangle_two):
    # Get top left x-coordinate, y-coordinate, and the width, and height of each contour's bounding rectangle
    x1, y1, w1, h1 = rectangle_one
    x2, y2, h1, h2 = rectangle_two

    # Align both contours vertically
    x2 = x1

    # Compute area of intersection
    # TODO

    # If are of intersection is significant, then they are aligned
    # TODO
    return False


def is_aligned_vertically(contour_one, contour_two):
    # Get top left x-coordinate, y-coordinate, and the width, and height of each contour's bounding rectangle
    x1, y1, w1, h1 = cv2.boundingRect(contour_one)
    x2, y2, h1, h2 = cv2.boundingRect(contour_two)

    # Align both contours horizontally
    y2 = y1
    return False
