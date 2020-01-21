import cv2
import imutils


def find_contours(image):
    def preprocess(image):
        grayscaled_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred_image = cv2.GaussianBlur(grayscaled_image, (5, 5), 0)
        thresholded_image = cv2.threshold(blurred_image, 60, 255, cv2.THRESH_BINARY)[1]
        return thresholded_image

    image = preprocess(image)
    contours = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    return contours
