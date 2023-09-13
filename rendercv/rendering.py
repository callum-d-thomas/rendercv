"""This module implements LaTeX file generation and LaTeX runner utilities for RenderCV.
"""
import os
import subprocess

import os
import json
import logging
import re

from jinja2 import Environment, FileSystemLoader, PackageLoader

import rendercv.templates


def markdown_to_latex(markdown_string: str) -> str:
    """Convert a markdown string to LaTeX.

    Example:
        >>> markdown_to_latex("This is a **bold** text with an [*italic link*](https://google.com).")
        "This is a \\textbf{bold} text with a \\hrefExternal{https://google.com}{\\textit{link}}."

    Args:
        value (str): The markdown string to convert.

    Returns:
        str: The LaTeX string.
    """
    if not isinstance(markdown_string, str):
        raise ValueError("markdown_to_latex should only be used on strings!")

    # convert links
    links = re.findall(r"\[([^\]\[]*)\]\((.*?)\)", markdown_string)
    if links is not None:
        for link in links:
            link_text = link[0]
            link_url = link[1]

            old_link_string = f"[{link_text}]({link_url})"
            new_link_string = "\\hrefExternal{" + link_url + "}{" + link_text + "}"

            markdown_string = markdown_string.replace(old_link_string, new_link_string)

    # convert bold
    bolds = re.findall(r"\*\*([^\*]*)\*\*", markdown_string)
    if bolds is not None:
        for bold_text in bolds:
            old_bold_text = f"**{bold_text}**"
            new_bold_text = "\\textbf{" + bold_text + "}"

            markdown_string = markdown_string.replace(old_bold_text, new_bold_text)

    # convert italic
    italics = re.findall(r"\*([^\*]*)\*", markdown_string)
    if italics is not None:
        for italic_text in italics:
            old_italic_text = f"*{italic_text}*"
            new_italic_text = "\\textit{" + italic_text + "}"

            markdown_string = markdown_string.replace(old_italic_text, new_italic_text)

    latex_string = markdown_string

    return latex_string


def markdown_url_to_url(value: str) -> bool:
    """Convert a markdown link to a normal string URL.

    Example:
        >>> markdown_url_to_url("[Google](https://google.com)")
        "https://google.com"

    Args:
        value (str): The markdown link to convert.

    Returns:
        str: The URL as a string.
    """
    if not isinstance(value, str):
        raise ValueError("markdown_to_latex should only be used on strings!")

    link = re.search(r"\[(.*)\]\((.*?)\)", value)
    if link is not None:
        url = link.groups()[1]
        return url
    else:
        raise ValueError("markdown_url_to_url should only be used on markdown links!")


def render_template(data):
    """Render the template using the given data.

    Example:
        >>> render_template(data)
        

    """
    # templates_directory = os.path.dirname(os.path.dirname())

    # create a Jinja2 environment:
    environment = Environment(
        loader=PackageLoader("rendercv", "templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # add new functions to the environment:
    environment.globals.update(str=str)

    # set custom delimiters for LaTeX templating:
    environment.block_start_string = "((*"
    environment.block_end_string = "*))"
    environment.variable_start_string = "<<"
    environment.variable_end_string = ">>"
    environment.comment_start_string = "((#"
    environment.comment_end_string = "#))"

    # load the template:
    theme = data.design.theme
    template = environment.get_template(f"{theme}.tex.j2")

    # add custom filters:
    environment.filters["markdown_to_latex"] = markdown_to_latex
    environment.filters["markdown_url_to_url"] = markdown_url_to_url

    output_latex_file = template.render(design=data.design.options, cv=data.cv)

    # Create an output file and write the rendered LaTeX code to it:
    output_file_path = os.path.join(os.getcwd(), "tests", "outputs", "test.tex")
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, "w") as file:
        file.write(output_latex_file)

    return output_file_path


def run_latex(latexFilePath):
    """
    Run LuaLateX on the given LaTeX file and generate a PDF.

    :param latexFilePath: The path to the LaTeX file to compile.
    :type latexFilePath: str
    :return: None
    :rtype: None
    """
    latexFilePath = os.path.normpath(latexFilePath)
    latexFile = os.path.basename(latexFilePath)

    if os.name == "nt":
        # remove all files except the .tex file
        for file in os.listdir(os.path.dirname(latexFilePath)):
            if file.endswith(".tex"):
                continue
            os.remove(os.path.join(os.path.dirname(latexFilePath), file))

        tinytexPath = os.path.join(
            os.path.dirname(__file__),
            "vendor",
            "TinyTeX",
            "bin",
            "windows",
        )
        subprocess.run(
            [
                f"{tinytexPath}\\latexmk.exe",
                "-lualatex",
                # "-c",
                f"{latexFile}",
                "-synctex=1",
                "-interaction=nonstopmode",
                "-file-line-error",
            ],
            cwd=os.path.dirname(latexFilePath),
        )
    else:
        print("Only Windows is supported for now.")