import argparse
import logging

from cv2 import cv2
from collections import namedtuple

import paper
import segment


def show_image(title, image):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyWindow(title)


def main(args):
    if args.use_camera and args.filename is not None:
        raise ValueError("Camera and image cannot be simultaneously provided")
    if args.use_camera:
        capture = cv2.VideoCapture(0)
        while True:
            can_read, frame = capture.read()
            if can_read:
                process(frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                break
        capture.release()
        cv2.destroyAllWindows()
    elif args.filename is not None:
        image = cv2.imread(args.filename)
        process(image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        raise Exception("Must provide arguments")
    cv2.destroyAllWindows()


def process(image):
    capture = paper.Capture(image)
    wireframe = Wireframe(capture)

    image_copy = capture.image.copy()
    for symbol in wireframe.symbols:
        cv2.drawContours(image_copy, [symbol], -1, (0, 255, 0), 2)
        # x, y, w, h = cv2.boundingRect(symbol)
        # cv2.rectangle(image_copy, (x, y), (x + w, y + h), (255, 0, 0), 2)
        show_image("Image", image_copy)
    wireframe.grid()


class Wireframe:
    def __init__(self, capture):
        # TODO: Get predicate from configuration
        contours = capture.contours(predicate=lambda contour: cv2.arcLength(contour, True) >= 100)
        # TODO: Get epsilon constant and minimum contour-area-to-minimum-rectangle-area ratio from configuration
        squares = [contour for contour in contours if segment.is_quadrangle(contour)]
        # TODO: Add other supported symbols

        self.symbols = squares

    def grid(self):
        column_coordinates = self.__column_coordinates()
        row_coordinates = self.__row_coordinates()

        if len(self.symbols) != len(column_coordinates):
            raise AssertionError(f"Found '{len(self.symbols)}' wireframe symbols "
                                 f"but got '{len(column_coordinates)}' column coordinates")
        if len(self.symbols) != len(row_coordinates):
            raise AssertionError(f"Found '{len(self.symbols)}' wireframe symbols "
                                 f"but got '{len(row_coordinates)}' row coordinates")

        Element = namedtuple('Element', 'starting_column starting_row ending_column ending_row')

        grid_coordinates = []
        for i in range(len(self.symbols)):
            x1, x2 = column_coordinates[i]
            y1, y2 = row_coordinates[i]
            grid_coordinates.append(Element(starting_column=x1, starting_row=y1, ending_column=x2, ending_row=y2))

        return grid_coordinates

    def __coordinates(self, transform, sort):
        def span(index, rectangles):
            reference = rectangles[index]
            rectangles = rectangles[:index] + rectangles[index + 1:]

            overlapping_rectangles = 0
            for other in rectangles:
                if overlaps(reference, other):
                    overlapping_rectangles += 1
            return overlapping_rectangles + 1

        def overlaps(reference_rectangle, other_rectangle):
            intersection = segment.intersection(reference_rectangle, other_rectangle)
            intersection_area = intersection[2] * intersection[3]

            if intersection_area == 0:
                return False

            reference_area = reference_rectangle[2] * reference_rectangle[3]
            ratio = intersection_area / reference_area
            return ratio >= 0.40

        if len(self.symbols) == 0:
            logging.debug("No wireframe symbols found in image")
            return []

        bounding_rectangles = [cv2.boundingRect(symbol) for symbol in self.symbols]
        bounding_rectangles = [transform(bounding_rectangle) for bounding_rectangle in bounding_rectangles]
        bounding_rectangles.sort(key=sort)

        Element = namedtuple('Element', 'i starting_coordinate')
        reference_element = Element(i=0, starting_coordinate=0)

        coordinates = []
        for i in range(len(bounding_rectangles)):
            span = span(i, bounding_rectangles)
            starting_coordinate = reference_element.starting_coordinate

            if not overlaps(bounding_rectangles[reference_element.i], bounding_rectangles[i]):
                starting_coordinate = reference_element.starting_coordinate + 1

            ending_coordinate = starting_coordinate + span - 1

            # This way, multi-spanning cells never get to be used for reference
            if span == 1:
                reference_element = Element(i=i, starting_coordinate=starting_coordinate)

            coordinates.append((starting_coordinate, ending_coordinate))

        return coordinates

    def __column_coordinates(self):
        return self.__coordinates(
            # Use uniform y-coordinates for all bounding rectangles
            # The y-coordinate can be any number, as long as it's the same across all elements
            transform=lambda bounding_rectangle: bounding_rectangle[0:1] + (0,) + bounding_rectangle[2:],
            # Sort by x-coordinate
            sort=lambda bounding_rectangle: bounding_rectangle[0])

    def __row_coordinates(self):
        return self.__coordinates(
            # Use uniform x-coordinates for all bounding rectangles
            # The x-coordinate can be any number, as long as it's the same across all elements
            transform=lambda bounding_rectangle: (0,) + bounding_rectangle[1:],
            # Sort by y-coordinate
            sort=lambda bounding_rectangle: bounding_rectangle[1])

    def to_html(self):
        # TODO
        # Extract wireframe symbols
        # Create occupancy grid for wireframe symbols
        # Create HTML rows and columns from occupancy grid
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", dest="filename", help="Path to input image")
    parser.add_argument("-c", "--camera", dest="use_camera", help="Flag for using camera as source",
                        action='store_true')
    parsed_args, unparsed_args = parser.parse_known_args()
    main(parsed_args)
