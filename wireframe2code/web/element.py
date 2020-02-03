from enum import Enum
from typing import Set


class Attribute:

    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'{self.name}="{self.value}"'


class Tag(Enum):

    IMAGE = "img", True
    PARAGRAPH = "p", False
    BUTTON = "button", False
    INPUT = "input", False
    DIV = "div", False

    def __init__(self, tag_name: str, self_closing: bool):
        self.tag_name = tag_name
        self.self_closing = self_closing

    @classmethod
    def all(cls):
        return {e.name for e in cls}

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class Element:

    def __init__(self, tag: Tag, attributes: Set[Attribute] = None, content=None):
        self.tag = tag
        self.attributes = [] if attributes is None else attributes
        self.content = content
