import logging
from enum import Enum
from functools import partial
from capture import Capture

from cv2 import cv2
from more_itertools import pairwise

from shape import is_rectangle


class Container:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def center(self):
        x = self.x + self.width / 2
        y = self.y + self.height / 2
        return int(x), int(y)

    def intersection(self, other):
        x = max(self.x, other.x)
        y = max(self.y, other.y)
        w = min(self.x + self.width, other.x + other.width) - x
        h = min(self.y + self.height, other.y + other.height) - y
        if w < 0 or h < 0:
            return Container(0, 0, 0, 0)
        return Container(x, y, w, h)

    def union(self, other):
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.x + self.width, other.x + other.width) - x
        h = max(self.y + self.height, other.y + other.height) - y
        return Container(x, y, w, h)

    def draw(self, image, color=(255, 255, 255), thickness=1):
        cv2.rectangle(image, (self.x, self.y), (self.x + self.width, self.y + self.height), color, thickness)

    def show(self, image, color=(255, 255, 255), thickness=1, title=''):
        self.draw(image, color, thickness)
        cv2.imshow(title, image)

    @staticmethod
    def show_all(rectangles, image, color=(255, 255, 255), thickness=1, title=''):
        for rectangle in rectangles:
            rectangle.draw(image, color, thickness)
        cv2.imshow(title, image)

    def label(self, image, text,
              org=None, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, color=(255, 255, 255), thickness=1):
        if org is None:
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            x, y = self.center()
            x -= text_size[0] / 2
            y -= text_size[1] / 2
            org = x, y
        cv2.putText(image, text, org, font, font_scale, color, thickness)

    def __key(self):
        return self.x, self.y, self.width, self.height

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__key() == other.__key()
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.__key())


class Direction(Enum):

    ROW = \
        (partial(lambda border: Container(0, border.y, border.width, border.height)),
         partial(lambda border: border.height),
         partial(lambda border: border.y),
         partial(lambda top, bottom: bottom.y - top.y - top.height))
    COLUMN = \
        (partial(lambda border: Container(border.x, 0, border.width, border.height)),
         partial(lambda border: border.width),
         partial(lambda border: border.x),
         partial(lambda left, right: right.x - left.x - left.width))

    def __init__(self, snap_function, size_function, coordinate_function, gap_function):
        self.snap = snap_function
        self.size = size_function
        self.coordinate = coordinate_function
        self.gap = gap_function


class Wireframe:

    def __init__(self, capture: Capture):
        # TODO: Get predicate from configuration
        contours = capture.contours(predicate=lambda contour: cv2.arcLength(contour, True) >= 100)

        # TODO: Get epsilon constant and minimum contour-area-to-minimum-rectangle-area ratio from configuration
        rectangles = [contour for contour in contours if is_rectangle(contour)]

        # TODO: Add other supported elements
        self.elements = rectangles

    def shape(self):
        return self.row_count(), self.column_count()

    def row_count(self) -> int:
        return self.__reference_count(direction=Direction.ROW)

    def column_count(self) -> int:
        return self.__reference_count(direction=Direction.COLUMN)

    def __reference_count(self, direction: Direction):
        align = direction.snap
        size = direction.size
        coordinate = direction.coordinate
        gap = direction.gap

        containers = [Wireframe.__container(element) for element in self.__reference_elements(direction)]
        containers = [align(container) for container in containers]
        containers.sort(key=coordinate)

        pairs = list(pairwise(containers))
        gaps = [gap(e1, e2) for (e1, e2) in pairs]
        pairs_to_distances = dict(zip(pairs, gaps))

        shortest_gap = min(gaps)
        shortest_border = min(size(container) for container in containers)
        reference_length = shortest_border + (shortest_gap * 2)

        # TODO: Improve logic for counting spans of 'missing' elements
        missing = 0
        for pair, gap in pairs_to_distances.items():
            missing += int(round(gap / reference_length))

        return len(containers) + missing

    def __reference_elements(self, direction: Direction, threshold: float = 0.55):
        """
        Computes and returns the smallest spanning elements in the provided direction.
        :param threshold: percentage of overlap between two elements to be considered as one element
        """

        align = direction.snap
        size = direction.size

        def parent_of_child(parent: Container, child: Container) -> bool:
            intersection = parent.intersection(child)
            intersection_ratio = size(intersection) / size(child)
            return size(parent) > size(child) and intersection_ratio >= threshold

        def duplicate(r1: Container, r2: Container):
            intersection = r1.intersection(r2)
            intersection_ratio_r1 = size(intersection) / size(r1)
            intersection_ratio_r2 = size(intersection) / size(r2)
            return 1 >= intersection_ratio_r1 >= threshold and 1 >= intersection_ratio_r2 >= threshold

        def filter(containers, predicate):
            unfiltered_containers = containers[:]
            containers = []

            while len(unfiltered_containers) > 0:
                reference = unfiltered_containers[0]

                others = unfiltered_containers[:]
                others.remove(reference)

                unfiltered_containers = [other for other in others if not predicate(other, reference)]
                containers.append(reference)

            return containers

        if len(self.elements) == 0:
            logging.debug("No wireframe symbols found in image")
            return 0

        container_to_element = dict((Wireframe.__container(element), element) for element in self.elements)
        container_to_element = dict((align(border), symbol) for (border, symbol) in container_to_element.items())

        containers = [*container_to_element]
        containers.sort(key=size)
        containers = filter(containers, parent_of_child)
        containers = filter(containers, duplicate)

        return [container_to_element[container] for container in containers]

    @staticmethod
    def __container(symbol):
        return Container(*cv2.boundingRect(symbol))

    def grid(self):
        pass

    def html(self):
        # TODO
        # Extract wireframe symbols
        # Create occupancy grid for wireframe symbols
        # Create HTML rows and columns from occupancy grid
        return """<html><head><title>Wireframe2Code</title></head></html>"""
