from urllib.parse import urlencode
from urllib.request import Request, urlopen

import re

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'

class VKSessionError(Exception):
    pass

class VKSession:

    _headers = {
        'User-Agent': USER_AGENT,
        'Accept':     'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Origin':     'https://vk.com',
        'Cookie':     '',}

    _logged_in = False

    def __enter__(self):
        return self

    def __exit__(self, extype, exvalue, traceback):
        try:
            self.logout()
        except VKSessionError:
            raise VKSessionError

    def _get(self, url):
        request = Request(url, headers=self._headers)
        response = urlopen(request)
        return response, response.read().decode('cp1251'), response.getheader('set-cookie', default='')

    def _post(self, url, data, headers=None):
        request = Request(url, headers= headers or self._headers)
        request.add_header('Content-type', 'application/x-www-form-urlencoded')
        response = urlopen(request, urlencode(data).encode())
        return response, response.read().decode('cp1251'), response.getheader('set-cookie', default='')

    def login(self, email, password):
        if self._logged_in:
            raise VKSessionError
        response, body, cookie = self._get('http://vk.com')
        print(response.msg)

        ip_h = re.search('"ip_h" value="(?P<h>[A-Za-z0-9]+)"', body).group('h')
        lg_h = re.search('"lg_h" value="(?P<h>[A-Za-z0-9]+)"', body).group('h')
        remix_lhk = re.search('remixlhk=(?P<h>[A-Za-z0-9]+);', cookie).group('h')

        self._headers['Cookie'] = 'remixlang=0; remixflash=0.0.0; remixscreen_depth=24; remixdt=0; remixseenads=2; remixlhk=' + remix_lhk

        send = {'act': 'login',
                'role': 'al_frame',
                'expire': '',
                'captcha_sid': '',
                'captcha_key': '',
                '_origin': 'https://vk.com',
                'ip_h': ip_h,
                'lg_h': lg_h,
                'email': email,
                'pass': password,}

        response, body, cookie = self._post('https://login.vk.com/?act=slogin', send)
        print(response.msg)

        remix_sid = re.search('remixsid=(?P<h>[A-Za-z0-9]+);', cookie).group('h')

        self._headers['Cookie'] = 'remixlang=0; remixflash=0.0.0; remixscreen_depth=24; remixdt=0; remixseenads=2; remixsid=' + remix_sid

        response, body, cookie = self._get('https://vk.com')

        print(response.msg)
        self._logged_in = True
        return response, body, cookie

    def logout(self):
        if not self._logged_in:
            raise VKSessionError
        response, body, cookie = self._get('https://vk.com/')

        hhash = re.search('hash=(?P<h>[a-f0-9]+)', body).group('h')
        response, body, cookie = self._get('https://login.vk.com/?act=logout&hash=' + hhash +
                                          '&_origin=https://vk.com')
        self._headers['Cookie'] = ''
        print(response.msg)
        self._logged_in = False
        return response, body, cookie

    def get_cookie(self):
        return self.headers['Cookie']

if __name__ == '__main__':
    with VKSession() as session:
        session.login('', '')
        # do nothing and log out
