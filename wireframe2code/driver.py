from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from contextlib import contextmanager

from capture import *
from wireframe import *


def main(args):
    if args.camera and args.filename is not None:
        raise ValueError("Camera and image cannot be simultaneously provided")
    if args.camera:
        consume_camera(preview_detection=args.interactive, preview_html=args.interactive)
    elif args.filename is not None:
        image = cv2.imread(args.filename)

        if args.interactive:
            # TODO: Show image processing applied
            html = consume_file(image, preview_elements)
            cv2.waitKey(0)
        else:
            html = consume_file(image)

        # TODO: Write HTML string to file
        # TODO: Preview generated HTML document
    else:
        raise ValueError("Must provide arguments")
    cv2.destroyAllWindows()


def consume_camera(interval=25, exit_key=None, preview_detection=False, preview_html=False):
    def callback(image, wireframe):
        preview_elements(image, wireframe.elements)
        return cv2.waitKey(interval)

    def should_exit(key):
        if exit_key is not None:
            return ord(exit_key) == key & 0xFF
        return key != -1

    capture = cv2.VideoCapture(0)
    while True:
        can_read, frame = capture.read()
        if can_read:
            html, key = consume_file(frame, callback) if preview_detection else consume_file(frame)
            # TODO: Write HTML string to file
            # TODO: Preview generated HTML document

            if key is not None and should_exit(key):
                break
        else:
            logging.error("Can't read from camera")
            break
    capture.release()
    cv2.destroyAllWindows()


def consume_file(image, callback=lambda *_, **__: None):
    capture = Capture(image)
    wireframe = Wireframe(capture)

    html = wireframe.html()
    result = callback(capture.image.copy(), wireframe)

    return html, result if result is not None else html


def preview_elements(image, elements, title='', color=(0, 0, 255)):
    for element in elements:
        rectangle = Container(*cv2.boundingRect(element))
        rectangle.draw(image, color)
    cv2.imshow(title, image)


def write_file(content, filename):
    directory = os.path.dirname(filename)
    os.makedirs(directory, exist_ok=True)
    with open(filename, 'w') as file:
        file.write(content)


def preview_preprocessing(capture):
    images = capture.preprocess()
    for index, value in enumerate(images):
        cv2.imshow(index, value)


def open_browser(url):
    if sys.platform == 'darwin':
        subprocess.Popen(f"open {url}", shell=True)
    else:
        webbrowser.open_new_tab(url)


@contextmanager
def temporary_directory():
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        try:
            shutil.rmtree(path)
        except IOError:
            logging.error(f"Failed to clean up temporary directory '{path}'")


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename",
                        dest="filename", help="Path to input image")
    parser.add_argument("-c", "--camera",
                        dest="camera", action='store_true', help="Use camera as source")
    parser.add_argument("-d", "--destination",
                        dest="destination_directory", required=True, help="Destination of generated HTML/JS/CSS files")
    parser.add_argument("-i", "--interactive",
                        dest="interactive", action='store_true', help="Toggle interactive mode")

    parsed_args, unparsed_args = parser.parse_known_args()
    main(parsed_args)
