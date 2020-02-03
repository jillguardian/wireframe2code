import contextlib
import logging
import shutil
import tempfile
from contextlib import contextmanager
import os


@contextmanager
def tempdir():
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        try:
            shutil.rmtree(path)
        except IOError:
            logging.error(f"Failed to clean up temporary directory '{path}'")


def write(filename: str, content: str):
    directory = os.path.dirname(filename)
    os.makedirs(directory, exist_ok=True)
    with open(filename, 'w') as file:
        file.write(content)


def read(filename):
    if not os.path.isfile(filename):
        raise IOError(f"'{filename}' either does not exist, or is not a file")
    with open(filename, 'r') as file:
        return file.read()


def copy(files, destination):
    directory = os.path.dirname(destination)
    for file in files:
        logging.debug(f"Copying '{file.name}' to '{directory}'")
        shutil.copy(file, directory)
