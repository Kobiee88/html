import unittest
from htmlnode import HTMLNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(props={"class": "test", "id": "unique"})
        self.assertEqual(node.props_to_html(), ' class="test" id="unique"')

    def test_props_to_html2(self):
        node = HTMLNode(props={"style": "color: red;"})
        self.assertEqual(node.props_to_html(), ' style="color: red;"')

    def test_props_to_html_empty(self):
        node = HTMLNode(props={})
        self.assertEqual(node.props_to_html(), "")