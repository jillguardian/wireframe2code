from unittest import TestCase

from webpage.elements import Attribute, Element


class AttributeTest(TestCase):
    def test_attribute_to_string(self):
        attribute = Attribute('class', 'col-xs-6').to_string()
        self.assertEquals(attribute, 'class="col-xs-6"')


class ElementTest(TestCase):
    def test_no_attribute_to_string(self):
        element = Element(name='div').to_string()
        self.assertEquals(element, '<div></div>')

    def test_single_attribute_to_string(self):
        element = Element(name='p', attributes=[Attribute('class', 'col-xs-6')]).to_string()
        self.assertEquals(element, '<p class="col-xs-6"></p>')

    def test_multiple_attributes_to_string(self):
        element = Element(name='p', attributes=[Attribute('class', 'col-xs-6'), Attribute('id', 'my-element')])\
            .to_string()
        self.assertEquals(element, '<p class="col-xs-6" id="my-element"></p>')

    def test_element_no_body(self):
        element = Element(name='img', attributes=[Attribute('src', 'hello.png')], has_body=False).to_string()
        self.assertEquals(element, '<img src="hello.png" />')

    def test_no_attribute_no_body(self):
        element = Element(name='br', has_body=False).to_string()
        self.assertEquals(element, '<br />')

    def test_element_with_content(self):
        element = Element(name='p', content="Hello World!").to_string()
        self.assertEquals(element, '<p>Hello World!</p>')
