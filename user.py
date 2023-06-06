from flask import session, redirect, url_for
from functools import wraps

# get user from session


def getUser():
    if 'username' in session:
        print(session)
        return {
            'username': session['username'],
            'firstname': session['firstname'],
            'lastname': session['lastname'],
            'email': session['email']
        }
    else:
        return None

# set user to session


def setUser(user, type):
    session['username'] = user['username']
    session['firstname'] = user['firstname']
    session['lastname'] = user['lastname']
    session['email'] = user['email']
    session['type'] = type


# decorator to protect authenticated routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getUser():
            return redirect(url_for('login'))
        else:
            user = getUser()
            if session['type'] == 'admin':
                return redirect(url_for('login'))
            return f(user, *args, **kwargs)
    return decorated_function

# decorator to protect admin routes


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getUser():
            return redirect(url_for('adminlogin'))
        else:
            user = getUser()
            if session['type'] != 'admin':
                return redirect(url_for('adminlogin'))
            return f(user, *args, **kwargs)
    return decorated_function
