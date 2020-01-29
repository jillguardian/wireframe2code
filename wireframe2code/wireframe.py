import logging

from cv2 import cv2

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


class Wireframe:

    def __init__(self, capture):
        # TODO: Get predicate from configuration
        contours = capture.contours(predicate=lambda contour: cv2.arcLength(contour, True) >= 100)
        # TODO: Get epsilon constant and minimum contour-area-to-minimum-rectangle-area ratio from configuration
        rectangles = [contour for contour in contours if is_rectangle(contour)]
        # TODO: Add other supported symbols

        self.symbols = rectangles
        self.image = capture.image.copy()

    def shape(self):
        return self.column_count(), self.row_count()

    def grid(self):
        pass

    def __basic_elements(self, align, size, threshold=0.55):

        def parent_of_child(parent: Rectangle, child: Rectangle) -> bool:
            intersection = parent.intersection(child)
            intersection_ratio = size(intersection) / size(child)
            return size(parent) > size(child) and intersection_ratio >= threshold

        def duplicate(r1: Rectangle, r2: Rectangle):
            intersection = r1.intersection(r2)
            intersection_ratio_r1 = size(intersection) / size(r1)
            intersection_ratio_r2 = size(intersection) / size(r2)
            return 1 >= intersection_ratio_r1 >= threshold and 1 >= intersection_ratio_r2 >= threshold

        def filter(wrappers, predicate):
            unfiltered_wrappers = wrappers[:]
            wrappers = []

            while len(unfiltered_wrappers) > 0:
                reference = unfiltered_wrappers[0]

                # image = self.image.copy()
                # reference.show(image, color=(0, 255, 0))
                # cv2.waitKey(0)

                others = unfiltered_wrappers[:]
                others.remove(reference)

                # Rectangle.show_all(others, image, color=(0, 0, 255))
                # cv2.waitKey(0)

                unfiltered_wrappers = [other for other in others if not predicate(other, reference)]

                # Rectangle.show_all(unfiltered_wrappers, image)
                # cv2.waitKey(0)

                wrappers.append(reference)

            return wrappers

        if len(self.symbols) == 0:
            logging.debug("No wireframe symbols found in image")
            return 0

        wrappers = [Rectangle(*cv2.boundingRect(symbol)) for symbol in self.symbols]
        wrappers = [align(wrapper) for wrapper in wrappers]

        wrappers.sort(key=size)
        wrappers = filter(wrappers, parent_of_child)
        wrappers = filter(wrappers, duplicate)

        return wrappers

    def basic_rows(self):
        return self.__basic_elements(
            # Use uniform x-coordinates for all bounding rectangles
            # The x-coordinate can be any number, as long as it's the same across all elements
            align=lambda rectangle: Rectangle(0, rectangle.y, rectangle.width, rectangle.height),
            size=lambda rectangle: rectangle.height)

    def basic_columns(self):
        return self.__basic_elements(
            # Use uniform y-coordinates for all bounding rectangles
            # The y-coordinate can be any number, as long as it's the same across all elements
            align=lambda rectangle: Rectangle(rectangle.x, 0, rectangle.width, rectangle.height),
            size=lambda rectangle: rectangle.width)

    def column_count(self):
        return len(self.basic_columns())

    def row_count(self):
        return len(self.basic_rows())

    def html(self):
        # TODO
        # Extract wireframe symbols
        # Create occupancy grid for wireframe symbols
        # Create HTML rows and columns from occupancy grid
        return """<html><head><title>Wireframe2Code</title></head></html>"""
