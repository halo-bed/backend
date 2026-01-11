from ..decorators import login_required
from flask import Blueprint, render_template, request, session, redirect, url_for
from ..user.model import User
from ..extensions import mongo
import os

from google_auth_oauthlib.flow import Flow

import requests
import cachecontrol
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import google.auth.transport.requests

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" #TODO remove after deploy

client_secret_file = os.path.join(BASE_DIR, "client_secret.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secret_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
)

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

        if getattr(user, "auth_provider", None) == "google":
            return redirect(url_for('auth.login_page', next=next))
    
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
            return redirect(url_for('auth.login_page', next=next))
        
    else:
        return redirect(url_for('auth.login_page', next=next))

@auth_bp.route('/login/google', methods=['GET'])
def login_google():
    authhorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authhorization_url)

@auth_bp.route('/callback', methods=['GET'])
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session['state'] == request.args['state']:
        return "State does not match!", 400

    credentials = flow.credentials
    request_session = requests.Session() 
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=os.getenv("GOOGLE_CLIENT_ID")
    )


    email = id_info.get("email")
    username = id_info.get("name")

    session.clear()
    session['user_id'] =id_info.get("sub")
    session['user_email'] = email
    session['user_name'] = username
    session["auth_provider"] = "google"

    existing_user = User.get_by_email(email)
    if existing_user is None:
        new_user = User(
            device_id=str(os.getenv("DEVICE_ID")),
            username=username,
            password=None,
            email=email,
            google_id=id_info.get("sub")
        )
        new_user.save()

    return redirect(url_for('dashboard.dashboard_page'))

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