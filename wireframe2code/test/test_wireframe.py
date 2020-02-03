import os

import numpy as np
import pytest
from cv2 import cv2
from pytest import fail

from sketch.capture import Capture
from sketch.wireframe import Container
from sketch.wireframe import Wireframe
from sketch.wireframe import Location


@pytest.fixture(scope="module")
def wireframe_sketch():
    path = os.path.join(os.path.dirname(__file__), 'resources/clean_wireframe_sketch.jpg')
    yield cv2.imread(path)


@pytest.fixture(scope="module")
def gapped_wireframe_sketch():
    path = os.path.join(os.path.dirname(__file__), 'resources/gapped_wireframe_sketch.jpg')
    yield cv2.imread(path)


@pytest.fixture(scope="module")
def canvas():

    def _make(width, height, color=(255, 255, 255)):
        image = np.zeros((height, width, 3), np.uint8)
        color = tuple(reversed(color))
        image[:] = color
        return image

    return _make


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


def test_can_draw_container_contour(canvas):
    background = canvas(20, 20)
    container = Container(10, 5, 5, 5)

    try:
        cv2.drawContours(background, container.contour(), -1, (0, 0, 0))
    except Exception:
        fail("Can't draw")


def test_can_detect_elements_correctly_of_clean_wireframe_sketch(wireframe_sketch):
    capture = Capture(wireframe_sketch)
    wireframe = Wireframe(capture)
    assert len(wireframe.placeholders) == 7


def test_can_compute_row_count_of_clean_wireframe_sketch(wireframe_sketch):
    capture = Capture(wireframe_sketch)
    wireframe = Wireframe(capture)
    assert wireframe.row_count() == 4


def test_can_compute_row_count_of_gapped_wireframe_sketch(gapped_wireframe_sketch):
    capture = Capture(gapped_wireframe_sketch)
    wireframe = Wireframe(capture)
    assert wireframe.row_count() == 3


def test_can_compute_column_count_of_clean_wireframe_sketch(wireframe_sketch):
    capture = Capture(wireframe_sketch)
    wireframe = Wireframe(capture)
    assert wireframe.column_count() == 4


def test_can_compute_grid_shape_of_clean_wireframe_sketch(wireframe_sketch):
    capture = Capture(wireframe_sketch)
    wireframe = Wireframe(capture)
    assert wireframe.shape() == (4, 4)


def test_can_compute_grids_of_clean_wireframe_sketch(wireframe_sketch):
    capture = Capture(wireframe_sketch)
    wireframe = Wireframe(capture)

    shape = wireframe.shape()
    grids = wireframe.grids()

    assert len(grids) == shape[0] * shape[1]


def test_widget_locations_of_clean_wireframe_sketch(wireframe_sketch):
    capture = Capture(wireframe_sketch)
    wireframe = Wireframe(capture)
    actual = {widget.location for widget in wireframe.widgets()}
    expected = {
        Location((0, 0), (1, 1)),
        Location((0, 2)),
        Location((0, 3), (2, 3)),
        Location((2, 0)),
        Location((2, 1)),
        Location((1, 2), (2, 2)),
        Location((3, 0), (3, 3))
    }

    assert actual == expected
