from redis import Redis

# rethink config
RDB_HOST = 'localhost'
RDB_PORT = 28015
TODO_DB = 'knuth'


DEFAULT_PIC = '/static/images/justen.jpg'
FB_APP_ID = 161142620896547

CAPTCHA_SECRET = '6LesFgwTAAAAAIy1YjMlYaWJ27QbqXP4Sm3tcDpI'

redis = Redis()
