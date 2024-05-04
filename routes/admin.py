# admin.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Coupon, db
from forms import CouponForm
import random
import string

admin = Blueprint('admin', __name__)

@admin.route('/admin_panel')
@login_required
def admin_panel():
    # Check if user is admin
    if current_user.email == 'pradyumn.tandon@hotmail.com':  # Change to actual admin email
        return render_template('admin_panel.html')
    else:
        flash('You do not have access to the admin panel.', 'error')
        return redirect(url_for('main.home'))

@admin.route('/generate_coupon', methods=['POST'])
@login_required
def generate_coupon():
    # Check if user is admin
    if current_user.email == 'pradyumn.tandon@hotmail.com':  # Change to actual admin email
        form = CouponForm()
        if form.validate_on_submit():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            coupon = Coupon(code=code)
            db.session.add(coupon)
            db.session.commit()
            flash('Coupon code generated successfully!', 'success')
            return redirect(url_for('admin.admin_panel'))
    else:
        flash('You do not have access to generate coupon codes.', 'error')
        return redirect(url_for('main.home'))
