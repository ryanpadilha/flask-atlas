from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, session
from flask_login import login_required, login_user, logout_user, current_user
from ..forms import LoginForm, UserForm, UserEditForm, UserChangePasswordForm, RoleForm
from ..application import f_images, login_manager
from ..util.library import jwt_decode
from ..util.enums import FlashMessagesCategory
from .client_api import LoginResource, UserResource, RoleResource
from ..models import AuthenticationObject, Credential, UserObject, RoleObject, ErrorObject
from ..util.authentication import AuthHeader
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
from flask import current_app as app

auth = Blueprint('auth', __name__)


G_USERS_AUTH = []


def add_user_global_auth(token, user):
    global G_USERS_AUTH
    remove_user_by_internal(user.internal)
    G_USERS_AUTH.append(
        {
            'token': token,
            'user': user
        }
    )


def find_user_by_internal(internal):
    for item in G_USERS_AUTH:
        if item.get('user').internal == internal:
            return item
    return None


def remove_user_by_internal(internal):
    G_USERS_AUTH[:] = [item for item in G_USERS_AUTH if item.get('user').internal != internal]
    l = G_USERS_AUTH
    return l


@login_manager.user_loader
def load_user(internal):
    user = None
    token = None

    item = find_user_by_internal(internal=internal)
    if item:
        user = item.get('user')
        token = item.get('token')

    if user and token:
        try:
            claims = jwt_decode(token)
        except (JWTError, ExpiredSignatureError, JWTClaimsError) as e:
            app.logger.error('Authentication Exception for user: {}'.format(e))
            return None

    return user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    next_url = request.args.get('next')

    if form.validate_on_submit():
        next_url = request.form['next']

        # check if user exists on API
        user_json = AuthenticationObject(username=form.email.data, password=form.password.data).to_json()
        l_credentials = Credential(provider='', authorization='', expires=0)
        transaction = LoginResource(credentials=l_credentials).authentication(data=user_json)

        if isinstance(transaction, ErrorObject):
            flash(u'O email ou o número de telefone inserido não corresponde a nenhuma conta',
                  category=FlashMessagesCategory.ERROR.value)
        else:
            AuthHeader.set_credentials(access_token=transaction.get('access_token'),
                                       expires=transaction.get('expires_in'))

            # recovery user object
            user = UserResource(credentials=AuthHeader.get_credentials()).find_by_username(username=form.email.data)

            if user:
                # validations over user
                if not user.active:
                    flash(u'Usuário não encontra-se ativo', category=FlashMessagesCategory.INFO.value)
                else:
                    login_user(user, remember=form.remember_me.data)
                    session.permanent = True
                    add_user_global_auth(transaction.get('access_token'), user)

                    # redirect to dashboard after login
                    return redirect(next_url or url_for('website.index'))
            else:
                flash(u'Problema desconhecido ao recuperar usuário', category=FlashMessagesCategory.ERROR.value)

    return render_template('auth/login.html', form=form, next=next_url)


@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect('login')


@auth.route('/manage/user', methods=['GET'])
@login_required
def list_users():
    users = UserResource(credentials=AuthHeader.get_credentials()).list()
    return render_template('manage/list-user.html', users=users)


@auth.route('/manage/user/form', methods=['GET', 'POST'])
@login_required
def form_user():
    form = UserForm()

    if form.validate_on_submit():
        # upload-file
        file = form.photo.data
        file_name = None
        file_url = None

        if file:
            file_folder = 'profile'
            # a = secure_filename(str(time.time()) + file.filename)

            file_name = f_images.save(file, folder=file_folder)
            file_url = f_images.url(file_name)
            # v = s3_upload(file, file_name)

        user = UserObject(active=form.active.data,
                          name=form.name.data,
                          user_name=form.user_email.data.lower(),
                          user_email=form.user_email.data.lower(),
                          password=form.user_password.data,
                          user_group_id=form.groups.data,
                          file_name=file_name,
                          file_url=file_url,
                          company=form.company.data,
                          occupation=form.occupation.data,
                          phone=form.phone.data.replace('(','').replace(') ', '').replace('-',''),
                          document_main=form.document_main.data)

        data = user.to_json()

        try:
            UserResource(credentials=AuthHeader.get_credentials()).persist(data=data)
            return redirect(url_for('auth.list_users'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-user.html', form=form)


@auth.route('/manage/user/<uuid:internal>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(internal):
    user = UserResource(credentials=AuthHeader.get_credentials()).get_by_internal(internal=internal)
    form = UserEditForm(obj=user, groups=user.user_group.internal)

    file_name = user.file_name if user else ''
    file_url = user.file_url if user else ''

    if form.validate_on_submit():
        # upload-file
        file = form.photo.data

        if file:
            file_folder = 'profile'
            file_name = f_images.save(file, folder=file_folder)
            file_url = f_images.url(file_name)

            user.file_name = file_name
            user.file_url = file_url

        user.name = form.name.data
        user.user_name = form.user_email.data.lower()
        user.user_email = form.user_email.data.lower()
        user.company = form.company.data
        user.occupation = form.occupation.data
        user.active = form.active.data
        user.user_group_id = form.groups.data
        user.phone = form.phone.data.replace('(','').replace(') ', '').replace('-','')
        user.document_main = form.document_main.data
        data = user.to_json()

        try:
            UserResource(credentials=AuthHeader.get_credentials()).update(internal=internal, data=data)
            return redirect(url_for('auth.list_users'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-user.html',
                           form=form, file_name=file_name, file_url=file_url)


@auth.route('/manage/user/delete', methods=['POST'])
@login_required
def delete_user():
    try:
        internal = request.form['recordId']
        UserResource(credentials=AuthHeader.get_credentials()).delete_entity(internal=internal)

        flash(u'Registro deletado com sucesso.', category=FlashMessagesCategory.INFO.value)
        return redirect(url_for('auth.list_users'))
    except Exception as e:
        abort(500, e)


@auth.route('/manage/user/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    form = UserChangePasswordForm()

    if form.validate_on_submit():
        obj = UserResource(credentials=AuthHeader.get_credentials()).get_by_internal(current_user.internal)
        user = UserObject.from_dict(obj)

        # verificando se senha atual confere
        # if not user.verify_password(form.current_password.data):
        #     flash(u'Senha atual informada está incorreta.', category=FlashMessagesCategory.ERROR.value)
        #     return render_template('manage/view-profile.html', form=form)

        user.password = form.user_password.data
        data = user.to_json()

        try:
            UserResource.persist(data=data)

            flash(u'Alteração de senha realizada com sucesso. A alteração ocorre apenas uma vez por sessão.',
                  category=FlashMessagesCategory.INFO.value)
            return redirect(url_for('auth.view_profile'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/view-profile.html', form=form)


@auth.route('/manage/role')
@login_required
def list_roles():
    roles = RoleResource(credentials=AuthHeader.get_credentials()).list()
    return render_template('manage/list-role.html', roles=roles)


@auth.route('/manage/role/form', methods=['GET', 'POST'])
@login_required
def form_role():
    form = RoleForm()

    if form.validate_on_submit():
        role = RoleObject(name=form.name.data,
                          type=form.type.data.upper(),
                          description=form.description.data).to_json()

        try:
            obj = RoleResource(credentials=AuthHeader.get_credentials()).persist(data=role)
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('manage/form-role.html', form=form)

            return redirect(url_for('auth.list_roles'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-role.html', form=form)


@auth.route('/manage/role/<uuid:internal>/edit', methods=['GET', 'POST'])
@login_required
def edit_role(internal):
    form = RoleForm()

    if request.method == 'GET':
        role = RoleResource(credentials=AuthHeader.get_credentials()).get_by_internal(internal=internal)
        if not isinstance(role, ErrorObject):
            form.process(obj=role)

    if form.validate_on_submit():
        role = RoleObject(name=form.name.data,
                          type=form.type.data.upper(),
                          description=form.description.data).to_json()

        try:
            obj = RoleResource(credentials=AuthHeader.get_credentials()).update(internal=internal, data=role)
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('manage/form-role.html', form=form)

            return redirect(url_for('auth.list_roles'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-role.html', form=form)


@auth.route('/manage/role/delete', methods=['POST'])
@login_required
def delete_role():
    try:
        obj = RoleResource(credentials=AuthHeader.get_credentials()).delete_entity(internal=request.form['recordId'])
        if isinstance(obj, ErrorObject):
            flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
        else:
            flash(u'Registro deletado com sucesso.', category=FlashMessagesCategory.INFO.value)

        return redirect(url_for('auth.list_roles'))
    except Exception as e:
        abort(500, e)
