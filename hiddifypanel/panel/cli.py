import click


from hiddifypanel.panel.database import db
from hiddifypanel.panel.init_db import init_db
from hiddifypanel.models import *

from hiddifypanel.panel import hiddify, usage
import random
import uuid
import urllib
import string
from dateutil import relativedelta
import datetime


def drop_db():
    """Cleans database"""
    db.drop_all()


def downgrade():
    if (hconfig(ConfigEnum.db_version) == "41"):
        set_hconfig(ConfigEnum.db_version, 39, commit=False)
        StrConfig.query.filter(StrConfig.key == ConfigEnum.core_type).delete()
        for d in Domain.query.filter(Domain.mode == DomainType.sub_link_only).all():
            d.sub_link_only = True
            d.mode = DomainType.direct
        db.session.commit()
        Domain.query.filter(Domain.mode.in_(['reality', 'old_xtls_direct', 'worker'])).delete()
        db.session.commit()


def backup():
    dbdict = hiddify.dump_db_to_dict()
    import json
    import os
    os.makedirs('backup', exist_ok=True)
    dst = f'backup/{datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")}.json'
    with open(dst, 'w') as fp:
        json.dump(dbdict, fp, indent=4, sort_keys=True, default=str)

    if hconfig(ConfigEnum.telegram_bot_token):
        for admin in AdminUser.query.filter(AdminUser.mode == AdminMode.super_admin, AdminUser.telegram_id != None).all():
            from hiddifypanel.panel.commercial.telegrambot import bot
            with open(dst, 'rb') as document:
                caption = ("Backup \n"+admin_links())
                bot.send_document(admin.telegram_id, document, visible_file_name=dst.replace("backup/", ""), caption=caption[:min(len(caption), 1000)])


def all_configs():
    import json
    valid_users = [u.to_dict() for u in User.query.filter((User.usage_limit_GB > User.current_usage_GB)).all() if is_user_active(u)]

    configs = {
        "users": valid_users,
        "domains": [u.to_dict() for u in Domain.query.all() if "*" not in u.domain],
        # "parent_domains": [hiddify.parent_domain_dict(u) for u in ParentDomain.query.all()],
        "hconfigs": get_hconfigs()
    }
    for d in configs['domains']:
        d['domain'] = d['domain'].lower()
        # del d['domain']['show_domains']

    def_user = None if len(User.query.all()) > 1 else User.query.filter(User.name == 'default').first()
    domains = Domain.query.all()
    sslip_domains = [d.domain for d in domains if "sslip.io" in d.domain]

    configs['hconfigs']['first_setup'] = def_user != None and len(sslip_domains) > 0
    # configs

    print(json.dumps(configs))


def update_usage():
    print(usage.update_local_usage())


def test():
    print(ConfigEnum("auto_update1"))


def admin_links():
    proxy_path = hconfig(ConfigEnum.proxy_path)

    admin_secret = get_super_admin_secret()
    server_ip = hiddify.get_ip(4)
    admin_links = f"Not Secure:\n   http://{server_ip}/{proxy_path}/{admin_secret}/admin/\n"
    domains = get_panel_domains()
    admin_links += f"Secure:\n"
    admin_links += f"   (not signed) https://{server_ip}/{proxy_path}/{admin_secret}/admin/\n"
    # domains=[*domains,f'{server_ip}.sslip.io']
    for d in domains:
        admin_links += f"   https://{d.domain}/{proxy_path}/{admin_secret}/admin/\n"

    print(admin_links)
    return admin_links


def admin_path():
    proxy_path = hconfig(ConfigEnum.proxy_path)
    admin = Admin.query.filter(Admin.mode == AdminMode.super_admin).first()
    if not admin:
        db.session.add(Admin(mode=AdminMode.super_admin))
        db.session.commit()
        admin = Admin.query.filter(Admin.mode == AdminMode.super_admin).first()

    admin_secret = admin.uuid
    print(f"/{proxy_path}/{admin_secret}/admin/")


def init_app(app):
    # add multiple commands in a bulk
    # print(app.config['SQLALCHEMY_DATABASE_URI'] )
    for command in [init_db, drop_db, all_configs, update_usage, test, admin_links, admin_path, backup, downgrade]:
        app.cli.add_command(app.cli.command()(command))

    @app.cli.command()
    @click.option("--domain", "-d")
    def add_domain(domain):
        table = ParentDomain if hconfig(ConfigEnum.is_parent) else Domain

        if table.query.filter(table.domain == domain).first():
            return "Domain already exist."
        d = table(domain=domain)
        if not hconfig(ConfigEnum.is_parent):
            d.mode = DomainType.direct
        db.session.add(d)
        db.session.commit()
        return "success"

    @app.cli.command()
    @click.option("--admin_secret", "-a")
    def set_admin_secret(admin_secret):
        StrConfig.query.filter(StrConfig.key == ConfigEnum.admin_secret).update({'value': admin_secret})
        db.session.commit()
        return "success"

    @app.cli.command()
    @click.option("--key", "-k")
    @click.option("--val", "-v")
    def set_setting(key, val):
        old_hconfigs = get_hconfigs()
        hiddify.add_or_update_config(key=key, value=val)

        return "success"

    @app.cli.command()
    @click.option("--config", "-c")
    def import_config(config):
        next10year = datetime.date.today() + relativedelta.relativedelta(years=10)
        data = []
        if "USER_SECRET" in config:
            secrets = config["USER_SECRET"].split(";")
            for i, s in enumerate(secrets):
                data.append(User(name=f"default {i}", uuid=uuid.UUID(s), usage_limit_GB=9000, package_days=3650))

        if "MAIN_DOMAIN" in config:
            domains = config["MAIN_DOMAIN"].split(";")
            for i, d in enumerate(domains):
                if not Domain.query.filter(Domain.domain == d).first():
                    data.append(Domain(domain=d, mode=DomainType.direct),)

        strmap = {
            "TELEGRAM_FAKE_TLS_DOMAIN": ConfigEnum.telegram_fakedomain,
            "TELEGRAM_SECRET": ConfigEnum.shared_secret,
            "SS_FAKE_TLS_DOMAIN": ConfigEnum.ssfaketls_fakedomain,
            "FAKE_CDN_DOMAIN": ConfigEnum.domain_fronting_domain,
            "BASE_PROXY_PATH": ConfigEnum.proxy_path,
            "ADMIN_SECRET": ConfigEnum.admin_secret,
            "TELEGRAM_AD_TAG": ConfigEnum.telegram_adtag
        }
        boolmap = {
            "ENABLE_SS": ConfigEnum.ssfaketls_enable,
            "ENABLE_TELEGRAM": ConfigEnum.telegram_enable,
            "ENABLE_VMESS": ConfigEnum.vmess_enable,
            # "ENABLE_MONITORING":ConfigEnum.ssfaketls_enable,
            "ENABLE_FIREWALL": ConfigEnum.firewall,
            "ENABLE_NETDATA": ConfigEnum.netdata,
            "ENABLE_HTTP_PROXY": ConfigEnum.http_proxy_enable,
            "ALLOW_ALL_SNI_TO_USE_PROXY": ConfigEnum.allow_invalid_sni,
            "ENABLE_AUTO_UPDATE": ConfigEnum.auto_update,
            "ENABLE_SPEED_TEST": ConfigEnum.speed_test,
            "BLOCK_IR_SITES": ConfigEnum.block_iran_sites,
            "ONLY_IPV4": ConfigEnum.only_ipv4
        }

        for k in config:
            if k in strmap:
                if hconfig(strmap[k]) is None:
                    data.append(StrConfig(key=strmap[k], value=config[k]))
                else:
                    StrConfig.query.filter(StrConfig.key == strmap[k]).update({
                        'value': config[k]
                    })
            if k in boolmap:
                if hconfig(boolmap[k]) is None:
                    data.append(BoolConfig(key=boolmap[k], value=config[k]))
                else:
                    BoolConfig.query.filter(BoolConfig.key == strmap[k]).update({
                        'value': config[k]
                    })
        if len(data):
            db.session.bulk_save_objects(data)
        db.session.commit()
