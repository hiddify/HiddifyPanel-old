import glob
import user_agents
import json
import subprocess
import psutil
from typing import Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from flask import current_app, g, jsonify, request
from flask_babelex import gettext as __
from flask_babelex import lazy_gettext as _
from wtforms.validators import ValidationError
from apiflask import abort as apiflask_abort
from apiflask import abort

from datetime import timedelta
from babel.dates import format_timedelta as babel_format_timedelta

from hiddifypanel.cache import cache
from hiddifypanel.models import *
from hiddifypanel.panel.database import db
from hiddifypanel.hutils.utils import *
from hiddifypanel.Events import domain_changed
from hiddifypanel import hutils
from hiddifypanel.panel.run_commander import commander, Command

to_gig_d = 1000*1000*1000


def add_temporary_access():
    random_port = random.randint(30000, 50000)
    # exec_command(
    #     f'sudo /opt/hiddify-manager/hiddify-panel/temporary_access.sh {random_port} &')

    # run temporary_access.sh
    commander(Command.temporary_access, port=random_port)
    temp_admin_link = f"http://{hutils.ip.get_ip(4)}:{random_port}{get_admin_path()}"
    g.temp_admin_link = temp_admin_link


# with user panel url format we don't really need this function
def add_short_link(link: str, period_min: int = 5) -> Tuple[str, int]:
    short_code, expire_date = add_short_link_imp(link, period_min)
    return short_code, (expire_date - datetime.now()).seconds


@cache.cache(ttl=300)
# TODO: Change ttl dynamically
def add_short_link_imp(link: str, period_min: int = 5) -> Tuple[str, datetime]:
    # pattern = "\^/([^/]+)(/)?\?\$\ {return 302 " + re.escape(link) + ";}"

    pattern = r"([^/]+)\("

    with open(current_app.config['HIDDIFY_CONFIG_PATH']+"/nginx/parts/short-link.conf", 'r') as f:
        for line in f:
            if link in line:
                return re.search(pattern, line).group(1), datetime.now() + timedelta(minutes=period_min)

    short_code = get_random_string(6, 10).lower()
    # exec_command(
    #     f'sudo /opt/hiddify-manager/nginx/add2shortlink.sh {link} {short_code} {period_min} &')

    commander(Command.temporary_short_link, url=link, slug=short_code, period=period_min)

    return short_code, datetime.now() + timedelta(minutes=period_min)


def get_admin_path():
    proxy_path = hconfig(ConfigEnum.proxy_path_admin)
    # admin_secret = g.account.uuid or get_super_admin_secret()
    return (f"/{proxy_path}/admin/")


def exec_command(cmd, cwd=None):
    try:
        subprocess.Popen(cmd.split(" "))  # run in background
    except Exception as e:
        print(e)


def user_auth(function):
    def wrapper(*args, **kwargs):
        if g.account.uuid == None:
            return jsonify({"error": "auth failed"})
        if not g.account:
            return jsonify({"error": "user not found"})
        if g.account and g.is_admin:
            return jsonify({"error": "admin can not access user page. add /admin/ to your url"})
        return function()

    return wrapper


def super_admin(function):
    def wrapper(*args, **kwargs):
        if g.account.mode not in [AdminMode.super_admin]:
            abort(403, __("Access Denied"))
            # return jsonify({"error": "auth failed"})
        return function(*args, **kwargs)

    return wrapper


def admin(function):
    def wrapper(*args, **kwargs):
        if g.account.mode not in [AdminMode.admin, AdminMode.super_admin]:
            abort(403, __("Access Denied"))
            # return jsonify({"error": "auth failed"})

        return function(*args, **kwargs)
    return wrapper


def api_v1_auth(function):
    def wrapper(*args, **kwargs):
        a_uuid = kwargs.get('admin_uuid')
        if not a_uuid or a_uuid != AdminUser.get_super_admin_uuid():
            apiflask_abort(403, 'invalid request')
        return function(*args, **kwargs)
    return wrapper


def current_account_api_key():
    # TODO: send real apikey
    return g.account.uuid


def current_account_user_pass() -> Tuple[str, str]:
    return g.account.username, g.account.password


def is_api_call(req_path: str) -> bool:
    return 'api/v1/' in req_path or 'api/v2/' in req_path


def is_user_api_call() -> bool:
    if request.blueprint and (request.blueprint == 'api_user' or request.blueprint == 'api_user_uuid'):
        return True
    user_api_call_format = '/api/v2/user/'
    if user_api_call_format in request.path:
        return True
    return False


def is_admin_api_call() -> bool:
    if request.blueprint and (request.blueprint == 'api_admin' or request.blueprint == 'api_admin_uuid' or request.blueprint == 'api_v1'):
        return True
    admin_api_call_format = '/api/v2/admin/'
    if admin_api_call_format in request.path:
        return True
    return False


def is_user_panel_call(deprecated_format=False) -> bool:
    if request.blueprint and request.blueprint == 'client':
        return True
    if deprecated_format:
        user_panel_url = f'/{hconfig(ConfigEnum.proxy_path)}/'
    else:
        user_panel_url = f'/{hconfig(ConfigEnum.proxy_path_client)}/'
    if f'{request.path}'.startswith(user_panel_url) and "admin" not in f'{request.path}':
        return True
    return False


def is_admin_panel_call(deprecated_format: bool = False) -> bool:
    if request.blueprint and request.blueprint == 'admin':
        return True
    if deprecated_format:
        if f'{request.path}'.startswith(f'/{hconfig(ConfigEnum.proxy_path)}/') and "admin" in f'{request.path}':
            return True
    elif f'{request.path}'.startswith(f'/{hconfig(ConfigEnum.proxy_path_admin)}/admin/'):
        return True
    return False


def is_api_v1_call(endpoint=None) -> bool:
    if (request.blueprint and 'api_v1' in request.blueprint):
        return True
    elif endpoint and 'api_v1' in endpoint:
        return True
    elif request.endpoint and 'api_v1' in request.endpoint:
        return True

    api_v1_path = f'{request.host}/{hconfig(ConfigEnum.proxy_path_admin)}/api/v1/{AdminUser.get_super_admin_uuid()}/'
    if f'{request.host}{request.path}'.startswith(api_v1_path):
        return True
    return False


def is_telegram_call() -> bool:
    if request.endpoint and (request.endpoint == 'tgbot' or request.endpoint == 'send_msg'):
        return True
    if request.blueprint and request.blueprint == 'api_v1' and ('tgbot' in request.path or 'send_msg' in request.path):
        return True
    if '/tgbot/' in request.path or 'send_msg/' in request.path:
        return True
    return False


def is_admin_home_call() -> bool:
    admin_home = f'{request.host}/{hconfig(ConfigEnum.proxy_path_admin)}/admin/'
    if f'{request.host}{request.path}' == admin_home:
        return True
    return False


def is_login_call() -> bool:
    # print(request.blueprint)
    return request.blueprint == 'common_bp'
    # base_path = f'{request.host}'
    # requested_url = f'{request.host}{request.path}'
    # if requested_url == f'{base_path}/{hconfig(ConfigEnum.proxy_path_admin)}/' or requested_url == f'{base_path}/{hconfig(ConfigEnum.proxy_path_client)}/':
    #     return True
    # return False


def is_admin_role(role: Role):
    if role in {Role.super_admin, Role.admin, Role.agent}:
        return True
    return False


def is_admin_proxy_path() -> bool:
    proxy_path = g.get('proxy_path', None) or get_proxy_path_from_url(request.url)
    return proxy_path == hconfig(ConfigEnum.proxy_path_admin)


def is_client_proxy_path() -> bool:
    proxy_path = g.get('proxy_path', None) or get_proxy_path_from_url(request.url)
    return proxy_path == hconfig(ConfigEnum.proxy_path_client)


def proxy_path_validator(proxy_path):
    # DEPRECATED PROXY_PATH HANDLED BY BACKWARD COMPATIBILITY MIDDLEWARE
    # does not nginx handle proxy path validation?

    if not proxy_path:
        return apiflask_abort(400, 'invalid request')

    dbg_mode = True if current_app.config['DEBUG'] else False
    admin_proxy_path = hconfig(ConfigEnum.proxy_path_admin)
    client_proxy_path = hconfig(ConfigEnum.proxy_path_client)
    deprecated_path = hconfig(ConfigEnum.proxy_path)
    if proxy_path == deprecated_path:
        return

    if proxy_path not in [admin_proxy_path, deprecated_path, client_proxy_path]:
        abort(400, 'invalid request')

    if is_admin_panel_call() and proxy_path != admin_proxy_path:
        abort(400, 'invalid request')
    if is_user_panel_call() and proxy_path != client_proxy_path:
        abort(400, 'invalid request')

    if is_api_call(request.path):
        if is_admin_api_call() and proxy_path != admin_proxy_path:
            return apiflask_abort(400, Markup(f"Invalid Proxy Path <a href=/{admin_proxy_path}/admin>Admin Panel</a>")) if dbg_mode else abort(400, 'invalid request')
        if is_user_api_call() and proxy_path != client_proxy_path:
            return apiflask_abort(400, Markup(f"Invalid Proxy Path <a href=/{client_proxy_path}/admin>User Panel</a>")) if dbg_mode else abort(400, 'invalid request')


def asset_url(path) -> str:
    return f"/{g.proxy_path}/{path}"


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
    #     if user.is_active:
    #         xray_api.add_client(user.uuid)
    #     else:
    #         xray_api.remove_client(user.uuid)

    # exec_command("sudo /opt/hiddify-manager/install.sh apply_users --no-gui")

    # run install.sh apply_users
    commander(Command.apply_users)

    # time.sleep(1)
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


def check_connection_to_remote(api_url):

    path = f"{api_url}/api/v1/hello/"

    try:
        res = requests.get(path, verify=False, timeout=2).json()
        return True

    except:
        return False


def check_connection_for_domain(domain):

    proxy_path = hconfig(ConfigEnum.proxy_path_admin)
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
                print(f"http://{hutils.ip.get_domain_ip(domain)}/{path}")
                res = requests.get(
                    f"http://{hutils.ip.get_domain_ip(domain)}/{path}", verify=False, timeout=10).json()
                return res['status'] == 200
            except:
                return False
    return True


def get_user_link(uuid, domain, mode='', username=''):
    is_cdn = domain.mode == DomainType.cdn if type(domain) == Domain else False
    res = ""
    if mode == "multi":
        res += "<div class='btn-group'>"
    d = domain.domain
    if "*" in d:
        d = d.replace("*", get_random_string(5, 15))
    proxy_path = hconfig(ConfigEnum.proxy_path_admin) if mode == 'admin' else hconfig(ConfigEnum.proxy_path_client)
    # account = AdminUser.query.filter(AdminUser.uuid == uuid).first() if mode == 'admin' else User.query.filter(User.uuid == uuid).first()
    # link = f"https://{account.username}:{account.password}@{d}/{proxy_path}/admin/#{username}" if mode == 'admin' else f"https://{account.username}:{account.password}@{d}/{proxy_path}/#{username}"
    link = f"https://{d}/{proxy_path}/{uuid}/#{username}"

    # if mode == 'new':
    #     link = f"{link}new"
    text = domain.alias or domain.domain
    color_cls = 'info'

    if type(domain) == Domain and not domain.sub_link_only and domain.mode in [DomainType.cdn, DomainType.auto_cdn_ip]:
        auto_cdn = (domain.mode == DomainType.auto_cdn_ip) or (domain.cdn_ip and "MTN" in domain.cdn_ip)
        color_cls = "success" if auto_cdn else 'warning'
        text = f'<span class="badge badge-secondary" >{"Auto" if auto_cdn else "CDN"}</span> '+text

    res += f"<a target='_blank' data-copy='{link}' href='{link}' class='btn btn-xs btn-{color_cls} ltr copy-link' ><i class='fa-solid fa-arrow-up-right-from-square d-none'></i> {text}</a>"

    return res


def validate_domain_exist(form, field):
    domain = field.data
    if not domain:
        return
    dip = hutils.ip.get_domain_ip(domain)
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
    if unique_id is None or unique_id == "default":
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


def set_db_from_json(json_data, override_child_id=None, set_users=True, set_domains=True, set_proxies=True, set_settings=True, remove_domains=False, remove_users=False,
                     override_unique_id=True, set_admins=True, override_root_admin=False, replace_owner_admin=False, fix_admin_hierarchy=True):
    new_rows = []

    uuids_without_parent = get_ids_without_parent({u['uuid']: u for u in json_data['admin_users']})
    print('uuids_without_parent===============', uuids_without_parent)
    if replace_owner_admin and len(uuids_without_parent):
        new_owner_uuid = uuids_without_parent[0]
        old_owner = AdminUser.query.filter(AdminUser.id == 1).first()
        old_uuid_admin = AdminUser.query.filter(AdminUser.uuid == new_owner_uuid).first()
        if old_owner and not old_uuid_admin:
            old_owner.uuid = new_owner_uuid
            db.session.commit()

    all_admins = {u.uuid: u for u in AdminUser.query.all()}
    uuids_without_parent = [uuid for uuid in uuids_without_parent if uuid not in all_admins]
    print('uuids_not admin exist===============', uuids_without_parent)

    if "admin_users" in json_data:
        for u in json_data['admin_users']:
            if override_root_admin and u['uuid'] in uuids_without_parent:
                u['uuid'] = AdminUser.current_admin_or_owner().uuid
            if u['parent_admin_uuid'] in uuids_without_parent:
                u['parent_admin_uuid'] = AdminUser.current_admin_or_owner().uuid
        # fix admins hierarchy
        if fix_admin_hierarchy and len(json_data['admin_users']) > 2:
            hierarchy_is_ok = False
            for u in json_data['admin_users']:
                if u['uuid'] == AdminUser.current_admin_or_owner().uuid:
                    continue
                if u['parent_admin_uuid'] == AdminUser.current_admin_or_owner().uuid:
                    hierarchy_is_ok = True
                    break
            if not hierarchy_is_ok:
                json_data['admin_users'][1]['parent_admin_uuid'] = AdminUser.current_admin_or_owner().uuid

    if "users" in json_data and override_root_admin:
        for u in json_data['users']:
            if u['added_by_uuid'] in uuids_without_parent:
                u['added_by_uuid'] = AdminUser.current_admin_or_owner().uuid

    if set_admins and 'admin_users' in json_data:
        AdminUser.bulk_register(json_data['admin_users'], commit=False)
    if set_users and 'users' in json_data:
        User.bulk_register(json_data['users'], commit=False, remove=remove_users)
    if set_domains and 'domains' in json_data:
        bulk_register_domains(json_data['domains'], commit=False, remove=remove_domains, override_child_id=override_child_id)
    if set_domains and 'parent_domains' in json_data:
        bulk_register_parent_domains(json_data['parent_domains'], commit=False, remove=remove_domains)
    if set_settings and 'hconfigs' in json_data:
        bulk_register_configs(json_data["hconfigs"], commit=True, override_child_id=override_child_id, override_unique_id=override_unique_id)
        if 'proxies' in json_data:
            bulk_register_proxies(json_data['proxies'], commit=False, override_child_id=override_child_id)

    ids_without_parent = get_ids_without_parent({u.id: u.to_dict() for u in AdminUser.query.all()})
    owner = AdminUser.get_super_admin()
    ids_without_parent = [id for id in ids_without_parent if id != owner.id]

    for u in AdminUser.query.all():
        if u.parent_admin_id in ids_without_parent:
            u.parent_admin_id = owner.id
    # for u in User.query.all():
    #     if u.added_by in uuids_without_parent:
    #         u.added_by = g.account.id

    db.session.commit()


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

    hiddify_used = get_folder_size('/opt/hiddify-manager/') / 1024**3

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
    from hiddifypanel.hutils.auto_ip_selector import ipasn
    ipv4 = hutils.ip.get_ip(4)
    dip = hutils.ip.get_domain_ip(domain)
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
    priv = x25519.X25519PrivateKey.generate()
    pub = priv.public_key()
    priv_bytes = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    import base64
    pub_str = base64.urlsafe_b64encode(pub_bytes).decode()[:-1]
    priv_str = base64.urlsafe_b64encode(priv_bytes).decode()[:-1]

    return {'private_key': priv_str, 'public_key': pub_str}


def get_random_decoy_domain():
    for i in range(10):
        domains = get_random_domains(10)
        for d in domains:
            if is_domain_use_letsencrypt(d):
                return d

    return "bbc.com"


def is_domain_use_letsencrypt(domain):
    """
    This function is used to filter the payment and big companies to 
    avoid phishing detection
    """
    import ssl
    import socket

    # Create a socket connection to the website
    with socket.create_connection((domain, 443)) as sock:
        context = ssl.create_default_context()
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            certificate = ssock.getpeercert()

    issuer = dict(x[0] for x in certificate.get("issuer", []))

    return issuer['organizationName'] == "Let's Encrypt"


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
    return __parse_user_agent(request.user_agent.string)


@cache.cache()
def __parse_user_agent(ua):
    uaa = user_agents.parse(request.user_agent.string)
    res = {}
    res["is_browser"] = re.match('^Mozilla', ua, re.IGNORECASE) and True
    res['os'] = uaa.os.family
    res['os_version'] = uaa.os.version
    res['is_clash'] = re.match('^(Clash|Stash)', ua, re.IGNORECASE) and True
    res['is_clash_meta'] = re.match('^(Clash-verge|Clash-?Meta|Stash|NekoBox|NekoRay|Pharos|hiddify-desktop)', ua, re.IGNORECASE) and True
    res['is_singbox'] = re.match('^(HiddifyNext|Dart|SFI|SFA)', ua, re.IGNORECASE) and True
    if (res['is_singbox']):
        res['singbox_version'] = (1, 4, 0)
    res['is_hiddify'] = re.match('^(HiddifyNext)', ua, re.IGNORECASE) and True
    if ['is_hiddify']:
        res['hiddify_version'] = uaa
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


def is_ssh_password_authentication_enabled():
    if os.path.isfile('/etc/ssh/sshd_config'):
        content = ''
        with open('/etc/ssh/sshd_config', 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith('#'):
                    continue
                if re.search("^PasswordAuthentication\s+no", line, re.IGNORECASE):
                    return False

    return True


@cache.cache(ttl=300)
def get_direct_host_or_ip(prefer_version: int):
    direct = Domain.query.filter(Domain.mode == DomainType.direct, Domain.sub_link_only == False).first()
    if not (direct):
        direct = Domain.query.filter(Domain.mode == DomainType.direct).first()
    if direct:
        direct = direct.domain
    else:
        direct = hutils.ip.get_ip(prefer_version)
    if not direct:
        direct = hutils.ip.get_ip(socket.AF_INET if prefer_version == socket.AF_INET6 else socket.AF_INET6)
    return direct
