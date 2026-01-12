from ..decorators import login_required
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from ..user.model import User
from ..extensions import mongo
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException

import os

from google_auth_oauthlib.flow import Flow

import requests
import cachecontrol
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import google.auth.transport.requests

pubnub_admin = None

def must_env(name: str) -> str:
    v = os.getenv(name)
    if not v or not v.strip():
        raise RuntimeError(f"Missing env var: {name}")
    return v.strip()

def get_pubnub_admin() -> PubNub:
    global pubnub_admin
    if pubnub_admin is None:
        pnconfig = PNConfiguration()
        pnconfig.publish_key = must_env("PUBNUB_PUBLISH_KEY")
        pnconfig.subscribe_key = must_env("PUBNUB_SUBSCRIBE_KEY")
        pnconfig.secret_key = must_env("PUBNUB_SECRET_KEY")
        pnconfig.user_id = "server"
        pubnub_admin = PubNub(pnconfig)
    return pubnub_admin

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
        

@auth_bp.route("/pubnub-token", methods=["GET"])
def pubnub_token():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        from pubnub.models.consumer.v3.channel import Channel

        channels = [
            Channel.id("pir-events").read(),     # web client can read events
            Channel.id("pir-control").write(),   # web client can publish control messages
        ]
        admin = get_pubnub_admin()
        envelope = (
            admin.grant_token()
            .channels(channels)
            .ttl(60)   # minutes
            .sync()
        )

        # SDKs differ slightly; this is the canonical accessor in docs
        token = envelope.result.get_token() if hasattr(envelope.result, "get_token") else envelope.result.token

        return jsonify({"token": token})

    except PubNubException as e:
        return jsonify({"error": "Failed to generate PubNub token", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Server error generating token", "details": str(e)}), 500
    
@auth_bp.route("/device/pubnub-token", methods=["POST"])
def device_pubnub_token():
    # Pi sends: X-DEVICE-KEY: <DEVICE_KEY>
    device_key = request.headers.get("X-DEVICE-KEY", "")
    if not device_key or device_key != os.getenv("DEVICE_KEY", ""):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        from pubnub.models.consumer.v3.channel import Channel
        channels = [
            Channel.id("pir-events").write(),   # Pi publishes events
            Channel.id("pir-control").read(),   # Pi reads control messages
        ]
        admin = get_pubnub_admin()
        envelope = (
            admin.grant_token()
            .channels(channels)
            .ttl(43200)  # minutes = 30 days (adjust as you like)
            .sync()
        )

        token = envelope.result.get_token() if hasattr(envelope.result, "get_token") else envelope.result.token
        return jsonify({"token": token})

    except PubNubException as e:
        return jsonify({"error": "Failed to generate PubNub device token", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Server error generating device token", "details": str(e)}), 500
