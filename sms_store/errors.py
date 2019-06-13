#!/usr/bin/env python
# encoding: utf-8


class ApiException(Exception):
    pass


class NoMobileError(Exception):
    pass


class NoSmsError(Exception):
    pass

