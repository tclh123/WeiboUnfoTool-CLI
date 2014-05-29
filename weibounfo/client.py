# coding: utf-8

import os
from weibounfo.lib.snspy import APIClient, APIError
from weibounfo.lib.snspy import SinaWeiboMixin

from weibounfo.config import APP_KEY, APP_SECRET, CALLBACK_URL

here = os.path.abspath(os.path.dirname(__file__))


def get_access_token():
    try:
        with open(os.path.join(here, 'access_token.bak'), 'r') as f:
            text = f.read()
            res = text.splitlines()
        return res
    except Exception as e:
        print 'Error with get_access_token()'
        raise e

access_token, expires, owner_uid = get_access_token()


def client_with_access_token(a):
    c = APIClient(SinaWeiboMixin,
                  app_key=APP_KEY, app_secret=APP_SECRET,
                  redirect_uri=CALLBACK_URL,
                  access_token=a, expires=expires)
    return c

client = client_with_access_token(access_token)


def test_friends():
    idx = [0]

    def f(cursor):
        r = client.friendships.friends.get(uid=1659177872, count=200, cursor=cursor)
        for u in r.users:
            idx[0] += 1
            print '%s: %s' % (idx[0], u.screen_name)
        return r.next_cursor

    c = f(0)
    while c:
        print c
        c = f(c)

    print idx[0]


if __name__ == '__main__':
    test_friends()
