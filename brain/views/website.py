from flask import Blueprint, render_template
from flask_login import login_required
from jinja2 import evalcontextfilter
from ..util.library import epoch_to_date

website = Blueprint('website', __name__)


@website.route('/')
@login_required
def index():
    return render_template('website/index.html')


@website.app_template_filter()
def epoch2date(value):
    return epoch_to_date(value)
