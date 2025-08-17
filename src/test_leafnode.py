import unittest
from leafnode import LeafNode

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
    
    def test_to_html_with_value(self):
        node = LeafNode("p", "This is a paragraph.")
        self.assertEqual(node.to_html(), "<p>This is a paragraph.</p>")

    def test_to_html_with_props(self):
        node = LeafNode("div", "Content", {"class": "container"})
        self.assertEqual(node.to_html(), '<div class="container">Content</div>')

    def test_to_html_without_value(self):
        node = LeafNode("span", None)
        with self.assertRaises(ValueError):
            node.to_html()