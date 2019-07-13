import morpfw
import morpfw.sql
import sqlalchemy as sa
import sqlalchemy_jsonfield as sajson
from .model import PageModel


class Page(morpfw.sql.Base):

    __tablename__ = 'democms_page'

    title = sa.Column(sa.String(length=1024))
    description = sa.Column(sa.Text())
    location = sa.Column(sa.String(length=2048))
    body = sa.Column(sa.Text())
    form_date = sa.Column(sa.String())


class PageStorage(morpfw.SQLStorage):
    model = PageModel
    orm_model = Page
