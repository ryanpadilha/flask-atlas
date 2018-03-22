from flask import Blueprint, render_template

error_handler = Blueprint('error_handler', __name__)


@error_handler.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404


@error_handler.app_errorhandler(500)
def internal_server_error(error):
    return render_template('500.html', error=error), 500


@error_handler.app_errorhandler(Exception)
def unhandled_exception(error):
    return render_template('500.html', error=error), 500
