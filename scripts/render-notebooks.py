#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Ref: https://www.datisticsblog.com/2018/08/post_with_jupyter/
# https://github.com/dfm-io/dfm.io/blob/main/scripts/render-notebooks

import re
import shutil
import tempfile
from pathlib import Path
from subprocess import CalledProcessError, check_call

import nbformat
import yaml
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import Preprocessor
from traitlets.config import Config

inline_pat = re.compile(r"\$(.+?)\$", flags=re.M | re.S)
block_pat = re.compile(r"\$\$(.+?)\$\$", flags=re.M | re.S)
this_path = Path(__file__).parent


class CustomPreprocessor(Preprocessor):
    def preprocess(self, nb, resources):
        for index, cell in enumerate(nb.cells):
            if cell.cell_type == "code" and not cell.source:
                nb.cells.pop(index)
            elif cell.cell_type == "code" and cell.source.startswith("%matplotlib"):
                nb.cells.pop(index)
            else:
                nb.cells[index], resources = self.preprocess_cell(
                    cell, resources, index
                )
        return nb, resources

    def preprocess_cell(self, cell, resources, cell_index):
        if cell.cell_type == "code":
            cell.source = cell.source.strip()
        else:
            text = "$$".join(
                inline_pat.sub(r"$\1$", t) for t in cell.source.split("$$")
            )
            cell.source = block_pat.sub(r"<div>$$\1$$</div>", text)
        return cell, resources


def render_notebook(path, metadata):
    meta = yaml.safe_load(metadata)
    slug = meta["slug"]

    with path.open() as fp:
        notebook = nbformat.read(fp, as_version=4)

    c = Config()
    c.MarkdownExporter.preprocessors = [CustomPreprocessor]
    markdown_exporter = MarkdownExporter(
        config=c, template_file=str(this_path / "custom_md.j2")
    )
    markdown, resources = markdown_exporter.from_notebook_node(notebook)
    markdown = f"---\n{metadata.strip()}\n---\n\n" + markdown

    output = Path(f"./content/blog/notebook.{slug}.md")
    with output.open("w") as f:
        f.write(markdown)

    if "outputs" in resources.keys():
        out_path = Path(f"./static/blog/{slug}")
        out_path.mkdir(parents=True, exist_ok=True)

        for key in resources["outputs"].keys():
            with (out_path / key).open("wb") as f:
                f.write(resources["outputs"][key])

        for filename in meta.get("other_files", []):
            file_path = path.parent / filename
            shutil.copyfile(file_path, out_path / filename)


def process_repo(repo):
    name = repo["full_name"]
    if not name.split("/")[1].startswith("post--"):
        return

    print(f"===> Rendering {name} <===")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            check_call(
                f"git clone --depth 1  --branch executed https://github.com/{name}.git {tmp}".split()
            )

        except CalledProcessError:
            print(f"Failed to clone {name}")
            return

        repo = Path(tmp)
        with (repo / "metadata.yml").open("r") as f:
            metadata = f.read()
        render_notebook(repo / "post.ipynb", metadata)


if __name__ == "__main__":
    import requests

    url = "https://api.github.com/orgs/adrn-blog/repos"
    with requests.Session() as s:
        while True:
            r = s.get(url)
            r.raise_for_status()
            data = r.json()
            list(map(process_repo, data))
            url = r.links.get("next", {}).get("url")
            if not url:
                break
