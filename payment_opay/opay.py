# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import base64
import collections
import hashlib
import urllib


OPAY_LANG_MAP = {
    'lt': 'LIT',
    'lv': 'LAV',
    'ru': 'RUS',
    'en': 'ENG',
}
OPAY_DEFAULT_LANG = 'LIT'
OPAY_SPEC_VERSION = 'opay_8.1'
OPAY_DEFAULT_COUNTRY = 'LT'
OPAY_GATEWAY_URL = 'https://gateway.opay.lt/pay/'

ENCODE_TRANSLATE_MAP = bytes.maketrans(b'=', b',')
DECODE_TRANSLATE_MAP = bytes.maketrans(b',', b'=')


def opay_bool_to_str(value):
    return '1' if value else '0'


def opay_sign_with_password(values, signing_key: str, encoding='utf-8') -> str:
    string_to_sign = ('%s%s' % (
        ''.join('%s%s' % (k, v) for k, v in values.items() if v),
        signing_key)
    ).encode(encoding)
    return hashlib.md5(string_to_sign).hexdigest()


def opay_encode_values(values, encoding='utf-8') -> str:
    return base64.urlsafe_b64encode(
        urllib.parse.urlencode(values).encode(encoding)).translate(
            ENCODE_TRANSLATE_MAP).decode('ascii')


def opay_decode_values(
        encoded: str, encoding='utf-8') -> collections.OrderedDict:
    return collections.OrderedDict(urllib.parse.parse_qsl(base64.b64b64decode(
        encoded.encode(encoding).translate(DECODE_TRANSLATE_MAP),
    )))
