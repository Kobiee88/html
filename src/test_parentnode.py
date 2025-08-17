import unittest
from parentnode import ParentNode
from leafnode import LeafNode

class TestParentNode(unittest.TestCase):
    def test_to_html_with_tag_and_children(self):
        child1 = LeafNode("span", "child1")
        child2 = LeafNode("div", "child2")
        parent = ParentNode("section", [child1, child2])
        self.assertEqual(
            parent.to_html(),
            "<section><span>child1</span><div>child2</div></section>"
        )

    def test_to_html_without_tag(self):
        parent = ParentNode(None, [])
        with self.assertRaises(ValueError):
            parent.to_html()

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_grandchildren_and_props(self):
        grandchild_node = LeafNode("a", "grandchild", {"href": "www.example.com"})
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node], {"class": "container"})
        self.assertEqual(
            parent_node.to_html(),
            '<div class="container"><span><a href="www.example.com">grandchild</a></span></div>'
        )