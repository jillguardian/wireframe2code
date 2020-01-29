import logging

from cv2 import cv2
from functools import reduce
from shape import is_rectangle


class Rectangle:

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
            return Rectangle(0, 0, 0, 0)
        return Rectangle(x, y, w, h)

    def union(self, other):
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.x + self.width, other.x + other.width) - x
        h = max(self.y + self.height, other.y + other.height) - y
        return Rectangle(x, y, w, h)

    def draw(self, image, color=(255, 255, 255), thickness=1):
        cv2.rectangle(image, (self.x, self.y), (self.x + self.width, self.y + self.height), color, thickness)

    def label(self, image, text, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, color=(255, 255, 255), thickness=1):
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        x, y = self.center()
        x += text_size[0]
        y -= text_size[1]
        cv2.putText(image, text, (x, y), font, font_scale, color, thickness)


class Wireframe:

    def __init__(self, capture):
        # TODO: Get predicate from configuration
        contours = capture.contours(predicate=lambda contour: cv2.arcLength(contour, True) >= 100)
        # TODO: Get epsilon constant and minimum contour-area-to-minimum-rectangle-area ratio from configuration
        rectangles = [contour for contour in contours if is_rectangle(contour)]
        # TODO: Add other supported symbols

        self.symbols = rectangles

    def shape(self):
        # return self.column_count(), self.row_count()
        return self.column_count(), self.row_count()

    def grid(self):
        pass

    def __count(self, align, size, coordinate):

        def remove_overlaps(wrappers):
            unfiltered_wrappers = wrappers[:]
            wrappers = []

            while len(unfiltered_wrappers) > 0:
                reference = unfiltered_wrappers[0]
                others = unfiltered_wrappers[:]
                others.remove(reference)

                unfiltered_wrappers = [other for other in others if not overlaps(reference, other)]
                wrappers.append(reference)

            return wrappers

        def overlaps(r1, r2, threshold=0.40):
            intersection = r1.intersection(r2)
            intersection_to_r1 = size(intersection) / size(r1)
            intersection_to_r2 = size(intersection) / size(r2)
            return 1 >= intersection_to_r1 >= threshold and 1 >= intersection_to_r2 >= threshold

        if len(self.symbols) == 0:
            logging.debug("No wireframe symbols found in image")
            return 0

        wrappers = [Rectangle(*cv2.boundingRect(symbol)) for symbol in self.symbols]
        wrappers = [align(wrapper) for wrapper in wrappers]
        wrappers = remove_overlaps(wrappers)
        wrappers.sort(key=coordinate)

        base_size = min(wrappers, key=size)
        grand_wrapper = reduce(Rectangle.union, wrappers)

        return 0

    def column_count(self):
        return self.__count(
            # Use uniform y-coordinates for all bounding rectangles
            # The y-coordinate can be any number, as long as it's the same across all elements
            align=lambda rectangle: Rectangle(rectangle.x, 0, rectangle.width, rectangle.height),
            # Use width for size
            size=lambda rectangle: rectangle.width,
            coordinate=lambda rectangle: rectangle.x)

    def row_count(self):
        return self.__count(
            # Use uniform x-coordinates for all bounding rectangles
            # The x-coordinate can be any number, as long as it's the same across all elements
            align=lambda rectangle: Rectangle(0, rectangle.y, rectangle.width, rectangle.height),
            # Use height for size
            size=lambda rectangle: rectangle.height,
            coordinate=lambda rectangle: rectangle.y)

    def html(self):
        # TODO
        # Extract wireframe symbols
        # Create occupancy grid for wireframe symbols
        # Create HTML rows and columns from occupancy grid
        return """<html><head><title>Wireframe2Code</title></head></html>"""

