import morepath
import html
import deform
from morpfw.crud import permission as crudperms
from ..model import CollectionUI, ModelUI
from ...app import App
from ...util import dataclass_to_colander


@App.view(model=CollectionUI)
def collection_index(context, request):
    return morepath.redirect(request.link(context, '+%s' % context.default_view))


@App.view(model=ModelUI)
def model_index(context, request):
    return morepath.redirect(request.link(context, '+%s' % context.default_view))


@App.html(model=ModelUI, name='view', template='master/crud/form.pt', permission=crudperms.View)
def view(context, request):
    formschema = dataclass_to_colander(
        context.model.schema,
        include_fields=context.view_include_fields,
        exclude_fields=context.view_exclude_fields)
    data = context.model.data.as_dict()
    sm = context.model.statemachine()
    if sm:
        triggers = [i for i in sm._machine.get_triggers(
            sm.state) if not i.startswith('to_')]
    else:
        triggers = None
    return {
        'page_title': 'View %s' % html.escape(str(context.model.__class__.__name__)),
        'form_title': 'View',
        'form': deform.Form(formschema(), buttons=('Submit',)),
        'form_data': data,
        'readonly': True,
        'transitions': triggers
    }


@App.view(model=ModelUI, name='statemachine', permission=crudperms.Edit, request_method='POST')
def statemachine(context, request):
    transition = request.POST.get('transition', None)
    sm = context.model.statemachine()
    if transition:
        attr = getattr(sm, transition, None)
        if attr:
            attr()
            request.notify('success', 'State updated',
                           'Object state have been updated')
            return morepath.redirect(request.link(context))
    request.notify('error', 'Unknown transition',
                   'Transition "%s" is unknown' % transition)
    return morepath.redirect(request.link(context))
