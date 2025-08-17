import os
import shutil

from functions import markdown_to_html_node

def main():
    init_file_copy("./static", "./public")
    #generate_page("./content/index.md", "./template.html", "./public/index.html")
    generate_pages_recursive("./content", "./template.html", "./public", "./content")

def init_file_copy(source, destination):
    if not os.path.exists(source):
        print(f"Source directory {source} does not exist.")
        return
    delete_directory_and_subdirectories(destination)
    copy_files_from(source, destination)

def copy_files_from(source, destination):
    if not os.path.exists(destination):
        os.makedirs(destination)
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(destination, item)
        if os.path.isdir(s):
            copy_files_from(s, d)
        else:
            shutil.copy2(s, d)

def delete_directory_and_subdirectories(path):
    if os.path.exists(path) and os.path.isdir(path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                delete_directory_and_subdirectories(item_path)
            else:
                os.remove(item_path)
        os.rmdir(path)
    else:
        print(f"Path {path} does not exist or is not a directory.")

def extract_title(markdown):
    lines = markdown.splitlines()
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    return None

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} using template {template_path} to {dest_path}")
    with open(from_path, 'r') as f:
        markdown_content = f.read()
    with open(template_path, 'r') as template_file:
        template_content = template_file.read()
    title = extract_title(markdown_content)
    html_content = markdown_to_html_node(markdown_content).to_html()
    template_content = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path))
    with open(dest_path, 'w') as dest_file:
        dest_file.write(template_content)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, root_content_dir=None):
    if root_content_dir is None:
        root_content_dir = dir_path_content
    for item in os.listdir(dir_path_content):
        item_path = os.path.join(dir_path_content, item)
        if os.path.isdir(item_path):
            generate_pages_recursive(item_path, template_path, dest_dir_path, root_content_dir)
        elif item.endswith('.md'):
            relative_path = os.path.relpath(item_path, root_content_dir)
            dest_path = os.path.join(dest_dir_path, relative_path.replace('.md', '.html'))
            if not os.path.exists(os.path.dirname(dest_path)):
                os.makedirs(os.path.dirname(dest_path))
            generate_page(item_path, template_path, dest_path)

main()