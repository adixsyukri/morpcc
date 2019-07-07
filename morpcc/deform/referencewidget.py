from deform.widget import Widget, SelectWidget
from deform.compat import string_types
from colander import null
from colander import Invalid
from morpfw.authn.pas.user.path import get_user_collection
from ..users.model import UserModelUI
from ..users.path import get_user_collection_ui


class ReferenceWidget(SelectWidget):
    template = 'reference'
    readonly_template = 'readonly/reference'
    null_value = ""
    values = ()
    multiple = False

    def __init__(self, resource_type, term_field, value_field, **kwargs):
        self.resource_type = resource_type
        self.term_field = term_field
        self.value_field = value_field
        super().__init__(**kwargs)

    def deserialize(self, *args, **kwargs):
        result = super().deserialize(*args, **kwargs)
        return result

    def get_resource_search_url(self, context, request):
        return request.link(context, '+term-search?resource_type=%s&term_field=%s&value_field=%s' % (
            self.resource_type, self.term_field, self.value_field))

    def get_resource_url(self, request, identifier):
        m = self.get_resource(request, identifier)
        if not m:
            return None
        return request.link(m)

    def get_resource(self, request, identifier):
        typeinfo = request.app.config.type_registry.get_typeinfo(
            name=self.resource_type, request=request)
        # Fixme: should not handle string None
        if not (identifier or '').strip() or identifier == 'None':
            return None
        m = typeinfo['model_ui_factory'](request, identifier)
        return m

    def get_resource_term(self, request, identifier):
        m = self.get_resource(request, identifier)
        if not m:
            return None
        return m.model[self.term_field]


class UserReferenceWidget(ReferenceWidget):

    def __init__(self, resource_type='morpfw.pas.user', term_field='username', value_field='uuid', **kwargs):
        super().__init__(resource_type, term_field, value_field, **kwargs)

    def get_resource(self, request, identifier):
        # Fixme: should not handle string None
        if not identifier or identifier == 'None':
            return None
        newreq = request.get_authn_request()
        users = get_user_collection(newreq)
        user = users.get_by_uuid(identifier)
        if user:
            return UserModelUI(request, user, get_user_collection_ui(request))
        return None
