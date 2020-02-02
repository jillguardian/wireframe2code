from wireframe2code.webpage.elements import Element, Attribute
from wireframe2code.webpage.generator import Widget, Point
from wireframe2code.webpage import generator

if __name__ == "__main__":
    # Sorted
    # widget_list = [
    #     Widget(element=Element("p"), start=Point(0, 0), end=Point(1, 0)),
    #     Widget(element=Element("p"), start=Point(2, 0), end=Point(5, 0)),
    #     Widget(element=Element("p"), start=Point(6, 0), end=Point(7, 1)),
    #     Widget(element=Element("p"), start=Point(0, 1), end=Point(0, 1)),
    #     Widget(element=Element("p"), start=Point(1, 1), end=Point(1, 3)),
    #     Widget(element=Element("p"), start=Point(2, 1), end=Point(3, 3)),
    #     Widget(element=Element("p"), start=Point(4, 1), end=Point(4, 1)),
    #     Widget(element=Element("p"), start=Point(5, 1), end=Point(5, 1)),
    #     Widget(element=Element("p"), start=Point(0, 2), end=Point(0, 3)),
    #     Widget(element=Element("p"), start=Point(4, 2), end=Point(5, 3)),
    #     Widget(element=Element("p"), start=Point(0, 4), end=Point(4, 4)),
    #     Widget(element=Element("p"), start=Point(5, 4), end=Point(5, 4)),
    #     Widget(element=Element("p"), start=Point(0, 5), end=Point(2, 8)),
    #     Widget(element=Element("p"), start=Point(3, 5), end=Point(5, 5))
    # ]

    widget_list = [
        Widget(element=Element("p", content="Hello World!", attributes=[Attribute("class", "h1")]), start=Point(0, 4), end=Point(4, 4)),
        Widget(element=Element("p"), start=Point(0, 5), end=Point(2, 8)),
        Widget(element=Element("p"), start=Point(5, 1)),
        Widget(element=Element("p"), start=Point(1, 1), end=Point(1, 3)),
        Widget(element=Element("p"), start=Point(0, 2), end=Point(0, 3)),
        Widget(element=Element("p"), start=Point(3, 5), end=Point(5, 5)),
        Widget(element=Element("p"), start=Point(0, 0), end=Point(1, 0)),
        Widget(element=Element("p"), start=Point(0, 1)),
        Widget(element=Element("p"), start=Point(2, 1), end=Point(3, 3)),
        Widget(element=Element("p"), start=Point(4, 1)),
        Widget(element=Element("p"), start=Point(4, 2), end=Point(5, 3)),
        Widget(element=Element("p"), start=Point(5, 4)),
        Widget(element=Element("p"), start=Point(2, 0), end=Point(5, 0)),
        Widget(element=Element("p"), start=Point(6, 0), end=Point(7, 1))
    ]

    generator.create(widgets=widget_list, output_directory="../../output")
