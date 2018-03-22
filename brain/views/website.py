from flask import Blueprint, render_template
from flask_login import login_required

website = Blueprint('website', __name__)


@website.route('/')
@login_required
def index():
    return render_template('website/index.html')
