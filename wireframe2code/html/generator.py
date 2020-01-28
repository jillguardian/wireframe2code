import webbrowser
from typing import List
from enum import Enum
from wireframe2code.html import output


class Position(Enum):
    COLUMN = 1
    ROW = 2


class Point:
    def __init__(self, column: int, row: int) -> None:
        self.column = column
        self.row = row

    def __str__(self) -> str:
        return "Point{{column={}, row={}}}".format(self.column, self.row)

    def get_position_value(self, position: Position) -> int:
        return self.column if position is Position.COLUMN else self.row


class Widget:
    def __init__(self, start: Point, end: Point = None) -> None:
        self.start = start
        self.end = end if end is not None else start

    def __str__(self) -> str:
        return "Widget{{start={}, end={}}}'".format(self.start, self.end)


def create(widgets: List[Widget], output_directory: str, open_in_browser: bool = True,
           title: str = "Generated HTML Page") -> None:
    sorted_widgets = __sort_widgets(widgets)
    html_code = __get_full_code(body=__get_html_elements(sorted_widgets), title=title,
                                column_count=__get_max_number(sorted_widgets))
    output_file_path = output.to_file(html_code, output_directory)

    if open_in_browser:
        webbrowser.open("file://{}".format(output_file_path))


def __get_span_value(widget: Widget, span_type: Position) -> int:
    return abs(widget.start.get_position_value(span_type) - widget.end.get_position_value(span_type)) + 1


def __get_html_element(widget: Widget) -> str:
    styles = []
    for position in Position:
        span_value = __get_span_value(widget, position)
        if span_value > 1:
            styles.append("grid-{}: {} span;".format(position.name.lower(), span_value))

    return "<div class=\"block\" style=\"{}\"></div>".format("".join(styles))


def __get_html_elements(widgets: List[Widget]) -> str:
    return "\n".join([__get_html_element(widget) for widget in widgets])


def __get_max_number(widgets: List[Widget], span: Position = Position.COLUMN) -> int:
    widget_end_position_value = lambda widget: widget.end.get_position_value(span)
    max_widget = max(widgets, key=lambda widget: widget_end_position_value(widget))
    return widget_end_position_value(max_widget) + 1


def __sort_widgets(widgets: List[Widget]) -> List[Widget]:
    widgets.sort(key=lambda widget: widget.start.row)
    sorted_widgets = []

    for current_row in range(__get_max_number(widgets, Position.ROW)):
        filtered_widgets = []
        for filtered_widget in filter(lambda widget: widget.start.row == current_row, widgets):
            filtered_widgets.append(filtered_widget)

        filtered_widgets.sort(key=lambda widget: widget.start.column)
        sorted_widgets.extend(filtered_widgets)

        for widget in filtered_widgets:
            widgets.remove(widget)

    return sorted_widgets


def __get_full_code(body: str, title: str, column_count: int = 1) -> str:
    return """<!doctype html>
<html lang="en">
   <head>
      <!-- Required meta tags -->
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
      <!-- Bootstrap CSS -->
      <link rel="shortcut icon" href="favicon-torocloud.ico" type="image/x-icon" />
      <link rel="stylesheet" href="bootstrap.min.css">
      <link rel="stylesheet" href="style.css">
      <style>
         .wrapper {{
             display: grid;
             grid-gap: 25px;
             grid-template-columns: repeat({1}, auto);
             grid-template-rows: auto auto auto auto;
             height: 90vh;
             width: 100%;
         }}
         
         .block {{
            background-color: rgb(69, 169, 212);
         }}
      </style>
      <title>{2}</title>
   </head>
   <body>
      <div class="gradient-bg"></div>
      <main role="main" class="container mt-5 text-center">
         <div class="wrapper">
            {0}
         </div>
      </main>
      <script src="bootstrap.min.js"></script>
   </body>
</html>""".format(body, column_count, title)
