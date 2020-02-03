from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import webbrowser

from cv2 import cv2

from sketch.capture import Capture
from sketch.wireframe import Wireframe
from web.writer import Html


def main(args):
    if args.camera and args.filename is not None:
        raise ValueError("Camera and image cannot be simultaneously provided")

    if args.camera:
        consume_camera(args.output)
    elif args.filename is not None:
        consume_file(args.filename, args.output, args.debug)
    else:
        raise ValueError("Must provide arguments")

    cv2.destroyAllWindows()


def consume_camera(destination: str, interval: int = 25, exit_key: chr = None):

    def should_exit():
        if exit_key is not None:
            return ord(exit_key) == key & 0xFF
        return key != -1

    capture = cv2.VideoCapture(0)
    while True:
        can_read, frame = capture.read()
        if can_read:
            _, wireframe = write_html(frame, destination)

            preview_widgets(wireframe.source, wireframe)

            key = cv2.waitKey(interval)
            if should_exit():
                break
        else:
            logging.error("Can't read from camera")
            break

    capture.release()
    cv2.destroyAllWindows()


def write_html(image, destination):
    capture = Capture(image)
    wireframe = Wireframe(capture)

    html = Html(destination)
    html.write(wireframe)

    return capture, wireframe


def preview_widgets(image, wireframe, title='Bounding Rectangles', color=(0, 255, 0)):
    for widget in wireframe.widgets():
        widget.container.draw(image, color=color)
    cv2.imshow(title, image)


def consume_file(filename, destination: str, debug: bool = False):

    def preview_preprocessing():
        for image in [capture.image] + capture.preprocess():
            cv2.imshow('Preprocessing', image)
            cv2.waitKey(0)

    def preview_contours():
        image = capture.image.copy()
        cv2.drawContours(image, capture.contours(), -1, color=(0, 255, 0))
        cv2.imshow('Contours', image)
        cv2.waitKey(0)

    def preview_grids():
        for grid in wireframe.grids():
            grid.draw(image)
        cv2.imshow('Grids', image)
        cv2.waitKey(0)

    source = cv2.imread(filename)

    capture, wireframe = write_html(source, destination)
    open_browser(destination + '/index.html')
    image = wireframe.source.copy()

    if debug:
        preview_preprocessing()
        preview_contours()
        preview_grids()

    preview_widgets(image, wireframe)
    cv2.waitKey(0)


def open_browser(url):
    if sys.platform == 'darwin':
        subprocess.Popen(f"open {url}", shell=True)
    else:
        webbrowser.open(url, new=0)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', type=str,
                        dest='filename', help='Path to input image')
    parser.add_argument('-c', '--camera',
                        action='store_true', help='Use camera as source')
    parser.add_argument('-o', '--output', type=str,
                        required=True, help='Destination of generated HTML/JS/CSS files')
    parser.add_argument('-d', '--debug',
                        action='store_true', help='')

    parsed_args, unparsed_args = parser.parse_known_args()
    main(parsed_args)
