import weakref

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectMultipleField, \
    BooleanField, HiddenField, SelectField, FileField, FieldList

from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileAllowed
from .application import f_images
from .views.client_api import RoleResource
from .util.authentication import AuthHeader


def my_strip_filter(value):
    if value is not None and hasattr(value, 'strip'):
        return value.strip()
    return value


class BaseForm(FlaskForm):
    class Meta:
        def bind_field(self, form, unbound_field, options):
            # We don't set default filters for query-based fields as it breaks them if no query_factory is set
            # while the Form is instantiated. Also, it's quite pointless for those fields...
            # FieldList simply doesn't support filters.
            no_filter_fields = FieldList  # QuerySelectField
            filters = [my_strip_filter] if not issubclass(unbound_field.field_class, no_filter_fields) else []
            filters += unbound_field.kwargs.get('filters', [])
            bound = unbound_field.bind(form=form, filters=filters, **options)
            bound.get_form = weakref.ref(form)  # GC won't collect the form if we don't use a weakref
            return bound


class LoginForm(FlaskForm):
    email = StringField(u'Email ou telefone', validators=[DataRequired(u'Informe o e-mail ou telefone')])
    password = PasswordField(u'Senha', validators=[DataRequired(u'Informe a senha')])
    remember_me = BooleanField(u'Permanecer logado')


class RoleForm(BaseForm):
    internal = HiddenField()
    name = StringField(u'Nome *', validators=[DataRequired(u'Informe o nome')])
    type = StringField(u'Sigla (25 caracteres) *', validators=[DataRequired(u'Informe a sigla'),
                                                              Length(min=1, max=25, message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres')])
    description = StringField(u'Descrição')


class UserEditForm(FlaskForm):
    internal = HiddenField()
    active = SelectField(u'Situação *', coerce=int, default=1)
    name = StringField(u'Nome Completo *', validators=[DataRequired(u'Informe o nome completo')])
    user_email = StringField(u'E-mail *',
                             validators=[DataRequired(u'Informe o e-mail'), Email(u'Endereço de e-mail inválido')])
    photo = FileField(u'Foto do Perfil', validators=[FileAllowed(f_images, 'Selecione apenas imagens')])
    company = StringField(u'Empresa')
    occupation = StringField(u'Cargo')
    phone = StringField(u'Telefone Celular *', validators=[DataRequired(u'Informe o telefone')])
    document_main = StringField(u'CPF')
    roles = SelectMultipleField(u'Papeis *', coerce=int,
                                validators=[DataRequired(u'Selecione pelo menos um papel')])

    def __init__(self, **kwargs):
        super(UserEditForm, self).__init__(**kwargs)
        roles = RoleResource(credentials=AuthHeader.get_credentials()).list()
        self.roles.choices = [(g.internal, g.name) for g in roles]
        self.active.choices = [(1, u'Ativo'),(0, u'Inativo')]


class UserForm(UserEditForm):
    user_password = PasswordField(u'Senha *', validators=[DataRequired(u'Informe uma senha'),
                                                          Length(min=6, max=20,
                                                                 message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres')])

    confirm_password = PasswordField(u'Confirmar Senha *', validators=[DataRequired(u'Informe um confirmar senha'),
                                                                       Length(min=6, max=20,
                                                                              message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres'),
                                                                       EqualTo('user_password',
                                                                               u'A confirmação de senha não confere')])


class UserChangePasswordForm(FlaskForm):
    current_password = PasswordField(u'Senha Atual *', validators=[DataRequired(u'Informe a senha atual'),
                                                                   Length(min=6, max=20,
                                                                          message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres')])

    user_password = PasswordField(u'Nova Senha *', validators=[DataRequired(u'Informe a nova senha'),
                                                               Length(min=6, max=20,
                                                                      message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres')])

    confirm_password = PasswordField(u'Confirmar Nova Senha *', validators=[DataRequired(u'Informe um confirmar senha'),
                                                                            Length(min=6, max=20,
                                                                                   message='Campo deve ter no mínimo %(min)d e no máximo %(max)d caracteres'),
                                                                            EqualTo('user_password',
                                                                               u'A confirmação de senha não confere')])
