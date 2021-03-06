from ..app import App
from morpfw.authn.pas.group.typeinfo import get_typeinfo as get_basetypeinfo
from .model import GroupCollectionUI, GroupModelUI
from .path import get_group_collection_ui, get_group_model_ui


@App.typeinfo('morpfw.pas.group')
def get_typeinfo(request):
    ti = get_basetypeinfo(request)
    ti['collection_ui'] = GroupCollectionUI
    ti['model_ui'] = GroupModelUI
    ti['collection_ui_factory'] = get_group_collection_ui
    ti['model_ui_factory'] = get_group_model_ui
    return ti
