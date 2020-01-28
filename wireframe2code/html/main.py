from wireframe2code.html.generator import Widget, Point
from wireframe2code.html import generator

if __name__ == "__main__":
    # Sorted
    # widget_list = [
    #     Widget(Point(0, 0), Point(1, 0)),
    #     Widget(Point(2, 0), Point(5, 0)),
    #     Widget(Point(6, 0), Point(7, 1)),
    #     Widget(Point(0, 1), Point(0, 1)),
    #     Widget(Point(1, 1), Point(1, 3)),
    #     Widget(Point(2, 1), Point(3, 3)),
    #     Widget(Point(4, 1), Point(4, 1)),
    #     Widget(Point(5, 1), Point(5, 1)),
    #     Widget(Point(0, 2), Point(0, 3)),
    #     Widget(Point(4, 2), Point(5, 3)),
    #     Widget(Point(0, 4), Point(4, 4)),
    #     Widget(Point(5, 4), Point(5, 4)),
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
        Widget(Point(2, 0), Point(5, 0)),
        Widget(Point(6, 0), Point(7, 1))
    ]

    generator.create(widgets=widget_list, output_directory="../../output")
