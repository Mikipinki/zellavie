#!/usr/bin/env python3
"""Build tree.json for Zellavie from the products directory.

Each immediate subdirectory of products/ is one clothing product.
The product folder may contain one Markdown description file and any
number of common image formats with different dimensions.
"""
import json
import os
import sys

PRODUCTS_DIR = "products"
IGNORE = {".git", ".github", "__pycache__", ".DS_Store", "Thumbs.db",
          "tree.json", "generate_tree.py", ".gitignore", ".nojekyll"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".svg"}


def is_ignored(name):
    """Return True if the file/folder name should be skipped."""
    return name in IGNORE or name.startswith(".")


def scan_directory(path):
    rel = os.path.relpath(path, ".").replace("\\", "/")
    node = {"name": os.path.basename(path), "type": "dir",
            "path": rel, "children": []}
    try:
        entries = sorted(os.listdir(path), key=str.lower)
    except OSError as exc:
        print(f"Warning: cannot read {path}: {exc}")
        return node
    for entry in entries:
        if is_ignored(entry):
            continue
        full = os.path.join(path, entry)
        entry_rel = os.path.relpath(full, ".").replace("\\", "/")
        if os.path.isdir(full):
            node["children"].append(scan_directory(full))
        else:
            node["children"].append({
                "name": entry, "type": "file",
                "path": entry_rel, "download_url": entry_rel
            })
    return node


def count_files(base_dir):
    """Count Markdown and image files, ignoring hidden/ignored entries."""
    md_count = 0
    image_count = 0
    for root, dirs, files in os.walk(base_dir):
        # Prune ignored directories in-place so os.walk skips them
        dirs[:] = [d for d in dirs if not is_ignored(d)]
        for name in files:
            if is_ignored(name):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext == ".md":
                md_count += 1
            elif ext in IMAGE_EXTS:
                image_count += 1
    return md_count, image_count


def main():
    if not os.path.isdir(PRODUCTS_DIR):
        print(f"Error: '{PRODUCTS_DIR}/' was not found.")
        print("Create products/<product-name>/ and place a .md file plus images inside.")
        sys.exit(1)

    folders = sorted(
        d for d in os.listdir(PRODUCTS_DIR)
        if os.path.isdir(os.path.join(PRODUCTS_DIR, d))
        and not is_ignored(d)
    )
    if not folders:
        print("No product folders found.")
        sys.exit(1)

    tree = [scan_directory(os.path.join(PRODUCTS_DIR, folder)) for folder in folders]
    with open("tree.json", "w", encoding="utf-8") as file:
        json.dump(tree, file, indent=2, ensure_ascii=False)

    md_count, image_count = count_files(PRODUCTS_DIR)

    print("Zellavie tree built successfully.")
    print(f"Products: {len(tree)}")
    print(f"Markdown files: {md_count}")
    print(f"Images: {image_count}")
    print("Generated: tree.json")


if __name__ == "__main__":
    main()
