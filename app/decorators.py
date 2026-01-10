def login_required(func):
    from flask import session, redirect, url_for
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login_page'))
        return func(*args, **kwargs)
    
    return wrapper