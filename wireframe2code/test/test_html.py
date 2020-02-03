import os
from pathlib import Path

import pytest
from cv2 import cv2

import file
from sketch.capture import Capture
from sketch.wireframe import Wireframe, Location
from web.writer import Html
from web.writer import sort

from bs4 import BeautifulSoup


@pytest.fixture(scope="module")
def basedir():
    base_path = Path(__file__).parent
    return base_path


@pytest.fixture(scope="module")
def tempdir():
    with file.tempdir() as tempdir:
        yield tempdir


@pytest.fixture(scope="module")
def wireframe():
    path = os.path.join(os.path.dirname(__file__), 'resources/clean_wireframe_sketch.jpg')
    capture = Capture(cv2.imread(path))
    yield Wireframe(capture)


def test_sort_widgets_by_location(wireframe):
    widgets = wireframe.widgets()
    widgets = sort(widgets)
    actual = [widget.location for widget in widgets]
    expected = [
        Location((0, 0), (1, 1)),
        Location((2, 0)),
        Location((3, 0), (3, 3)),
        Location((2, 1)),
        Location((0, 2)),
        Location((1, 2), (2, 2)),
        Location((0, 3), (2, 3)),
    ]
    assert actual == expected


def test_generate_html_file_from_wireframe(wireframe, basedir, tempdir):
    tempdir = Path(tempdir)

    html = Html(tempdir)
    html.write(wireframe)

    apath = (tempdir / "index.html").resolve()
    epath = (basedir / "resources/clean_wireframe_sketch.html").resolve()

    with open(apath, 'r') as afile, open(epath, 'r') as efile:
        actual = BeautifulSoup(afile)
        expected = BeautifulSoup(efile)
        assert actual == expected


def test_copy_assets_to_destination_directory(wireframe, tempdir):
    html = Html(tempdir)
    html.write(wireframe)

    files = os.listdir(tempdir)
    assert set(files) == {
        'index.html',
        'style.css',
        'favicon.ico',
        'bootstrap.min.css',
        'bootstrap.min.js'
    }
