from wireframe2code import segment
from wireframe2code import paper
import imutils
import argparse
import cv2


def show_image(title, image):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyWindow(title)


def main(args):
    """
    Example usage::

        python driver.py --image shapes_and_colors.png

    """
    # Image has to be resized for better approximation and performance
    image = cv2.imread(args.filename)
    image = imutils.resize(image, width=500)

    capture = paper.Capture(image)
    contours = capture.contours(predicate=lambda contour: cv2.arcLength(contour, True) >= 100)

    for contour in contours:
        if not segment.is_square(contour):
            continue

        cv2.drawContours(image, [contour], -1, (255, 0, 0), 2)
        show_image("Image", image)

        # Draw bounding rectangles
        # x, y, w, h = segment.bounding_rectangle(contour)
        # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--filename", required=True, help="Path to input image")
    parsed_args, unparsed_args = parser.parse_known_args()
    main(parsed_args)