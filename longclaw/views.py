from longclaw import app
import rethinkdb as rdb
import json
from rethinkdb.errors import RqlRuntimeError
from flask import request, render_template, redirect
import requests
from config import *
from urllib import urlencode
from urllib2 import urlopen
import re
import hashlib
from facebook import GraphAPI, GraphAPIError
from auth import *
import ipdb


@app.route('/xyz/')
def test():
    # ipdb.set_trace()
    return render_template('test.html')


def response_msg(status, msg, **kwargs):
    res = {}
    res['status'] = status
    res['msg'] = msg
    for name, value in kwargs.items():
        res[name] = value
    return json.dumps(res), 200


def authenticate_webkiosk(enroll, passwd):
    try:
        check = requests.get(
            'https://webkiosk.jiit.ac.in/CommonFiles/UserActionn.jsp?' +
            'x=&txtInst=Institute&' +
            'InstCode=JIIT&' +
            'txtuType=Member+Type&' +
            'UserType=S&' +
            'txtCode=Enrollment+No&' +
            'MemberCode=' + enroll +
            '&txtPin=Password%2FPin&' +
            'Password=' + passwd +
            '&BTNSubmit=Submit',
            timeout=5)
    except:
        return False
    response = check.content
    # check if enroll and passwd are correct
    incorrect = ['please', 'Administrator', 'Invalid', 'NullPointer']
    if any(word in response for word in incorrect):
        return False
    return True


def get_rdb_conn():
    connection = rdb.connect(host=RDB_HOST, port=RDB_PORT)
    return connection


def gen_auth_key(user):
    s = URLSafeSerializer('secret-key', salt='be_efficient')
    return s.dumps(user)


# db setup; only run once
# will add a check that this is only run by admin
@app.route('/create_db/')
def dbSetup():
    res = ""
    connection = rdb.connect(host=RDB_HOST, port=RDB_PORT)
    try:
        rdb.db_create(TODO_DB).run(connection)
        res = 'Database setup completed'
    except RqlRuntimeError:
        res = 'Database already exists.'
    finally:
        connection.close()
    return res


@app.route('/')
def hello_world():
    return 'Hello World!'


# error 404 not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


def check_captcha(response, remoteip):
    # ipdb.set_trace()
    captcha_url = 'https://www.google.com/recaptcha/api/siteverify'
    params = urlencode({
        'secret': CAPTCHA_SECRET,
        'response': response,
        'remoteip': remoteip
        })
    response = urlopen(captcha_url, params)
    try:
        ret = json.load(response)['success']
    except:
        ret = False
    return ret


def validate_fb_email(email, access_token):
    # check if user is has synced fb email
    try:
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('user').filter(
            rdb.row['fb_email'] == email
            ).run(connection)
    except:
        return response_msg('error', 'Could not connect to db')

    if len(cursor.items) == 0:
        return response_msg('error', 'facebook not synced')

    # if user has already synced fb email
    # check whether access token and email is valid
    try:
        graph = GraphAPI(access_token)
        profile = graph.get_object('me', fields='email')
        fb_email = profile['email']
    except GraphAPIError as e:
        return response_msg('error', e)
    except:
        return response_msg('error', 'Could not connect to facebook')

    if fb_email == email:
        return response_msg('success', 'OK')
    else:
        return response_msg('error', 'facebook not synced')


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    elif request.method == 'POST':
        form_data = json.loads(request.data)
        try:
            fname = form_data['fname']
            lname = form_data['lname']
            email = form_data['email']
            username = form_data['user']
            passwd = form_data['passwd']
            cpasswd = form_data['cpasswd']
            enroll = form_data['enroll']
            wbpass = form_data['wbpass']
            ccuser = form_data['ccuser']
            cfuser = form_data['cfuser']
            if request.headers.get('key'):
                key = request.headers.get('key')
            else:
                captcha_resp = form_data['g-recaptcha-response']
        except:
            return response_msg('error', 'form data not complete')

        remoteip = request.remote_addr

        # form validation
        if len(fname) <= 0:
            return response_msg('error', "First name shouldn't be empty")

        if len(lname) <= 0:
            return response_msg('error', "Last name shouldn't be empty")

        if not re.match("^[a-zA-Z0-9_.-]+$", username):
            return response_msg(
                'error',
                'username should be alphnumeric and/or -_'
                )

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return response_msg('error', 'Invalid email')

        if len(username) < 4 or len(username) > 16:
            return response_msg('error', 'Please enter a 4-16 letter username')

        if len(passwd) < 6:
            return response_msg(
                'error',
                'Password should be minimum of 6 characters'
                )

        if cpasswd != passwd:
            return response_msg('error', 'Passwords do not match')

        if not authenticate_webkiosk(enroll, wbpass):
            return response_msg('error', 'Webkiosk authentication faiiled')

        if key:
            if key != ANDROID_HEADER_KEY:
                return response_msg('error', 'Authentication faiiled')
        else:
            if not check_captcha(captcha_resp, remoteip):
                return response_msg('error', 'Captcha authentication faiiled')
        # authenticate online judge handles
        cc_url = requests.get('https://www.codechef.com/users/' + ccuser)
        try:
            if cc_url.url == 'https://www.codechef.com/':
                return response_msg('error', 'Incorrect Codechef Handle')
        except:
            return response_msg('error', 'could not connect to codeforces')

        cf_url = requests.get(
            'http://codeforces.com/api/user.info?handles=' + cfuser
            )
        try:
            if json.loads(cf_url.text)['status'] != 'OK':
                return response_msg('error', 'Incorrect Codeforces Handle')
        except:
            return response_msg('error', 'could not connect to codeforces')

        # check if user exists
        try:
            connection = get_rdb_conn()
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['enroll'] == enroll
                ).run(connection)
        except:
            return response_msg('error', 'Could not connect to db')
        if len(cursor.items) != 0:
            return response_msg('error', 'User is already registered')

        # check if username is unique
        try:
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['username'] == username
                ).run(connection)
        except:
            return response_msg('error', 'Could not connect to db')
        if len(cursor.items) != 0:
            return response_msg('error', 'Username is already taken')

        # finally inserting in db
        # import ipdb; ipdb.set_trace()
        try:
            new_user = rdb.db(TODO_DB).table("user").insert({
                "fname": fname,
                "lname": lname,
                "email": email,
                "fb_email": "",
                "username": username,
                "passwd": hashlib.sha224(passwd).hexdigest(),
                "enroll": enroll,
                "cchandle": ccuser,
                "cfhandle": cfuser,
                "pic": DEFAULT_PIC + username + '.png'
            }).run(connection)
        except:
            return response_msg('error', 'error inserting in db')
        try:
            if new_user['inserted'] != 1:
                return response_msg('error', 'error inserting in db')
        except:
            return response_msg('error', 'error inserting in db')

        # return response_msg('success', 'OK')
        return response_msg('success', 'OK', auth_key=gen_auth_key(username))

    else:
        return response_msg('error', 'only GET/POST supported')


@app.route('/signin/', methods=['GET', 'POST'])
def signin():
    # import ipdb; ipdb.set_trace()
    remoteip = request.remote_addr
    if request.method == 'GET':
        try:
            user = get_user_from_auth(request.cookies['auth_key'])
            return redirect('/')
        except:
            pass
        return render_template('signin.html', app_id=FB_APP_ID)

    elif request.method == 'POST':
        form_data = json.loads(request.data)
        try:
            username = form_data['user']
            passwd = hashlib.sha224(form_data['passwd']).hexdigest()
            if request.headers.get('key'):
                key = request.headers.get('key')
            else:
                captcha_resp = form_data['g-recaptcha-response']
        except:
            return response_msg('error', 'form data not complete')

        if key:
            if key != ANDROID_HEADER_KEY:
                return response_msg('error', 'Authentication faiiled')
        else:
            if not check_captcha(captcha_resp, remoteip):
                return response_msg('error', 'Captcha authentication faiiled')

        # check if credentials are correct
        try:
            connection = get_rdb_conn()
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['username'] == username
                ).run(connection)
        except:
            return response_msg('error', 'Could not connect to db')

        if len(cursor.items) == 0:
            return response_msg('error', "User doesn't exists")

        db_pass = cursor.items[0]['passwd']
        if db_pass != passwd:
            return response_msg('error', 'Passwords do not match')

        return response_msg('success', 'logged in', auth_key=gen_auth_key(username))

    else:
        return response_msg('error', 'only GET/POST supported')


def auth_username(name):
    # import ipdb; ipdb.set_trace();
    try:
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('user').filter(
            rdb.row['username'] == name
            ).run(connection)
    except:
        return False

    if len(cursor.items) == 0:
        return False
    return True


@app.route('/profile/<name>/', methods=['GET'])
def profile(name):
    # import ipdb; ipdb.set_trace();
    auth = auth_username(name)
    if auth != True:
        return render_template('404.html'), 404
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''

    try:
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('user').filter(
            rdb.row['username'] == name
            ).run(connection)
        pic = cursor.items[0]['pic']
    except:
        return response_msg('error', 'Could not connect to db')

    return render_template('profile.html', pic=pic, username=name, login_user=user)


@app.route('/blog/new/<name>/', methods=['GET', 'POST'])
@login_required
def blog(name):
    return render_template('new_blog.html', username=name, login_user=name)

@app.route('/settings/<name>/', methods=['GET', 'POST'])
@login_required
def user_settings(name):
    auth = auth_username(name)
    if auth != True:
        return render_template('404.html'), 404

    if request.method == 'GET':
        try:
            user = get_user_from_auth(request.cookies['auth_key'])
            # return redirect('/')
        except:
            user = ''
        try:
            connection = get_rdb_conn()
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['username'] == name
                ).run(connection)
            pic = cursor.items[0]['pic']
        except:
            return response_msg('error', 'Could not connect to db')

        return render_template('settings.html',pic=pic, username=name, login_user=user, app_id=FB_APP_ID)
    else:
        import ipdb; ipdb.set_trace();
        return True


@app.route('/sync/<name>/', methods=['POST'])
@login_required
def sync_facebook(name):
    try:
        form_data = json.loads(request.data)
    except:
        return response_msg('error', 'data not correct')

    try:
        graph = GraphAPI(form_data['access_token'])
        try:
            # import ipdb; ipdb.set_trace();
            email = graph.get_object('me', fields='email')['email']
            pic = graph.get_object('me/picture', width='400', height='400')['url']
            print pic
            if email != form_data['fb_email']:
                return response_msg('error', 'incorrect facebook email')
        except:
            return response_msg('error', 'data not complete')
    except:
        return response_msg('error', 'invalid access token')

    try:
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('user').filter(
            rdb.row['username'] == name
            ).update({'fb_email': email, 'pic': pic}
            ).run(connection)
    except:
        return response_msg('error', 'Could not connect to db')

    return response_msg('success', 'OK')


@app.route('/about/', methods=['GET'])
def about():
    return render_template('about_us.html'), 200

@app.route('/discuss/', methods=['GET'])
def discuss():
    return render_template('discuss.html'), 200

@app.route('/problems/', methods=['GET'])
def problems():
    return render_template('problems.html'), 200


@app.route('/signin/facebook/', methods=['POST'])
def fb_signin():
    try:
        form_data = json.loads(request.data)
    except:
        return response_msg('error', 'json not found')
    try:
        fb_email = form_data['fb_email']
        access_token = form_data['access_token']
    except:
        return response_msg('error', 'form data not complete')

    # check access_token is correct
    # ipdb.set_trace()
    res = validate_fb_email(fb_email, access_token)
    resp = json.loads(res[0])
    if resp['status'] != 'success':
        return res

    # check if credentials are correct
    try:
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('user').filter(
            rdb.row['fb_email'] == fb_email
            ).run(connection)
    except:
        return response_msg('error', 'Could not connect to db')

    if len(cursor.items) == 0:
        return response_msg('error', "User doesn't exists")

    # store in session
    return response_msg('success', 'logged in', auth_key=gen_auth_key(cursor.items[0]['username']))    
