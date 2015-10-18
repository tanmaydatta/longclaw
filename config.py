from redis import Redis
from runserver import host

# rethink config
RDB_HOST = 'localhost'
RDB_PORT = 28015
TODO_DB = 'knuth'

rds = Redis()

DEFAULT_PIC = 'https://github.com/identicons/'
FB_APP_ID = 122742198082740

CAPTCHA_SECRET = '6LesFgwTAAAAAIy1YjMlYaWJ27QbqXP4Sm3tcDpI'

ANDROID_HEADER_KEY = 'a12eaa81ccd9743e3baee14f4425a4f5e23574dc6a505afb9c1a5d1b'
redis = Redis()
