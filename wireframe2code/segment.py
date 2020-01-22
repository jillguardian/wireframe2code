import cv2


def is_square(contour):
    perimeter = cv2.arcLength(contour, True)
    curves = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
    if len(curves) == 4:
        rectangle = cv2.minAreaRect(contour)
        ratio = abs(cv2.contourArea(contour)) / (rectangle[1][0] * rectangle[1][1])
        return ratio > 0.85
    return False


def center(contour):
    moments = cv2.moments(contour)
    x = int(moments["m10"] / moments["m00"])
    y = int(moments["m01"] / moments["m00"])
    return x, y
