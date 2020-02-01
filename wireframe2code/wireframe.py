from __future__ import annotations

import logging
from copy import deepcopy
from enum import Enum
from typing import Callable
from typing import List
from typing import Set
from typing import Union

import numpy as np
from cv2 import cv2
from more_itertools import pairwise

from capture import Capture
from shape import is_rectangle


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


class Type(Enum):
    IMAGE = "img"
    PARAGRAPH = "p"
    BUTTON = "button"
    INPUT = "input"
    DIV = "div"

    def __init__(self, tag_name):
        self.tag_name = tag_name

    @classmethod
    def all(cls):
        return {e.name for e in cls}


class Widget:

    def __init__(self, contour: np.ndarray, type: Type = Type.DIV):
        self.contour = contour
        self.type = type
        self.container = Container(*cv2.boundingRect(contour))

    @classmethod
    def with_contour_and_container(cls, contour: np.ndarray, container: Container):
        instance = cls(contour)
        instance.container = container
        return instance

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.container == other.container
        else:
            return False

    def __hash__(self):
        # While ndarrays can be checked for equality, there is no proper way to hash ndarrays.
        # For now, we'll assume two instances are identical if their containers are equal.
        return hash(self.container)


class View:

    @staticmethod
    def intersection(w1: Widget, w2: Widget):
        return Widget(w1.container.intersection(w2.container).contour())


class RowView(View):

    @staticmethod
    def snap(widget: Widget, x=0) -> Widget:
        container = widget.container
        container = Container(x, container.y, container.width, container.height)
        return Widget(container.contour())

    @staticmethod
    def size(widget: Widget) -> int:
        return widget.container.height

    @staticmethod
    def coordinate(widget: Widget) -> int:
        return widget.container.y

    @staticmethod
    def gap(w1: Widget, w2: Widget) -> int:
        if w1.container.x != w2.container.x:
            raise ValueError("Widgets are not aligned")
        widgets = [w1, w2]
        widgets.sort(key=RowView.coordinate)
        return widgets[1].container.y - widgets[0].container.y - widgets[0].container.height


class ColumnView(View):

    @staticmethod
    def snap(widget: Widget, y=0) -> Widget:
        container = widget.container
        container = Container(container.x, y, container.width, container.height)
        return Widget(container.contour())

    @staticmethod
    def size(widget: Widget) -> int:
        return widget.container.width

    @staticmethod
    def coordinate(widget: Widget):
        return widget.container.x

    @staticmethod
    def gap(w1: Widget, w2: Widget) -> int:
        if w1.container.y != w2.container.y:
            raise ValueError("Widgets are not aligned")
        widgets = [w1, w2]
        widgets.sort(key=RowView.coordinate)
        return widgets[1].container.x - widgets[0].container.x - widgets[0].container.height


class Wireframe:

    def __init__(self, capture: Capture):
        # TODO: Get predicate from configuration
        contours = capture.contours(predicate=lambda contour: cv2.arcLength(contour, True) >= 100)

        # TODO: Get epsilon constant and minimum contour-area-to-minimum-rectangle-area ratio from configuration
        rectangles = [contour for contour in contours if is_rectangle(contour)]
        logging.debug(f"Found '{len(rectangles)}' rectangles")

        # TODO: Add other supported elements
        self.widgets = {Widget(rectangle) for rectangle in rectangles}
        logging.debug(f"Found '{len(self.widgets)}' widgets")

    def shape(self):
        return self.row_count(), self.column_count()

    def row_count(self) -> int:
        return self.__reference_count(RowView())

    def column_count(self) -> int:
        return self.__reference_count(ColumnView())

    def __reference_count(self, view):
        widgets = self.reference_widgets(view)
        widgets = [view.snap(widget) for widget in widgets]
        widgets.sort(key=view.coordinate)

        pairs = list(pairwise(widgets))
        gaps = [view.gap(e1, e2) for (e1, e2) in pairs]
        pairs_to_distances = dict(zip(pairs, gaps))

        shortest_gap = min(gaps)
        shortest_border = min(view.size(widget) for widget in widgets)
        reference_length = shortest_border + (shortest_gap * 2)

        # TODO: Improve logic for counting spans of 'missing' elements
        missing = 0
        for pair, gap in pairs_to_distances.items():
            missing += int(round(gap / reference_length))

        return len(widgets) + missing

    def reference_widgets(self, view: Union[RowView, ColumnView], threshold: float = 0.55) -> Set[Widget]:
        """
        Computes and returns the smallest spanning elements in the provided direction.
        :param threshold: percentage of overlap between two elements to be considered as one element
        """

        def parent_of_child(parent: Widget, child: Widget) -> bool:
            intersection = view.intersection(parent, child)
            intersection_ratio = view.size(intersection) / view.size(child)
            return view.size(parent) > view.size(child) and intersection_ratio >= threshold

        def duplicate(w1: Widget, w2: Widget):
            intersection = view.intersection(w1, w2)
            intersection_ratio_r1 = view.size(intersection) / view.size(w1)
            intersection_ratio_r2 = view.size(intersection) / view.size(w2)
            return 1 >= intersection_ratio_r1 >= threshold and 1 >= intersection_ratio_r2 >= threshold

        def filter(widgets: List[Widget], predicate: Callable[[Widget, Widget], bool]):
            unfiltered = widgets[:]
            widgets = []

            while len(unfiltered) > 0:
                reference = unfiltered[0]

                others = unfiltered[:]
                others.remove(reference)

                unfiltered = [other for other in others if not predicate(other, reference)]
                widgets.append(reference)

            return widgets

        if len(self.widgets) == 0:
            logging.debug("No wireframe symbols found in image")
            return 0

        copies_to_widgets = {deepcopy(widget): widget for widget in self.widgets}
        copies_to_widgets = {view.snap(copy): widget for copy, widget in copies_to_widgets.items()}

        copies = [*copies_to_widgets]
        copies.sort(key=view.size)
        copies = filter(copies, parent_of_child)
        copies = filter(copies, duplicate)

        return {copies_to_widgets[copy] for copy in copies}

    def grid(self):
        pass

    def html(self):
        # TODO
        # Extract wireframe symbols
        # Create occupancy grid for wireframe symbols
        # Create HTML rows and columns from occupancy grid
        return """<html><head><title>Wireframe2Code</title></head></html>"""
