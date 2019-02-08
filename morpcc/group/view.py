import morepath
from .model import GroupModelUI
from ..app import App
from morpfw.crud import permission as crudperms

@App.html(model=GroupModelUI, name='view', template='master/group/view.pt', permission=crudperms.View)
def view(context, request):
    pass

@App.html(model=GroupModelUI, name='delete', template='master/group/delete.pt', permission=crudperms.Delete)
def delete(context, request):
    pass

@App.html(model=GroupModelUI, name='delete', template='master/group/delete.pt',
          permission=crudperms.Delete, request_method='POST')
def process_delete(context, request):
    context.model.delete()
    return morepath.redirect(request.link(context.collection_ui))