# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU GPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import dataclasses
import functools
import re
from collections.abc import Callable, Hashable, Sequence
from dataclasses import dataclass
from typing import Any

from .consts import NOTE_TYPES_DIR, REPO_MEDIA_DIR

RE_MEDIA_IMPORT = re.compile(r"url\([\"']([^\"']+\.(?:[ot]tf|woff\d?|css))[\"']\)", flags=re.IGNORECASE)
RE_JS_IMPORT = re.compile(r"<script [^<>]*src=[\"']([^\"']+\.js)[\"']></script>", flags=re.IGNORECASE)


class ANTPError(Exception):
    pass


@dataclass(frozen=True)
class CardTemplate:
    name: str
    front: str
    back: str


@dataclass(frozen=True)
class NoteType:
    name: str
    fields: list[str]
    css: str
    templates: list[CardTemplate]

    def rename(self, new_name: str):
        return dataclasses.replace(self, name=new_name)


def read_num(msg: str = "Input number: ", min_val: int = 0, max_val: int | None = None) -> int:
    try:
        resp = int(input(msg))
    except ValueError as ex:
        raise ANTPError(ex) from ex
    if resp < min_val or (max_val and resp > max_val):
        raise ANTPError("Value out of range.")
    return resp


def select(items: list[str], msg: str = "Select item number: ") -> str | None:
    if not items:
        print("Nothing to show.")
        return None

    for idx, model in enumerate(items):
        print(f"{idx}: {model}")
    print()

    idx = read_num(msg, max_val=len(items) - 1)
    return items[idx]


def as_unique[Ret: Hashable](fn: Callable[[Any], Sequence[Ret]]) -> Callable[[Any], frozenset[Ret]]:
    @functools.wraps(fn)
    def decorator(*args, **kwargs) -> frozenset[Ret]:
        return frozenset(fn(*args, **kwargs))

    return decorator


@as_unique
def find_js_files(templates: list[CardTemplate]) -> list[str]:
    return re.findall(
        pattern=RE_JS_IMPORT,
        string="\n".join(f"{template.front}\n{template.back}" for template in templates),
    )


@as_unique
def find_url_imports(model_css: str) -> list[str]:
    return re.findall(
        pattern=RE_MEDIA_IMPORT,
        string=model_css,
    )


def find_referenced_media_files(model: NoteType) -> frozenset[str]:
    """
    Find files referenced by the note type's templates. E.g., fonts, CSS files, JS scripts.
    """
    return find_url_imports(model.css) | find_js_files(model.templates)


def init():
    for path in (NOTE_TYPES_DIR, REPO_MEDIA_DIR):
        path.mkdir(exist_ok=True)
