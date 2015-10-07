from functools import wraps
from flask import request
from itsdangerous import URLSafeSerializer

def get_user_from_auth(auth_key):
    s = URLSafeSerializer('secret-key', salt='be_efficient')
    return s.loads(auth_key)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
    	try:
            user = get_user_from_auth(request.cookies['auth_key'])
            if user == kwargs['name']:
            	return f(*args, **kwargs)
            else:
            	return "error"
        except:
            return "error"
        
    return decorated_function