import json
from datetime import datetime
from pprint import pp
from random import randint
from time import sleep

import requests
from urllib3.util import parse_url

class MosRu:
    """ Класс для авторизации через логин/пароль Mos.Ru """

    _login: str = None
    _password: str = None
    OAUTH_URL = "https://login.mos.ru/sps/oauth/ae?" \
                "scope=openid+profile+blitz_user_rights+snils+contacts+blitz_change_password&" \
                "access_type=offline&" \
                "response_type=code&" \
                "redirect_uri=https://dnevnik.mos.ru/sudir" \
                "&client_id=dnevnik.mos.ru"

    def __init__(self, login, password):
        self._login = login
        self._password = password

    def dnevnik_authorization(self):
        """ Функция для проведения авторизации """
        ss = requests.Session()
        # ss.proxies = {
        #     'http': '85.26.146.169:80',
        #     'https': '85.26.146.169:80'
        # }
        ip_req = ss.get("http://icanhazip.com")
        my_ip = ip_req.content.decode("utf-8").strip()
        print(f"[+] Proxy ip - {ip_req.content.decode('utf-8')}")
        login_form_request = ss.get(self.OAUTH_URL)
        sleep(randint(10, 30) / 10)
        ss.get("https://stats.mos.ru/handler/handler.js?time={time}".format(time=datetime.today().timestamp()))
        sleep(randint(10, 30) / 10)
        login_request = ss.post("https://login.mos.ru/sps/login/methods/password", data={
            "isDelayed": False,
            "login": self._login,
            "password": self._password,
        }, allow_redirects=False)
        sleep(randint(10, 30) / 10)
        if login_request.status_code in range(300, 400):
            redirect_uri = login_request.headers["Location"]
            code = parse_url(redirect_uri).query.split("=")[1]
            req = ss.get("https://dnevnik.mos.ru/lms/api/sudir/oauth/te?code={}".format(code), headers={
                "Accept": "application/vnd.api.v3+json"
            })
            return json.loads(req.content.decode("utf-8"))["user_details"]["authentication_token"]
        else:
            raise Exception("Something went wrong!")

