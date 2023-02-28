import socket
from sqlalchemy.orm import Load
from babel.dates import format_timedelta as babel_format_timedelta
from hiddifypanel import xray_api
from flask_babelex import gettext as __
from flask_babelex import lazy_gettext as _
import urllib
from hiddifypanel.models import *
from hiddifypanel.panel.database import db
import datetime
from flask import jsonify, g, url_for, Markup
from wtforms.validators import ValidationError
from flask import flash as flask_flash
to_gig_d = 1000*1000*1000


def add_temporary_access():
    import random

    random_port = random.randint(30000, 50000)
    exec_command(
        f'/opt/hiddify-config/hiddify-panel/temporary_access.sh {random_port} &')
    # iptableparm=f'PREROUTING -p tcp --dport {random_port} -j REDIRECT --to-port 9000'
    # exec_command(f'iptables -t nat -I {iptableparm}')
    # exec_command(f'echo "iptables -t nat -D {iptableparm}" | at now + 4 hour')

    # iptableparm=f'INPUT -p tcp --dport {random_port} -j ACCEPT'
    # exec_command(f'iptables -I {iptableparm}')
    # exec_command(f'echo "iptables -D {iptableparm}" | at now + 4 hour')

    temp_admin_link = f"http://{get_ip(4)}:{random_port}{get_admin_path()}"
    g.temp_admin_link = temp_admin_link


def get_admin_path():
    proxy_path = hconfig(ConfigEnum.proxy_path)
    admin_secret = hconfig(ConfigEnum.admin_secret)
    return (f"/{proxy_path}/{admin_secret}/admin/")


def exec_command(cmd, cwd=None):
    try:
        import os
        os.system(cmd)
    except Exception as e:
        print(e)


def auth(function):
    def wrapper(*args, **kwargs):
        if g.user_uuid == None:
            return jsonify({"error": "auth failed"})
        if not admin and g.is_admin:
            return jsonify({"error": "admin can not access user page. add /admin/ to your url"})

        return function()

    return wrapper


def admin(function):
    def wrapper(*args, **kwargs):
        if g.user_uuid == None:
            return jsonify({"error": "auth failed"})
        if not g.is_admin:
            return jsonify({"error": "invalid admin"})

        return function()

    return wrapper


def abs_url(path):
    return f"/{g.proxy_path}/{g.user_uuid}/{path}"


def asset_url(path):
    return f"/{g.proxy_path}/{path}"

# def update_usage():

#         res={}
#         have_change=False
#         for user in User.query.all():
#             if user.monthly and (datetime.date.today()-user.last_reset_time).days>=30:
#                 user.last_reset_time=datetime.date.today()
#                 if user.current_usage_GB > user.usage_limit_GB:
#                     xray_api.add_client(user.uuid)
#                     have_change=True
#                 user.current_usage_GB=0

#             d = xray_api.get_usage(user.uuid,reset=True)

#             if d == None:
#                res[user.uuid]="No value"
#             else:
#                 in_gig=(d)/to_gig_d
#                 res[user.uuid]=in_gig
#                 user.current_usage_GB += in_gig
#             if user.current_usage_GB > user.usage_limit_GB:
#                 xray_api.remove_client(user.uuid)
#                 have_change=True
#                 res[user.uuid]=f"{res[user.uuid]} !OUT of USAGE! Client Removed"

#         db.session.commit()
#         if have_change:
#             quick_apply_users()
#         return {"status": 'success', "comments":res}


def domain_dict(d):
    return {
        'domain': d.domain,
        'mode': d.mode,
        'alias': d.alias,
        'child_ip': d.child.ip if d.child else '',
        'cdn_ip': d.cdn_ip,
        'show_domains': [dd.domain for dd in d.show_domains]
    }


def parent_domain_dict(d):
    return {
        'domain': d.domain,
        'show_domains': [dd.domain for dd in d.show_domains]
    }


def proxy_dict(d):
    return {
        'name': d.name,
        'enable': d.enable,
        'proto': d.proto,
        'l3': d.l3,
        'transport': d.transport,
        'cdn': d.cdn,
        'child_ip': d.child.ip if d.child else ''
    }


def parent_domain_dict(d):
    return {
        'domain': d.domain,
    }


def config_dict(d):
    return {
        'key': d.key,
        'value': d.value,
        'child_ip': d.child.ip if d.child else ''
    }


def get_ip(version, retry=3):
    try:
        return urllib.request.urlopen(f'https://v{version}.ident.me/').read().decode('utf8')
    except:
        if retry == 0:
            return None
        return get_ip(version, retry=retry-1)


def get_available_proxies():
    proxies = Proxy.query.all()

    if not hconfig(ConfigEnum.domain_fronting_domain):
        proxies = [c for c in proxies if 'Fake' not in c.cdn]
    if not hconfig(ConfigEnum.ssfaketls_enable):
        proxies = [c for c in proxies if 'faketls' != c.transport]
        proxies = [c for c in proxies if 'v2ray' != c.proto]
    if not hconfig(ConfigEnum.shadowtls_enable):
        proxies = [c for c in proxies if c.transport != 'shadowtls']
    if not hconfig(ConfigEnum.ssr_enable):
        proxies = [c for c in proxies if 'ssr' != c.proto]
    if not hconfig(ConfigEnum.vmess_enable):
        proxies = [c for c in proxies if 'vmess' not in c.proto]

    if not hconfig(ConfigEnum.kcp_enable):
        proxies = [c for c in proxies if 'kcp' not in c.l3]

    if not hconfig(ConfigEnum.http_proxy_enable):
        proxies = [c for c in proxies if 'http' != c.l3]

    if not Domain.query.filter(Domain.mode == DomainType.cdn).first():
        proxies = [c for c in proxies if c.cdn != "CDN"]
    return proxies


def quick_apply_users():
    if hconfig(ConfigEnum.is_parent):
        return
    exec_command("/opt/hiddify-config/install.sh apply_users &")


def flash_config_success(restart_mode='', domain_changed=True):

    if restart_mode and not hconfig(ConfigEnum.is_parent):
        url = url_for('admin.Actions:reinstall', complete_install=restart_mode ==
                      'reinstall', domain_changed=domain_changed)
        apply_btn = f"<a href='{url}' class='btn btn-primary form_post'>" + \
            _("admin.config.apply_configs")+"</a>"
        flash((_('config.validation-success', link=apply_btn)), 'success')
    else:
        flash((_('config.validation-success-no-reset')), 'success')


# Importing socket library

# Function to display hostname and
# IP address

def get_domain_ip(domain):
    import socket
    try:
        return socket.gethostbyname(domain)
    except:
        try:
            return socket.getaddrinfo(domain, None, socket.AF_INET6)
        except:
            return None


def check_connection_to_remote(api_url):
    import requests
    path = f"{api_url}/api/v1/hello/"

    try:
        res = requests.get(path, verify=False, timeout=2).json()
        return True

    except:
        return False


def check_connection_for_domain(domain):
    import requests
    proxy_path = hconfig(ConfigEnum.proxy_path)
    admin_secret = hconfig(ConfigEnum.admin_secret)
    path = f"{proxy_path}/{admin_secret}/api/v1/hello/"
    try:
        print(f"https://{domain}/{path}")
        res = requests.get(
            f"https://{domain}/{path}", verify=False, timeout=2).json()
        return res['status'] == 200

    except:
        try:
            print(f"http://{domain}/{path}")
            res = requests.get(
                f"http://{domain}/{path}", verify=False, timeout=2).json()
            return res['status'] == 200
        except:
            try:
                print(f"http://{get_domain_ip(domain)}/{path}")
                res = requests.get(
                    f"http://{get_domain_ip(domain)}/{path}", verify=False, timeout=2).json()
                return res['status'] == 200
            except:
                return False
    return True


def get_user_link(uuid, domain, mode=''):
    proxy_path = hconfig(ConfigEnum.proxy_path)
    res = ""
    if mode == "multi":
        res += "<div class='btn-group'>"

    link = f"https://{domain.domain}/{proxy_path}/{uuid}/"
    link_multi = f"{link}multi"
    if mode == 'new':
        link = f"{link}new"
    text = domain.domain

    if hasattr(domain, 'mode') and domain.mode == DomainType.cdn:
        text = f'<span class="badge badge-success" >{_("domain.cdn")}</span>'+text

    if mode == "multi":
        res += f"<a class='btn btn-xs btn-secondary' target='_blank' href='{link_multi}' >{_('all')}</a>"
    res += f"<a target='_blank' href='{link}' class='btn btn-xs btn-info ltr' ><i class='fa-solid fa-arrow-up-right-from-square'></i> {text}</a>"

    if mode == "multi":
        res += "</div>"
    return res


def flash(message, category):
    print(message)
    return flask_flash(Markup(message), category)


def validate_domain_exist(form, field):
    domain = field.data
    if not domain:
        return
    dip = get_domain_ip(domain)
    if dip == None:
        raise ValidationError(
            _("Domain can not be resolved! there is a problem in your domain"))


def check_need_reset(old_configs):
    restart_mode = ''
    for c in old_configs:
        if old_configs[c] != hconfig(c) and c.apply_mode():
            if restart_mode != 'reinstall':
                restart_mode = c.apply_mode()
    # do_full_install=old_config[ConfigEnum.telegram_lib]!=hconfig(ConfigEnum.telegram_lib)

    flash_config_success(restart_mode=restart_mode, domain_changed=False)


def dump_db_to_dict():
    return {"users": [u.to_dict() for u in User.query.all()],
            "domains": [domain_dict(u) for u in Domain.query.all()],
            "proxies": [proxy_dict(u) for u in Proxy.query.all()],
            "parent_domains": [parent_domain_dict(u) for u in ParentDomain.query.all()],
            "hconfigs": [*[config_dict(u) for u in BoolConfig.query.all()],
                         *[config_dict(u) for u in StrConfig.query.all()]]
            }


def set_db_from_json(json_data, override_child_id=None, set_users=True, set_domains=True, set_proxies=True, set_settings=True, remove_domains=False, remove_users=False, override_unique_id=True):
    def get_child(dic):
        print(override_child_id)
        if override_child_id is not None:
            return override_child_id
        if 'child_ip' in dic:
            child = Child.query.filter(Child.ip == dic['child_ip']).first()
            if child:
                return child.id
        return 0

    new_rows = []
    if set_users and 'users' in json_data:
        for user in json_data['users']:
            print(user)
            dbuser = User.query.filter(User.uuid == user['uuid']).first()

            if not dbuser:
                dbuser = User()
                dbuser.uuid = user['uuid']
                new_rows.append(dbuser)

            dbuser.current_usage_GB = user['current_usage_GB']
            dbuser.expiry_time = datetime.datetime.strptime(
                user['expiry_time'], '%Y-%m-%d')
            dbuser.last_reset_time = datetime.datetime.strptime(
                user['last_reset_time'], '%Y-%m-%d')
            dbuser.usage_limit_GB = user['usage_limit_GB']
            dbuser.name = user['name']
            dbuser.comment = user.get('comment', '')
            dbuser.mode = user.get('mode', user.get(
                'monthly', 'false') == 'true')
            # dbuser.last_online=user.get('last_online','')
    if remove_users and 'users' in json_data:
        dd = {u.uuid: 1 for u in json_data['users']}
        for d in User.query.all():
            if d.uuid not in dd:
                db.session.delete(d)

    if set_domains and 'domains' in json_data:
        for domain in json_data['domains']:
            dbdomain = Domain.query.filter(
                Domain.domain == domain['domain']).first()
            if not dbdomain:
                dbdomain = Domain(domain=domain['domain'])
                new_rows.append(dbdomain)
            dbdomain.child_id = get_child(domain)

            dbdomain.mode = domain['mode']
            dbdomain.cdn_ip = domain.get('cdn_ip', '')
            domain.alias = domain.get('alias', '')
            show_domains = domain.get('show_domains', [])
            dbdomain.show_domains = Domain.query.filter(
                Domain.domain.in_(show_domains)).all()
    if remove_domains and override_child_id is not None and 'domains' in json_data:
        dd = {d['domain']: 1 for d in json_data['domains']}
        for d in Domain.query.filter(Domain.child_id == override_child_id):
            if d.domain not in dd:
                db.session.delete(d)
    if set_settings and 'hconfigs' in json_data:

        for config in json_data["hconfigs"]:
            c = config['key']
            ckey = ConfigEnum(c)
            if c == ConfigEnum.unique_id and not override_unique_id:
                continue
            v = config['value']
            child_id = get_child(config)
            print(c, ckey, ckey.type(), "child_id", child_id)
            if ckey in [ConfigEnum.db_version]:
                continue
            if ckey.type() == bool:
                dbconf = BoolConfig.query.filter(
                    BoolConfig.key == ckey, BoolConfig.child_id == child_id).first()
                # print(dbconf,dbconf.child_id)
                print("====", dbconf)
                if not dbconf:
                    dbconf = BoolConfig(key=ckey, child_id=child_id)
                    new_rows.append(dbconf)

                v = str(v).lower() == "true"
            else:
                dbconf = StrConfig.query.filter(
                    StrConfig.key == ckey, StrConfig.child_id == child_id).first()
                print("====", dbconf)
                if not dbconf:
                    dbconf = StrConfig(key=ckey, child_id=child_id)
                    new_rows.append(dbconf)

            dbconf.value = v
            print(">>>>", dbconf)
        if 'proxies' in json_data:
            for proxy in json_data["proxies"]:
                dbproxy = Proxy.query.filter(
                    Proxy.name == proxy['name']).first()
                if not dbproxy:
                    dbproxy = Proxy()
                    new_rows.append(dbproxy)
                dbproxy.enable = proxy['enable']
                dbproxy.name = proxy['name']
                dbproxy.proto = proxy['proto']
                dbproxy.transport = proxy['transport']
                dbproxy.cdn = proxy['cdn']
                dbproxy.l3 = proxy['l3']
                dbproxy.child_id = get_child(proxy)

    print(new_rows)
    db.session.bulk_save_objects(new_rows)
    db.session.commit()


def format_timedelta(delta, add_direction=True):

    if delta.days < 7 or delta.days >= 60:
        return babel_format_timedelta(delta, threshold=1, add_direction=add_direction, locale=g.locale)
    if delta.days < 60:
        return babel_format_timedelta(delta, granularity="day", threshold=10, add_direction=add_direction, locale=g.locale)
