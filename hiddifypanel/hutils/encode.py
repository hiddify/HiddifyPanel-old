import urllib.parse
import base64
import uuid
import string
from slugify import slugify


def unicode_slug(instr: str) -> str:
    return slugify(instr, lowercase=False, allow_unicode=True)


def url_encode(url: str) -> str:
    return urllib.parse.quote(url)


def do_base_64(input: str) -> str:
    resp = base64.b64encode(f'{input}'.encode("utf-8"))
    return resp.decode()


def is_valid_uuid(val: str, version: int | None = None) -> bool:
    try:
        uuid.UUID(val, version=version)
    except BaseException:
        return False

    return True


def trim_ssh_key_headers(key: str) -> str:
    begin_marker = '-----BEGIN OPENSSH PRIVATE KEY-----'
    end_marker = '-----END OPENSSH PRIVATE KEY-----'

    return key.removeprefix(begin_marker).replace(end_marker, '')

# not used
# def is_assci_alphanumeric(str):
#     for c in str:
#         if c not in string.ascii_letters + string.digits:
#             return False
#     return True
