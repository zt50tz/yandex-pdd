# coding: utf8

"""
Yandex.PDD API module
:author: Alexeev Nick
:email: n@akolka.ru
:version: 0.1b
"""

import requests
import datetime
import inspect
from functools import wraps


def inspect_args_func(frame):
    """
    Inspect current def arguments
    :param frame: inspect.currentframe()
    :return: dict
    """
    args, _, _, values = inspect.getargvalues(frame)
    return {key: values[key] for key in args if key != 'self'}


def response_full_d(key):
    """
    Wrap method of class for returning full response or only one key
    :param key: key for return / bool
    :return: mixed / bool
    """
    def wrapper(func):
        @wraps(func)
        def authorize_and_call(*args, **kwargs):
            r = func(*args, **kwargs)
            if args[0].response_full:
                return r
            if type(key) is bool:
                return key
            return r[key]
        return authorize_and_call
    return wrapper


class YandexPddException(Exception):
    """
    Exception of module
    """
    pass


class YandexPddExceptionY(Exception):
    """
    Exception by yandex request
    """
    pass


class YandexPdd(object):
    """ YandexPdd API object """

    _domain = None  # Domain name
    _token = None  # PDD Token
    _url = u'https://pddimp.yandex.ru/api2/'  # Request URL
    _registrar = False  # Request as registrar

    response_full = False  # Return full response by method or only functional key

    def __init__(self, domain, token, registrar=False, response_full=False):
        """
        Init
        :param token: PDD Token — https://tech.yandex.ru/pdd/doc/concepts/access-docpage/#access-admin
        :param domain: Domain name
        :param response_full: Return full response by method or only functional key
        :param registrar: Request as registrar
        """
        self._domain = domain
        self._token = token

        self._registrar = registrar
        self.response_full = response_full

    def _request(self, name, data, method='post'):
        """
        Base request method
        :param name: url path
        :param data: data / args of request
        :param method: request method - get/post
        :raise YandexPddException: bad request, jsonify failed
        :raise YandexPddExceptionY: yandex exception - success=false
        :return: dict
        """
        for key in data.keys():
            if data[key] is None:
                del data[key]
                continue
        if not data.get('domain'):
            data['domain'] = self._domain
        method = method.lower()
        if method not in ['get', 'post']:
            raise ValueError('Not right method')
        if method == 'post':
            kwargs = {'data': data}
        else:
            kwargs = {'params': data}
        kwargs.update({
            'headers': {'PddToken': self._token}
        })
        try:
            r = getattr(requests, method)(u'%s%s/%s' % (self._url, u'registrar' if self._registrar else u'admin', name), **kwargs)
        except Exception:
            raise YandexPddException(u'Request error: send', name, data)
        try:
            json = r.json()
        except Exception:
            raise YandexPddException(u'Request error: json', name, data, r.text)
        if not json.get('success') or json['success'] != 'ok':
            if not json.get('error'):
                json['error'] = u'Unknown'
            raise YandexPddExceptionY(json['error'])
        return json

    # -----------------------------------------------------------------------------------------------------------------
    # DOMAIN ACTIONS
    # -----------------------------------------------------------------------------------------------------------------

    def domain_register(self):
        """
        Register domain
        :return: dict
        """
        return self._request('domain/register', inspect_args_func(inspect.currentframe()))

    @response_full_d('status')
    def domain_registration_status(self):
        """
        Registration status
        :return: str: domain-activate;mx-activate;added / dict
        """
        return self._request('domain/registration_status', inspect_args_func(inspect.currentframe()), method='get')

    def domain_details(self):
        """
        Domain details
        :return: dict
        """
        return self._request('domain/details', inspect_args_func(inspect.currentframe()), method='get')

    @response_full_d(True)
    def domain_delete(self):
        """
        Domain delete
        :return: True / dict
        """
        return self._request('domain/delete', inspect_args_func(inspect.currentframe()))

    @response_full_d(True)
    def domain_settings_set_country(self, country):
        """
        Set country for domain
        :param country: Country name by ISO 3166-1
        :return: True / dict
        """
        return self._request('domain/settings/set_country', inspect_args_func(inspect.currentframe()))

    # -----------------------------------------------------------------------------------------------------------------
    # EMAIL ACTIONS
    # -----------------------------------------------------------------------------------------------------------------

    @response_full_d('uid')
    def email_add(self, login, password):
        """
        Email add
        :param login: email
        :param password: password
        :return: uid(int) / dict
        """
        return self._request('email/add', inspect_args_func(inspect.currentframe()))

    def email_list(self, page=1, on_page=30):
        """
        Email list
        :param page: Page
        :param on_page: Items on page
        :return: dict
        """
        return self._request('email/list', inspect_args_func(inspect.currentframe()), method='get')

    def email_list_all(self):
        """
        Email full list
        :return: list
        """
        pages = None
        page = 1
        on_page = 100
        ret = []
        while True:
            r = self.email_list(page=page, on_page=on_page)
            if pages is None:
                pages = r['pages']
            ret += r['accounts']
            if page > pages:
                break
        return ret

    @response_full_d(True)
    def email_edit(self, login=None, uid=None, password=None, iname=None, fname=None, enabled=None, birth_date=None, sex=None, hintq=None, hinta=None):
        """
        Email edit
        :param login: |Login / email
        :param uid: |Email uid
        :param password: Password
        :param iname: First name
        :param fname: Second name
        :param enabled: bool
        :param birth_date: datetime / %Y-%m-%d
        :param sex: 0-not set;1-male;2-female
        :param hintq: Secret question
        :param hinta: Secret answer
        :return: True / dict
        """
        if not login and not uid:
            raise ValueError('Login or uid required')
        data = inspect_args_func(inspect.currentframe())
        if data.get('enabled'):
            data['enabled'] = 'yes' if data['enabled'] else 'no'
        if data.get('bith_date'):
            if isinstance(data['bith_date'], datetime.date):
                data['bith_date'] = data['bith_date'].strftime('%Y-%m-%d')
        return self._request('email/edit', data)

    @response_full_d(True)
    def email_del(self, login=None, uid=None):
        """
        Email delete
        :param login: |Login / email
        :param uid: |Email uid
        :return: True / dict
        """
        if not login and not uid:
            raise ValueError('Login or uid required')
        return self._request('email/del', inspect_args_func(inspect.currentframe()))

    @response_full_d('counters')
    def email_counters(self, login=None, uid=None):
        """
        Email counters - messages
        :param login: |Login / email
        :param uid: |Email uid
        :return: dict
        """
        if not login and not uid:
            raise ValueError('Login or uid required')
        return self._request('email/counters', inspect_args_func(inspect.currentframe()), method='get')

    # -----------------------------------------------------------------------------------------------------------------
    # MAIL LIST ACTIONS
    # -----------------------------------------------------------------------------------------------------------------

    @response_full_d('uid')
    def email_ml_add(self, maillist):
        """
        Mail list add
        :param maillist: email
        :return: uid(int) / dict
        """
        return self._request('email/ml/add', inspect_args_func(inspect.currentframe()))

    ml_add = email_ml_add  # Alias

    @response_full_d('maillists')
    def email_ml_list(self):
        """
        List of mail lists
        :return: list / dict
        """
        return self._request('email/ml/list', inspect_args_func(inspect.currentframe()), method='get')

    ml_list = email_ml_list  # Alias

    @response_full_d(True)
    def email_ml_del(self, maillist=None, maillist_uid=None):
        """
        Mail list delete
        :param maillist: |Email
        :param maillist_uid: |Email uid
        :return: True / dict
        """
        if not maillist and not maillist_uid:
            raise ValueError('Maillist or uid required')
        return self._request('email/ml/del', inspect_args_func(inspect.currentframe()))

    ml_del = email_ml_del  # Alias

    @response_full_d(True)
    def email_ml_subscribe(self, maillist=None, maillist_uid=None, subscriber=None, subscriber_uid=None, can_send_on_behalf=None):
        """
        Mail list subscribe email
        :param maillist: |Email
        :param maillist_uid: |Email uid
        :param subscriber: |Email subscriber
        :param subscriber_uid: |Email subscriber uid
        :param can_send_on_behalf: can send by email list name
        :return: True / dict
        """
        if not maillist and not maillist_uid:
            raise ValueError('Maillist or uid required')
        if not subscriber and not subscriber_uid:
            raise ValueError('Subscriber or uid required')
        return self._request('email/ml/subscribe', inspect_args_func(inspect.currentframe()))

    ml_subscribe = email_ml_subscribe  # Alias

    @response_full_d('subscribers')
    def email_ml_subscribers(self, maillist=None, maillist_uid=None):
        """
        Mail list subscribes list
        :param maillist: | Email
        :param maillist_uid: |Email uid
        :return: list / dict
        """
        if not maillist and not maillist_uid:
            raise ValueError('Maillist or uid required')
        return self._request('email/ml/subscribers', inspect_args_func(inspect.currentframe()), method='get')

    ml_subscribers = email_ml_subscribers # Alias

    @response_full_d(True)
    def email_ml_unsubscribe(self, maillist=None, maillist_uid=None, subscriber=None, subscriber_uid=None):
        """
        Email list unsubscribe email
        :param maillist: |Email
        :param maillist_uid: |Email uid
        :param subscriber: |Email subscriber
        :param subscriber_uid: |Email subscriber uid
        :return: True / dict
        """
        if not maillist and not maillist_uid:
            raise ValueError('Maillist or uid required')
        if not subscriber and not subscriber_uid:
            raise ValueError('Subscriber or uid required')
        return self._request('email/ml/unsubscribe', inspect_args_func(inspect.currentframe()))

    ml_unsubscribe = email_ml_unsubscribe # Alias

    @response_full_d('can_send_on_behalf')
    def email_ml_get_can_send_on_behalf(self, maillist=None, maillist_uid=None, subscriber=None, subscriber_uid=None):
        """
        Email list get subscriber can send mail by name of mail list
        :param maillist: |Email
        :param maillist_uid: |Email uid
        :param subscriber: |Email subscriber
        :param subscriber_uid: |Email subscriber uid
        :return: bool / dict
        """
        if not maillist and not maillist_uid:
            raise ValueError('Maillist or uid required')
        if not subscriber and not subscriber_uid:
            raise ValueError('Subscriber or uid required')
        return self._request('email/ml/get_can_send_on_behalf', inspect_args_func(inspect.currentframe()), method='get')

    ml_send_get = email_ml_get_can_send_on_behalf # Alias

    @response_full_d(True)
    def email_ml_set_can_send_on_behalf(self, maillist=None, maillist_uid=None, subscriber=None, subscriber_uid=None, can_send_on_behalf=None):
        """
        Email list set subscriber can send mail by name of mail list
        :param maillist: |Email
        :param maillist_uid: |Email uid
        :param subscriber: |Email subscriber
        :param subscriber_uid: |Email subscriber uid
        :param can_send_on_behalf: can send by email list name
        :return: True / dict
        """
        if not maillist and not maillist_uid:
            raise ValueError('Maillist or uid required')
        if not subscriber and not subscriber_uid:
            raise ValueError('Subscriber or uid required')
        return self._request('email/ml/set_can_send_on_behalf', inspect_args_func(inspect.currentframe()))

    ml_send_set = email_ml_set_can_send_on_behalf  # Alias

    # -----------------------------------------------------------------------------------------------------------------
    # IMPORT MAILBOX ACTIONS
    # -----------------------------------------------------------------------------------------------------------------

    @response_full_d(True)
    def import_check_settings(self, method='imap', server='imap.yandex.ru', port=993, ssl=True):
        """
        Check that yandex can import server
        :param method: imap;imap4;pop;pop3
        :param server: Domain name / ip ext server
        :param port: Port
        :param ssl: bool
        :return: True / dict
        """
        return self._request('import/check_settings', inspect_args_func(inspect.currentframe()), method='get')

    @response_full_d(True)
    def import_start_one_import(self, method='imap', server='imap.yandex.ru', port=993, ssl=True, ext_login=None, ext_passwd=None, int_login=None, int_passwd=None):
        """
        Import mailbox
        :param method: imap;imap4;pop;pop3
        :param server: Domain name / ip ext server
        :param port: Port
        :param ssl: bool
        :param ext_login: External login
        :param ext_passwd: External password
        :param int_login: opt, internal login
        :param int_passwd: opt, internal password
        :return:
        """
        data = inspect_args_func(inspect.currentframe())
        for key in data:
            for key_fix in ['ext', 'int']:
                if key.startswith('%s_' % key_fix):
                    data['%s-%s' % (key_fix, key[len(key_fix) + 1:])] = data[key]
                    del data[key]
        return self._request('import/start_one_import', data)

    @response_full_d('import')
    def import_check_imports(self, page=1, on_page=10):
        """
        Check status of imports
        :param page: Page
        :param on_page: Items on page
        :return: list / dict
        """
        return self._request('import/check_imports', inspect_args_func(inspect.currentframe()), method='get')

    @response_full_d(True)
    def import_stop_all_imports(self):
        """
        Stop all imports
        :return: True / dict
        """
        return self._request('import/stop_all_imports', inspect_args_func(inspect.currentframe()))

    # -----------------------------------------------------------------------------------------------------------------
    # ADMIN ACTIONS
    # -----------------------------------------------------------------------------------------------------------------

    @response_full_d(True)
    def deputy_add(self, login):
        """
        Add subadmin for domain
        :param login: Email, *@yandex.ru
        :return: True / dict
        """
        return self._request('deputy/add', inspect_args_func(inspect.currentframe()))

    @response_full_d('deputies')
    def deputy_list(self):
        """
        Get subadmin list for domain
        :return: list / dict
        """
        return self._request('deputy/list', inspect_args_func(inspect.currentframe()), method='get')

    @response_full_d(True)
    def deputy_delete(self, login):
        """
        Remove subadmin from domain
        :param login: Email, *@yandex.ru
        :return: True / dict
        """
        return self._request('deputy/delete', inspect_args_func(inspect.currentframe()))

    # -----------------------------------------------------------------------------------------------------------------
    # DKIM ACTIONS
    # -----------------------------------------------------------------------------------------------------------------

    @response_full_d('dkim')
    def dkim_status(self, secretkey=None):
        """
        DKIM get status
        :param secretkey: bool, get secret key
        :return: dict
        """
        data = inspect_args_func(inspect.currentframe())
        data['secretkey'] = 'yes' if data['secretkey'] else None
        return self._request('dkim/status', data, method='get')

    @response_full_d('dkim')
    def dkim_enable(self):
        """
        DKIM enable
        :return: dict
        """
        return self._request('dkim/enable', inspect_args_func(inspect.currentframe()))

    @response_full_d('dkim')
    def dkim_disable(self):
        """
        DKIM disable
        :return: dict
        """
        return self._request('dkim/disable', inspect_args_func(inspect.currentframe()))

    # -----------------------------------------------------------------------------------------------------------------
    # DNS ACTIONS
    # -----------------------------------------------------------------------------------------------------------------

    @response_full_d('record')
    def dns_add(self, type, admin_mail=None, content=None, priority=None, weight=None, port=None, target=None, subdomain=None, ttl=None):
        """
        DNS add record
        :param type: SRV;TXT;NS;MX;SOA;A;AAAA;CNAME.
        :param admin_mail: admin mail
        :param content: value
        :param priority: int
        :param weight: int
        :param port: int
        :param target: value
        :param subdomain: value
        :param ttl: int
        :return: dict
        """
        return self._request('dns/add', inspect_args_func(inspect.currentframe()))

    @response_full_d('records')
    def dns_list(self):
        """
        DNS get records
        :return: list / dict
        """
        return self._request('dns/list', inspect_args_func(inspect.currentframe()), method='get')

    @response_full_d(True)
    def dns_edit(self, record_id, admin_mail=None, content=None, priority=None, weight=None, port=None, target=None, subdomain=None, ttl=None):
        """
        DNS edit record
        :param record_id: Record id
        :param admin_mail: admin mail
        :param content: value
        :param priority: int
        :param weight: int
        :param port: int
        :param target: value
        :param subdomain: value
        :param ttl: int
        :return: True / dict
        """
        return self._request('dns/edit', inspect_args_func(inspect.currentframe()))

    @response_full_d(True)
    def dns_del(self, record_id):
        """
        DNS delete record
        :param record_id: Record id
        :return: True / dict
        """
        return self._request('dns/del', inspect_args_func(inspect.currentframe()))

    # -----------------------------------------------------------------------------------------------------------------
    # AUTH ACTIONS
    # -----------------------------------------------------------------------------------------------------------------

    @response_full_d('oauth-token')
    def email_get_oauth_token(self, login=None, uid=None):
        """
        Get oauth token
        :param login: |Email / login
        :param uid: |Email uid
        :return: str / dict
        """
        return self._request('email/get_oauth_token', inspect_args_func(inspect.currentframe()))

    def passport_oauth(self, retpath, access_token=None, email=None):
        """
        Get link for auth
        :param retpath: return url
        :param access_token: |access token
        :param email: |email
        :return:
        """
        data = {
            'retpath': retpath,
            'access_token': access_token
        }
        if not data['access_token']:
            if not email:
                raise ValueError('Access token or email required')
            data['access_token'] = self.email_get_oauth_token(login=email)
        return ''''https://passport.yandex.ru/passport?mode=oauth&access_token=%(access_token)s&type=trusted-pdd-partner&retpath=%(retpath)s''' % data
