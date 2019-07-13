from ..app import App
from .modelui import PageModelUI, PageCollectionUI
import rulez
import morepath
import html
import deform
from morpfw.crud import permission as crudperms
from morpcc.util import dataclass_to_colander
from datetime import date

@App.html(model=PageCollectionUI, name='create', template='master/simple-form.pt',
          permission=crudperms.Create)
def create(context, request):
    formschema = dataclass_to_colander(
        context.collection.schema, include_fields=context.create_include_fields,
        exclude_fields=context.create_exclude_fields)
    return {
        'page_title': 'Create %s' % html.escape(
            str(context.collection.__class__.__name__.replace('Collection', ''))),
        'form_title': 'Create',
        'form': deform.Form(formschema(), buttons=('Submit',)),
    }


@App.html(model=PageCollectionUI, name='create', template='master/simple-form.pt',
          permission=crudperms.Create, request_method='POST')
def process_create(context, request):
    formschema = dataclass_to_colander(
        context.collection.schema, include_fields=context.create_include_fields,
        exclude_fields=context.create_exclude_fields)

    controls = list(request.POST.items())
    form = deform.Form(formschema(), buttons=('Submit', ))

    failed = False
    try:
        data = form.validate(controls)
    except deform.ValidationFailure as e:
        form = e
        failed = True

    if not failed:
        today = date.today().isoformat()
        pagecol = context.collection
        objs = pagecol.search(query=rulez.field['form_date'] == 'not today date' and rulez.field['creator'] == request.identity.userid) # should not return results
        if objs:
            failed = True
            return {
                'page_title': 'Create %s' % html.escape(
                    str(context.collection.__class__.__name__.replace('Collection', ''))),
                'form_title': 'Create',
                'form': form,
            }
        else:
            data['form_date'] = today
            obj = context.collection.create(data)
        return morepath.redirect(request.link(context.modelui_class(request, obj, context)))

    return {
        'page_title': 'Create %s' % html.escape(
            str(context.collection.__class__.__name__.replace('Collection', ''))),
        'form_title': 'Create',
        'form': form,
    }