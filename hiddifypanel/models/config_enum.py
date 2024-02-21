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
    admin = auto()
    branding = auto()
    general = auto()
    proxies = auto()
    domain_fronting = auto()
    telegram = auto()
    http = auto()
    tls = auto()
    ssh = auto()
    ssfaketls = auto()
    shadowtls = auto()
    restls = auto()
    tuic = auto()
    hysteria = auto()
    ssr = auto()
    kcp = auto()
    hidden = auto()
    advanced = auto()
    too_advanced = auto()
    warp = auto()
    reality = auto()


class ConfigEnum(StrEnum):
    create_easysetup_link = auto()
    ssh_server_redis_url = auto()
    ssh_server_port = auto()
    ssh_server_enable = auto()
    first_setup = auto()
    core_type = auto()
    warp_enable = auto()
    warp_mode = auto()
    warp_plus_code = auto()
    dns_server = auto()
    reality_fallback_domain = auto()
    reality_server_names = auto()
    reality_short_ids = auto()
    reality_private_key = auto()
    reality_public_key = auto()

    restls1_2_domain = auto()
    restls1_3_domain = auto()
    show_usage_in_sublink = auto()
    cloudflare = auto()
    license = auto()
    country = auto()
    package_mode = auto()
    utls = auto()
    telegram_bot_token = auto()
    is_parent = auto()
    parent_panel = auto()
    unique_id = auto()
    last_hash = auto()
    cdn_forced_host = auto()  # removed
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

    hysteria_enable = auto()
    hysteria_port = auto()

    ssr_enable = auto()
    # ssr_secret="ssr_secret"
    ssr_fakedomain = auto()

    vmess_enable = auto()
    domain_fronting_domain = auto()
    domain_fronting_http_enable = auto()
    domain_fronting_tls_enable = auto()

    db_version = auto()

    branding_title = auto()
    branding_site = auto()
    branding_freetext = auto()
    not_found = auto()
    path_vmess = auto()
    path_vless = auto()
    path_trojan = auto()
    path_v2ray = auto()  # deprecated
    path_ss = auto()

    path_ws = auto()
    path_tcp = auto()
    path_grpc = auto()

    # cdn_forced_host=auto()
    @ classmethod
    def _missing_(cls, value):
        return cls.not_found  # "key not found"

    def info(self):
        map = {
            self.create_easysetup_link: {'category': ConfigCategory.hidden},
            self.ssh_server_redis_url: {'category': ConfigCategory.hidden},
            self.ssh_server_port: {'category': ConfigCategory.ssh, 'apply_mode': 'apply'},
            self.ssh_server_enable: {'category': ConfigCategory.ssh, 'type': bool, 'apply_mode': 'apply'},
            self.core_type: {'category': ConfigCategory.advanced, 'apply_mode': 'apply'},
            self.dns_server: {'category': ConfigCategory.general, 'apply_mode': 'apply'},
            self.warp_enable: {'category': ConfigCategory.hidden, 'type': bool, 'apply_mode': 'restart'},
            self.warp_mode: {'category': ConfigCategory.warp, 'apply_mode': 'apply'},
            self.warp_plus_code: {'category': ConfigCategory.warp, 'apply_mode': 'apply'},
            self.restls1_2_domain: {'category': ConfigCategory.hidden},
            self.restls1_3_domain: {'category': ConfigCategory.hidden},
            self.first_setup: {'category': ConfigCategory.hidden, 'type': bool},
            self.show_usage_in_sublink: {'category': ConfigCategory.general, 'type': bool},
            self.reality_fallback_domain: {'category': ConfigCategory.hidden, 'apply_mode': 'apply'},
            self.reality_server_names: {'category': ConfigCategory.hidden, 'apply_mode': 'apply'},
            self.reality_short_ids: {'category': ConfigCategory.reality, 'apply_mode': 'apply'},
            self.reality_private_key: {'category': ConfigCategory.reality, 'apply_mode': 'apply'},
            self.reality_public_key: {'category': ConfigCategory.reality, 'apply_mode': 'apply'},
            self.lang: {'category': ConfigCategory.branding, 'show_in_parent': True, 'commercial': True},
            self.admin_lang: {'category': ConfigCategory.admin, 'show_in_parent': True, 'commercial': True},
            self.cloudflare: {'category': ConfigCategory.too_advanced, 'commercial': True},
            self.license: {'category': ConfigCategory.hidden, 'commercial': True},
            self.proxy_path: {'category': ConfigCategory.too_advanced, 'apply_mode': 'apply', 'show_in_parent': True},
            self.path_vmess: {'category': ConfigCategory.too_advanced},
            self.path_vless: {'category': ConfigCategory.too_advanced},
            self.path_trojan: {'category': ConfigCategory.too_advanced},
            self.path_ss: {'category': ConfigCategory.hidden},
            self.path_tcp: {'category': ConfigCategory.too_advanced},
            self.path_ws: {'category': ConfigCategory.too_advanced},
            self.path_grpc: {'category': ConfigCategory.too_advanced},
            self.path_v2ray: {'category': ConfigCategory.hidden},
            self.last_hash: {'category': ConfigCategory.hidden},

            self.utls: {'category': ConfigCategory.advanced, 'commercial': True},
            self.package_mode: {'category': ConfigCategory.advanced, 'show_in_parent': True, 'commercial': True},
            self.telegram_bot_token: {'category': ConfigCategory.telegram, 'show_in_parent': True, 'commercial': True},
            self.is_parent: {'category': ConfigCategory.hidden, 'type': bool},
            self.parent_panel: {'category': ConfigCategory.hidden, 'commercial': True},
            self.unique_id: {'category': ConfigCategory.hidden, },
            self.cdn_forced_host: {'category': ConfigCategory.hidden, },
            self.branding_title: {'category': ConfigCategory.branding, 'show_in_parent': True, 'commercial': True},
            self.branding_site: {'category': ConfigCategory.branding, 'show_in_parent': True, 'commercial': True},
            self.branding_freetext: {'category': ConfigCategory.branding, 'show_in_parent': True, 'commercial': True},
            self.not_found: {'category': ConfigCategory.hidden},
            self.admin_secret: {'category': ConfigCategory.hidden, 'show_in_parent': True, 'commercial': True},

            self.tls_ports: {'category': ConfigCategory.tls, 'apply_mode': 'apply'},  # tls
            self.http_ports: {'category': ConfigCategory.http, 'apply_mode': 'apply'},  # http
            self.kcp_ports: {'category': ConfigCategory.hidden, 'apply_mode': 'apply'},
            self.kcp_enable: {'category': ConfigCategory.hidden, 'type': bool, 'apply_mode': 'apply'},
            self.decoy_domain: {'category': ConfigCategory.general, 'apply_mode': 'apply'},
            self.country: {'category': ConfigCategory.general, 'apply_mode': 'restart'},
            self.firewall: {'category': ConfigCategory.general, 'type': bool, 'apply_mode': 'apply'},
            self.netdata: {'category': ConfigCategory.hidden, 'type': bool, 'apply_mode': 'apply'},
            self.http_proxy_enable: {'category': ConfigCategory.http, 'type': bool},
            self.block_iran_sites: {'category': ConfigCategory.proxies, 'type': bool, 'apply_mode': 'apply'},
            self.allow_invalid_sni: {'category': ConfigCategory.tls, 'type': bool, 'apply_mode': 'apply'},
            self.auto_update: {'category': ConfigCategory.general, 'type': bool, 'apply_mode': 'apply', 'show_in_parent': True},
            self.speed_test: {'category': ConfigCategory.general, 'type': bool, 'apply_mode': 'apply'},
            self.only_ipv4: {'category': ConfigCategory.general, 'type': bool, 'apply_mode': 'apply'},
            self.torrent_block: {'category': ConfigCategory.general, 'type': bool, 'apply_mode': 'apply'},

            self.shared_secret: {'category': ConfigCategory.proxies, 'apply_mode': 'apply'},

            self.telegram_enable: {'category': ConfigCategory.telegram, 'type': bool, 'apply_mode': 'apply'},
            # telegram_secret:{'category':'general'},
            self.telegram_adtag: {'category': ConfigCategory.telegram, 'apply_mode': 'apply'},
            self.telegram_fakedomain: {'category': ConfigCategory.telegram, 'apply_mode': 'apply'},
            self.telegram_lib: {'category': ConfigCategory.telegram, 'apply_mode': 'reinstall'},

            self.v2ray_enable: {'category': ConfigCategory.proxies, 'type': bool, 'apply_mode': 'apply'},

            self.ssfaketls_enable: {'category': ConfigCategory.ssfaketls, 'type': bool, 'apply_mode': 'apply'},
            # ssfaketls_secret:{'category':'ssfaketls'},
            self.ssfaketls_fakedomain: {'category': ConfigCategory.ssfaketls, 'apply_mode': 'apply'},

            self.shadowtls_enable: {'category': ConfigCategory.shadowtls, 'type': bool, 'apply_mode': 'apply'},
            # shadowtls_secret:{'category':'shadowtls'},
            self.shadowtls_fakedomain: {'category': ConfigCategory.shadowtls, 'apply_mode': 'apply'},

            self.tuic_enable: {'category': ConfigCategory.hidden, 'type': bool, 'apply_mode': 'apply'},
            self.tuic_port: {'category': ConfigCategory.hidden, 'apply_mode': 'apply'},

            self.hysteria_enable: {'category': ConfigCategory.hidden, 'type': bool, 'apply_mode': 'apply'},
            self.hysteria_port: {'category': ConfigCategory.hidden, 'apply_mode': 'apply'},

            self.ssr_enable: {'category': ConfigCategory.hidden, 'type': bool, 'apply_mode': 'apply'},
            # ssr_secret:{'category':'ssr'},
            self.ssr_fakedomain: {'category': ConfigCategory.hidden, 'apply_mode': 'apply'},

            self.vmess_enable: {'category': ConfigCategory.proxies, 'type': bool},
            self.domain_fronting_domain: {'category': ConfigCategory.hidden},
            self.domain_fronting_http_enable: {'category': ConfigCategory.hidden, 'type': bool},
            self.domain_fronting_tls_enable: {'category': ConfigCategory.hidden, 'type': bool},
            self.db_version: {'category': ConfigCategory.hidden},
        }
        return map[self]

    def commercial(self):
        # print(self,self.info().get('commercial',False))
        return self.info().get('commercial', False)

    def category(self):
        return self.info()['category']

    def type(self):
        return self.info().get('type', str)

    def apply_mode(self):
        return self.info().get('apply_mode', '')

    def show_in_parent(self):
        return self.info().get('show_in_parent', False)
