import morpfw
from dataclasses import dataclass
import typing


@dataclass
class PageSchema(morpfw.Schema):

    title: typing.Optional[str] = None
    description: typing.Optional[str] = None
    location: typing.Optional[str] = None
    body: typing.Optional[str] = None
    form_date: typing.Optional[str] = None
