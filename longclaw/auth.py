from functools import wraps
from flask import request
from itsdangerous import URLSafeSerializer
from config import *
import json

def response_msg(status, msg, **kwargs):
    res = {}
    res['status'] = status
    res['msg'] = msg
    for name, value in kwargs.items():
        res[name] = value
    return json.dumps(res), 200


def get_user_from_auth(auth_key):
    s = URLSafeSerializer('secret-key', salt='be_efficient')
    return s.loads(auth_key)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # import ipdb; ipdb.set_trace();
        try:
            if request.headers.get('key'):
                key = request.headers.get('key')
            else:
                key = ""
            if key:
                if key != ANDROID_HEADER_KEY:
                    return response_msg('error', 'Authentication faiiled')
                try:
                    user = get_user_from_auth(request.headers.get('auth_key'))
                except:
                    user = ""
            else:
                user = get_user_from_auth(request.cookies['auth_key'])
            if user == kwargs['name']:
                return f(*args, **kwargs)
            else:
                return response_msg('error', 'user not authorized')
        except:
            return response_msg('error', 'some error occured')
        
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # import ipdb; ipdb.set_trace();
        try:
            user = get_user_from_auth(request.cookies['admin_key'])
            if user == 'admin':
                return f(*args, **kwargs)
            else:
                return response_msg('error', 'user not authorized')
        except:
            return response_msg('error', 'some error occured')
        
    return decorated_function