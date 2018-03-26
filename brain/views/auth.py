from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import login_required, login_user, logout_user
from ..forms import LoginForm
from ..application import login_manager
from ..util.library import jwt_decode
from ..util.enums import FlashMessagesCategory
from .client_api import LoginResource, UserResource
from ..models import AuthenticationObject, ErrorObject
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
    return G_USERS_AUTH


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
        user_json = AuthenticationObject(username=form.email.data, password=form.password.data).to_json()
        transaction = LoginResource().authentication(data=user_json)

        if isinstance(transaction, ErrorObject):
            flash(u'O email ou o número de telefone inserido não corresponde a nenhuma conta',
                  category=FlashMessagesCategory.ERROR.value)
        else:
            AuthHeader.set_credentials(access_token=transaction.get('access_token'),
                                       expires=transaction.get('expires_in'))

            user = UserResource().find_by_username(username=form.email.data)

            if user:
                if not user.active:
                    flash(u'Usuário não encontra-se ativo', category=FlashMessagesCategory.INFO.value)
                else:
                    login_user(user, remember=form.remember_me.data)
                    session.permanent = True
                    add_user_global_auth(transaction.get('access_token'), user)

                    return redirect(next_url or url_for('website.index'))
            else:
                flash(u'Problema desconhecido ao recuperar usuário', category=FlashMessagesCategory.ERROR.value)

    return render_template('auth/login.html', form=form, next=next_url)


@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect('login')

