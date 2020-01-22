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

        python center.py --image shapes_and_colors.png

    """
    # Image has to be resized for better approximation and performance
    image = cv2.imread(args.filename)
    image = imutils.resize(image, width=500)

    capture = paper.Capture(image)
    contours = capture.contours(predicate=lambda contour: cv2.arcLength(contour, True) >= 100)

    for contour in contours:
        x, y = segment.find_center(contour)
        vertices_count = segment.count_vertices(contour)

        # Draw outline
        cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)

        # Draw vertices count
        cv2.putText(image, str(vertices_count), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Draw bounding rectangles
        # x, y, w, h = segment.bounding_rectangle(contour)
        # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    show_image("Image", image)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--filename", required=True, help="Path to input image")
    parsed_args, unparsed_args = parser.parse_known_args()
    main(parsed_args)