from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user
from app.admin.models import User
from app import login_manager

admin_bp = Blueprint('admin', __name__,)

@login_manager.user_loader
def load_user(user_id):
    from app.admin.models import User  # Avoid circular import
    return User.query.get(int(user_id))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('cms.admin_dashboard'))
        flash("Invalid credentials")
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.login'))
