from flask import Blueprint, render_template
from ..decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_page():
    return render_template('base.html')