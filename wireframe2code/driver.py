import argparse
import logging

from cv2 import cv2

import paper
import segment


def show_image(title, image):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyWindow(title)


def main(args):
    if args.use_camera and args.filename is not None:
        raise Exception("Camera and image cannot be simultaneously provided")
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

    image_copy = image.copy()
    for symbol in wireframe.symbols():
        cv2.drawContours(image_copy, [symbol], -1, (0, 255, 0), 2)
        # x, y, w, h = cv2.boundingRect(symbol)
        # cv2.rectangle(image_copy, (x, y), (x + w, y + h), (255, 0, 0), 2)
        show_image("Image", image_copy)
    wireframe.row_count()


class Wireframe:
    def __init__(self, capture):
        self.capture = capture

    def column_count(self):
        pass

    def row_count(self):
        def overlap(x1, y1, x2, y2):
            return max(0, min(y1, y2) - max(x1, x2))

        def spans_multiple_rows(row, rows):
            rows = rows[:]
            rows.remove(row)

            child_count = 0
            for possible_child in rows:
                ratio = overlap(row[0], row[1], possible_child[0], possible_child[1]) / possible_child[3]
                if ratio >= 0.40:
                    child_count += 1
                if child_count > 1:
                    return True

            return False

        symbols = self.symbols()
        if len(symbols) == 0:
            logging.debug("No wireframe symbols found in image")
            return 0

        cells = [cv2.boundingRect(symbol) for symbol in symbols]
        # Sort by y-coordinate
        cells.sort(key=lambda cell: cell[1])
        # Use uniform x-coordinates for all bounding rectangles
        # The x-coordinate can be any number, as long as it's the same across all elements
        cells = [(cells[0][0],) + cell[1:] for cell in cells]
        # Remove multi-row spanning cells
        cells = [cell for cell in cells if not spans_multiple_rows(cell, cells)]

        count = 1
        previous_cell = cells[0]
        for current_cell in cells[1:]:
            intersection = segment.intersection(previous_cell, current_cell)

        return count

    def symbols(self):
        # TODO: Get predicate from configuration
        contours = self.capture.contours(predicate=lambda contour: cv2.arcLength(contour, True) >= 100)
        # TODO: Get epsilon constant and minimum contour-area-to-minimum-rectangle-area ratio from configuration
        squares = [contour for contour in contours if segment.is_quadrangle(contour)]
        return squares

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
