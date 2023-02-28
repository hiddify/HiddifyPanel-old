from sqlalchemy_serializer import SerializerMixin
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from wtforms import SelectMultipleField

from sqlalchemy.orm import backref

from flask import Markup
from dateutil import relativedelta
from hiddifypanel.panel.database import db
import enum
import datetime
import uuid as uuid_mod
from enum import auto
from strenum import StrEnum

class ConfigCategory(StrEnum):
    admin=auto()
    branding=auto()
    general=auto()
    proxies=auto()
    domain_fronting=auto()
    telegram=auto()
    http=auto()
    tls=auto()
    ssfaketls=auto()
    shadowtls=auto()
    tuic=auto()
    ssr=auto()
    kcp=auto()
    hidden=auto()
    advanced=auto()

class ConfigEnum(StrEnum):
    telegram_bot_token=auto()
    is_parent=auto()
    parent_panel=auto()
    unique_id=auto()
    cdn_forced_host=auto() # removed
    lang = auto()
    admin_lang = auto()
    admin_secret = auto()
    tls_ports = auto()
    http_ports = auto()
    kcp_ports = auto()
    kcp_enable = auto()
    decoy_domain = auto()
    proxy_path = auto()
    firewall = auto()
    netdata = auto()
    http_proxy_enable = auto()
    block_iran_sites = auto()
    allow_invalid_sni = auto()
    auto_update = auto()
    speed_test = auto()
    only_ipv4 = auto()

    shared_secret = auto()

    telegram_enable = auto()
    # telegram_secret=auto()
    telegram_adtag = auto()
    telegram_lib = auto()
    telegram_fakedomain = auto()

    v2ray_enable = auto()
    torrent_block = auto()

    ssfaketls_enable = auto()
    # ssfaketls_secret="ssfaketls_secret"
    ssfaketls_fakedomain = auto()

    shadowtls_enable = auto()
    # shadowtls_secret=auto()
    shadowtls_fakedomain = auto()

    tuic_enable = auto()
    tuic_port = auto()

    ssr_enable = auto()
    # ssr_secret="ssr_secret"
    ssr_fakedomain = auto()

    vmess_enable = auto()
    domain_fronting_domain = auto()
    domain_fronting_http_enable = auto()
    domain_fronting_tls_enable = auto()

    db_version = auto()

    branding_title=auto()
    branding_site=auto()
    branding_freetext=auto()
    not_found=auto()
    # cdn_forced_host=auto()
    @classmethod
    def _missing_(cls, value):
      return cls.not_found #"key not found"
    def info(self):
        map = {
            self.telegram_bot_token: {'category': ConfigCategory.advanced,'show_in_parent':True},
            self.is_parent:{'category': ConfigCategory.hidden,'type':bool},
            self.parent_panel:{'category': ConfigCategory.advanced},
            self.unique_id:{'category': ConfigCategory.hidden,},
            self.cdn_forced_host:{'category': ConfigCategory.hidden,},
            self.branding_title:{'category': ConfigCategory.branding,'show_in_parent':True},
            self.branding_site:{'category': ConfigCategory.branding,'show_in_parent':True},
            self.branding_freetext:{'category': ConfigCategory.branding,'show_in_parent':True},
            self.not_found:{'category': ConfigCategory.hidden},
            self.admin_secret: {'category': ConfigCategory.admin,'show_in_parent':True},
            self.lang: {'category': ConfigCategory.branding,'show_in_parent':True},
            self.admin_lang: {'category': ConfigCategory.admin,'show_in_parent':True},
            self.tls_ports: {'category': ConfigCategory.tls,'apply_mode':'apply'},
            self.http_ports: {'category': ConfigCategory.http,'apply_mode':'apply'},
            self.kcp_ports: {'category': ConfigCategory.kcp,'apply_mode':'apply'},
            self.kcp_enable: {'category': ConfigCategory.kcp,'type':bool,'apply_mode':'apply'},
            self.decoy_domain: {'category': ConfigCategory.general,'apply_mode':'apply'},
            self.proxy_path: {'category': ConfigCategory.advanced,'apply_mode':'apply','show_in_parent':True},
            self.firewall: {'category': ConfigCategory.general,'type':bool,'apply_mode':'apply'},
            self.netdata: {'category': ConfigCategory.general,'type':bool,'apply_mode':'apply'},
            self.http_proxy_enable: {'category': ConfigCategory.http,'type':bool},
            self.block_iran_sites: {'category': ConfigCategory.proxies,'type':bool,'apply_mode':'apply'},
            self.allow_invalid_sni: {'category': ConfigCategory.tls,'type':bool,'apply_mode':'apply'},
            self.auto_update: {'category': ConfigCategory.general,'type':bool,'apply_mode':'apply','show_in_parent':True},
            self.speed_test: {'category': ConfigCategory.general,'type':bool,'apply_mode':'apply'},
            self.only_ipv4: {'category': ConfigCategory.general,'type':bool,'apply_mode':'apply'},
            self.torrent_block: {'category': ConfigCategory.general,'type':bool,'apply_mode':'apply'},

            self.shared_secret: {'category': ConfigCategory.proxies,'apply_mode':'apply'},

            self.telegram_enable: {'category': ConfigCategory.telegram,'type':bool,'apply_mode':'apply'},
            # telegram_secret:{'category':'general'},
            self.telegram_adtag: {'category': ConfigCategory.telegram,'apply_mode':'apply'},
            self.telegram_fakedomain: {'category': ConfigCategory.telegram,'apply_mode':'apply'},
            self.telegram_lib: {'category': ConfigCategory.telegram,'apply_mode':'reinstall'},

            self.v2ray_enable: {'category': ConfigCategory.proxies,'type':bool,'apply_mode':'apply'},

            self.ssfaketls_enable: {'category': ConfigCategory.ssfaketls,'type':bool,'apply_mode':'apply'},
            # ssfaketls_secret:{'category':'ssfaketls'},
            self.ssfaketls_fakedomain: {'category': ConfigCategory.ssfaketls,'apply_mode':'apply'},

            self.shadowtls_enable: {'category': ConfigCategory.shadowtls,'type':bool,'apply_mode':'apply'},
            # shadowtls_secret:{'category':'shadowtls'},
            self.shadowtls_fakedomain: {'category': ConfigCategory.shadowtls,'apply_mode':'apply'},

            self.tuic_enable: {'category': ConfigCategory.tuic,'type':bool,'apply_mode':'apply'},
            self.tuic_port: {'category': ConfigCategory.tuic,'apply_mode':'apply'},

            self.ssr_enable: {'category': ConfigCategory.ssr,'type':bool,'apply_mode':'apply'},
            # ssr_secret:{'category':'ssr'},
            self.ssr_fakedomain: {'category': ConfigCategory.ssr,'apply_mode':'apply'},

            self.vmess_enable: {'category': ConfigCategory.proxies,'type':bool},
            self.domain_fronting_domain: {'category': ConfigCategory.domain_fronting},
            self.domain_fronting_http_enable: {'category': ConfigCategory.domain_fronting,'type':bool},
            self.domain_fronting_tls_enable: {'category': ConfigCategory.domain_fronting,'type':bool},

            self.db_version: {'category': ConfigCategory.hidden},
        }
        return map[self]

    def category(self):
        return self.info()['category']
    def type(self):
        info=self.info()
        return info['type'] if 'type' in info else str
    def apply_mode(self):
        info=self.info()
        return info['apply_mode'] if 'apply_mode' in info else ''
    def show_in_parent(self):
        info=self.info()
        return info['show_in_parent'] if 'show_in_parent' in info else False