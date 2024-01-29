import datetime
import json
import os
import random
import string
import sys
import uuid

from dateutil import relativedelta

from hiddifypanel import Events, hutils
from hiddifypanel.models import *
from hiddifypanel.panel import hiddify
from hiddifypanel.panel.database import db
import hiddifypanel.models.utils as model_utils
from hiddifypanel import statics
from flask import g
MAX_DB_VERSION = 80


def init_db():
    # db.init_migration(app)
    # db.migrate()
    # db.upgrade()
    db.create_all()
    hconfig.invalidate_all()
    # get_hconfigs.invalidate_all()
    db_version = int(hconfig(ConfigEnum.db_version) or 0)
    # set_hconfig(ConfigEnum.db_version, 69)
    if db_version == latest_db_version():
        return
    execute('ALTER TABLE proxy DROP INDEX `name`;')

    execute("alter table user alter column telegram_id bigint;")
    execute("alter table admin_user alter column telegram_id bigint;")

    add_column(Child.mode)
    add_column(Child.name)
    add_column(User.lang)
    add_column(AdminUser.lang)
    add_column(User.username)
    add_column(User.password)
    add_column(AdminUser.username)
    add_column(AdminUser.password)
    add_column(User.wg_pk)
    add_column(User.wg_pub)
    add_column(User.wg_psk)

    add_column(Domain.extra_params)

    Events.db_prehook.notify()
    if db_version < 52:
        execute(f'update domain set mode="sub_link_only", sub_link_only=false where sub_link_only = true or mode=1  or mode="1"')
        execute(f'update domain set mode="direct", sub_link_only=false where mode=0  or mode="0"')
        execute(f'update proxy set transport="WS" where transport = "ws"')
        execute(f'update admin_user set mode="agent" where mode = "slave"')
        execute(f'update admin_user set mode="super_admin" where id=1')
        execute(f'DELETE from proxy where transport = "h1"')
        # add_column(Domain.grpc)
        # add_column(ParentDomain.alias)
        # add_column(User.ed25519_private_key)
        # add_column(User.ed25519_public_key)
        # add_column(User.start_date)
        # add_column(User.package_days)
        # add_column(User.telegram_id)
        # add_column(Child.unique_id)
        # add_column(Domain.alias)
        # add_column(Domain.sub_link_only)
        # add_column(Domain.child_id)
        # add_column(Proxy.child_id)
        # add_column(User.added_by)
        # add_column(User.max_ips)
        # add_column(AdminUser.parent_admin_id)
        # add_column(AdminUser.can_add_admin)
        # add_column(AdminUser.max_active_users)
        # add_column(AdminUser.max_users)
        # add_column(BoolConfig.child_id)
        # add_column(StrConfig.child_id)
        # add_column(DailyUsage.admin_id)
        # add_column(DailyUsage.child_id)
        # add_column(User.monthly)
        # add_column(User.enable)
        # add_column(Domain.cdn_ip)
        # add_column(Domain.servernames)
        # add_column(User.lang)

        if len(Domain.query.all()) != 0 and BoolConfig.query.count() == 0:
            execute(f'DROP TABLE bool_config')
            execute(f'ALTER TABLE bool_config_old RENAME TO bool_config')
        if len(Domain.query.all()) != 0 and StrConfig.query.count() == 0:
            execute(f'DROP TABLE str_config')
            execute(f'ALTER TABLE str_config_old RENAME TO str_config')

        execute('ALTER TABLE user RENAME COLUMN monthly_usage_limit_GB TO usage_limit_GB')
        execute(f'update admin_user set parent_admin_id=1 where parent_admin_id is NULL and 1!=id')
        execute(f'update admin_user set max_users=100,max_active_users=100 where max_users is NULL')
        execute(f'update dailyusage set child_id=0 where child_id is NULL')
        execute(f'update dailyusage set admin_id=1 where admin_id is NULL')
        execute(f'update dailyusage set admin_id=1 where admin_id = 0')
        execute(f'update user set added_by=1 where added_by = 1')
        execute(f'update user set enable=True, mode="no_reset" where enable is NULL')
        execute(f'update user set enable=False, mode="no_reset" where mode = "disable"')
        execute(f'update user set added_by=1 where added_by is NULL')
        execute(f'update user set max_ips=10000 where max_ips is NULL')
        execute(f'update str_config set child_id=0 where child_id is NULL')
        execute(f'update bool_config set child_id=0 where child_id is NULL')
        execute(f'update domain set child_id=0 where child_id is NULL')
        execute(f'update domain set sub_link_only=False where sub_link_only is NULL')
        execute(f'update proxy set child_id=0 where child_id is NULL')

    add_new_enum_values()

    if not Child.query.filter(Child.id == 0).first():
        print(Child.query.filter(Child.id == 0).first())
        tmpuuid = str(uuid.uuid4())
        db.session.add(Child(unique_id=tmpuuid, name="Root", id=0))
        db.session.commit()
        execute(f'update child set id=0 where unique_id="{tmpuuid}"')

    if not AdminUser.query.filter(AdminUser.id == 1).first():
        db.session.add(AdminUser(id=1, uuid=str(uuid.uuid4()), name="Owner", mode=AdminMode.super_admin, comment=""))
        db.session.commit()
        execute("update admin_user set id=1 where name='owner'")

    upgrade_database()
    Child.query.filter(Child.id == 0).first().mode = ChildMode.virtual
    if db_version < 69:
        _v70(0)

    db.session.commit()

    for child in Child.query.filter(Child.mode == ChildMode.virtual).all():
        g.__child_id = child.id
        db_version = int(hconfig(ConfigEnum.db_version, child.id) or 0)
        start_version = db_version
        for ver in range(1, MAX_DB_VERSION):
            if ver <= db_version:
                continue

            db_action = sys.modules[__name__].__dict__.get(f'_v{ver}', None)
            if not db_action:
                continue
            if start_version == 0 and ver == 10:
                continue

            hiddify.error(f"Updating db from version {db_version} for node {child.id}")
            if ver < 70 and child.id == 0:
                db_action()
            else:
                db_action(child.id)
            Events.db_init_event.notify(db_version=db_version)
            hiddify.error(f"Updated successfuly db from version {db_version} to {ver}")

            db_version = ver
            db.session.commit()
            set_hconfig(ConfigEnum.db_version, db_version, child_id=child.id, commit=False)

        db.session.commit()
    g.current_child_id = 0
    return BoolConfig.query.all()


def _v71():
    # ignore [parent_domain,show_domain,show_domain_parent]
    tables = ['bool_config', 'str_config', 'daily_usage', 'domain', 'proxy']
    for t in tables:
        execute(f'ALTER TABLE {t} RENAME COLUMN child_id TO node_id')


def _v70(child_id):
    Domain.query.filter(Domain.child_id != 0).delete()
    StrConfig.query.filter(StrConfig.child_id != 0).delete()
    BoolConfig.query.filter(BoolConfig.child_id != 0).delete()
    Proxy.query.filter(Proxy.child_id != 0).delete()
    Child.query.filter(Child.id != 0).delete()

    child = Child.by_id(0)
    child.unique_id = str(uuid.uuid4())
    child.type = ChildMode.virtual


# using child_id in lower version is not needed as it is introduced in v70


def _v69():
    db.session.bulk_save_objects(get_proxy_rows_v1())
    add_config_if_not_exist(ConfigEnum.wireguard_enable, True)
    add_config_if_not_exist(ConfigEnum.wireguard_port, random.randint(30000, 40000))
    add_config_if_not_exist(ConfigEnum.wireguard_ipv4, "10.90.0.1")
    add_config_if_not_exist(ConfigEnum.wireguard_ipv6, "fd42:42:90::1")
    wg_pk, wg_pub, _ = hiddify.get_wg_private_public_psk_pair()
    add_config_if_not_exist(ConfigEnum.wireguard_private_key, wg_pk)
    add_config_if_not_exist(ConfigEnum.wireguard_public_key, wg_pub)
    add_config_if_not_exist(ConfigEnum.wireguard_noise_trick, "5-10")
    for u in User.query.all():
        u.wg_pk, u.wg_pub, u.wg_psk = hiddify.get_wg_private_public_psk_pair()


def _v65():
    add_config_if_not_exist(ConfigEnum.mux_enable, False)
    add_config_if_not_exist(ConfigEnum.mux_protocol, 'smux')
    add_config_if_not_exist(ConfigEnum.mux_max_connections, '4')
    add_config_if_not_exist(ConfigEnum.mux_min_streams, '4')
    add_config_if_not_exist(ConfigEnum.mux_max_streams, '0')
    add_config_if_not_exist(ConfigEnum.mux_padding_enable, False)
    add_config_if_not_exist(ConfigEnum.mux_brutal_enable, True)
    add_config_if_not_exist(ConfigEnum.mux_brutal_up_mbps, '100')
    add_config_if_not_exist(ConfigEnum.mux_brutal_down_mbps, '100')


def _v64():
    set_hconfig(ConfigEnum.ssh_server_redis_url, "unix:///opt/hiddify-manager/other/redis/run.sock?db=1")


def _v63():
    add_config_if_not_exist(ConfigEnum.hysteria_enable, True)
    add_config_if_not_exist(ConfigEnum.hysteria_port, "11478")
    add_config_if_not_exist(ConfigEnum.hysteria_obfs_enable, True)
    add_config_if_not_exist(ConfigEnum.hysteria_up_mbps, "150")
    add_config_if_not_exist(ConfigEnum.hysteria_down_mbps, "300")


def _v62():
    add_config_if_not_exist(ConfigEnum.tls_fragment_enable, False)
    add_config_if_not_exist(ConfigEnum.tls_fragment_size, "10-100")
    add_config_if_not_exist(ConfigEnum.tls_fragment_sleep, "50-200")
    add_config_if_not_exist(ConfigEnum.tls_mixed_case, False)
    add_config_if_not_exist(ConfigEnum.tls_padding_enable, False)
    add_config_if_not_exist(ConfigEnum.tls_padding_length, "50-200")


def _v61():
    execute("ALTER TABLE user MODIFY COLUMN username VARCHAR(100);")
    execute("ALTER TABLE user MODIFY COLUMN password VARCHAR(100);")


def _v60():
    add_config_if_not_exist(ConfigEnum.proxy_path_admin, hutils.random.get_random_string())
    add_config_if_not_exist(ConfigEnum.proxy_path_client, hutils.random.get_random_string())


def _v59():
    # set user model username and password
    for u in User.query.all():
        model_utils.fill_username(u)
        model_utils.fill_password(u)

    # set admin model username and password
    for a in AdminUser.query.all():
        model_utils.fill_username(a)
        model_utils.fill_password(a)


def _v57():
    add_config_if_not_exist(ConfigEnum.warp_sites, "")


def _v56():
    reality_port = random.randint(20000, 30000)
    set_hconfig(ConfigEnum.reality_port, reality_port)


def _v55():
    tuic_port = random.randint(20000, 30000)
    hystria_port = random.randint(10000, 20000)
    set_hconfig(ConfigEnum.tuic_port, tuic_port)
    set_hconfig(ConfigEnum.hysteria_port, hystria_port)
    set_hconfig(ConfigEnum.tuic_enable, True)
    set_hconfig(ConfigEnum.hysteria_enable, True)
    Proxy.query.filter(Proxy.proto.in_(["tuic", "hysteria2", "hysteria"])).delete()
    db.session.add(Proxy(l3='tls', transport='custom', cdn='direct', proto='tuic', enable=True, name="TUIC"))
    db.session.add(Proxy(l3='tls', transport='custom', cdn='direct', proto='hysteria2', enable=True, name="Hysteria2"))


def _v52():
    db.session.bulk_save_objects(get_proxy_rows_v1())


def _v51():
    Proxy.query.filter(Proxy.l3.in_([ProxyL3.h3_quic])).delete()


def _v50():
    set_hconfig(ConfigEnum.show_usage_in_sublink, True)


def _v49():

    for u in User.query.all():
        priv, publ = hiddify.get_ed25519_private_public_pair()
        u.ed25519_private_key = priv
        u.ed25519_public_key = publ


def _v48():
    add_config_if_not_exist(ConfigEnum.ssh_server_enable, True)
    set_hconfig(ConfigEnum.ssh_server_enable, True)


def _v47():
    StrConfig.query.filter(StrConfig.key == ConfigEnum.ssh_server_enable).delete()


def _v45():

    if not Proxy.query.filter(Proxy.name == "SSH").first():
        db.session.add(Proxy(l3='ssh', transport='ssh', cdn='direct', proto='ssh', enable=True, name="SSH"))
    add_config_if_not_exist(ConfigEnum.ssh_server_redis_url, "unix:///opt/hiddify-manager/other/redis/run.sock?db=1")
    while 1:
        port = random.randint(5000, 40000)
        if port not in [10085, 10086]:
            break
    add_config_if_not_exist(ConfigEnum.ssh_server_port, port)
    add_config_if_not_exist(ConfigEnum.ssh_server_enable, False)
# def _v43():
#     if not (Domain.query.filter(Domain.domain==hconfig(ConfigEnum.domain_fronting_domain)).first()):
#         db.session.add(Domain(domain=hconfig(ConfigEnum.domain_fronting_domain),servernames=hconfig(ConfigEnum.domain_fronting_domain),mode=DomainType.cdn))

# v7.0.0


def _v42():

    for k in [ConfigEnum.telegram_fakedomain, ConfigEnum.ssfaketls_fakedomain, ConfigEnum.shadowtls_fakedomain]:
        if not hconfig(k):
            rnd_domains = hutils.network.get_random_domains(1)
            add_config_if_not_exist(k, rnd_domains[0])


def _v41():
    add_config_if_not_exist(ConfigEnum.core_type, "xray")
    if not (Domain.query.filter(Domain.domain == hconfig(ConfigEnum.reality_fallback_domain)).first()):
        db.session.add(Domain(domain=hconfig(ConfigEnum.reality_fallback_domain), servernames=hconfig(ConfigEnum.reality_server_names), mode=DomainType.reality))


def _v38():
    add_config_if_not_exist(ConfigEnum.dns_server, "1.1.1.1")
    add_config_if_not_exist(ConfigEnum.warp_mode, "all" if hconfig(ConfigEnum.warp_enable) else "none")
    add_config_if_not_exist(ConfigEnum.warp_plus_code, '')


# def _v34():
#     add_config_if_not_exist(ConfigEnum.show_usage_in_sublink, True)


def _v33():
    Proxy.query.filter(Proxy.l3 == ProxyL3.reality).delete()
    _v31()


def _v31():
    add_config_if_not_exist(ConfigEnum.reality_short_ids, uuid.uuid4().hex[0:random.randint(1, 8)*2])
    key_pair = hiddify.generate_x25519_keys()
    add_config_if_not_exist(ConfigEnum.reality_private_key, key_pair['private_key'])
    add_config_if_not_exist(ConfigEnum.reality_public_key, key_pair['public_key'])
    db.session.bulk_save_objects(get_proxy_rows_v1())
    if not (AdminUser.query.filter(AdminUser.id == 1).first()):
        db.session.add(AdminUser(id=1, uuid=hconfig(ConfigEnum.admin_secret), name="Owner", mode=AdminMode.super_admin, comment=""))
        execute("update admin_user set id=1 where name='owner'")
    for i in range(1, 10):
        for d in hutils.network.get_random_domains(50):
            if hutils.network.is_domain_reality_friendly(d):
                add_config_if_not_exist(ConfigEnum.reality_fallback_domain, d)
                add_config_if_not_exist(ConfigEnum.reality_server_names, d)
                return
    add_config_if_not_exist(ConfigEnum.reality_fallback_domain, "yahoo.com")
    add_config_if_not_exist(ConfigEnum.reality_server_names, "yahoo.com")

    # add_config_if_not_exist(ConfigEnum.cloudflare, "")


def _v27():
    # add_config_if_not_exist(ConfigEnum.cloudflare, "")
    set_hconfig(ConfigEnum.netdata, False)


def _v26():
    add_config_if_not_exist(ConfigEnum.cloudflare, "")
    add_config_if_not_exist(ConfigEnum.country, "ir")
    add_config_if_not_exist(ConfigEnum.parent_panel, "")
    add_config_if_not_exist(ConfigEnum.is_parent, False)
    add_config_if_not_exist(ConfigEnum.license, "")


def _v21():
    db.session.bulk_save_objects(get_proxy_rows_v1())


def _v20():
    if hconfig(ConfigEnum.domain_fronting_domain):
        fake_domains = [hconfig(ConfigEnum.domain_fronting_domain)]

        direct_domain = Domain.query.filter(Domain.mode in [DomainType.direct, DomainType.relay]).first()
        if direct_domain:
            direct_host = direct_domain.domain
        else:
            direct_host = hutils.network.get_ip(4)

        for fd in fake_domains:
            if not Domain.query.filter(Domain.domain == fd).first():
                db.session.add(Domain(domain=fd, mode='fake', alias='moved from domain fronting', cdn_ip=direct_host))


def _v19():
    set_hconfig(ConfigEnum.path_trojan, hutils.random.get_random_string(7, 15))
    set_hconfig(ConfigEnum.path_vless, hutils.random.get_random_string(7, 15))
    set_hconfig(ConfigEnum.path_vmess, hutils.random.get_random_string(7, 15))
    set_hconfig(ConfigEnum.path_ss, hutils.random.get_random_string(7, 15))
    set_hconfig(ConfigEnum.path_grpc, hutils.random.get_random_string(7, 15))
    set_hconfig(ConfigEnum.path_tcp, hutils.random.get_random_string(7, 15))
    set_hconfig(ConfigEnum.path_ws, hutils.random.get_random_string(7, 15))
    add_config_if_not_exist(ConfigEnum.tuic_enable, False)
    add_config_if_not_exist(ConfigEnum.shadowtls_enable, False)
    add_config_if_not_exist(ConfigEnum.shadowtls_fakedomain, "en.wikipedia.org")
    add_config_if_not_exist(ConfigEnum.utls, "chrome")
    add_config_if_not_exist(ConfigEnum.telegram_bot_token, "")
    add_config_if_not_exist(ConfigEnum.package_mode, "release")


def _v17():
    for u in User.query.all():
        if u.expiry_time:
            if not u.package_days:
                if not u.last_reset_time:
                    u.package_days = (u.expiry_time-datetime.date.today()).days
                    u.start_date = datetime.date.today()
                else:
                    u.package_days = (u.expiry_time-u.last_reset_time).days
                    u.start_date = u.last_reset_time
            u.expiry_time = None


def _v1():
    external_ip = str(hutils.network.get_ip(4))
    rnd_domains = hutils.network.get_random_domains(5)

    data = [
        StrConfig(key=ConfigEnum.db_version, value=1),
        User(name="default", usage_limit_GB=3000, package_days=3650, mode=UserMode.weekly),
        Domain(domain=external_ip+".sslip.io", mode=DomainType.direct),
        StrConfig(key=ConfigEnum.admin_secret, value=uuid.uuid4()),
        StrConfig(key=ConfigEnum.http_ports, value="80"),
        StrConfig(key=ConfigEnum.tls_ports, value="443"),
        BoolConfig(key=ConfigEnum.first_setup, value=True),
        StrConfig(key=ConfigEnum.decoy_domain, value=hutils.network.get_random_decoy_domain()),
        StrConfig(key=ConfigEnum.proxy_path, value=hutils.random.get_random_string()),
        BoolConfig(key=ConfigEnum.firewall, value=False),
        BoolConfig(key=ConfigEnum.netdata, value=True),
        StrConfig(key=ConfigEnum.lang, value='en'),
        BoolConfig(key=ConfigEnum.block_iran_sites, value=True),
        BoolConfig(key=ConfigEnum.allow_invalid_sni, value=True),
        BoolConfig(key=ConfigEnum.kcp_enable, value=False),
        StrConfig(key=ConfigEnum.kcp_ports, value="88"),
        BoolConfig(key=ConfigEnum.auto_update, value=True),
        BoolConfig(key=ConfigEnum.speed_test, value=True),
        BoolConfig(key=ConfigEnum.only_ipv4, value=False),
        BoolConfig(key=ConfigEnum.vmess_enable, value=True),
        BoolConfig(key=ConfigEnum.http_proxy_enable, value=True),
        StrConfig(key=ConfigEnum.shared_secret, value=str(uuid.uuid4())),
        BoolConfig(key=ConfigEnum.telegram_enable, value=True),
        # StrConfig(key=ConfigEnum.telegram_secret,value=uuid.uuid4().hex),
        StrConfig(key=ConfigEnum.telegram_adtag, value=""),
        StrConfig(key=ConfigEnum.telegram_fakedomain, value=rnd_domains[1]),
        BoolConfig(key=ConfigEnum.ssfaketls_enable, value=False),
        # StrConfig(key=ConfigEnum.ssfaketls_secret,value=str(uuid.uuid4())),
        StrConfig(key=ConfigEnum.ssfaketls_fakedomain, value=rnd_domains[2]),
        BoolConfig(key=ConfigEnum.shadowtls_enable, value=False),
        # StrConfig(key=ConfigEnum.shadowtls_secret,value=str(uuid.uuid4())),
        StrConfig(key=ConfigEnum.shadowtls_fakedomain, value=rnd_domains[3]),

        BoolConfig(key=ConfigEnum.ssr_enable, value=False),
        # StrConfig(key=ConfigEnum.ssr_secret,value=str(uuid.uuid4())),
        StrConfig(key=ConfigEnum.ssr_fakedomain, value=rnd_domains[4]),

        # BoolConfig(key=ConfigEnum.tuic_enable, value=False),
        # StrConfig(key=ConfigEnum.tuic_port, value=3048),

        BoolConfig(key=ConfigEnum.domain_fronting_tls_enable, value=False),
        BoolConfig(key=ConfigEnum.domain_fronting_http_enable, value=False),
        StrConfig(key=ConfigEnum.domain_fronting_domain, value=""),

        # BoolConfig(key=ConfigEnum.torrent_block,value=False),

        *get_proxy_rows_v1()
    ]
    # fake_domains=['speedtest.net']
    # for fd in fake_domains:
    #     if not Domain.query.filter(Domain.domain==fd).first():
    #         db.session.add(Domain(domain=fd,mode='fake',alias='fake domain',cdn_ip=external_ip))
    db.session.bulk_save_objects(data)


def _v7():
    try:
        Proxy.query.filter(Proxy.name == 'tls XTLS direct trojan').delete()
        Proxy.query.filter(Proxy.name == 'tls XTLSVision direct trojan').delete()
    except:
        pass
    add_config_if_not_exist(ConfigEnum.telegram_lib, "python")
    add_config_if_not_exist(ConfigEnum.admin_lang, hconfig(ConfigEnum.lang))
    add_config_if_not_exist(ConfigEnum.branding_title, "")
    add_config_if_not_exist(ConfigEnum.branding_site, "")
    add_config_if_not_exist(ConfigEnum.branding_freetext, "")
    add_config_if_not_exist(ConfigEnum.v2ray_enable, False)
    add_config_if_not_exist(ConfigEnum.is_parent, False)
    add_config_if_not_exist(ConfigEnum.parent_panel, '')
    add_config_if_not_exist(ConfigEnum.unique_id, str(uuid.uuid4()))


def _v9():
    # add_column(User.mode)
    # add_column(User.comment)
    try:
        for u in User.query.all():
            u.mode = UserMode.monthly if u.monthly else UserMode.no_reset
    except:
        pass


def _v10():
    all_configs = get_hconfigs()
    execute("ALTER TABLE `str_config` RENAME TO `str_config_old`")
    execute("ALTER TABLE `bool_config` RENAME TO `bool_config_old`")
    # db.create_all()
    rows = []
    for c, v in all_configs.items():
        if c.type() == bool:
            rows.append(BoolConfig(key=c, value=v, child_id=0))
        else:
            rows.append(StrConfig(key=c, value=v, child_id=0))

    db.session.bulk_save_objects(rows)


def get_proxy_rows_v1():
    rows = list(make_proxy_rows([
        "h2 direct vless",
        "XTLS direct vless",
        "WS direct vless",
        "WS direct trojan",
        "WS direct vmess",
        "tcp direct vless",
        "tcp direct trojan",
        "tcp direct vmess",
        "grpc direct vless",
        "grpc direct trojan",
        "grpc direct vmess",
        "faketls direct ss",
        "WS direct v2ray",
        "shadowtls direct ss",

        "h2 relay vless",
        "XTLS relay vless",
        "WS relay vless",
        "WS relay trojan",
        "WS relay vmess",
        "tcp relay vless",
        "tcp relay trojan",
        "tcp relay vmess",
        "grpc relay vless",
        "grpc relay trojan",
        "grpc relay vmess",
        "faketls relay ss",
        "WS relay v2ray",
        "shadowtls relay ss",
        # "restls1_2 direct ss",
        # "restls1_3 direct ss",
        # "tcp direct ssr",
        "WS CDN v2ray",
        "WS CDN vless",
        "WS CDN trojan",
        "WS CDN vmess",
        "grpc CDN vless",
        "grpc CDN trojan",
        "grpc CDN vmess",

    ]
    ))

    rows.append(Proxy(l3='ssh', transport='ssh', cdn='direct', proto='ssh', enable=True, name="SSH"))
    rows.append(Proxy(l3='ssh', transport=ProxyTransport.ssh, cdn=ProxyCDN.relay, proto=ProxyProto.ssh, enable=True, name="SSH Relay"))

    rows.append(Proxy(l3='tls', transport='custom', cdn='direct', proto='tuic', enable=True, name="TUIC"))
    rows.append(Proxy(l3='tls', transport='custom', cdn='relay', proto='tuic', enable=True, name="TUIC Relay"))
    rows.append(Proxy(l3='tls', transport='custom', cdn='direct', proto='hysteria2', enable=True, name="Hysteria2"))
    rows.append(Proxy(l3='tls', transport='custom', cdn='relay', proto='hysteria2', enable=True, name="Hysteria2 Relay"))
    rows.append(Proxy(l3=ProxyL3.udp, transport=ProxyTransport.custom, cdn=ProxyCDN.direct, proto=ProxyProto.wireguard, enable=True, name="WireGuard"))
    rows.append(Proxy(l3=ProxyL3.udp, transport=ProxyTransport.custom, cdn=ProxyCDN.relay, proto=ProxyProto.wireguard, enable=True, name="WireGuard Relay"))
    for p in rows:
        is_exist = Proxy.query.filter(Proxy.name == p.name).first() or Proxy.query.filter(
            Proxy.l3 == p.l3, Proxy.transport == p.transport, Proxy.cdn == p.cdn, Proxy.proto == p.proto).first()
        if not is_exist:
            yield p


def make_proxy_rows(cfgs):
    # "h3_quic",
    for l3 in ["tls_h2", "tls", "http", "kcp", "reality"]:
        for c in cfgs:
            transport, cdn, proto = c.split(" ")
            if l3 in ["kcp", 'reality'] and cdn != "direct":
                continue
            if l3 == "reality" and ((transport not in ['tcp', 'grpc', 'XTLS']) or proto != 'vless'):
                continue
            if proto == "trojan" and l3 not in ["tls", 'xtls', 'tls_h2', 'h3_quic']:
                continue
            if transport in ["grpc", "XTLS", "faketls"] and l3 == "http":
                continue
            if transport in ["h2"] and l3 != "reality":
                continue
            # if l3 == "tls_h2" and transport =="grpc":
            #     continue
            enable = l3 != "http" or proto == "vmess"
            enable = enable and transport != 'tcp'
            name = f'{l3} {c}'
            # is_exist = Proxy.query.filter(Proxy.name == name).first() or Proxy.query.filter(
            #     Proxy.l3 == l3, Proxy.transport == transport, Proxy.cdn == cdn, Proxy.proto == proto).first()
            # if not is_exist:
            yield Proxy(l3=l3, transport=transport, cdn=cdn, proto=proto, enable=enable, name=name)


def add_config_if_not_exist(key: ConfigEnum, val, child_id=statics.current_child_id):
    old_val = hconfig(key, child_id)
    if old_val is None:
        set_hconfig(key, val)


def add_column(column):
    try:
        column_type = column.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE {column.table.name} ADD COLUMN {column.name} {column_type}')
    except:
        pass


def execute(query):
    try:
        db.engine.execute(query)
    except:
        pass


def add_new_enum_values():
    columns = [
        Proxy.l3, Proxy.proto, Proxy.cdn, Proxy.transport,
        User.mode, Domain.mode, BoolConfig.key, StrConfig.key
    ]
    for col in columns:
        enum_class = col.type.enum_class
        column_name = col.name
        table_name = col.table

        # Get the existing values in the enum
        existing_values = [f'{e}' if isinstance(e, ConfigEnum) else e.value for e in enum_class]
        # print("existing_values--------------", existing_values)
        # Get the values in the enum column in the database
        # result = db.engine.execute(f"SELECT DISTINCT `{column_name}` FROM {table_name}")
        # db_values = {row[0] for row in result}
        result = db.engine.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{column_name}';")
        db_values = []

        for row in result:
            if "enum" in row[1]:
                db_values = row[1][5:-1].split(",")
                break
        db_values = [value.strip("'") for value in db_values]

        # Find the new values that need to be added to the enum column in the database
        new_values = set(existing_values) - set(db_values)
        old_values = set(db_values)-set(existing_values)
        # print('new_values-=-----------------', new_values)
        if len(new_values) == 0 and len(old_values) == 0:
            continue

        # Add the new value to the enum column in the database
        enumstr = ','.join([f"'{a}'" for a in [*existing_values, *old_values]])

        db.engine.execute(f"ALTER TABLE {table_name} MODIFY COLUMN `{column_name}` ENUM({enumstr});")

        db.session.commit()


def latest_db_version():
    for ver in range(MAX_DB_VERSION, 1, -1):
        db_action = sys.modules[__name__].__dict__.get(f'_v{ver}', None)
        if db_action:
            return ver
    return 0


def upgrade_database():

    panel_root = '/opt/hiddify-manager/hiddify-panel/'
    backup_root = f"{panel_root}backup/"
    sqlite_db = f"{panel_root}hiddifypanel.db"
    if not os.path.isdir(backup_root) or len(os.listdir(backup_root)) == 0:
        if os.path.isfile(sqlite_db):
            os.rename(sqlite_db, sqlite_db+".old")
        print("no backup found...")
        return
    if os.path.isfile(sqlite_db):
        hiddify.error("Finding Old Version Database... importing configs from latest backup")
        newest_file = max([(f, os.path.getmtime(os.path.join(backup_root, f)))
                          for f in os.listdir(backup_root) if os.path.isfile(os.path.join(backup_root, f))], key=lambda x: x[1])[0]
        with open(f'{backup_root}{newest_file}', 'r') as f:
            hiddify.error(f"importing configs from {newest_file}")
            json_data = json.load(f)
            hiddify.set_db_from_json(json_data,
                                     set_users=True,
                                     set_domains=True,
                                     remove_domains=True,
                                     remove_users=True,
                                     set_settings=True,
                                     override_unique_id=True,
                                     set_admins=True,
                                     override_root_admin=True,
                                     override_child_id=0,
                                     replace_owner_admin=True
                                     )
            db_version = int([d['value'] for d in json_data['hconfigs'] if d['key'] == "db_version"][0])
            os.rename(sqlite_db, sqlite_db+".old")
            set_hconfig(ConfigEnum.db_version, db_version, commit=True)
        hiddify.error("Upgrading to the new dataset succuess.")
