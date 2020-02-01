import os

import numpy as np
from cv2 import cv2
from pytest import fail

from capture import Capture
from wireframe import ColumnView
from wireframe import Container
from wireframe import RowView
from wireframe import Wireframe


def clean_wireframe_sketch():
    path = os.path.join(os.path.dirname(__file__), 'clean_wireframe_sketch.jpg')
    return cv2.imread(path)


def cursed_wireframe_sketch():
    path = os.path.join(os.path.dirname(__file__), 'cursed_wireframe_sketch.jpg')
    return cv2.imread(path)


def canvas(width, height, color=(255, 255, 255)):
    image = np.zeros((height, width, 3), np.uint8)
    color = tuple(reversed(color))
    image[:] = color
    return image


def test_container_points_are_returned_in_clockwise_order():
    container = Container(0, 0, 5, 5)
    assert container.points() == tuple([(0, 0), (4, 0), (4, 4), (0, 4)])


def test_container_intersection_is_symmetric():
    r1 = Container(50, 50, 100, 100)
    r2 = Container(75, 75, 100, 100)
    assert r1.intersection(r2) == r2.intersection(r1)
    assert r2.intersection(r1) == r1.intersection(r2)


def test_container_contour():
    container = Container(10, 5, 5, 5)
    expected = np.array([
        [[10, 5]], [[11, 5]], [[12, 5]], [[13, 5]],
        [[14, 5]], [[14, 6]], [[14, 7]], [[14, 8]],
        [[14, 9]], [[13, 9]], [[12, 9]], [[11, 9]],
        [[10, 9]], [[10, 8]], [[10, 7]], [[10, 6]]])
    assert np.array_equal(container.contour(), expected)


def test_can_draw_container_contour():
    background = canvas(20, 20)
    container = Container(10, 5, 5, 5)

    try:
        cv2.drawContours(background, container.contour(), -1, (0, 0, 0))
    except Exception:
        fail("Can't draw")


def test_can_detect_elements_correctly_of_clean_wireframe_sketch():
    capture = Capture(clean_wireframe_sketch())
    wireframe = Wireframe(capture)
    assert len(wireframe.widgets) == 7


def test_can_compute_row_count_of_clean_wireframe_sketch():
    capture = Capture(clean_wireframe_sketch())
    wireframe = Wireframe(capture)
    assert wireframe.row_count() == 4


def test_can_compute_column_count_of_clean_wireframe_sketch():
    capture = Capture(clean_wireframe_sketch())
    wireframe = Wireframe(capture)
    assert wireframe.column_count() == 4


def test_can_compute_grid_shape_of_clean_wireframe_sketch():
    capture = Capture(clean_wireframe_sketch())
    wireframe = Wireframe(capture)
    assert wireframe.shape() == (4, 4)


def test_can_compute_grid_shape_of_cursed_wireframe_sketch():
    capture = Capture(cursed_wireframe_sketch())
    wireframe = Wireframe(capture)
    assert wireframe.shape() == (3, 8)
