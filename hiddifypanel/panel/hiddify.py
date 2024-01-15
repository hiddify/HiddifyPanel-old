import socket
import user_agents
from hiddifypanel.cache import cache
from sqlalchemy.orm import Load
import glob
import json
from babel.dates import format_timedelta as babel_format_timedelta
from flask_babelex import gettext as __
from flask_babelex import lazy_gettext as _
from hiddifypanel.models import *
from hiddifypanel.panel.database import db
import datetime
from flask import jsonify, g, url_for, Markup, abort, current_app, request
from flask import flash as flask_flash
import re
from wtforms.validators import ValidationError
import requests

import string
import random
from babel.dates import format_timedelta as babel_format_timedelta
import urllib
import time
import os
import psutil
from urllib.parse import urlparse
import ssl
import h2.connection
import subprocess
import netifaces
import time

to_gig_d = 1000*1000*1000


def add_temporary_access():
    random_port = random.randint(30000, 50000)
    exec_command(
        f'sudo /opt/hiddify-config/hiddify-panel/temporary_access.sh {random_port} &')
    temp_admin_link = f"http://{get_ip(4)}:{random_port}{get_admin_path()}"
    g.temp_admin_link = temp_admin_link


def add_short_link(link, period_min=5):
    # pattern = "\^/([^/]+)(/)?\?\$\ {return 302 " + re.escape(link) + ";}"
    pattern = r"([^/]+)\("

    with open(current_app.config['HIDDIFY_CONFIG_PATH']+"/nginx/parts/short-link.conf", 'r') as f:
        for line in f:
            if link in line:
                return re.search(pattern, line).group(1)

    short_code = get_random_string(6, 10).lower()
    exec_command(
        f'sudo /opt/hiddify-config/nginx/add2shortlink.sh {link} {short_code} {period_min} &')
    return short_code


def get_admin_path():
    proxy_path = hconfig(ConfigEnum.proxy_path)
    admin_secret = g.admin.uuid or get_super_admin_secret()
    return (f"/{proxy_path}/{admin_secret}/admin/")


def exec_command(cmd, cwd=None):
    try:
        subprocess.Popen(cmd.split(" "))  # run in background
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


def super_admin(function):
    def wrapper(*args, **kwargs):
        if g.admin.mode not in [AdminMode.super_admin]:
            abort(403, __("Access Denied"))
            return jsonify({"error": "auth failed"})
        return function(*args, **kwargs)

    return wrapper


def admin(function):
    def wrapper(*args, **kwargs):
        if g.admin.mode not in [AdminMode.admin, AdminMode.super_admin]:
            abort(_("Access Denied"), 403)
            return jsonify({"error": "auth failed"})

        return function(*args, **kwargs)
    return wrapper


def abs_url(path):
    return f"/{g.proxy_path}/{g.user_uuid}/{path}"


def asset_url(path):
    return f"/{g.proxy_path}/{path}"


@cache.cache(ttl=600)
def get_direct_host_or_ip(prefer_version):
    direct = Domain.query.filter(Domain.mode == DomainType.direct, Domain.sub_link_only == False).first()
    if not (direct):
        direct = Domain.query.filter(Domain.mode == DomainType.direct).first()
    if direct:
        direct = direct.domain
    else:
        direct = get_ip(prefer_version)
    if not direct:
        direct = get_ip(4 if prefer_version == 6 else 6)
    return direct


@cache.cache(ttl=600)
def get_ip(version, retry=5):
    ips = get_interface_public_ip(version)
    ip = None
    if (ips):
        ip = random.sample(ips, 1)[0]

    if ip is None:
        ip = get_socket_public_ip(version)

    if ip is None:
        try:
            ip = urllib.request.urlopen(f'https://v{version}.ident.me/').read().decode('utf8')

        except:
            pass
    if ip is None and retry > 0:
        ip = get_ip(version, retry=retry-1)
    return ip


def get_socket_public_ip(version):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if version == 6:
            s.connect(("2001:4860:4860::8888", 80))
        else:
            s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()

        return ip_address if is_public_ip(ip_address) else None
    except socket.error:
        return None


def is_public_ip(address):
    if address.startswith('127.') or address.startswith('169.254.') or address.startswith('10.') or address.startswith('192.168.') or address.startswith('172.'):
        return False
    if address.startswith('fe80:') or address.startswith('fd') or address.startswith('fc00:'):
        return False
    return True


def get_interface_public_ip(version):
    addresses = []
    try:
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            if version == 4:
                address_info = netifaces.ifaddresses(interface).get(netifaces.AF_INET, [])
            elif version == 6:
                address_info = netifaces.ifaddresses(interface).get(netifaces.AF_INET6, [])
            else:
                return None

            if address_info:
                for addr in address_info:
                    address = addr['addr']
                    if (is_public_ip(address)):
                        addresses.append(address)

        return addresses if addresses else None

    except (OSError, KeyError):
        return None


@cache.cache(ttl=300)
def get_available_proxies(child_id):
    proxies = Proxy.query.filter(Proxy.child_id == child_id).all()
    proxies = [c for c in proxies if 'restls' not in c.transport]
    if not hconfig(ConfigEnum.domain_fronting_domain, child_id):
        proxies = [c for c in proxies if 'Fake' not in c.cdn]
    if not hconfig(ConfigEnum.ssfaketls_enable, child_id):
        proxies = [c for c in proxies if 'faketls' != c.transport]
    if not hconfig(ConfigEnum.v2ray_enable, child_id):
        proxies = [c for c in proxies if 'v2ray' != c.proto]
    if not hconfig(ConfigEnum.shadowtls_enable, child_id):
        proxies = [c for c in proxies if c.transport != 'shadowtls']
    if not hconfig(ConfigEnum.ssr_enable, child_id):
        proxies = [c for c in proxies if 'ssr' != c.proto]
    if not hconfig(ConfigEnum.vmess_enable, child_id):
        proxies = [c for c in proxies if 'vmess' not in c.proto]

    if not hconfig(ConfigEnum.kcp_enable, child_id):
        proxies = [c for c in proxies if 'kcp' not in c.l3]

    if not hconfig(ConfigEnum.http_proxy_enable, child_id):
        proxies = [c for c in proxies if 'http' != c.l3]

    if not Domain.query.filter(Domain.mode.in_([DomainType.cdn, DomainType.auto_cdn_ip])).first():
        proxies = [c for c in proxies if c.cdn != "CDN"]

    proxies = [c for c in proxies if not ('vless' == c.proto and ProxyTransport.tcp == c.transport and c.cdn == ProxyCDN.direct)]
    return proxies


def quick_apply_users():
    if hconfig(ConfigEnum.is_parent):
        return
    # from hiddifypanel.panel import usage
    # usage.update_local_usage()
    # return
    # for user in User.query.all():
    #     if is_user_active(user):
    #         xray_api.add_client(user.uuid)
    #     else:
    #         xray_api.remove_client(user.uuid)

    exec_command("sudo /opt/hiddify-config/install.sh apply_users &")

    time.sleep(1)
    return {"status": 'success'}


def flash_config_success(restart_mode='', domain_changed=True):
    if restart_mode:
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


def get_domain_ip(dom, retry=3, version=None):

    res = None
    if not version:
        try:
            res = socket.gethostbyname(dom)
        except:
            pass

    if not res and version != 6:
        try:
            res = socket.getaddrinfo(dom, None, socket.AF_INET)[0][4][0]
        except:
            pass

    if not res and version != 4:
        try:
            res = f"[{socket.getaddrinfo(dom, None, socket.AF_INET6)[0][4][0]}]"
        except:
            pass

    if retry <= 0:
        return None

    return res or get_domain_ip(dom, retry=retry-1)


def check_connection_to_remote(api_url):

    path = f"{api_url}/api/v1/hello/"

    try:
        res = requests.get(path, verify=False, timeout=2).json()
        return True

    except:
        return False


def check_connection_for_domain(domain):

    proxy_path = hconfig(ConfigEnum.proxy_path)
    admin_secret = hconfig(ConfigEnum.admin_secret)
    path = f"{proxy_path}/{admin_secret}/api/v1/hello/"
    try:
        print(f"https://{domain}/{path}")
        res = requests.get(
            f"https://{domain}/{path}", verify=False, timeout=10).json()
        return res['status'] == 200

    except:
        try:
            print(f"http://{domain}/{path}")
            res = requests.get(
                f"http://{domain}/{path}", verify=False, timeout=10).json()
            return res['status'] == 200
        except:
            try:
                print(f"http://{get_domain_ip(domain)}/{path}")
                res = requests.get(
                    f"http://{get_domain_ip(domain)}/{path}", verify=False, timeout=10).json()
                return res['status'] == 200
            except:
                return False
    return True


def get_user_link(uuid, domain, mode='', username=''):
    is_cdn = domain.mode == DomainType.cdn if type(domain) == Domain else False
    proxy_path = hconfig(ConfigEnum.proxy_path)
    res = ""
    if mode == "multi":
        res += "<div class='btn-group'>"
    d = domain.domain
    if "*" in d:
        d = d.replace("*", get_random_string(5, 15))

    link = f"https://{d}/{proxy_path}/{uuid}/#{username}"
    if mode == "admin":
        link = f"https://{d}/{proxy_path}/{uuid}/admin/#{username}"
    link_multi = f"{link}multi"
    # if mode == 'new':
    #     link = f"{link}new"
    text = domain.alias or domain.domain
    color_cls = 'info'

    if type(domain) == Domain and not domain.sub_link_only and domain.mode in [DomainType.cdn, DomainType.auto_cdn_ip]:
        auto_cdn = (domain.mode == DomainType.auto_cdn_ip) or (domain.cdn_ip and "MTN" in domain.cdn_ip)
        color_cls = "success" if auto_cdn else 'warning'
        text = f'<span class="badge badge-secondary" >{"Auto" if auto_cdn else "CDN"}</span> '+text

    if mode == "multi":
        res += f"<a class='btn btn-xs btn-secondary' target='_blank' href='{link_multi}' >{_('all')}</a>"
    res += f"<a target='_blank' href='{link}' class='btn btn-xs btn-{color_cls} ltr' ><i class='fa-solid fa-arrow-up-right-from-square d-none'></i> {text}</a>"

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


def reinstall_action(complete_install=False, domain_change=False, do_update=False):
    from hiddifypanel.panel.admin.Actions import Actions
    action = Actions()
    if do_update:
        return action.update()
    return action.reinstall(complete_install=complete_install, domain_changed=domain_changed)


def check_need_reset(old_configs, do=False):
    restart_mode = ''
    for c in old_configs:
        # c=ConfigEnum(c)
        if old_configs[c] != hconfig(c) and c.apply_mode():
            if restart_mode != 'reinstall':
                restart_mode = c.apply_mode()

    # do_full_install=old_config[ConfigEnum.telegram_lib]!=hconfig(ConfigEnum.telegram_lib)
    if old_configs[ConfigEnum.package_mode] != hconfig(ConfigEnum.package_mode):
        return reinstall_action(do_update=True)
    if not (do and restart_mode == 'reinstall'):
        return flash_config_success(restart_mode=restart_mode, domain_changed=False)

    return reinstall_action(complete_install=True, domain_changed=domain_changed)


def format_timedelta(delta, add_direction=True, granularity="days"):
    res = delta.days
    locale = g.locale if g and hasattr(g, "locale") else hconfig(ConfigEnum.admin_lang)
    if granularity == "days" and delta.days == 0:
        res = _("0 - Last day")
    elif delta.days < 7 or delta.days >= 60:
        res = babel_format_timedelta(delta, threshold=1, add_direction=add_direction, locale=locale)
    elif delta.days < 60:
        res = babel_format_timedelta(delta, granularity="day", threshold=10, add_direction=add_direction, locale=locale)
    return res


def get_child(unique_id):
    child_id = 0
    if unique_id is None:
        child_id = 0
    else:
        child = Child.query.filter(Child.unique_id == str(unique_id)).first()
        if not child:
            child = Child(unique_id=str(unique_id))
            db.session.add(child)
            db.session.commit()
            child = Child.query.filter(Child.unique_id == str(unique_id)).first()
        child_id = child.id
    return child_id


def date_to_json(d):
    return d.strftime("%Y-%m-%d") if d else None


def json_to_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except:
        return None


def time_to_json(d):
    return d.strftime("%Y-%m-%d %H:%M:%S") if d else None


def json_to_time(time_str):
    try:
        return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except:
        return None


def dump_db_to_dict():
    return {"users": [u.to_dict() for u in User.query.all()],
            "domains": [u.to_dict() for u in Domain.query.all()],
            "proxies": [u.to_dict() for u in Proxy.query.all()],
            "parent_domains": [] if not hconfig(ConfigEnum.license) else [u.to_dict() for u in ParentDomain.query.all()],
            'admin_users': [d.to_dict() for d in AdminUser.query.all()],
            "hconfigs": [*[u.to_dict() for u in BoolConfig.query.all()],
                         *[u.to_dict() for u in StrConfig.query.all()]]
            }


def get_ids_without_parent(input_dict):
    selector = "uuid"
    # Get all parent_uuids in a set for faster lookup
    parent_uuids = {item.get(f'parent_admin_uuid') for item in input_dict.values()
                    if item.get(f'parent_admin_uuid') is not None
                    and item.get(f'parent_admin_uuid') != item.get('uuid')}
    print("PARENTS", parent_uuids)
    uuids = {v['uuid']: v for v in input_dict.values()}
    # Find all uuids that do not have a parent_uuid in the dict
    uuids_without_parent = [key for key, item in input_dict.items()
                            if item.get(f'parent_admin_uuid') is None
                            or item.get(f'parent_admin_uuid') == item.get('uuid')
                            or item[f'parent_admin_uuid'] not in uuids]
    print("abondon uuids", uuids_without_parent)

    return uuids_without_parent


def set_db_from_json(json_data, override_child_id=None, set_users=True, set_domains=True, set_proxies=True, set_settings=True, remove_domains=False, remove_users=False, override_unique_id=True, set_admins=True, override_root_admin=False):
    new_rows = []

    uuids_without_parent = get_ids_without_parent({u['uuid']: u for u in json_data['admin_users']})
    print('uuids_without_parent===============', uuids_without_parent)
    all_admins = {u.uuid: u for u in AdminUser.query.all()}
    uuids_without_parent = [uuid for uuid in uuids_without_parent if uuid not in all_admins]
    print('uuids_not admin exist===============', uuids_without_parent)

    if "admin_users" in json_data:
        for u in json_data['admin_users']:
            if override_root_admin and u['uuid'] in uuids_without_parent:
                u['uuid'] = g.admin.uuid
            if u['parent_admin_uuid'] in uuids_without_parent:
                u['parent_admin_uuid'] = g.admin.uuid
    if "users" in json_data and override_root_admin:
        for u in json_data['users']:
            if u['added_by_uuid'] in uuids_without_parent:
                u['added_by_uuid'] = g.admin.uuid

    if set_admins and 'admin_users' in json_data:
        bulk_register_admins(json_data['admin_users'], commit=False)
    if set_users and 'users' in json_data:
        bulk_register_users(json_data['users'], commit=False, remove=remove_users)
    if set_domains and 'domains' in json_data:
        bulk_register_domains(json_data['domains'], commit=False, remove=remove_domains, override_child_id=override_child_id)
    if set_domains and 'parent_domains' in json_data:
        bulk_register_parent_domains(json_data['parent_domains'], commit=False, remove=remove_domains)
    if set_settings and 'hconfigs' in json_data:
        bulk_register_configs(json_data["hconfigs"], commit=False, override_child_id=override_child_id, override_unique_id=override_unique_id)
        if 'proxies' in json_data:
            bulk_register_proxies(json_data['proxies'], commit=False, override_child_id=override_child_id)

    ids_without_parent = get_ids_without_parent({u.id: u.to_dict() for u in AdminUser.query.all()})
    owner = get_super_admin()
    ids_without_parent = [id for id in ids_without_parent if id != owner.id]

    for u in AdminUser.query.all():
        if u.parent_admin_id in ids_without_parent:
            u.parent_admin_id = owner.id
    # for u in User.query.all():
    #     if u.added_by in uuids_without_parent:
    #         u.added_by = g.admin.id

    db.session.commit()


def get_random_string(min_=10, max_=30):
    # With combination of lower and upper case
    length = random.randint(min_, max_)
    characters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(characters) for i in range(length))
    return result_str


def get_warp_info():
    proxies = dict(http='socks5://127.0.0.1:3000',
                   https='socks5://127.0.0.1:3000')
    res = requests.get("https://cloudflare.com/cdn-cgi/trace", proxies=proxies, timeout=1).text

    dicres = {line.split("=")[0]: line.split("=")[0] for line in res}
    return dicres


def system_stats():
    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)

    # RAM usage
    ram_stats = psutil.virtual_memory()
    ram_used = ram_stats.used / 1024**3
    ram_total = ram_stats.total / 1024**3

    # Disk usage (in GB)
    disk_stats = psutil.disk_usage('/')
    disk_used = disk_stats.used / 1024**3
    disk_total = disk_stats.total / 1024**3

    hiddify_used = get_folder_size('/opt/hiddify-config/') / 1024**3

    # Network usage
    net_stats = psutil.net_io_counters()
    bytes_sent_cumulative = net_stats.bytes_sent
    bytes_recv_cumulative = net_stats.bytes_recv
    bytes_sent = net_stats.bytes_sent - getattr(system_stats, 'prev_bytes_sent', 0)
    bytes_recv = net_stats.bytes_recv - getattr(system_stats, 'prev_bytes_recv', 0)
    system_stats.prev_bytes_sent = net_stats.bytes_sent
    system_stats.prev_bytes_recv = net_stats.bytes_recv

    # Total connections and unique IPs
    connections = psutil.net_connections()
    total_connections = len(connections)
    unique_ips = set([conn.raddr.ip for conn in connections if conn.status == 'ESTABLISHED' and conn.raddr])
    total_unique_ips = len(unique_ips)

    # Load average
    num_cpus = psutil.cpu_count()
    load_avg = [avg / num_cpus for avg in os.getloadavg()]
    # Return the system information
    return {
        "cpu_percent": cpu_percent / num_cpus,
        "ram_used": ram_used,
        "ram_total": ram_total,
        "disk_used": disk_used,
        "disk_total": disk_total,
        "hiddify_used": hiddify_used,
        "bytes_sent": bytes_sent,
        "bytes_recv": bytes_recv,
        "bytes_sent_cumulative": bytes_sent_cumulative,
        "bytes_recv_cumulative": bytes_recv_cumulative,
        "net_sent_cumulative_GB": bytes_sent_cumulative / 1024**3,
        "net_total_cumulative_GB": (bytes_sent_cumulative+bytes_recv_cumulative) / 1024**3,
        "total_connections": total_connections,
        "total_unique_ips": total_unique_ips,
        "load_avg_1min": load_avg[0],
        "load_avg_5min": load_avg[1],
        "load_avg_15min": load_avg[2],
        'num_cpus': num_cpus
    }


def top_processes():
    # Get the process information
    processes = [p for p in psutil.process_iter(['name', 'memory_full_info', 'cpu_percent']) if p.info['name'] != '']
    num_cores = psutil.cpu_count()
    # Calculate memory usage, RAM usage, and CPU usage for each process
    memory_usage = {}
    ram_usage = {}
    cpu_usage = {}
    for p in processes:
        name = p.info['name']
        if "python3" in name or "uwsgi" in name or 'flask' in name:
            name = "Hiddify"
        mem_info = p.info['memory_full_info']
        if mem_info is None:
            continue
        mem_usage = mem_info.uss
        cpu_percent = p.info['cpu_percent']/num_cores
        if name in memory_usage:
            memory_usage[name] += mem_usage / (1024 ** 3)
            ram_usage[name] += mem_info.rss / (1024 ** 3)
            cpu_usage[name] += cpu_percent
        else:
            memory_usage[name] = mem_usage / (1024 ** 3)
            ram_usage[name] = mem_info.rss / (1024 ** 3)
            cpu_usage[name] = cpu_percent

    while len(cpu_usage) < 5:
        cpu_usage[" "*len(cpu_usage)] = 0
    while len(ram_usage) < 5:
        ram_usage[" "*len(ram_usage)] = 0
    while len(memory_usage) < 5:
        memory_usage[" "*len(memory_usage)] = 0
    # Sort the processes by memory usage, RAM usage, and CPU usage
    top_memory = sorted(memory_usage.items(), key=lambda x: x[1], reverse=True)[:5]
    top_ram = sorted(ram_usage.items(), key=lambda x: x[1], reverse=True)[:5]
    top_cpu = sorted(cpu_usage.items(), key=lambda x: x[1], reverse=True)[:5]

    # Return the top processes for memory usage, RAM usage, and CPU usage
    return {
        "memory": top_memory,
        "ram": top_ram,
        "cpu": top_cpu
    }


def get_folder_size(folder_path):
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                try:
                    total_size += os.path.getsize(file_path)
                except:
                    pass
    except:
        pass
    return total_size


def get_domain_btn_link(domain):
    text = domain.alias or domain.domain
    color_cls = "info"
    if domain.mode in [DomainType.cdn, DomainType.auto_cdn_ip]:
        auto_cdn = (domain.mode == DomainType.auto_cdn_ip) or (domain.cdn_ip and "MTN" in domain.cdn_ip)
        color_cls = "success" if auto_cdn else 'warning'
        text = f'<span class="badge badge-secondary" >{"Auto" if auto_cdn else "CDN"}</span> '+text
    res = f"<a target='_blank' href='#' class='btn btn-xs btn-{color_cls} ltr' ><i class='fa-solid fa-arrow-up-right-from-square d-none'></i> {text}</a>"
    return res


def get_random_domains(count=1, retry=3):
    try:
        irurl = "https://api.ooni.io/api/v1/measurements?probe_cc=IR&test_name=web_connectivity&anomaly=false&confirmed=false&failure=false&order_by=test_start_time&limit=1000"
        # cnurl="https://api.ooni.io/api/v1/measurements?probe_cc=CN&test_name=web_connectivity&anomaly=false&confirmed=false&failure=false&order_by=test_start_time&limit=1000"
        data_ir = requests.get(irurl).json()
        # data_cn=requests.get(url).json()

        domains = [urlparse(d['input']).netloc.lower() for d in data_ir['results'] if d['scores']['blocking_country'] == 0.0]
        domains = [d for d in domains if not d.endswith(".ir") and not ".gov" in d]

        return random.sample(domains, count)
    except Exception as e:
        print('Error, getting random domains... ', e, 'retrying...', retry)
        if retry <= 0:
            defdomains = ["fa.wikipedia.org", 'en.wikipedia.org', 'wikipedia.org', 'yahoo.com', 'en.yahoo.com']
            print('Error, using default domains')
            return random.sample(defdomains, count)
        return get_random_domains(count, retry-1)


def is_domain_support_tls_13(domain):
    context = ssl.create_default_context()
    with socket.create_connection((domain, port)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            return ssock.version() == "TLSv1.3"


def is_domain_support_h2(sni, server=None):
    try:

        context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
        context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
        context.options |= ssl.OP_NO_COMPRESSION
        context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20")
        context.set_alpn_protocols(["h2"])
        start_time = time.monotonic()
        with socket.create_connection((server or sni, 443), timeout=2) as sock:

            with context.wrap_socket(sock, server_hostname=sni) as ssock:
                elapsed_time = time.monotonic() - start_time
                valid = ssock.version() == "TLSv1.3"
                if valid:
                    return int(max(1, elapsed_time*1000))
                return False
    except Exception as e:
        print(f'{domain} {e}')
        return False


def is_domain_reality_friendly(domain):
    return is_domain_support_h2(domain)


def debug_flash_if_not_in_the_same_asn(domain):
    from hiddifypanel.panel.clean_ip import ipasn
    ipv4 = get_ip(4)
    dip = get_domain_ip(domain)
    try:
        if ipasn:
            asn_ipv4 = ipasn.get(ipv4)
            asn_dip = ipasn.get(dip)
            # country_ipv4= ipcountry.get(ipv4)
            # country_dip= ipcountry.get(dip)
            if asn_ipv4.get('autonomous_system_organization') != asn_dip.get('autonomous_system_organization'):
                flash(_("selected domain for REALITY is not in the same ASN. To better use of the protocol, it is better to find a domain in the same ASN.") +
                      f"<br> Server ASN={asn_ipv4.get('autonomous_system_organization','unknown')}<br>{domain}_ASN={asn_dip.get('autonomous_system_organization','unknown')}", "warning")
    except:
        pass


def fallback_domain_compatible_with_servernames(fallback_domain, servername):
    return is_domain_support_h2(servername, fallback_domain)


def generate_x25519_keys():
    # Run the "xray x25519" command and capture its output
    try:
        cmd = "xray x25519"
        output = subprocess.check_output(cmd, shell=True, text=True)
    except:
        output = """
        Private key: ILnwK6Ii9PWgnkq5Lbb8G_chyP4ba5cGRpZbaJjf7lg
        Public key: no36JbbL8uPH4VT2PNe9husJBN2mu5DbgDASH7hK32A
        """
        # Extract the private and public keys from the output
    private_key = output.split("Private key: ")[1].split("\n")[0]
    public_key = output.split("Public key: ")[1].split("\n")[0]

    # Return the keys as a tuple
    return {"private_key": private_key, "public_key": public_key}


def get_hostkeys(dojson=False):
    key_files = glob.glob(current_app.config['HIDDIFY_CONFIG_PATH'] + "/other/ssh/host_key/*_key.pub")
    host_keys = []
    for file_name in key_files:
        with open(file_name, "r") as f:
            host_key = f.read().strip()
            host_key = host_key.split()
            if len(host_key) > 2:
                host_key = host_key[:2]  # strip the hostname part
            host_key = " ".join(host_key)
            host_keys.append(host_key)
    if dojson:
        return json.dumps(host_keys)
    return host_keys


def get_ssh_client_version(user):
    return 'SSH-2.0-OpenSSH_7.4p1'


def get_ed25519_private_public_pair():
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    privkey = ed25519.Ed25519PrivateKey.generate()
    pubkey = privkey.public_key()
    priv_bytes = privkey.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_bytes = pubkey.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )
    return priv_bytes.decode(), pub_bytes.decode()


def do_base_64(str):
    import base64
    resp = base64.b64encode(f'{str}'.encode("utf-8"))
    return resp.decode()


def get_user_agent():
    ua = __parse_user_agent(request.user_agent.string)

    if ua.get('v', 1) < 3:
        __parse_user_agent.invalidate_all()
        ua = __parse_user_agent(request.user_agent.string)
    return ua


ua_version_pattern = re.compile(r'/(\d+\.\d+(\.\d+)?)')


@cache.cache()
def __parse_user_agent(ua):
    # Example: SFA/1.8.0 (239; sing-box 1.8.0)
    # Example: SFA/1.7.0 (239; sing-box 1.7.0)
    # Example: HiddifyNext/0.13.6 (android) like ClashMeta v2ray sing-box

    uaa = user_agents.parse(request.user_agent.string)

    match = re.search(ua_version_pattern, request.user_agent.string)
    generic_version = list(map(int, match.group(1).split('.'))) if match else [0, 0, 0]
    res = {}
    res['v'] = 3
    res["is_bot"] = uaa.is_bot
    res["is_browser"] = re.match('^Mozilla', ua, re.IGNORECASE) and True
    res['os'] = uaa.os.family
    res['os_version'] = uaa.os.version
    res['is_clash'] = re.match('^(Clash|Stash)', ua, re.IGNORECASE) and True
    res['is_clash_meta'] = re.match('^(Clash-verge|Clash-?Meta|Stash|NekoBox|NekoRay|Pharos|hiddify-desktop)', ua, re.IGNORECASE) and True
    res['is_singbox'] = re.match('^(HiddifyNext|Dart|SFI|SFA)', ua, re.IGNORECASE) and True
    res['is_hiddify'] = re.match('^(HiddifyNext)', ua, re.IGNORECASE) and True

    if (res['is_singbox']):
        res['singbox_version'] = generic_version

    if ['is_hiddify']:
        res['hiddify_version'] = generic_version
        if generic_version[0] == 0 and generic_version[1] <= 14:
            res['singbox_version'] = [1, 7, 0]
        else:
            res['singbox_version'] = [1, 8, 0]

    res['is_v2ray'] = re.match('^(Hiddify|FoXray|Fair|v2rayNG|SagerNet|Shadowrocket|V2Box|Loon|Liberty)', ua, re.IGNORECASE) and True

    if res['os'] == 'Other':
        if re.match('^(FoXray|Fair|Shadowrocket|V2Box|Loon|Liberty)', ua, re.IGNORECASE):
            res['os'] = 'iOS'
            # res['os_version']

    for a in ['Hiddify', 'FoXray', 'Fair', 'v2rayNG', 'SagerNet', 'Shadowrocket', 'V2Box', 'Loon', 'Liberty', 'Clash', 'Meta', 'Stash', 'SFI', 'SFA', 'HiddifyNext']:
        if a.lower() in ua.lower():
            res['app'] = a
    if res["is_browser"]:
        res['app'] = uaa.browser.family
    return res


def url_encode(strr):
    import urllib.parse
    return urllib.parse.quote(strr)


def error(str):
    import sys
    print(str, file=sys.stderr)


def static_url_for(**values):
    orig = url_for("static", **values)
    return orig.split("user_secret")[0]


def get_latest_release_version(repo_name):
    try:
        url = f"https://github.com/hiddify/{repo_name}/releases/latest"
        response = requests.head(url, allow_redirects=False)

        location_header = response.headers.get("Location")
        if location_header:
            version = re.search(r"/([^/]+)/?$", location_header)
            if version:
                return version.group(1).replace('v', '')
    except Exception as e:
        return f'{e}'

    return None
