# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import dataclasses
import enum
import io
import re

from gomi.common import NoteType

RE_AJT_CSS_IMPORT = re.compile(r'@import url\("_ajt_japanese(?:_(?P<version>\d+\.\d+\.\d+\.\d+))?\.css"\);\n?')
RE_AJT_JS_VERSION_COMMENT = re.compile(r"\s*/\* AJT Japanese JS (?P<version>\d+\.\d+\.\d+\.\d+) \*/\n?")


def find_ajt_japanese_js_import(template_html: str) -> str | None:
    buffer = io.StringIO()

    class Status(enum.Enum):
        none = 0
        found_script = 1
        identified_ajt_script = 2

    status = Status.none

    for line in template_html.splitlines(keepends=True):
        if line.strip() == "<script>":
            status = Status.found_script
        elif re.fullmatch(RE_AJT_JS_VERSION_COMMENT, line) and status == Status.found_script:
            status = Status.identified_ajt_script
            buffer.write("<script>\n")
            buffer.write(line)
        elif line.strip() == "</script>" and status == Status.identified_ajt_script:
            buffer.write(line)
            return buffer.getvalue()
        elif status == Status.identified_ajt_script:
            buffer.write(line)
        else:
            status = Status.none
    return None


def strip_ajt_js(template_html: str) -> str:
    if script := find_ajt_japanese_js_import(template_html):
        return template_html.replace(script, "").strip() + "\n"  # newline at the end of file
    return template_html


def strip_ajt_references(model: NoteType) -> NoteType:
    """
    AJT Japanese adds CSS and JS to every card template registered in its profiles.
    Strip the references because they aren't parts of the note type.
    The add-on will add them again.
    """
    return dataclasses.replace(
        model,
        css=re.sub(RE_AJT_CSS_IMPORT, "", model.css),
        templates=[
            dataclasses.replace(template, front=strip_ajt_js(template.front), back=strip_ajt_js(template.back))
            for template in model.templates
        ],
    )
