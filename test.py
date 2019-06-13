#!/usr/bin/env python
# encoding: utf-8

from sms_store import kma

kma = kma.KMA(cli=True)

mobile = kma.get_a_mobile()
print(kma.get_numerical_code())

