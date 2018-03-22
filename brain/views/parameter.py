from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required
from ..forms import ClientForm, InstitutionForm
from ..util.enums import FlashMessagesCategory

parameter = Blueprint('parameter', __name__)


@parameter.route('/parameter/client')
@login_required
def list_clients():
    clients = Client.query.all()
    return render_template('parameter/list-client.html', clients=clients)


@parameter.route('/parameter/client/form', methods=['GET', 'POST'])
@login_required
def form_client():
    form = ClientForm()

    if form.validate_on_submit():
        client = Client(name=form.name.data,
                        document_main=form.document_main.data,
                        address_street=form.address_street.data,
                        address_complement=form.address_complement.data,
                        address_zip=form.address_zip.data,
                        address_district=form.address_district.data,
                        address_city=form.address_city.data,
                        address_state=form.address_state.data,
                        date_start=form.date_start.data,
                        date_end=form.date_end.data)

        try:
            db.session.add(client)
            db.session.commit()

            return redirect(url_for('parameter.list_clients'))
        except Exception as e:
            abort(500, e)

    return render_template('parameter/form-client.html', form=form)


@parameter.route('/parameter/client/<uuid:internal>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(internal):
    client = Client.query.filter_by(internal=internal).first()
    form = ClientForm(obj=client)

    if form.validate_on_submit():
        client.name = form.name.data
        client.document_main = form.document_main.data
        client.address_street = form.address_street.data
        client.address_complement = form.address_complement.data
        client.address_zip = form.address_zip.data
        client.address_district = form.address_district.data
        client.address_city = form.address_city.data
        client.address_state = form.address_state.data
        client.date_start = form.date_start.data
        client.date_end = form.date_end.data

        try:
            db.session.commit()

            return redirect(url_for('parameter.list_clients'))
        except Exception as e:
            abort(500, e)

    return render_template('parameter/form-client.html', form=form)


@parameter.route('/parameter/client/delete', methods=['POST'])
@login_required
def delete_client():
    client = Client.query.filter_by(internal=request.form['recordId']).first()

    if client and client.institutions:
        flash(u'Não é possível deletar o registro, pois está associado a uma instituição.',
              category=FlashMessagesCategory.WARNING.value)
        return redirect(url_for('parameter.list_clients'))

    try:
        db.session.delete(client)
        db.session.commit()

        flash(u'Registro deletado com sucesso.', category=FlashMessagesCategory.INFO.value)
        return redirect(url_for('parameter.list_clients'))
    except Exception as e:
        abort(500, e)


@parameter.route('/parameter/institution')
@login_required
def list_institutions():
    institutions = Institution.query.all()
    return render_template('parameter/list-institution.html', institutions=institutions)


@parameter.route('/parameter/institution/form', methods=['GET', 'POST'])
@login_required
def form_institution():
    form = InstitutionForm()

    if form.validate_on_submit():
        institution = Institution(name=form.name.data,
                                  phone=form.phone.data,
                                  email=form.email.data,
                                  document_main=form.document_main.data,
                                  principal=form.principal.data,
                                  coordinator=form.coordinator.data,
                                  address_street=form.address_street.data,
                                  address_complement=form.address_complement.data,
                                  address_zip=form.address_zip.data,
                                  address_district=form.address_district.data,
                                  address_city=form.address_city.data,
                                  address_state=form.address_state.data,
                                  client_global_id=form.clients.data)

        try:
            db.session.add(institution)
            db.session.commit()

            return redirect(url_for('parameter.list_institutions'))
        except Exception as e:
            abort(500, e)

    return render_template('parameter/form-institution.html', form=form)


@parameter.route('/parameter/institution/<uuid:internal>/edit', methods=['GET', 'POST'])
@login_required
def edit_institution(internal):
    institution = Institution.query.filter_by(internal=internal).first()
    form = InstitutionForm(obj=institution, clients=institution.client_global_id)

    if form.validate_on_submit():
        institution.name = form.name.data
        institution.phone = form.phone.data
        institution.email = form.email.data
        institution.document_main = form.document_main.data
        institution.principal = form.principal.data
        institution.coordinator = form.coordinator.data
        institution.address_street = form.address_street.data
        institution.address_complement = form.address_complement.data
        institution.address_zip = form.address_zip.data
        institution.address_district = form.address_district.data
        institution.address_city = form.address_city.data
        institution.address_state = form.address_state.data
        institution.client_global_id = form.clients.data

        try:
            db.session.commit()

            return redirect(url_for('parameter.list_institutions'))
        except Exception as e:
            abort(500, e)

    return render_template('parameter/form-institution.html', form=form)


@parameter.route('/parameter/institution/delete', methods=['POST'])
@login_required
def delete_institution():
    institution = Institution.query.filter_by(internal=request.form['recordId']).first()

    try:
        db.session.delete(institution)
        db.session.commit()

        flash(u'Registro deletado com sucesso.', category=FlashMessagesCategory.INFO.value)
        return redirect(url_for('parameter.list_institutions'))
    except Exception as e:
        abort(500, e)
