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
        if entry in IGNORE or entry.startswith("."):
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

def main():
    if not os.path.isdir(PRODUCTS_DIR):
        print(f"Error: '{PRODUCTS_DIR}/' was not found.")
        print("Create products/<product-name>/ and place a .md file plus images inside.")
        sys.exit(1)

    folders = sorted(
        d for d in os.listdir(PRODUCTS_DIR)
        if os.path.isdir(os.path.join(PRODUCTS_DIR, d)) and not d.startswith(".")
    )
    if not folders:
        print("No product folders found.")
        sys.exit(1)

    tree = [scan_directory(os.path.join(PRODUCTS_DIR, folder)) for folder in folders]
    with open("tree.json", "w", encoding="utf-8") as file:
        json.dump(tree, file, indent=2, ensure_ascii=False)

    md_count = 0
    image_count = 0
    for root, _, files in os.walk(PRODUCTS_DIR):
        for name in files:
            if name.lower().endswith(".md"):
                md_count += 1
            elif os.path.splitext(name)[1].lower() in IMAGE_EXTS:
                image_count += 1

    print("Zellavie tree built successfully.")
    print(f"Products: {len(tree)}")
    print(f"Markdown files: {md_count}")
    print(f"Images: {image_count}")
    print("Generated: tree.json")

if __name__ == "__main__":
    main()
