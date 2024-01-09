from flask import g, request, render_template
import enum
from hiddifypanel.models import *
import yaml
import json
from hiddifypanel.panel import hiddify
import random
import re
import datetime
from flask_babelex import gettext as _


def all_proxies(child_id=0):
    all_proxies = hiddify.get_available_proxies(child_id)
    all_proxies = [p for p in all_proxies if p.enable]
    # all_cfg=Proxy.query.filter(Proxy.enable==True).all()
    # if not hconfig(ConfigEnum.domain_fronting_domain):
    #     all_cfg=[c for c in all_cfg if 'Fake' not in c.cdn]
    # if not g.is_cdn:
    #     all_cfg=[c for c in all_cfg if 'CDN' not in c.cdn]
    # if not hconfig(ConfigEnum.ssfaketls_enable):
    #     all_cfg=[c for c in all_cfg if 'faketls' not in c.transport and 'v2ray' not in c.proto]
    # if not hconfig(ConfigEnum.vmess_enable):
    #     all_cfg=[c for c in all_cfg if 'vmess' not in c.proto]

    return all_proxies


def proxy_info(name, mode="tls"):
    return "error"


def pbase64(full_str):
    return full_str
    str = full_str.split("vmess://")[1]
    import base64
    resp = base64.b64encode(f'{str}'.encode("utf-8"))
    return "vmess://"+resp


def make_proxy(proxy: Proxy, domain_db: Domain, phttp=80, ptls=443, pport=None):
    def is_tls():
        return 'tls' in l3 or "reality" in l3
    if type(phttp) == str:
        phttp = int(phttp) if phttp != "None" else None
    if type(ptls) == str:
        ptls = int(ptls) if ptls != "None" else None
    l3 = proxy.l3

    domain = domain_db.domain

    child_id = domain_db.child_id
    hconfigs = get_hconfigs(child_id)
    port = 0

    if is_tls():
        port = ptls
    elif l3 == "http":
        port = phttp
    elif l3 == "kcp":
        port = hconfigs[ConfigEnum.kcp_ports].split(",")[0]
    elif l3 == "tuic":
        port = hconfigs[ConfigEnum.tuic_port].split(",")[0]
    elif l3 == 'ssh':
        port = hconfigs[ConfigEnum.ssh_server_port]
    if pport:
        port = pport

    name = proxy.name
    if not port:
        return {'name': name, 'msg': "port not defined", 'type': 'error', 'proto': proxy.proto}
    if "reality" not in l3 and domain_db.mode == DomainType.reality:
        return {'name': name, 'msg': "reality proxy not in reality domain", 'type': 'debug', 'proto': proxy.proto}

    if "reality" in l3 and domain_db.mode != DomainType.reality:
        return {'name': name, 'msg': "reality proxy not in reality domain", 'type': 'debug', 'proto': proxy.proto}

    if "reality" in l3 and domain_db.grpc and ProxyTransport.grpc != proxy.transport:
        return {'name': name, 'msg': "reality proxy not in reality domain", 'type': 'debug', 'proto': proxy.proto}

    if "reality" in l3 and (not domain_db.grpc) and ProxyTransport.grpc == proxy.transport:
        return {'name': name, 'msg': "reality proxy not in reality domain", 'type': 'debug', 'proto': proxy.proto}

    is_cdn = ProxyCDN.CDN in proxy.cdn
    if is_cdn and domain_db.mode not in [DomainType.cdn, DomainType.auto_cdn_ip, DomainType.worker]:
        # print("cdn proxy not in cdn domain", domain, name)
        return {'name': name, 'msg': "cdn proxy not in cdn domain", 'type': 'debug', 'proto': proxy.proto}
    if not is_cdn and domain_db.mode in [DomainType.cdn, DomainType.auto_cdn_ip, DomainType.worker]:
        # print("not cdn proxy  in cdn domain", domain, name, proxy.cdn)
        return {'name': name, 'msg': "not cdn proxy  in cdn domain", 'type': 'debug', 'proto': proxy.proto}
    if domain_db.mode == DomainType.worker and proxy.transport == ProxyTransport.grpc:
        return {'name': name, 'msg': "worker does not support grpc", 'type': 'debug', 'proto': proxy.proto}
    cdn_forced_host = domain_db.cdn_ip or (domain_db.domain if domain_db.mode != DomainType.reality else hiddify.get_direct_host_or_ip(4))

    if 'reality' in proxy.l3:
        alpn = "h2" if proxy.transport in ['h2'] else 'http/1.1'
    else:
        alpn = "h2" if proxy.l3 in ['tls_h2'] else 'h2,http/1.1' if proxy.l3 == 'tls_h2_h1' else "http/1.1"

    base = {
        'name': name,
        'cdn': is_cdn,
        'mode': "CDN" if is_cdn else "direct",
        'l3': l3,
        'host': domain,
        'port': port,
        'server': cdn_forced_host,
        'sni': domain_db.servernames if is_cdn and domain_db.servernames else domain,
        'uuid': str(g.user_uuid),
        'proto': proxy.proto,
        'transport': proxy.transport,
        'proxy_path': hconfigs[ConfigEnum.proxy_path],
        'alpn': alpn,
        'extra_info': f'{domain_db.alias or domain}',
        'fingerprint': hconfigs[ConfigEnum.utls],
        'allow_insecure': domain_db.mode == DomainType.fake or "Fake" in proxy.cdn,
        'dbe': proxy,
        'dbdomain': domain_db
    }

    if base["proto"] == "trojan" and not is_tls():
        return {'name': name, 'msg': "trojan but not tls", 'type': 'warning', 'proto': proxy.proto}

    if l3 == "http" and ProxyTransport.XTLS in proxy.transport:
        return {'name': name, 'msg': "http and xtls???", 'type': 'warning', 'proto': proxy.proto}
    if l3 == "http" and base["proto"] in ["ss", "ssr"]:
        return {'name': name, 'msg': "http and ss or ssr???", 'type': 'warning', 'proto': proxy.proto}

    if proxy.proto in ProxyProto.vmess:
        base['cipher'] = "chacha20-poly1305"

    if l3 in ['reality']:
        base['reality_short_id'] = random.sample(hconfigs[ConfigEnum.reality_short_ids].split(','), 1)[0]
        # base['flow']="xtls-rprx-vision"
        base['reality_pbk'] = hconfigs[ConfigEnum.reality_public_key]
        if (domain_db.servernames):
            all_servernames = re.split('[ \t\r\n;,]+', domain_db.servernames)
            base['sni'] = random.sample(all_servernames, 1)[0]
            if hconfigs[ConfigEnum.core_type] == "singbox":
                base['sni'] = all_servernames[0]
        else:
            base['sni'] = domain_db.domain

        del base['host']
        if base.get('fingerprint', 'none') != 'none':
            base['fingerprint'] = hconfigs[ConfigEnum.utls]
        # if not domain_db.cdn_ip:
        #     base['server']=hiddify.get_domain_ip(base['server'])

    if "Fake" in proxy.cdn:
        if not hconfigs[ConfigEnum.domain_fronting_domain]:
            return {'name': name, 'msg': "no domain_fronting_domain", 'type': 'debug', 'proto': proxy.proto}
        if l3 == "http" and not hconfigs[ConfigEnum.domain_fronting_http_enable]:
            return {'name': name, 'msg': "no http in domain_fronting_domain", 'type': 'debug', 'proto': proxy.proto}
        if l3 == "tls" and not hconfigs[ConfigEnum.domain_fronting_tls_enable]:
            return {'name': name, 'msg': "no tls in domain_fronting_domain", 'type': 'debug', 'proto': proxy.proto}
        base['server'] = hconfigs[ConfigEnum.domain_fronting_domain]
        base['sni'] = hconfigs[ConfigEnum.domain_fronting_domain]
        # base["host"]=domain
        base['mode'] = 'Fake'

    elif l3 == "http" and not hconfigs[ConfigEnum.http_proxy_enable]:
        return {'name': name, 'msg': "http but http is disabled ", 'type': 'debug', 'proto': proxy.proto}
    path = {
        'vless': f'{hconfigs[ConfigEnum.path_vless]}',
        'trojan': f'{hconfigs[ConfigEnum.path_trojan]}',
        'vmess': f'{hconfigs[ConfigEnum.path_vmess]}',
        'ss': f'{hconfigs[ConfigEnum.path_ss]}',
        'v2ray': f'{hconfigs[ConfigEnum.path_ss]}'
    }

    if base["proto"] in ['v2ray', 'ss', 'ssr']:
        base['cipher'] = 'chacha20-ietf-poly1305'
        if "shadowtls" not in proxy.transport:
            base['uuid'] = f'{hconfigs[ConfigEnum.shared_secret]}'

    if base["proto"] == "ssr":
        base["ssr-obfs"] = "tls1.2_ticket_auth"
        base["ssr-protocol"] = "auth_sha1_v4"
        base["fakedomain"] = hconfigs[ConfigEnum.ssr_fakedomain]
        base["mode"] = "FakeTLS"
        return base
    elif "faketls" in proxy.transport:
        base['fakedomain'] = hconfigs[ConfigEnum.ssfaketls_fakedomain]
        base['mode'] = 'FakeTLS'
        return base
    elif "shadowtls" in proxy.transport:

        base['fakedomain'] = hconfigs[ConfigEnum.shadowtls_fakedomain]
        base['mode'] = 'ShadowTLS'
        return base

    if ProxyTransport.XTLS in proxy.transport:
        base['flow'] = 'xtls-rprx-vision'
        return {**base, 'transport': 'tcp'}
    if "tcp" in proxy.transport:
        base['transport'] = 'tcp'
        base['path'] = f'/{path[base["proto"]]}{hconfigs[ConfigEnum.path_tcp]}'
        return base
    if proxy.transport in ["ws", "WS"]:
        base['transport'] = 'ws'
        base['path'] = f'/{path[base["proto"]]}{hconfigs[ConfigEnum.path_ws]}'
        base["host"] = domain
        return base

    if proxy.transport == "grpc":
        base['transport'] = 'grpc'
        # base['grpc_mode'] = "multi" if hconfigs[ConfigEnum.core_type]=='xray' else 'gun'
        base['grpc_mode'] = 'gun'
        base['grpc_service_name'] = f'{path[base["proto"]]}{hconfigs[ConfigEnum.path_grpc]}'
        base['path'] = base['grpc_service_name']
        return base

    if "h1" in proxy.transport:
        base['transport'] = 'tcp'
        base['alpn'] = 'http/1.1'
        return base
    if ProxyProto.ssh == proxy.proto:
        base['private_key'] = g.user.ed25519_private_key
        base['host_key'] = hiddify.get_hostkeys(False)
        # base['ssh_port'] = hconfig(ConfigEnum.ssh_server_port)
        return base
    return {'name': name, 'msg': 'not valid', 'type': 'error', 'proto': proxy.proto}


def to_link(proxy):
    if 'error' in proxy:
        return proxy
    orig_name_link = (proxy['extra_info'] + " " + proxy["name"]).strip()
    name_link = hiddify.url_encode(orig_name_link)
    if proxy['proto'] == 'vmess':
        # print(proxy)
        vmess_type = None
        if proxy["transport"] == 'tcp':
            vmess_type = 'http'
        if 'grpc_mode' in proxy:
            vmess_type = proxy['grpc_mode']
        vmess_data = {"v": "2",
                      "ps": orig_name_link,
                      "add": proxy['server'],
                      "port": proxy['port'],
                      "id": proxy["uuid"],
                      "aid": 0,
                      "scy": proxy['cipher'],
                      "net": proxy["transport"],
                      "type": vmess_type or "none",
                      "host": proxy.get("host", ""),
                      "alpn": proxy.get("alpn", "h2,http/1.1"),
                      "path": proxy["path"] if "path" in proxy else "",
                      "tls": "tls" if "tls" in proxy["l3"] else "",
                      "sni": proxy["sni"],
                      "fp": proxy["fingerprint"]
                      }
        if 'reality' in proxy["l3"]:
            vmess_data['tls'] = "reality"
            vmess_data['pbk'] = proxy['reality_pbk']
            vmess_data['sid'] = proxy['reality_short_id']

        return "vmess://" + hiddify.do_base_64(f'{json.dumps(vmess_data)}')
        # return pbase64(f'vmess://{json.dumps(vmess_data)}')
    if proxy['proto'] == 'ssh':
        strenssh = hiddify.do_base_64(f'{proxy["uuid"]}:0:{proxy["private_key"]}::@{proxy["server"]}:{proxy["port"]}')
        baseurl = f'ssh://{strenssh}#{name_link}'
        baseurl += f'\nssh://{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}/?pk='+hiddify.do_base_64(proxy["private_key"])+f"&hk={hiddify.get_hostkeys(True)}#{name_link}"

        return baseurl
    if proxy['proto'] == "ssr":
        baseurl = f'ssr://{proxy["cipher"]}:{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}'
        return baseurl
    if proxy['proto'] in ['ss', 'v2ray']:
        baseurl = f'ss://{proxy["cipher"]}:{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}'
        if proxy['mode'] == 'faketls':
            return f'{baseurl}?plugin=obfs-local%3Bobfs%3Dtls%3Bobfs-host%3D{proxy["fakedomain"]}%3Budp-over-tcp=true#{name_link}'
        # if proxy['mode'] == 'shadowtls':
        #     return f'{baseurl}?plugin=shadow-tls%3Bpassword%3D{proxy["proxy_path"]}%3Bhost%3D{proxy["fakedomain"]}%3Budp-over-tcp=true#{name_link}'
        if proxy['proto'] == 'v2ray':
            return f'{baseurl}?plugin=v2ray-plugin%3Bmode%3Dwebsocket%3Bpath%3D{proxy["path"]}%3Bhost%3D{proxy["host"]}%3Btls%3Budp-over-tcp=true#{name_link}'
    baseurl = f'{proxy["proto"]}://{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}?hiddify=1'
    baseurl += f'&sni={proxy["sni"]}&type={proxy["transport"]}'

    baseurl += f"&alpn={proxy['alpn']}"

    # infos+=f'&alpn={proxy["alpn"]}'
    baseurl += f'&path={proxy["path"]}' if "path" in proxy else ""
    baseurl += f'&host={proxy["host"]}' if "host" in proxy else ""
    if "grpc" == proxy["transport"]:
        baseurl += f'&serviceName={proxy["grpc_service_name"]}&mode={proxy["grpc_mode"]}'
    # print(proxy['cdn'],proxy["transport"])
    if request.args.get("fragment"):
        baseurl += f'&fragment='+request.args.get("fragment")
    if "ws" == proxy["transport"] and proxy['cdn'] and request.args.get("fragment_v1"):
        baseurl += f'&fragment_v1='+request.args.get("fragment_v1")
    if 'vless' == proxy['proto']:
        baseurl += "&encryption=none"
    if proxy.get('fingerprint', 'none') != 'none':
        baseurl += "&fp="+proxy['fingerprint']
    if proxy['l3'] != 'quic':
        baseurl += '&headerType=None'  # if not quic
    if proxy['mode'] == 'Fake' or proxy['allow_insecure']:
        baseurl += "&allowInsecure=true"
    if proxy.get('flow'):
        baseurl += f'&flow={proxy["flow"]}'

    infos = f'#{name_link}'

    if 'reality' in proxy["l3"]:
        return f"{baseurl}&security=reality&pbk={proxy['reality_pbk']}&sid={proxy['reality_short_id']}{infos}"
    if 'tls' in proxy['l3']:
        return f'{baseurl}&security=tls{infos}'
    if proxy['l3'] == 'http':
        return f'{baseurl}&security=none{infos}'
    return proxy


def to_clash_yml(proxy):
    return yaml.dump(to_clash(proxy))


def to_clash(proxy, meta_or_normal):

    name = proxy['name']
    if proxy['l3'] == "kcp":
        return {'name': name, 'msg': "clash does not support kcp", 'type': 'debug'}
    if proxy['proto'] == "ssh":
        return {'name': name, 'msg': "clash does not support ssh", 'type': 'debug'}
    if meta_or_normal == "normal":
        if proxy['proto'] == "vless":
            return {'name': name, 'msg': "vless not supported in clash", 'type': 'debug'}
        if proxy.get('flow'):
            return {'name': name, 'msg': "xtls not supported in clash", 'type': 'debug'}
        if proxy['transport'] == "shadowtls":
            return {'name': name, 'msg': "shadowtls not supported in clash", 'type': 'debug'}
    if proxy['l3'] == ProxyL3.tls_h2 and proxy['proto'] in [ProxyProto.vmess, ProxyProto.vless] and proxy['dbe'].cdn == ProxyCDN.direct:
        return {'name': name, 'msg': "bug tls_h2 vmess and vless in clash meta", 'type': 'warning'}
    base = {}
    # vmess ws
    base["name"] = f"""{proxy['extra_info']} {proxy["name"]} § {proxy['port']} {proxy["dbdomain"].id}"""
    base["type"] = str(proxy["proto"])
    base["server"] = proxy["server"]
    base["port"] = proxy["port"]
    base['alpn'] = proxy['alpn'].split(',')
    if proxy["proto"] == "ssr":
        base["cipher"] = proxy["cipher"]
        base["password"] = proxy["uuid"]
        base["udp"] = True
        base["obfs"] = proxy["ssr-obfs"]
        base["protocol"] = proxy["ssr-protocol"]
        base["obfs-param"] = proxy["fakedomain"]
        return base
    elif proxy["proto"] in ["ss", "v2ray"]:
        base["cipher"] = proxy["cipher"]
        base["password"] = proxy["uuid"]
        base["udp_over_tcp"] = True
        if proxy["transport"] == "faketls":
            base["plugin"] = "obfs"
            base["plugin-opts"] = {
                "mode": 'tls',
                "host": proxy["fakedomain"]
            }
        elif proxy["transport"] == "shadowtls":
            base["plugin"] = "shadow-tls"
            base["plugin-opts"] = {
                "host": proxy["fakedomain"],
                "password": proxy["proxy_path"],
                "version": 3  # support 1/2/3

            }

        elif proxy["proto"] == "v2ray":
            base["plugin"] = "v2ray-plugin"
            base["type"] = "ss"
            base["plugin-opts"] = {
                "mode": "websocket",
                "tls": "tls" in proxy["l3"],
                "skip-cert-verify": proxy["mode"] == "Fake" or proxy['allow_insecure'],
                "host": proxy['sni'],
                "path": proxy["path"]
            }
        return base
    elif proxy["proto"] == "trojan":
        base["password"] = proxy["uuid"]
        base["sni"] = proxy["sni"]

    else:
        base["uuid"] = proxy["uuid"]
        base["servername"] = proxy["sni"]
        base["tls"] = "tls" in proxy["l3"] or "reality" in proxy["l3"]
    if meta_or_normal == "meta":
        base['client-fingerprint'] = proxy['fingerprint']
    if proxy.get('flow'):
        base["flow"] = proxy['flow']
        # base["flow-show"] = True

    if proxy["proto"] == "vmess":
        base["alterId"] = 0
        base["cipher"] = proxy["cipher"]
    base["udp"] = True

    base["skip-cert-verify"] = proxy["mode"] == "Fake"

    base["network"] = proxy["transport"]

    if base["network"] == "ws":
        base["ws-opts"] = {
            "path": proxy["path"]
        }
        if "host" in proxy:
            base["ws-opts"]["headers"] = {"Host": proxy["host"]}

    if base["network"] == "tcp" and proxy['alpn'] != 'h2':
        if proxy['transport'] != ProxyTransport.XTLS:
            base["network"] = "http"

        if "path" in proxy:
            base["http-opts"] = {
                "path": [proxy["path"]]
            }
            if 'host' in proxy:
                base["http-opts"]["host"] = [proxy["host"]]
    if base["network"] == "tcp" and proxy['alpn'] == 'h2':
        base["network"] = "h2"

        if "path" in proxy:
            base["h2-opts"] = {
                "path": proxy["path"]
            }
            if 'host' in proxy:
                base["h2-opts"]["host"] = [proxy["host"]]
    if base["network"] == "grpc":
        base["grpc-opts"] = {
            "grpc-service-name": proxy["grpc_service_name"]
        }
    if proxy['l3'] == ProxyL3.reality:
        base["reality-opts"] = {
            "public-key": proxy['reality_pbk'],
            "short-id": proxy['reality_short_id'],
        }
        if proxy["transport"] != 'grpc':
            base["network"] = 'tcp'

    return base


def get_clash_config_names(meta_or_normal, domains):
    allp = []
    for pinfo in get_all_validated_proxies(domains):
        clash = to_clash(pinfo, meta_or_normal)
        if 'msg' not in clash:
            allp.append(clash['name'])

    return yaml.dump(allp, sort_keys=False)


def get_all_clash_configs(meta_or_normal, domains):
    allp = []
    for pinfo in get_all_validated_proxies(domains):
        clash = to_clash(pinfo, meta_or_normal)
        if 'msg' not in clash:
            allp.append(clash)

    return yaml.dump({"proxies": allp}, sort_keys=False)


def to_singbox(proxy):
    name = proxy['name']

    all_base = []
    if proxy['l3'] == "kcp":
        return {'name': name, 'msg': "clash does not support kcp", 'type': 'debug'}

    base = {}
    all_base.append(base)
    # vmess ws
    base["tag"] = f"""{proxy['extra_info']} {proxy["name"]} § {proxy['port']} {proxy["dbdomain"].id}"""
    base["type"] = str(proxy["proto"])
    base["server"] = proxy["server"]
    base["server_port"] = int(proxy["port"])
    # base['alpn'] = proxy['alpn'].split(',')
    if proxy["proto"] == "ssr":
        add_singbox_ssr(base, proxy)
        return all_base
    if proxy["proto"] in ["ss", "v2ray"]:
        add_singbox_shadowsocks_base(all_base, proxy)
        return all_base
    if proxy["proto"] == "ssh":
        add_singbox_ssh(all_base, proxy)
        return all_base
    if proxy["proto"] == "trojan":
        base["password"] = proxy["uuid"]
    elif proxy['proto'] in ['trojan', 'vmess', 'vless']:
        base["uuid"] = proxy["uuid"]
        add_singbox_multiplex(base)

    add_singbox_tls(base, proxy)

    if proxy.get('flow'):
        base["flow"] = proxy['flow']
        # base["flow-show"] = True

    if proxy["proto"] == "vmess":
        base["alter_id"] = 0
        base["security"] = proxy["cipher"]

    # base["udp"] = True
    if proxy["proto"] in ["vmess", "vless"]:
        base["packet_encoding"] = "xudp"  # udp packet encoding
    add_singbox_transport(base, proxy)

    return all_base


def add_singbox_multiplex(base):
    return
    base['multiplex'] = {
        "enabled": True,
        "protocol": "h2mux",
        "max_connections": 4,
        "min_streams": 4,
        "max_streams": 0,
        "padding": false
    }


def add_singbox_udp_over_tcp(base):
    base['udp_over_tcp'] = {
        "enabled": True,
        "version": 2
    }


def add_singbox_tls(base, proxy):
    if not ("tls" in proxy["l3"] or "reality" in proxy["l3"]):
        return
    base["tls"] = {
        "enabled": True,
        "server_name": proxy["sni"],
        "utls": {
            "enabled": True,
            "fingerprint": proxy.get('fingerprint', 'none')
        }
    }

    if "reality" in proxy["l3"]:
        base["tls"]["reality"] = {
            "enabled": True,
            "public_key": proxy['reality_pbk'],
            "short_id": proxy['reality_short_id']
        }
    base["tls"]['insecure'] = proxy['allow_insecure'] or (proxy["mode"] == "Fake")
    base["tls"]["alpn"] = proxy['alpn'].split(',')
    # base['ech'] = {
    #     "enabled": True,
    # }


def add_singbox_transport(base, proxy):
    if proxy['l3'] == 'reality':
        return
    base["transport"] = {}
    if proxy['transport'] in ["ws", "WS"]:
        base["transport"] = {
            "type": "ws",
            "path": proxy["path"],
            "early_data_header_name": "Sec-WebSocket-Protocol"
        }
        if "host" in proxy:
            base["transport"]["headers"] = {"Host": proxy["host"]}

    if proxy["transport"] in ["tcp", "h2"]:
        base["transport"] = {
            "type": "http",
            "path": proxy.get("path", ""),
            # "method": "",
            # "headers": {},
            "idle_timeout": "15s",
            "ping_timeout": "15s"
        }

        if 'host' in proxy:
            base["transport"]["host"] = [proxy["host"]]

    if proxy["transport"] == "grpc":
        base["transport"] = {
            "type": "grpc",
            "service_name": proxy["grpc_service_name"],
            "idle_timeout": "115s",
            "ping_timeout": "15s",
            # "permit_without_stream": false
        }


def add_singbox_ssr(base, proxy):

    base["method"] = proxy["cipher"]
    base["password"] = proxy["uuid"]
    # base["udp"] = True
    base["obfs"] = proxy["ssr-obfs"]
    base["protocol"] = proxy["ssr-protocol"]
    base["protocol-param"] = proxy["fakedomain"]


def add_singbox_shadowsocks_base(all_base, proxy):
    base = all_base[0]
    base["type"] = "shadowsocks"
    base["method"] = proxy["cipher"]
    base["password"] = proxy["uuid"]
    add_singbox_udp_over_tcp(base)
    add_singbox_multiplex(base)
    if proxy["transport"] == "faketls":
        base["plugin"] = "obfs-local"
        base["plugin_opts"] = f'obfs=tls&obfs-host={proxy["fakedomain"]}'
    if proxy['proto'] == 'v2ray':
        base["plugin"] = "v2ray-plugin"
        # "skip-cert-verify": proxy["mode"] == "Fake" or proxy['allow_insecure'],
        base["plugin_opts"] = f'mode=websocket&path={proxy["path"]}&host={proxy["host"]}&tls'

    if proxy["transport"] == "shadowtls":
        base['detour'] = base['tag']+"_shadowtls-out"

        shadowtls_base = {
            "type": "shadowtls",
            "tag": base['tag']+"_shadowtls-out",
            "server": base['server'],
            "server_port": base['server_port'],
            "version": 3,
            "password": proxy["proxy_path"],
            "tls": {
                "enabled": True,
                "server_name": proxy["fakedomain"],
                "utls": {
                    "enabled": True,
                    "fingerprint": proxy.get('fingerprint', 'none')
                }
            }
        }
        # add_singbox_utls(shadowtls_base)
        del base['server']
        del base['server_port']
        all_base.append(shadowtls_base)


def add_singbox_ssh(all_base, proxy):
    base = all_base[0]
    # base["client_version"]= "{{ssh_client_version}}"
    base["user"] = proxy['uuid']
    base["private_key"] = proxy['private_key']  # .replace('\n', '\\n')

    base["host_key"] = proxy.get('host_key', [])

    socks_front = {
        "type": "socks",
        "tag": base['tag']+"+UDP",
        "server": "127.0.0.1",
        "server_port": 2000,
        "version": "5",
        "udp_over_tcp": True,
        "network": "tcp",
        "detour": base['tag']
    }
    all_base.append(socks_front)


def make_full_singbox_config(domains, **kwargs):
    ua = hiddify.get_user_agent()
    # return render_template('base_singbox_config.json')
    base_config = json.loads(render_template('base_singbox_config.json'))
    allphttp = [p for p in request.args.get("phttp", "").split(',') if p]
    allptls = [p for p in request.args.get("ptls", "").split(',') if p]

    allp = []
    for d in domains:
        base_config['dns']['rules'][0]['domain'].append(d.domain)
    for pinfo in get_all_validated_proxies(domains):
        sing = to_singbox(pinfo)
        if 'msg' not in sing:
            allp += sing
    base_config['outbounds'] += allp

    select = {
        "type": "selector",
        "tag": "Select",
        "outbounds": [p['tag'] for p in allp if 'shadowtls-out' not in p['tag']],
        "default": "Auto"
    }
    select['outbounds'].insert(0, "Auto")
    base_config['outbounds'].insert(0, select)
    smart = {
        "type": "urltest",
        "tag": "Auto",
        "outbounds": [p['tag'] for p in allp if 'shadowtls-out' not in p],
        "url": "https://www.gstatic.com/generate_204",
        "interval": "10m",
        "tolerance": 200
    }
    base_config['outbounds'].insert(1, smart)
    res = json.dumps(base_config, indent=4)
    # if ua['is_hiddify']:
    #     res = res[:-1]+',"experimental": {}}'
    return res


def make_v2ray_configs(user, user_activate, domains, expire_days, ip_debug, db_domain, has_auto_cdn, asn, profile_title, **kwargs):
    res = []

    ua = hiddify.get_user_agent()
    if hconfig(ConfigEnum.show_usage_in_sublink):

        if not ua['is_hiddify']:

            fake_ip_for_sub_link = datetime.datetime.now().strftime(f"%H.%M--%Y.%m.%d.time:%H%M")
            # if ua['app'] == "Fair1":
            #     res.append(f'trojan://1@{fake_ip_for_sub_link}?sni=fake_ip_for_sub_link&security=tls#{round(user.current_usage_GB,3)}/{user.usage_limit_GB}GB_Remain:{expire_days}days')
            # else:

            # res.append(f'trojan://1@{fake_ip_for_sub_link}?sni=fake_ip_for_sub_link&security=tls#{hiddify.url_encode(profile_title)}')

            name = '⏳' if user_activate else '✖'
            if user.usage_limit_GB < 1000:
                name += f'{round(user.current_usage_GB,3)}/{user.usage_limit_GB}GB'
            elif user.usage_limit_GB < 100000:
                name += f'{round(user.current_usage_GB/1000,3)}/{round(user.usage_limit_GB/1000,1)}TB'
            else:
                res.append("#Unlimited usage")
            if expire_days < 1000:
                name += " "+_(f'📅%(expire_days)s days', expire_days=expire_days)
            else:
                res.append("#Unlimited Time")

            name = name.strip()
            if len(name) > 3:
                res.append(f'trojan://1@{fake_ip_for_sub_link}?sni=fake_ip_for_sub_link&security=tls#{hiddify.url_encode(name)}')

    if ua['is_browser']:
        res.append(f'#Hiddify auto ip: {ip_debug}')

    if not user_activate:

        if hconfig(ConfigEnum.lang) == 'fa':
            res.append('trojan://1@1.1.1.1#'+hiddify.url_encode('✖بسته شما به پایان رسید'))
        else:
            res.append('trojan://1@1.1.1.1#'+hiddify.url_encode('✖Package_Ended'))
        return "\n".join(res)

    for pinfo in get_all_validated_proxies(domains):
        link = to_link(pinfo)
        if 'msg' not in link:
            res.append(link)
    return "\n".join(res)


def get_all_validated_proxies(domains):
    allp = []
    allphttp = [p for p in request.args.get("phttp", "").split(',') if p]
    allptls = [p for p in request.args.get("ptls", "").split(',') if p]
    added_ip = {'ssh': {}, 'tuic': {}, 'hysteria': {}}
    for d in domains:
        # raise Exception(base_config)
        hconfigs = get_hconfigs(d.child_id)
        for type in all_proxies(d.child_id):
            options = []
            if type.proto in ['ssh', 'tuic', 'hysteria']:

                ip = hiddify.get_domain_ip(d.domain, version=4)
                ip6 = hiddify.get_domain_ip(d.domain, version=6)

                ips = [x for x in [ip, ip6]if x != None]

                if all([x in added_ip[type.proto] for x in ips]):
                    print('skiping ')
                    continue
                for x in ips:
                    added_ip[type.proto][x] = 1

                if type.proto == 'ssh':
                    if d.mode == 'fake':
                        continue
                    options = [{'pport': hconfigs[ConfigEnum.ssh_server_port]}]
                elif type.proto == 'tuic':
                    options = [{'pport': hconfigs[ConfigEnum.tuic_port]}]
                elif type.proto == 'hysteria':
                    options = [{'pport': hconfigs[ConfigEnum.hysteria_port]}]
            else:
                for t in (['http', 'tls'] if hconfigs[ConfigEnum.http_proxy_enable] else ['tls']):
                    for port in hconfigs[ConfigEnum.http_ports if t == 'http' else ConfigEnum.tls_ports].split(','):
                        phttp = port if t == 'http' else None
                        ptls = port if t == 'tls' else None
                        if phttp and len(allphttp) and phttp not in allphttp:
                            continue
                        if ptls and len(allptls) and ptls not in allptls:
                            continue
                        options.append({'phttp': phttp, 'ptls': ptls})

            for opt in options:
                pinfo = make_proxy(type, d, **opt)
                if 'msg' not in pinfo:
                    allp.append(pinfo)
    return allp
