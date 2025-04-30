# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import typing


class GomiOnDiskModelDict(typing.TypedDict):
    """
    Model JSON stored on disk.
    """

    modelName: str
    inOrderFields: list[str]
    cardTemplates: list[str]  # list of names


class AnkiConnectCardTemplateDict(typing.TypedDict):
    Name: str
    Front: str
    Back: str


class AnkiConnectModelDict(typing.TypedDict):
    modelName: str
    inOrderFields: list[str]
    css: str
    isCloze: typing.NotRequired[bool]  # isCloze is used when CSS is not specified.
    cardTemplates: list[AnkiConnectCardTemplateDict]
