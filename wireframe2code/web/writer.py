import os
from pathlib import Path
from typing import List

from sketch.wireframe import Widget
from sketch.wireframe import Wireframe
from file import write
from itertools import groupby

from jinja2 import Template
from jinja2 import Environment
from jinja2 import FileSystemLoader
from shutil import copy2


def sort(widgets):
    """
    :param widgets: widgets to sort
    :return: widgets sorted by column and row
    """
    def starting_row(widget):
        return widget.location.start[1]

    def starting_column(widget):
        return widget.location.start[0]

    widgets = list(widgets)
    widgets.sort(key=starting_row)

    sorted_widgets = []

    for row, columns in groupby(widgets, starting_row):
        columns = list(columns)
        columns.sort(key=starting_column)
        sorted_widgets.extend(columns)

    return sorted_widgets


class Html:

    def __init__(self, directory):
        self.directory = Path(directory)

    @staticmethod
    def __resources_directory():
        base_path = Path(__file__).parent
        return (base_path / "resources").resolve()

    @staticmethod
    def __template_filename():
        return 'index.html'

    @classmethod
    def __assets(cls):
        filenames = {
            'bootstrap.min.css',
            'bootstrap.min.js',
            'favicon.ico',
            'style.css'
        }

        base = cls.__resources_directory()
        return {(base / filename).resolve() for filename in filenames}

    def write(self, wireframe: Wireframe):

        def create_directory():
            self.directory.mkdir(parents=True, exist_ok=True)

        def generate_html():
            widgets = sort(wireframe.widgets())
            rows, columns = wireframe.shape()

            file_loader = FileSystemLoader(self.__resources_directory())
            environment = Environment(loader=file_loader)
            environment.trim_blocks = True

            template = environment.get_template(self.__template_filename())
            return template.render(widgets=widgets, rows=rows, columns=columns)

        def write_html():
            filename = (self.directory / 'index.html').resolve()
            with open(filename, 'w') as file:
                file.write(html)

        def copy_assets():
            assets = self.__assets()
            for asset in assets:
                copy2(asset, self.directory)

        create_directory()
        html = generate_html()
        write_html()
        copy_assets()

