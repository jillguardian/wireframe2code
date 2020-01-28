import webbrowser
from typing import List
from enum import Enum
from wireframe2code.html.output_generator import output


class Span(Enum):
    COLUMN = lambda point: point.x
    ROW = lambda point: point.y


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return "Point{{x={}, y={}}}".format(self.x, self.y)


class Widget:
    def __init__(self, start: Point, end: Point = None):
        self.start = start
        self.end = end if end is not None else start

    def __str__(self):
        return "Widget{{start={}, end={}}}'".format(self.start, self.end)


def __convert(widget: Widget) -> str:
    style = ""

    col_span = __get_span(widget, Span.COLUMN)
    if col_span > 1:
        style += "grid-column: {} span;".format(col_span)

    row_span = __get_span(widget, Span.ROW)
    if row_span > 1:
        style += "grid-row: {} span;".format(row_span)

    return "<div class=\"block\" style=\"{}\"></div>".format(style)


def __get_max_number(widgets: List[Widget], span: Span = Span.COLUMN) -> int:
    return span(max(widgets, key=lambda widget: span(widget.end)).end) + 1


def __to_code(widgets: List[Widget]) -> str:
    return "\n".join([__convert(widget) for widget in widgets])


def __get_full_code(body: str, column_count: int = 1) -> str:
    return """<!doctype html>
<html lang="en">
   <head>
      <!-- Required meta tags -->
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
      <!-- Bootstrap CSS -->
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
            background-color: red;
         }}
      </style>
      <title>Generated HTML Page</title>
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
</html>""".format(body, column_count)


def __get_span(widget: Widget, span_type: Span) -> int:
    return abs(span_type(widget.start) - span_type(widget.end)) + 1


def __sort_widgets(widgets: List[Widget]) -> List[Widget]:
    widgets.sort(key=lambda a: a.start.y)
    final = []

    for current in range(__get_max_number(widgets, Span.ROW)):
        filtered = []
        it = filter(lambda a: a.start.y == current, widgets)
        for o in it:
            filtered.append(o)

        filtered.sort(key=lambda a: a.start.x)
        final.extend(filtered)

        for x in filtered:
            widgets.remove(x)

    return final


if __name__ == "__main__":
    # widget_list = [
    #     Widget(Point(0, 0), Point(1, 0)),
    #     Widget(Point(2, 0), Point(5, 0)),
    #     Widget(Point(0, 1)),
    #     Widget(Point(1, 1), Point(1, 3)),
    #     Widget(Point(2, 1), Point(3, 3)),
    #     Widget(Point(4, 1)),
    #     Widget(Point(5, 1)),
    #     Widget(Point(0, 2), Point(0, 3)),
    #     Widget(Point(4, 2), Point(5, 3)),
    #     Widget(Point(0, 4), Point(4, 4)),
    #     Widget(Point(5, 4)),
    #     Widget(Point(0, 5), Point(2, 8)),
    #     Widget(Point(3, 5), Point(5, 5))
    # ]
    widget_list = [
        Widget(Point(0, 4), Point(4, 4)),
        Widget(Point(0, 5), Point(2, 8)),
        Widget(Point(5, 1)),
        Widget(Point(1, 1), Point(1, 3)),
        Widget(Point(0, 2), Point(0, 3)),
        Widget(Point(3, 5), Point(5, 5)),
        Widget(Point(0, 0), Point(1, 0)),
        Widget(Point(0, 1)),
        Widget(Point(2, 1), Point(3, 3)),
        Widget(Point(4, 1)),
        Widget(Point(4, 2), Point(5, 3)),
        Widget(Point(5, 4)),
        Widget(Point(2, 0), Point(5, 0))
    ]
    widget_list = __sort_widgets(widget_list)
    code = __get_full_code(__to_code(widget_list), __get_max_number(widget_list))
    file_path = output(code, "../output")
    webbrowser.open("file://{}".format(file_path))
