from __future__ import annotations

import logging
from enum import Enum
from typing import Callable
from typing import List
from typing import Set
from typing import Tuple
from typing import Union

import numpy as np
from cv2 import cv2
from more_itertools import pairwise

from sketch.capture import Capture
from sketch.shape import is_rectangle
from web.element import Tag


class Container:

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def points(self):
        return (self.x, self.y), \
               (self.x + self.width - 1, self.y), \
               (self.x + self.width - 1, self.y + self.height - 1),\
               (self.x, self.y + self.height - 1)

    def center(self):
        x = self.x + self.width / 2
        y = self.y + self.height / 2
        return int(x), int(y)

    def intersection(self, other: __class__):
        x = max(self.x, other.x)
        y = max(self.y, other.y)
        w = min(self.x + self.width, other.x + other.width) - x
        h = min(self.y + self.height, other.y + other.height) - y
        if w < 0 or h < 0:
            return Container.empty()
        return Container(x, y, w, h)

    def union(self, other: __class__):
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.x + self.width, other.x + other.width) - x
        h = max(self.y + self.height, other.y + other.height) - y
        return Container(x, y, w, h)

    @staticmethod
    def empty():
        return Container(0, 0, 0, 0)

    def contour(self) -> np.ndarray:
        """
        :return: set of points along the container, clockwise
        """

        x = np.arange(self.x, self.x + self.width - 1)
        y = np.full(x.shape[0], self.y)
        contours = np.column_stack((x, y))

        y = np.arange(self.y, self.y + self.height - 1)
        x = np.full(y.shape[0], self.x + self.width - 1)
        contours = np.concatenate((contours, np.column_stack((x, y))))

        x = np.arange(self.x + self.width - 1, self.x, -1)
        y = np.full(x.shape[0], self.y + self.height - 1)
        contours = np.concatenate((contours, np.column_stack((x, y))))

        y = np.arange(self.y + self.height - 1, self.y, -1)
        x = np.full(y.shape[0], self.x)
        contours = np.concatenate((contours, np.column_stack((x, y))))

        return np.reshape(contours, (contours.shape[0],) + (1,) + (contours.shape[1],))

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


class Location:

    def __init__(self, start: Tuple[int, int], end: Tuple[int, int] = None):
        """
        :param start: the starting location of a widget from a grid, in the format: row number, column number
        :param end: the ending location of a widget from a grid, in the format: row number, column number
        """
        self.start = start
        self.end = start if end is None else end

    @classmethod
    def unknown(cls):
        return cls((-1, -1), (-1, -1))

    def __key(self):
        return self.start, self.end

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__key() == other.__key()
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.__key())

    def __repr__(self):
        return f"({', '.join(map(str, self.start))}), ({', '.join(map(str, self.end))})"


class Widget:

    def __init__(self, contour: np.ndarray, tag: Tag, location: Location):
        self.contour = contour
        self.container = Container(*cv2.boundingRect(contour))
        self.tag = tag
        self.location = location

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.container == other.container
        else:
            return False

    def __hash__(self):
        # While ndarrays can be checked for equality, there is no proper way to hash ndarrays.
        # For now, we'll assume two instances are identical if their containers are equal.
        return hash(self.container)

    def colspan(self):
        starting_column = self.location.start[1]
        ending_column = self.location.end[1]
        return ending_column - starting_column + 1

    def rowspan(self):
        starting_row = self.location.start[0]
        ending_row = self.location.end[0]
        return ending_row - starting_row + 1


class PlaceholderWidget(Widget):

    def __init__(self, contour: np.ndarray):
        super().__init__(contour, Tag.DIV, Location.unknown())

    def occupies(self, container: Container, threshold=1):
        if not 1 > threshold > 0:
            raise ValueError("'threshold' must be a value between 0 and 1")

        intersection = self.container.intersection(container)

        intersection_area = intersection.width * intersection.height
        container_area = container.width * container.height
        ratio = intersection_area / container_area

        return 1 >= ratio >= threshold


class RowPlaceholderWidget(PlaceholderWidget):

    def __init__(self, widget: PlaceholderWidget):
        container = widget.container
        container = Container(0, container.y, container.width, container.height)
        super().__init__(container.contour())

    def size(self):
        return self.container.height

    def coordinate(self):
        return self.container.y

    def gap(self, other: Widget):
        if self.container.x != other.container.x:
            raise ValueError("Widgets are not aligned")

        if self.container.y < other.container.y:
            top = self.container
            bottom = other.container
        else:
            top = other.container
            bottom = self.container

        return bottom.y - top.y - top.height

    def overlap(self, other):
        intersection = self.container.intersection(other.container)
        return intersection.height


class ColumnPlaceholderWidget(PlaceholderWidget):

    def __init__(self, widget: PlaceholderWidget):
        container = widget.container
        container = Container(container.x, 0, container.width, container.height)
        super().__init__(container.contour())

    def size(self):
        return self.container.width

    def coordinate(self):
        return self.container.x

    def gap(self, other: Widget):
        if self.container.y != other.container.y:
            raise ValueError("Widgets are not aligned")

        if self.container.x < other.container.x:
            left = self.container
            right = other.container
        else:
            left = other.container
            right = self.container

        return right.x - left.x - left.width

    def overlap(self, other: ColumnPlaceholderWidget):
        intersection = self.container.intersection(other.container)
        return intersection.width


class Direction(Enum):

    ROW = RowPlaceholderWidget
    COLUMN = ColumnPlaceholderWidget


class Wireframe:

    def __init__(self, capture: Capture):
        self.source = capture.image.copy()

        # TODO: Get predicate from configuration
        contours = capture.contours(predicate=lambda contour: cv2.arcLength(contour, True) >= 100)

        # TODO: Get epsilon constant and minimum contour-area-to-minimum-rectangle-area ratio from configuration
        rectangles = [contour for contour in contours if is_rectangle(contour)]
        logging.debug(f"Found '{len(rectangles)}' rectangles")

        # TODO: Add other supported elements
        self.placeholders = {PlaceholderWidget(rectangle) for rectangle in rectangles}
        logging.debug(f"Found '{len(self.placeholders)}' widgets")

    def shape(self):
        return self.row_count(), self.column_count()

    def row_count(self) -> int:
        return self.__reference_count(Direction.ROW)

    def column_count(self) -> int:
        return self.__reference_count(Direction.COLUMN)

    def __reference_count(self, direction: Direction) -> int:
        widgets = self.__reference_widgets(direction)
        widgets = list([direction.value(widget) for widget in widgets])
        widgets.sort(key=direction.value.coordinate)

        pairs = list(pairwise(widgets))
        gaps = [w1.gap(w2) for (w1, w2) in pairs]
        pairs_to_distances = dict(zip(pairs, gaps))

        shortest_gap = min(gaps)
        shortest_border = min(widget.size() for widget in widgets)
        reference_length = shortest_border + (shortest_gap * 2)

        # TODO: Improve logic for counting spans of 'missing' elements
        missing = 0
        for pair, gap in pairs_to_distances.items():
            missing += int(round(gap / reference_length))

        return len(widgets) + missing

    def __reference_widgets(self, direction: Direction, threshold: float = 0.55)\
            -> Set[Union[RowPlaceholderWidget, ColumnPlaceholderWidget]]:
        """
        Computes and returns the smallest spanning elements in the provided direction.
        :param threshold: percentage of overlap between two elements to be considered as one element
        """

        def parent_of_child(parent: direction.value, child: direction.value) -> bool:
            intersection = parent.overlap(child)
            intersection_ratio = intersection / child.size()
            return parent.size() > child.size() and intersection_ratio >= threshold

        def duplicate(w1: direction.value, w2: direction.value):
            intersection = w1.overlap(w2)
            intersection_ratio_r1 = intersection / w1.size()
            intersection_ratio_r2 = intersection / w2.size()
            return 1 >= intersection_ratio_r1 >= threshold and 1 >= intersection_ratio_r2 >= threshold

        def filter(widgets: List[direction.value], predicate: Callable[[direction.value, direction.value], bool]):
            unfiltered = widgets[:]
            widgets = []

            while len(unfiltered) > 0:
                reference = unfiltered[0]

                others = unfiltered[:]
                others.remove(reference)

                unfiltered = [other for other in others if not predicate(other, reference)]
                widgets.append(reference)

            return widgets

        if len(self.placeholders) == 0:
            logging.debug("No wireframe widgets found in image")
            return set()

        copies_to_widgets = {direction.value(widget): widget for widget in self.placeholders}

        copies = [*copies_to_widgets]
        copies.sort(key=direction.value.size)
        copies = filter(copies, parent_of_child)
        copies = filter(copies, duplicate)

        return {copies_to_widgets[copy] for copy in copies}

    def widgets(self) -> Set[Widget]:

        def point(index: int):
            quotient, remainder = divmod(index, columns)
            return remainder, quotient

        rows, columns = self.shape()
        widgets = set()

        grids = self.grids()
        for grid in grids:
            grid.draw(self.source)

        for placeholder in self.placeholders:
            placeholder.container.draw(self.source, color=(255, 0, 0))
            # cv2.imshow('', self.source)
            # cv2.waitKey(0)

            occupied = [index for index, grid in enumerate(grids) if placeholder.occupies(grid, threshold=0.60)]

            start = occupied[0]
            end = occupied[-1]

            location = Location(point(start), point(end))
            widget = Widget(placeholder.contour, placeholder.tag, location)
            widgets.add(widget)

        return widgets

    def grids(self) -> List[Container]:
        container = self.container()
        rows, columns = self.shape()

        grid_height = int(container.height / rows)
        grid_width = int(container.width / columns)

        grids = []
        for i in range(rows):
            y = container.y + (grid_height * i)
            for j in range(columns):
                x = container.x + (grid_width * j)
                grid = Container(x, y, grid_width, grid_height)
                grids.append(grid)

        return grids

    def container(self) -> Container:
        container = next(iter(self.placeholders)).container
        for widget in self.placeholders:
            container = container.union(widget.container)
        return container
