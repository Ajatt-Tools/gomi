# Exporter exports note types from Anki to ../templates/
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU GPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import base64
import json
import os
import pathlib
import random
import shutil
from os import DirEntry
from typing import Any

from .ajt_japanese_scripts import strip_ajt_references
from .ankiconnect import invoke, request_model_names
from .common import CardTemplate, NoteType, find_referenced_media_files, select
from .consts import (
    AJT_FILE_NAME_PREFIX,
    BACK_FILENAME,
    CSS_FILENAME,
    FRONT_FILENAME,
    JSON_FILENAME,
    JSON_INDENT,
    NOTE_TYPES_DIR,
    README_FILENAME,
    REPO_MEDIA_DIR,
)
from .typing import GomiOnDiskModelDict


def fetch_card_templates(model_name: str) -> list[CardTemplate]:
    return [
        CardTemplate(name, val["Front"], val["Back"])
        for name, val in invoke("modelTemplates", modelName=model_name).items()
    ]


def fetch_template(model_name: str) -> NoteType:
    return NoteType(
        name=model_name,
        fields=invoke("modelFieldNames", modelName=model_name),
        css=invoke("modelStyling", modelName=model_name)["css"],
        templates=fetch_card_templates(model_name),
    )


def select_model_dir_path(model_name: str) -> pathlib.Path:
    dir_path = NOTE_TYPES_DIR / model_name
    dir_content = frozenset(os.listdir(NOTE_TYPES_DIR))

    if model_name in dir_content:
        ans = input("Template with this name already exists. Overwrite [y/N]? ")
        if ans.lower() != "y":
            while dir_path.name in dir_content:
                dir_path = NOTE_TYPES_DIR / f"{model_name}_{random.randint(0, 9999)}"

    return dir_path


def write_card_templates(model_dir_path: pathlib.Path, templates: list[CardTemplate]) -> None:
    for template in templates:
        dir_path = os.path.join(model_dir_path, template.name)
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        for filename, content in zip((FRONT_FILENAME, BACK_FILENAME), (template.front, template.back)):
            with open(os.path.join(dir_path, filename), "w", encoding="utf8") as f:
                f.write(content)


def format_export(model: NoteType) -> GomiOnDiskModelDict:
    return {
        "modelName": model.name,
        "inOrderFields": model.fields,
        "cardTemplates": [template.name for template in model.templates],
    }


def remove_deleted_templates(model_dir_path: pathlib.Path, templates: list[str]) -> None:
    entry: DirEntry
    for entry in os.scandir(model_dir_path):
        if entry.is_dir() and entry.name not in templates:
            shutil.rmtree(entry.path)


def save_note_type(model: NoteType):
    dir_path = select_model_dir_path(model.name)
    json_path = dir_path / JSON_FILENAME
    css_path = dir_path / CSS_FILENAME
    readme_path = dir_path / README_FILENAME

    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    with open(json_path, "w", encoding="utf8") as f:
        json.dump(format_export(model), f, indent=JSON_INDENT, ensure_ascii=False)

    with open(css_path, "w", encoding="utf8") as f:
        f.write(model.css)

    write_card_templates(dir_path, model.templates)
    remove_deleted_templates(dir_path, [template.name for template in model.templates])

    if not readme_path.is_file():
        with open(readme_path, "w", encoding="utf8") as f:
            f.write(f"# {model.name}\n\n*Description and screenshots here.*")


def is_ajt_japanese_addon_file(file_name: str) -> bool:
    """
    Skip files added by AJT Japanese.
    AJT Japanese will add them when a profile is opened or when the add-on's settings are saved.
    """
    return file_name.startswith(AJT_FILE_NAME_PREFIX)


def save_media_imports(model: NoteType) -> None:
    """
    Save fonts and CSS files referenced in the CSS template to the "media" folder.
    """
    for file_name in find_referenced_media_files(model):
        if is_ajt_japanese_addon_file(file_name):
            # Skip files added by AJT Japanese.
            # AJT Japanese will add them when a profile is opened or when the add-on's settings are saved.
            continue
        if file_b64 := invoke("retrieveMediaFile", filename=file_name):
            full_path = REPO_MEDIA_DIR / file_name
            with open(full_path, "bw") as f:
                f.write(base64.b64decode(file_b64))
            print(f"saved file: '{full_path}'")


def export_note_type() -> None:
    """
    Select a note type in Anki and add save it to the hard drive.
    """
    if model := select(request_model_names()):
        print(f"Selected model: {model}")
        template = fetch_template(model)
        template = strip_ajt_references(template)
        save_note_type(template)
        save_media_imports(template)
        print("Done.")
