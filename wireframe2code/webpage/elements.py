from typing import List


class Attribute:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def to_string(self) -> str:
        name = self.name
        value = self.value

        return f"{name}=\"{value}\""


class Element:
    def __init__(self, name: str, has_body: bool = True, attributes: List[Attribute] = None, content=None):
        self.name = name
        self.has_body = has_body
        self.content = content
        self.attributes = [] if attributes is None else attributes

    def to_string(self) -> str:
        name = self.name
        has_body = self.has_body
        content = self.content
        attributes = self.attributes

        if has_body:
            closing_tag = ">"
            if content:
                closing_tag += content
            closing_tag += f"</{name}>"
        else:
            closing_tag = " />"

        element = f"<{name}"
        if len(attributes) is not 0:
            element += " " + " ".join([attribute.to_string() for attribute in self.attributes])

        element += closing_tag
        return element
