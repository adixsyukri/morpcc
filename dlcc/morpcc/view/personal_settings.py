import morepath
import colander
import deform
import deform.widget
from morpfw.authn.pas.user.path import get_user_collection
import morpfw.authn.pas.exc
from ..app import App, SQLAuthApp
from ..root import Root
from .. import permission


class PersonalInfoSchema(colander.MappingSchema):
    username = colander.SchemaNode(
        colander.String(),
        oid='personalinfo-username',
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'))
    email = colander.SchemaNode(
        colander.String(),
        oid='personalinfo-email',
        validator=colander.Email(msg="Invalid e-mail address"))
    state = colander.SchemaNode(
        colander.String(),
        oid='personalinfo-state',
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'))
    created = colander.SchemaNode(
        colander.DateTime(),
        oid='personalinfo-created',
        missing=None,
        widget=deform.widget.DateTimeInputWidget(template='readonly/datetimeinput'))


class PasswordSchema(colander.MappingSchema):
    password_current = colander.SchemaNode(colander.String(),
                                           oid='password-current',
                                           title="Current password",
                                           widget=deform.widget.PasswordWidget(),
                                           missing='')

    password = colander.SchemaNode(colander.String(),
                                   oid='password-new',
                                   title="New password",
                                   widget=deform.widget.PasswordWidget(),
                                   missing='',
                                   validator=colander.Length(min=8))
    password_confirm = colander.SchemaNode(colander.String(),
                                           oid='password-confirm',
                                           widget=deform.widget.PasswordWidget(),
                                           title="Confirm new password",
                                           missing='')

    def validator(self, node: "PasswordSchema", appstruct: dict):
        if appstruct['password'] != appstruct['password_confirm']:
            raise colander.Invalid(node['password'], "Password does not match")


def personalinfo_form(request) -> deform.Form:
    return deform.Form(PersonalInfoSchema(), buttons=('Submit',),
                       formid='personalinfo-form')


def password_form(request) -> deform.Form:
    return deform.Form(PasswordSchema(), buttons=('Change password',),
                       formid='password-form')


@App.html(model=Root, name='personal-settings', template="master/multi-form.pt",
          permission=permission.EditOwnProfile)
def profile(context, request: morepath.Request):
    userid = request.identity.userid
    newreq = request.copy(app=request.app.get_authn_provider())
    usercol = get_user_collection(newreq)
    user = usercol.get_by_userid(userid)
    return {
        'page_title': 'Profile',
        'forms': [{
            'form_title': 'Personal Information',
            'form': personalinfo_form(request),
            'readonly': False,
            'form_data': user.data.as_dict()
        },
            {
            'form_title': 'Password',
            'form': password_form(request),
            'readonly': False,
        }]
    }


@App.html(model=Root, name='personal-settings', request_method='POST',
          template='master/multi-form.pt', permission=permission.EditOwnProfile)
def process_profile(context, request):
    personalinfo_f = personalinfo_form(request)
    password_f = password_form(request)
    controls = list(request.POST.items())
    controls_dict = dict(controls)
    active_form = controls_dict['__formid__']

    userid = request.identity.userid
    newreq = request.copy(app=request.app.get_authn_provider())
    usercol = get_user_collection(newreq)
    user = usercol.get_by_userid(userid)

    failed = False
    if active_form == 'personalinfo-form':
        try:
            data = personalinfo_f.validate(controls)
        except deform.ValidationFailure as e:
            failed = True
            personalinfo_f = e
            userdata = personalinfo_f.field.schema.serialize(
                user.data.as_dict())
            for k in userdata.keys():
                if personalinfo_f.cstruct[k] is not colander.null:
                    userdata[k] = personalinfo_f.cstruct[k]
            personalinfo_f.field.cstruct = userdata

        if not failed:
            updatedata = {}
            for f in ['email']:
                updatedata[f] = data[f]
            user.update(updatedata)

        if not failed:
            request.notify('success', 'Profile updated',
                           'Your profile have been successfully updated')
            return morepath.redirect(request.url)
    elif active_form == 'password-form':
        try:
            data = password_f.validate(controls)
        except deform.ValidationFailure as e:
            failed = True
            password_f = e

        if not failed:
            if not user.validate(data['password_current']):
                exc = colander.Invalid(password_f, 'Invalid password')
                password_f.widget.handle_error(password_f, exc)
                failed = True

        if not failed:
            try:
                user.change_password(
                    data['password_current'], data['password'])
            except morpfw.auth.exc.InvalidPasswordError as e:
                exc = colander.Invalid(password_f, 'Invalid password')
                password_f.widget.handle_error(password_f, exc)
                failed = True

        if not failed:
            request.notify('success', 'Password changed',
                           'Your password have been successfully changed')
            return morepath.redirect(request.url)

    else:
        request.notify('error', 'Unknown form',
                       'Invalid form identifier was supplied')

        return morepath.redirect(request.url)

    return {
        'page_title': 'Personal Settings',
        'forms': [{
            'form_title': 'Personal Information',
            'form': personalinfo_f,
            'readonly': False,
            'form_data': user.data.as_dict() if active_form == 'password-form' else None
        },
            {
            'form_title': 'Password',
            'form': password_f,
            'readonly': False,
        }]
    }