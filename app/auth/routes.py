from ..decorators import login_required
from flask import Blueprint, render_template, request, session, redirect, url_for
from ..user.model import User
from ..extensions import mongo
import os

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/login', methods=['GET'])
def login_page():
    next = request.args.get('next')
    return render_template('login.html', next=next)

@auth_bp.route('/login/default', methods=['POST'])
def login_default():
    email = request.form.get('email')
    password = request.form.get('password')
    next = request.form.get('next') or url_for('dashboard.dashboard_page')

    if email and password:
        user = User.get_by_email(email)
        if user and User.check_password(user.password, password):

            session.clear()
            session['user_id'] = str(user.id)
            session['user_email'] = email
            session['user_name'] = user.username
            session["auth_provider"] = "default"

            s = dict(session)
            print(f"Session after login: {s}")
            return redirect(next)
        else:
            return {"error": "Invalid credentials"}, 401
            return redirect(url_for('auth.login_page', next=next))
        
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/register', methods=['GET'])
def register_page():
    next = request.args.get('next')
    return render_template('register.html', next=next)

@auth_bp.route('/register/default', methods=['POST'])
def register_default():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    next = request.form.get('next') or url_for('dashboard.dashboard_page')

    if email and username and password:
        existing_user = User.get_by_email(email)
        if existing_user is None:
            password_hash = User.hash_password(password)
            new_user = User(device_id=str(os.getenv("DEVICE_ID")), username=username, password=password_hash, email=email)
            new_user.save()
            session.clear()
            session['user_id'] = str(new_user.id)
            session['user_email'] = email
            session['user_name'] = username
            session["auth_provider"] = "default"
            return redirect(next)
        else:
            return redirect(url_for('auth.register_page', next=next))