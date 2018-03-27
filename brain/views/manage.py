from flask import Blueprint, abort, render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from ..util.enums import FlashMessagesCategory
from .client_api import RoleResource, UserResource
from ..models import RoleObject, ErrorObject, UserObject
from ..forms import RoleForm, UserForm, UserEditForm, UserChangePasswordForm

manage = Blueprint('manage', __name__, url_prefix='/manage')


@manage.route('/role')
@login_required
def list_roles():
    roles = RoleResource().list()
    return render_template('manage/list-role.html', roles=roles)


@manage.route('/role/form', methods=['GET', 'POST'])
@login_required
def form_role():
    form = RoleForm()

    if form.validate_on_submit():
        role = RoleObject(name=form.name.data,
                          type=form.type.data.upper(),
                          description=form.description.data).to_json()

        try:
            obj = RoleResource().persist(data=role)
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('manage/form-role.html', form=form)

            return redirect(url_for('manage.list_roles'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-role.html', form=form)


@manage.route('/role/<uuid:internal>/edit', methods=['GET', 'POST'])
@login_required
def edit_role(internal):
    form = RoleForm()

    if request.method == 'GET':
        role = RoleResource().get_by_internal(internal=internal)
        if not isinstance(role, ErrorObject):
            form.process(obj=role)

    if form.validate_on_submit():
        role = RoleObject(name=form.name.data,
                          type=form.type.data.upper(),
                          description=form.description.data).to_json()

        try:
            obj = RoleResource().update(internal=internal, data=role)
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('manage/form-role.html', form=form)

            return redirect(url_for('manage.list_roles'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-role.html', form=form)


@manage.route('/role/delete', methods=['POST'])
@login_required
def delete_role():
    try:
        obj = RoleResource().delete_entity(internal=request.form['recordId'])
        if isinstance(obj, ErrorObject):
            flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
        else:
            flash(u'Registro deletado com sucesso.', category=FlashMessagesCategory.INFO.value)

        return redirect(url_for('manage.list_roles'))
    except Exception as e:
        abort(500, e)


@manage.route('/user', methods=['GET'])
@login_required
def list_users():
    users = UserResource().list()
    return render_template('manage/list-user.html', users=users)


@manage.route('/user/form', methods=['GET', 'POST'])
@login_required
def form_user():
    form = UserForm()

    if form.validate_on_submit():
        user = UserObject(active=form.active.data,
                          name=form.name.data,
                          username=form.user_email.data.lower(),
                          user_email=form.user_email.data.lower(),
                          password=form.user_password.data,
                          file_name=None,
                          file_url=None,
                          company=form.company.data,
                          occupation=form.occupation.data,
                          phone=form.phone.data.replace('(', '').replace(') ', '').replace('-', ''),
                          document_main=form.document_main.data)

        user.roles.clear()
        for role in form.roles.data:
            user.roles.append(role)

        try:
            obj = UserResource().persist(data=user.to_json())
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('manage/form-user.html', form=form)

            return redirect(url_for('manage.list_users'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-user.html', form=form)


@manage.route('/user/<uuid:internal>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(internal):
    form = UserEditForm()

    if request.method == 'GET':
        user = UserResource().get_by_internal(internal=internal)
        if not isinstance(user, ErrorObject):
            form.process(obj=user)

            role_list = []
            for r in user.roles:
                role_list.append(r.type)
            form.roles.default = role_list
            form.roles.process(request.form)

    if form.validate_on_submit():
        user = UserObject(active=form.active.data,
                          name=form.name.data,
                          username=form.user_email.data.lower(),
                          user_email=form.user_email.data.lower(),
                          file_name=None,
                          file_url=None,
                          company=form.company.data,
                          occupation=form.occupation.data,
                          phone=form.phone.data.replace('(', '').replace(') ', '').replace('-', ''),
                          document_main=form.document_main.data)

        user.roles.clear()
        for role in form.roles.data:
            user.roles.append(role)

        try:
            obj = UserResource().update(internal=internal, data=user.to_json())
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
                return render_template('manage/form-user.html', form=form)

            return redirect(url_for('manage.list_users'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/form-user.html', form=form, file_name='', file_url='')


@manage.route('/user/delete', methods=['POST'])
@login_required
def delete_user():
    try:
        obj = UserResource().delete_entity(internal=request.form['recordId'])
        if isinstance(obj, ErrorObject):
            flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
        else:
            flash(u'Registro deletado com sucesso.', category=FlashMessagesCategory.INFO.value)

        return redirect(url_for('manage.list_users'))
    except Exception as e:
        abort(500, e)


@manage.route('/user/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    form = UserChangePasswordForm()

    if form.validate_on_submit():
        user = UserResource().get_by_internal(current_user.internal)
        if isinstance(user, ErrorObject):
            flash(user.issues, category=FlashMessagesCategory.ERROR.value)
            return render_template('manage/view-profile.html', form=form)

        # verificando se senha atual confere
        # if not user.verify_password(form.current_password.data):
        #     flash(u'Senha atual informada está incorreta.', category=FlashMessagesCategory.ERROR.value)
        #     return render_template('manage/view-profile.html', form=form)

        user.password = form.user_password.data

        try:
            obj = UserResource().update(internal=user.internal, data=user.to_json())
            if isinstance(obj, ErrorObject):
                flash(obj.issues, category=FlashMessagesCategory.ERROR.value)
            else:
                flash(u'Alteração de senha realizada com sucesso. A alteração ocorre apenas uma vez por sessão.',
                      category=FlashMessagesCategory.INFO.value)

            return redirect(url_for('manage.view_profile'))
        except Exception as e:
            abort(500, e)

    return render_template('manage/view-profile.html', form=form)
