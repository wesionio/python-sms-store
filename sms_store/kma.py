#!/usr/bin/env python
# encoding: utf-8

import os
import requests
import time
import json
import re
import profig
import cli_print as cp
from urllib import parse as url_parse
from .errors import *


class KMA:
    def __init__(self,
                 path_to_conf: str = 'config.ini',

                 cli: bool = False,
                 header_dict: dict = None,
                 username: str = None,
                 password: str = None,
                 token: str = None,
                 item_id=None,
                 exclude_no=None,
                 sms_interval=None,
                 sms_wait_max=None,
                 mobile=None,
                 ):
        """
        KMA Service

        :param path_to_conf:
        :param cli:
        :param header_dict:
        :param username:
        :param password:
        :param token:
        :param item_id:
        :param exclude_no:
        :param sms_interval:
        :param sms_wait_max:
        :param mobile:
        """
        cfg = profig.Config(path_to_conf)
        cfg.init('sms_52kma.username', '')
        cfg.init('sms_52kma.password', '')
        cfg.init('sms_52kma.token', '')
        cfg.init('sms_52kma.item_id', '')
        cfg.init('sms_52kma.exclude_no', '')
        cfg.init('sms_52kma.sms_interval', 5)
        cfg.init('sms_52kma.sms_wait_max', 180)
        cfg.sync()

        self._base_url = 'http://api.fxhyd.cn/UserInterface.aspx'

        self._cli = cli

        self._header_dict = header_dict or {
            'User-Agent': os.getenv(
                'YM_USERAGENT',
                'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'),
        }

        self._username = username or cfg['sms_52kma.username']
        self._password = password or cfg['sms_52kma.password']
        self._token = token or cfg['sms_52kma.token'] or self._get_token()
        self._item_id = item_id or cfg['sms_52kma.item_id']
        self._exclude_no = exclude_no or cfg['sms_52kma.exclude_no']
        self._sms_interval = sms_interval or cfg['sms_52kma.sms_interval']
        self._sms_wait_max = sms_wait_max or cfg['sms_52kma.sms_wait_max']

        self._mobile = mobile
        pass

    @property
    def mobile(self):
        """
        Mobile number

        :return: string
        """
        if self._mobile:
            return '+86{}'.format(self._mobile)
        else:
            raise NoMobileError('No mobile number there.')

    @staticmethod
    def _raise(s):
        """
        Raise exception

        :param str s: Error string
        :return:
        """
        cp.fx()

        errors = {
            '1001': '参数 token 不能为空',
            '1002': '参数 action 不能为空',
            '1003': '参数 action 错误',
            '1004': 'token 失效',
            '1005': '用户名或密码错误',
            '1006': '用户名不能为空',
            '1007': '密码不能为空',
            '1008': '账户余额不足',
            '1009': '账户被禁用',
            '1010': '参数错误',
            '1011': '账户待审核',
            '1012': '登录数达到上限',
            '2001': '参数 itemid 不能为空',
            '2002': '项目不存在',
            '2003': '项目未启用',
            '2004': '暂时没有可用的号码',
            '2005': '获取号码数量已达到上限',
            '2006': '参数 mobile 不能为空',
            '2007': '号码已被释放',
            '2008': '号码已离线',
            '2009': '发送内容不能为空',
            '2010': '号码正在使用中',
            '3001': '尚未收到短信',
            '3002': '等待发送',
            '3003': '正在发送',
            '3004': '发送失败',
            '3005': '订单不存在',
            '3006': '专属通道不存在',
            '3007': '专属通道未启用',
            '3008': '专属通道密码与项目不匹配',
            '9001': '系统错误',
            '9002': '系统异常',
            '9003': '系统繁忙',
        }

        if s in errors:
            raise ApiException('Error #.%s    %s' % (s, errors[s]))
        else:
            raise ApiException('Error #.%s    Unknown' % s)

    def _get_url_by_query(self, query: dict):
        return '{base_url}?{query}'.format(
            base_url=self._base_url,
            query=url_parse.urlencode(query),
        )

    def _req_text(self, query):
        """
        Make request and get result as a list

        :param query:
        :return: list
        """
        url = '{base_url}?{query}'.format(
            base_url=self._base_url,
            query=url_parse.urlencode(query),
        )

        resp = requests.get(url=url, headers=self._header_dict)

        return resp.text

    def _req(self, query):
        """
        Make request and get result as a str

        :param dict query:
        :return: str
        """
        return self._req_text(query=query).split('|')

    def _get_result(self, query):
        r = self._req(query=query)

        if 'success' == r[0]:
            return r[1]
        else:
            self._raise(r)

    def _get_success(self, query):
        r = self._req(query=query)

        if 'success' == r[0]:
            return True
        else:
            self._raise(r)

    def _get_json(self, query):
        return json.loads(self._get_result(query=query))

    def _get_token(self):
        """
        Get token

        :return: str
        """
        if self._cli:
            cp.getting('Getting token')

        token = self._get_result({
            'action': 'login',
            'username': self._username,
            'password': self._password,
        })

        if self._cli:
            cp.value(token)

        return token

    def get_account_info(self):
        """
        Get account info.

        :return: dict
        """

        if self._cli:
            cp.getting('Getting account info', inline=False)

        # get account info
        account_info = self._get_json({
            'action': 'getaccountinfo',
            'token': self._token,
            'format': 1,
        })

        if self._cli:
            print(cp.Fore.GREEN + ' - Balance: %s' % account_info['Balance'])
            print(cp.Fore.LIGHTBLACK_EX + ' - Status: %s' % account_info['Status'])
            print(cp.Fore.LIGHTBLACK_EX + ' - UserLevel: %s' % account_info['UserLevel'])
            print(cp.Fore.LIGHTBLACK_EX + ' - MaxHold: %s' % account_info['MaxHold'])
            # print(xp.Fore.LIGHTBLACK_EX + ' - Discount: %s' % account_info['Discount'])
            # print(xp.Fore.LIGHTBLACK_EX + ' - Frozen: %s' % account_info['Frozen'])
            cp.fi()

        return account_info

    def get_a_mobile(self):
        """
        Get a mobile phone number.

        :return:
        """
        if self._cli:
            cp.getting('Getting a mobile phone number')

        self._mobile = self._get_result({
            'action': 'getmobile',
            'token': self._token,
            'itemid': self._item_id,
            'excludeno': self._exclude_no,
        })

        if self._cli:
            cp.value(self._mobile)

        return self._mobile

    def release_mobile(self, mobile=None, item_id=None):
        """
        Release a mobile phone number.

        :param mobile:
        :param item_id:
        :return:
        """
        mobile = mobile or self._mobile
        item_id = item_id or self._item_id

        if self._cli:
            cp.about_t('Releasing the mobile phone number', mobile)

        # release the mobile phone number
        if self._get_success({
            'action': 'release',
            'token': self._token,
            'itemid': item_id,
            'mobile': mobile,
        }):
            if self._cli:
                cp.success('Done.')
            self._mobile = None
            return True

        return

    def get_sms(self, mobile=None, item_id=None):
        """
        Get the SMS
        :param mobile:
        :param item_id:
        :return:
        """
        mobile = mobile or self._mobile
        item_id = item_id or self._item_id
        if self._cli:
            cp.watching('Getting SMS')

        # get sms
        query = {
            'action': 'getsms',
            'token': self._token,
            'itemid': item_id,
            'mobile': mobile,
            'release': 1,
        }

        started_at = time.time()
        while True:
            now = time.time()

            # try to get sms
            r = self._req_text(query=query)

            # success
            if r.split('|')[0] == 'success':
                txt = r.split('|')[1]
                if self._cli:
                    cp.wr(cp.Fore.LIGHTBLACK_EX + ' {}'.format(txt))
                    cp.fx()
                return txt

            # error
            if '3001' != r:
                self._raise(r)

            # timed out -> release mobile
            if (now - started_at) > self._sms_wait_max:
                cp.wr(' ')
                if self._cli:
                    cp.error(' TIMED OUT.')
                self.release_mobile()
                return False

            time.sleep(self._sms_interval)
            if self._cli:
                cp.step()

    def get_numerical_code(self, mobile=None, item_id=None):
        """
        Get the numerical code via SMS, by mobile.

        :param mobile:
        :param item_id:
        :return:
        """
        mobile = mobile or self._mobile
        item_id = item_id or self._item_id

        sms = self.get_sms(mobile=mobile, item_id=item_id)

        if sms:
            codes = re.search('[0-9]+', sms)

            if codes:
                return codes.group()
            else:
                self.release_mobile()
                raise ApiException('未能提取验证码或正则格式错误')

        raise NoSmsError('No SMS there')

    def add_ignore(self, mobile=None, item_id=None):
        """
        Ignore and release a mobile phone number.

        :param mobile:
        :param item_id:
        :return:
        """
        mobile = mobile or self._mobile
        item_id = item_id or self._item_id
        if self._cli:
            cp.about_t('IGNORE and RELEASE mobile phone number', mobile)

        if self._get_success({
            'action': 'addignore',
            'token': self._token,
            'itemid': item_id,
            'mobile': mobile,
            'release': 1,
        }):
            if self._cli:
                cp.success('Okay.')
            self._mobile = None
            return True

        return
