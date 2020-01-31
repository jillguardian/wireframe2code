import os

from cv2 import cv2

from capture import Capture
from wireframe import Wireframe
from wireframe import Border


def clean_wireframe_sketch():
    path = os.path.join(os.path.dirname(__file__), 'clean_wireframe_sketch.jpg')
    return cv2.imread(path)


def cursed_wireframe_sketch():
    path = os.path.join(os.path.dirname(__file__), 'cursed_wireframe_sketch.jpg')
    return cv2.imread(path)


def test_rectangle_intersection_is_symmetric():
    r1 = Border(50, 50, 100, 100)
    r2 = Border(75, 75, 100, 100)
    assert r1.intersection(r2) == r2.intersection(r1)
    assert r2.intersection(r1) == r1.intersection(r2)


def test_can_detect_elements_correctly_of_clean_wireframe_sketch():
    capture = Capture(clean_wireframe_sketch())
    wireframe = Wireframe(capture)
    assert len(wireframe.elements) == 7


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
