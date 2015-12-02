from longclaw import app
import rethinkdb as rdb
import json
from rethinkdb.errors import RqlRuntimeError
from flask import request, render_template, redirect
import requests
from urllib import urlencode
from urllib2 import urlopen
import re
import hashlib
from facebook import GraphAPI, GraphAPIError
from auth import *
from cors import *
import math
from bs4 import BeautifulSoup
import re

#from flask.ext.mail import Message
#from mail_config import *
#from longclaw import mail
import os
#from markdown2 import markdown


@app.route('/xyz/')
def test():
    return render_template('test.html')


def authenticate_webkiosk(enroll, passwd, dob):
    try:
        check = requests.get(
            'https://webkiosk.jiit.ac.in/CommonFiles/UserActionn.jsp?' +
            'x=&txtInst=Institute&' +
            'InstCode=JIIT&' +
            'txtuType=Member+Type&' +
            'UserType=S&' +
            'txtCode=Enrollment+No&' +
            'MemberCode=' + enroll +
            '&DOB=DOB' +
            '&DATE1=' + dob + 
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
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''
    return render_template('home.html', login_user=user), 200
    #return 'Hello World!'

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
        return response_msg('error',
            'facebook not synced or user not registered')

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
        return response_msg('error', 'invalid fb details')


@app.route('/signup/', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['Content-Type', 'auth_key'])
def signup():
    #import ipdb; ipdb.set_trace();
    if request.method == 'GET':
        return render_template("signup.html")
    elif request.method == 'POST':
        form_data = json.loads(request.data)
        try:
	    dob = form_data['dob']
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
                captcha_resp = ""
            else:
                key = ""
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

        if not authenticate_webkiosk(enroll, wbpass, dob):
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
        #import ipdb; ipdb.set_trace()
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

        #import ipdb;ipdb.set_trace()
        ratings = rating(cfuser, ccuser,0)
        ratings = json.loads(ratings[0])
        try:
            lrating = ratings['lrating']
            cfrating = ratings['cf_rating']
            srating = ratings['srating']
        except:
            lrating = 0
            srating = 0
            cfrating = 0

        colg_rating = 20 * ((cfrating/100)**2)
        colg_rating = colg_rating + 2000 + 7 * (((lrating/1000)**2) + (lrating/20))
        colg_rating = colg_rating + 2000 + 5 * (((srating/100)**2) + (srating/20))

        try:
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['username'] == username
                ).update({
                'lrating': lrating,
                'srating': srating,
                'cfrating': cfrating,
                'colg_rating': colg_rating/3
                }).run(connection)
        except:
            pass
        # return response_msg('success', 'OK')
        return response_msg('success', 'OK', auth_key=gen_auth_key(username), user=username)

    else:
        return response_msg('error', 'only GET/POST supported')


@app.route('/signin/', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['Content-Type', 'auth_key'])
def signin():
    # #import ipdb; ipdb.set_trace()
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
                captcha_resp = ''
            else:
                key = ""
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

        return response_msg('success', 'logged in', auth_key=gen_auth_key(username), user=username)

    else:
        return response_msg('error', 'only GET/POST supported')


def auth_username(name):
    # #import ipdb; ipdb.set_trace();
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
    # #import ipdb; ipdb.set_trace();
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

    return render_template('profile.html', user=cursor.items[0], login_user=user, username=name)


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

    # #import ipdb;ipdb.set_trace()
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
        # #import ipdb; ipdb.set_trace();
        try:
            form_data = json.loads(request.data)
            passwd = form_data['passwd']
            cpasswd = form_data['cpasswd']
            npasswd = form_data['npasswd']
            if len(npasswd) < 6:
                return response_msg(
                    'error',
                    'Password should be minimum of 6 characters'
                    )
            passwd = hashlib.sha224(form_data['passwd']).hexdigest()
            cpasswd = hashlib.sha224(form_data['cpasswd']).hexdigest()
            npasswd = hashlib.sha224(form_data['npasswd']).hexdigest()
            if request.headers.get('key'):
                key = request.headers.get('key')
            else:
                key = ""
        except:
            return response_msg('error', 'form data not complete')

        if key:
            if key != ANDROID_HEADER_KEY:
                return response_msg('error', 'Authentication faiiled')

        # check if credentials are correct
        try:
            connection = get_rdb_conn()
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['username'] == name
                ).run(connection)
        except:
            return response_msg('error', 'Could not connect to db')

        db_pass = cursor.items[0]['passwd']
        if db_pass != passwd:
            return response_msg('error', 'Current Password does not match')

        if cpasswd != npasswd:
            return response_msg('error', 'New Passwords do not match')

        try:
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['username'] == name
                ).update({'passwd': cpasswd}
                ).run(connection)
        except:
            return response_msg('error', 'Could not connect to db')

        return response_msg('success', 'OK')


@app.route('/sync/<name>/', methods=['POST'])
@login_required
def sync_facebook(name):
    #import ipdb; ipdb.set_trace();
    try:
        form_data = json.loads(request.data)
    except:
        return response_msg('error', 'data not correct')

    try:
        graph = GraphAPI(form_data['access_token'])
        try:
            # #import ipdb; ipdb.set_trace();
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
        cursor = rdb.db(TODO_DB).table('user').filter(
            rdb.row['username'] == name
            ).run(connection)
    except:
        return response_msg('error', 'Could not connect to db')

    return response_msg('success', 'OK', data=cursor.items[0])


@app.route('/about/', methods=['GET'])
def about():
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''
    return render_template('about_us.html', login_user=user), 200


@app.route('/ratings/', methods=['GET'])
def ratings():
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''
    return render_template('ratings.html', login_user=user), 200


@app.route('/all_ratings/', methods=['GET'])
def all_ratings():
    # import ipdb; ipdb.set_trace()
    try:
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('user').filter(
            rdb.row["username"] != "admin").pluck(
            "srating", "lrating", "cfrating", "colg_rating", "username"
            ).run(connection)
    except:
        return response_msg('error', 'could not connect to db')

    return response_msg('success', 'OK', users=cursor.items)


@app.route('/discuss/', methods=['GET'])
def discuss():
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''
    return render_template('discuss.html', login_user=user), 200


@app.route('/facebook/', methods=['GET'])
def facebook():
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''
    try:
        access_token = rds.get('access_token')
    except:
        access_token = ''
    return render_template('facebook.html', login_user=user, access_token=access_token), 200

@app.route('/facebook/album/<id>/', methods=['GET'])
def album(id):
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''
    try:
        access_token = rds.get('access_token')
    except:
        access_token = ''
    return render_template('album.html', login_user=user, album_id=id, access_token=access_token), 200

# @app.route('/facebook/album/<page>/', methods=['GET'])
# def album(page):
#     try:
#         user = get_user_from_auth(request.cookies['auth_key'])
#         # return redirect('/')
#     except:
#         user = ''
   
#     except Exception as e:
#         print e
#         return response_msg('error', 'Could not connect to db')
#     # #import ipdb; ipdb.set_trace()
#     return render_template('album.html', problems=cursor.items, count=count, login_user=user), 200



@app.route('/problem/<id>/', methods=['GET'])
def problems(id):
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''
    try:
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('problems').filter(
            rdb.row['prob_id'] == int(id)
            ).run(connection)
    except:
        return response_msg('error', 'Could not connect to db')

    if len(cursor.items) == 0:
        return render_template('404.html'), 404
    return render_template('problems.html', problem=cursor.items[0], login_user=user), 200

@app.route('/select/', methods=['GET'])
@admin_required
def select():
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''
    return render_template('select.html', login_user=user, app_id=FB_APP_ID), 200

    

@app.route('/add_problem/', methods=['GET', 'POST'])
@admin_required
def add_problem():
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''
    if request.method == 'GET':
        return render_template('add_problem.html'), 200
    elif request.method == 'POST':
        #import ipdb; ipdb.set_trace()
        try:
            form_data = json.loads(request.data)
        except:
            return response_msg('error', 'data not complete')

        try:
            name = form_data['name']
            tl = form_data['time']
            tags = form_data['tags'].split(',')
            statement = markdown(form_data['statement'])
            ip = markdown(form_data['ip'])
            op = markdown(form_data['op'])
            sip = markdown(form_data['sip'])
            sop = markdown(form_data['sop'])
            level = form_data['level']

        except:
            return response_msg('error', 'data not complete')


        try:
            connection = get_rdb_conn()
            prob_id = rdb.db(TODO_DB).table("problems").max(
                'prob_id'
                ).run(connection)
            prob_id = prob_id['prob_id'] + 1
            new_user = rdb.db(TODO_DB).table("problems").insert({
                "name": name,
                "level": level,
                "input": ip,
                "output": op,
                "prob_id": prob_id,
                "sample_input": sip,
                "sample_output": sop,
                "statement": statement,
                "tags": tags,
                "time_limit": float(tl)
            }).run(connection)
        except:
            return response_msg('error', 'error inserting in db')
        try:
            if new_user['inserted'] != 1:
                return response_msg('error', 'error inserting in db')
        except:
            return response_msg('error', 'error inserting in db')

        # return response_msg('success', 'OK')
        return response_msg('success', 'OK')

    else:
        return response_msg('error', 'only GET/POST')


@app.route('/admin/', methods=['GET', 'POST'])
def admin():
    # #import ipdb; ipdb.set_trace()
    if request.method == 'GET':
        return render_template('admin.html'), 200

    elif request.method == 'POST':
        try:
            form_data = json.loads(request.data)
        except:
            return response_msg('error', 'data not complete')

        try:
            user = form_data['user']
            passwd = hashlib.sha224(form_data['passwd']).hexdigest()
        except:
            return response_msg('error', 'data not complete')

        try:
            connection = get_rdb_conn()
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['username'] == user
                ).run(connection)
        except:
            return response_msg('error', 'Could not connect to db')

        if len(cursor.items) == 0:
            return response_msg('error', "User doesn't exists")

        db_pass = cursor.items[0]['passwd']
        if db_pass != passwd:
            return response_msg('error', 'Passwords do not match')

        return response_msg('success', 'logged in', admin_key=gen_auth_key(user), user=user)

    else:
        return response_msg('error', 'only GET/POST')


@app.route('/signin/facebook/', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def fb_signin():
    #import ipdb; ipdb.set_trace()
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
    return response_msg('success', 'logged in',
        auth_key=gen_auth_key(cursor.items[0]['username']),
        user=cursor.items[0]['username'])


@app.route('/auth_key/', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='auth_key')
def check_auth_key():
    # ipdb.set_trace()
    try:
        auth_key = request.headers.get('auth_key')
    except:
        return response_msg('error', 'auth_key not found')
    
    try:
        user = get_user_from_auth(request.headers.get('auth_key'))
        try:
            connection = get_rdb_conn()
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['username'] == user
                ).run(connection)
        except:
            return response_msg('error', 'Could not connect to db')
        return response_msg('success', 'user authenticated', user=cursor.items[0])
    except:
        return response_msg('error', 'invalid auth_key')       


@app.route('/get_user/<name>/', methods=['GET', 'POST', 'OPTIONS'])
def get_user(name):
    try:
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('user').filter(
            rdb.row['username'] == name
            ).run(connection)
    except:
        return response_msg('error', 'could not connect to db')

    if len(cursor.items) == 0:
        return response_msg('error', 'user doesn\'t exists')

    user = cursor.items[0]
    user.pop('id', None)
    user.pop('passwd', None)
    return response_msg('success', 'OK', data=user)


@app.route('/problemset/', methods=['GET'])
def problemset():
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''
    try:
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('problems').filter(
            (rdb.row['prob_id'] >= 1) & (rdb.row['prob_id'] <= 10)
            ).run(connection)

        count = int(math.ceil(rdb.db(TODO_DB).table('problems').count().run(connection)/10.0))
    except:
        return response_msg('error', 'Could not connect to db')
    # #import ipdb; ipdb.set_trace()
    return render_template('problem_set.html', problems=cursor.items, count=count, login_user=user), 200


@app.route('/problemset/page/<page>/', methods=['GET'])
def problemset_page(page):
    try:
        user = get_user_from_auth(request.cookies['auth_key'])
        # return redirect('/')
    except:
        user = ''
    try:
        # #import ipdb; ipdb.set_trace()
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('problems').filter(
            (rdb.row['prob_id'] >= int(page)*10-9) & (rdb.row['prob_id'] <= int(page)*10)
            ).run(connection)

        count = int(math.ceil(rdb.db(TODO_DB).table('problems').count().run(connection)/10.0))
        # count = 1
    except Exception as e:
        print e
        return response_msg('error', 'Could not connect to db')
    # #import ipdb; ipdb.set_trace()
    return render_template('problem_set.html', problems=cursor.items, count=count, login_user=user), 200


def send_mail(body, to):
    msg = Message('Change Password', sender=ADMINS[0], recipients=[to])
    msg.body = body
    mail.send(msg)


@app.route('/change_pass/<token>/', methods=['GET', 'POST'])
def change_pass(token):
    user = ''
    try:
        user = rds.get(token)
    except:
        return response_msg('error', 'could not connect to db')
    if request.method == 'GET':
        if not user:
            return response_msg('error', 'invalid token')
        return render_template('forgot.html', token=token), 200

    elif request.method == 'POST':
        if not user:
            return response_msg('error', 'invalid token')
        try:
            passwd = form_data['passwd']
            cpasswd = form_data['cpasswd']
        except:
            return response_msg('error', 'data not complete')

        if len(passwd) < 6:
            return response_msg('error', 'password should minimum 6 characters long')

        if passwd != cpasswd:
            return response_msg('error', 'passwords do not match')

        try:
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['username'] == user
                ).update({'passwd': cpasswd}
                ).run(connection)
        except:
            return response_msg('error', 'Could not connect to db')
        return render_template('signin.html', app_id=FB_APP_ID)

    else:
        return response_msg('error', 'only GET/POST')


@app.route('/forgot/', methods=['POST'])
def forgot():
    # #import ipdb; ipdb.set_trace()
    if request.method == 'POST':
        try:
            form_data = request.form
        except:
            return response_msg('error', 'data not complete')

        try:
            user = form_data['user']
        except:
            return response_msg('error', 'data not complete')

        try:
            connection = get_rdb_conn()
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['username'] == user
                ).run(connection)
        except:
            return response_msg('error', 'could not connect to db')

        if len(cursor.items) == 0:
            return response_msg('error', 'user doesn\'t exists')

        email = cursor.items[0]['email']
        token = hashlib.sha1(os.urandom(128)).hexdigest()
        try:
            if rds.set(token, user, ex=3600):
                pass
            else:
                return response_msg('error', 'could not generate token')
        except:
            return response_msg('error', 'could not connect to db')

        body = ('Please click the following link to change your password.\n' + 'http://'
            '' + host + ':5000/change_pass/' + token + '/')
        try:
            send_mail(body, email)
        except:
            return response_msg('error', 'could not send an email')

        return  response_msg('success', 'OK', token=token)

    else:
        return response_msg('error', 'only POST')


@app.route('/rating/<username>/', methods=['GET'])
def get_rating(username):
    try:
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('user').filter(
            rdb.row['username'] == username
            ).run(connection)
        if len(cursor.items) == 0:
            return response_msg('error', 'user doesnt exist')
        cf_username = cursor.items[0]['cfhandle']
        cc_username = cursor.items[0]['cchandle']
        try:
            colg_rating = cursor.items[0]['colg_rating']
        except:
            colg_rating = 0
    except:
        return response_msg('error', 'Could not connect to db')
    
    return rating(cf_username, cc_username, colg_rating)


def rating(cf_username, cc_username, colg_rating):
    # import ipdb;ipdb.set_trace()
    
    try:
        page = requests.get("https://www.codechef.com/users/" + cc_username)
        soup = BeautifulSoup(page.text, "html.parser")
        table = soup.find_all('table', {'class':'rating-table'})[0]
        trs = table.find_all('tr')
        
        td = trs[1].find_all('td')[2].text
        lrating = re.findall(r'\d+', td)
        if len(lrating) > 0:
            lrating = lrating[0]
        else:
            lrating = 0 
        td = trs[2].find_all('td')[2].text
        srating = re.findall(r'\d+', td)
        if len(srating) > 0:
            srating = srating[0]
        else:
            srating = 0
        
        # cf rating
        resp = requests.get("http://codeforces.com/api/user.info?handles=" + cf_username).json()
        try:
            cf_rating = resp['result'][0]['rating']
        except:
            cf_rating = 0

        return response_msg('success', 'OK',colg_rating=colg_rating,cf_rating=cf_rating, lrating=int(lrating), srating=int(srating))
    except:
        return response_msg("error", 'unable to fetch') 


@app.route('/sync_ratings/')
def sync_ratings():
    try:
        connection = get_rdb_conn()
        cursor = rdb.db(TODO_DB).table('user').run(connection)
    except:
        return response_msg('error', 'could not connect to db')
    for user in cursor.items:
        ratings = rating(user['cfhandle'], user['cchandle'], user['colg_rating'])
        ratings = json.loads(ratings[0])
        colg_rating = 0
        try:
            colg_rating = colg_rating + 20 * ((ratings['cf_rating']/100)**2)
            colg_rating = colg_rating + 2000 + 7 * (((ratings['lrating']/1000)**2) + (ratings['lrating']/20))
            colg_rating = colg_rating + 2000 + 5 * (((ratings['srating']/100)**2) + (ratings['srating']/20))
        except:
            pass
        print colg_rating
        try:
            cursor = rdb.db(TODO_DB).table('user').filter(
                rdb.row['username'] == user['username']
                ).update({
                'lrating': ratings['lrating'],
                'srating': ratings['srating'],
                'cfrating': ratings['cf_rating'],
                'colg_rating': colg_rating/3,
                }).run(connection)
            print user['username']
        except:
            print 'error' + user['username']

    return response_msg('sucess', 'OK')

@app.route("/admin/access_token/", methods=['POST'])
def sync_access_token():
    # import ipdb; ipdb.set_trace()
    form_data = json.loads(request.data)
    access_token = form_data['access_token']
    long_lived_url = ("https://graph.facebook.com/oauth/access_token?"
        "client_id=" + str(FB_APP_ID) + "&client_secret=" + FB_APP_SECRET + 
        "&grant_type=fb_exchange_token&fb_exchange_token=" + access_token)
    long_lived_resp = requests.get(long_lived_url).text
    long_lived_token = long_lived_resp.split('&')[0].split('=')[1]
    if rds.set('access_token', long_lived_token):
        return response_msg('success', 'OK')
    else:
        return response_msg('error', 'could not connect to redis server')
