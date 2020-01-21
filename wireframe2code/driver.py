from wireframe2code import shape
from wireframe2code import segment
import argparse
import cv2
import imutils


def main(args):
    """
    Example usage::

        python center.py --image shapes_and_colors.png

    """
    def resize_contour(contour, factor):
        contour = contour.astype("float")
        contour *= factor
        contour = contour.astype("int")
        return contour

    # Image has to be resized for better approximation and performance
    image = cv2.imread(args.image)
    resized_image = imutils.resize(image, width=300)
    size_factor = image.shape[0] / float(resized_image.shape[0])

    contours = segment.find_contours(resized_image)
    for contour in contours:
        vertices_count = shape.count_vertices(contour)

        contour = resize_contour(contour, size_factor)
        x, y = shape.find_center(contour)

        # Draw outline
        cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)

        # Draw vertices count
        cv2.putText(image, str(vertices_count), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Draw bounding rectangles
        x, y, w, h = shape.bounding_rectangle(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Draw canvas rectangle
    x, y, w, h = shape.bounding_rectangle(segment.find_contours(image))
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Shapes found", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", required=True, help="Path to input image")
    parsed_args, unparsed_args = parser.parse_known_args()
    main(parsed_args)