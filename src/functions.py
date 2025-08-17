import re

from textnode import TextNode, TextType
from blocks import block_to_block_type, BlockType
from leafnode import LeafNode
from parentnode import ParentNode

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes

def extract_markdown_images_with_alt_text(text):
    result = []
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    for match in matches:
        alt_text, url = match
        result.append((alt_text, url))
    return result

def extract_markdown_links(text):
    result = []
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    for match in matches:
        link_text, url = match
        result.append((link_text, url))
    return result

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if isinstance(node, TextNode):
            if node.text_type != TextType.TEXT:
                new_nodes.append(node)
            else:
                parts = extract_markdown_images_with_alt_text(node.text)
                remaining_text = node.text
                for alt_text, url in parts:
                    tmp_parts = remaining_text.split(f"![{alt_text}]({url})", 1)
                    new_nodes.append(TextNode(tmp_parts[0], TextType.TEXT))
                    remaining_text = tmp_parts[1] if len(tmp_parts) > 1 else ""
                    new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
                if len(remaining_text) > 0:
                    new_nodes.append(TextNode(remaining_text, TextType.TEXT))
        else:
            raise TypeError("All nodes must be of type TextNode")
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if isinstance(node, TextNode):
            if node.text_type != TextType.TEXT:
                new_nodes.append(node)
            else:
                parts = extract_markdown_links(node.text)
                remaining_text = node.text
                for link_text, url in parts:
                    tmp_parts = remaining_text.split(f"[{link_text}]({url})", 1)
                    new_nodes.append(TextNode(tmp_parts[0], TextType.TEXT))
                    remaining_text = tmp_parts[1] if len(tmp_parts) > 1 else ""
                    new_nodes.append(TextNode(link_text, TextType.LINK, url))
                if len(remaining_text) > 0:
                    new_nodes.append(TextNode(remaining_text, TextType.TEXT))
        else:
            raise TypeError("All nodes must be of type TextNode")
    return new_nodes

def text_to_textnodes(text):
    return split_nodes_link(split_nodes_image(split_nodes_delimiter(split_nodes_delimiter(split_nodes_delimiter([TextNode(text, TextType.TEXT)], "**", TextType.BOLD), "_", TextType.ITALIC), "`", TextType.CODE)))

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    filtered_blocks = []
    for block in blocks:
        if block == "":
            continue
        block = block.strip()
        filtered_blocks.append(block)
    return filtered_blocks


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.ORDERED_LIST:
        return olist_to_html_node(block)
    if block_type == BlockType.UNORDERED_LIST:
        return ulist_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    raise ValueError("invalid block type")


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = TextNode.text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("invalid code block")
    text = block[4:-3]
    raw_text_node = TextNode(text, TextType.TEXT)
    child = TextNode.text_node_to_html_node(raw_text_node)
    code = ParentNode("code", [child])
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)
'''
def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    html_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        match block_type:
            case BlockType.PARAGRAPH:
                if len(block.strip()) > 0:
                    #block = " ".join(block.split("\n").strip())
                    lines = block.split("\n")
                    block = " ".join(line.strip() for line in lines if line.strip())
                    children = text_to_children(block)
                    if children:
                        html_nodes.append(ParentNode("p", children))
                    else:
                        # If no children, treat as a plain text LeafNode
                        html_nodes.append(LeafNode("p", block))
            case BlockType.HEADING:
                level = block.count("#")
                tag = f"h{level}"
                content = block[level:].strip()
                children = text_to_children(content)
                if children:
                    html_nodes.append(ParentNode(tag, children))
                else:
                    # If no children, treat as a plain text LeafNode
                    html_nodes.append(LeafNode(tag, content))
            case BlockType.CODE:
                code_content = block.strip("`")
                #lines = code_content.split("\n")
                #code_content = " ".join(line.strip() for line in lines if line.strip())
                children = []
                children.append(LeafNode("code", code_content.strip()))
                html_nodes.append(ParentNode("pre", children))
            case BlockType.QUOTE:
                quote_content = block[1:].strip()
                children = text_to_children(quote_content)
                if children:
                    html_nodes.append(ParentNode("blockquote", children))
                else:
                    # If no children, treat as a plain text LeafNode
                    html_nodes.append(LeafNode("blockquote", quote_content))
            case BlockType.UNORDERED_LIST:
                items = [item.strip() for item in block.split("\n") if item.startswith("- ")]
                list_items = []
                for item in items:
                    children = text_to_children(item[2:])
                    if children:
                        list_items.append(ParentNode("li", children))
                    else:
                        list_items.append(LeafNode("li", item[2:]))
                html_nodes.append(ParentNode("ul", list_items))
            case BlockType.ORDERED_LIST:
                items = [item.strip() for item in block.split("\n")]
                list_items = []
                for item in items:
                    children = text_to_children(item[3:])
                    if children:
                        list_items.append(ParentNode("li", children))
                    else:
                        list_items.append(LeafNode("li", item[3:]))
                html_nodes.append(ParentNode("ol", list_items))
            case _:
                raise ValueError(f"Unsupported block type: {block_type}")
    return ParentNode("div", html_nodes) if html_nodes else None

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = [TextNode.text_node_to_html_node(node) for node in text_nodes]
    return html_nodes if html_nodes else None
'''
