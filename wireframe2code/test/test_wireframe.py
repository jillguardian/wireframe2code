import os

from cv2 import cv2

from capture import Capture
from wireframe import Wireframe
from wireframe import Rectangle


def clean_wireframe_sketch():
    path = os.path.join(os.path.dirname(__file__), 'clean_wireframe_sketch.jpg')
    return cv2.imread(path)


def test_rectangle_intersection_is_symmetric():
    r1 = Rectangle(50, 50, 100, 100)
    r2 = Rectangle(75, 75, 100, 100)
    assert r1.intersection(r2) == r2.intersection(r1)
    assert r2.intersection(r1) == r1.intersection(r2)


def test_wireframe_symbols():
    capture = Capture(clean_wireframe_sketch())
    wireframe = Wireframe(capture)
    assert len(wireframe.symbols) == 7


def test_wireframe_basic_rows():
    capture = Capture(clean_wireframe_sketch())
    wireframe = Wireframe(capture)
    assert len(wireframe.basic_rows()) == 4


def test_wireframe_basic_columns():
    capture = Capture(clean_wireframe_sketch())
    wireframe = Wireframe(capture)
    assert len(wireframe.basic_columns()) == 3


def test_wireframe_row_count():
    capture = Capture(clean_wireframe_sketch())
    wireframe = Wireframe(capture)
    assert wireframe.row_count() == 4


def test_wireframe_column_count():
    capture = Capture(clean_wireframe_sketch())
    wireframe = Wireframe(capture)
    assert wireframe.column_count() == 4

