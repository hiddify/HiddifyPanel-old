from flask import g, request, render_template
from ipaddress import IPv4Address, IPv6Address
from hiddifypanel import hutils
from hiddifypanel.models import *
import yaml
import json
from hiddifypanel.panel import hiddify
import random
import re
import datetime
from flask_babel import gettext as _


def all_proxies(child_id=0):
    all_proxies = hiddify.get_available_proxies(child_id)
    all_proxies = [p for p in all_proxies if p.enable]

    # all_proxies = [p for p in all_proxies if p.proto == ProxyProto.ss]
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


def check_proxy_incorrect(proxy, domain_db, port):
    name = proxy.name
    l3 = proxy.l3
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

    is_cdn = ProxyCDN.CDN == proxy.cdn or ProxyCDN.Fake == proxy.cdn
    if is_cdn and domain_db.mode not in [DomainType.cdn, DomainType.auto_cdn_ip, DomainType.worker]:
        # print("cdn proxy not in cdn domain", domain, name)
        return {'name': name, 'msg': "cdn proxy not in cdn domain", 'type': 'debug', 'proto': proxy.proto}

    if not is_cdn and domain_db.mode in [DomainType.cdn, DomainType.auto_cdn_ip, DomainType.worker]:
        # print("not cdn proxy  in cdn domain", domain, name, proxy.cdn)
        return {'name': name, 'msg': "not cdn proxy  in cdn domain", 'type': 'debug', 'proto': proxy.proto}

    if proxy.cdn == ProxyCDN.relay and domain_db.mode not in [DomainType.relay]:
        return {'name': name, 'msg': "relay proxy not in relay domain", 'type': 'debug', 'proto': proxy.proto}

    if proxy.cdn != ProxyCDN.relay and domain_db.mode in [DomainType.relay]:
        return {'name': name, 'msg': "relay proxy not in relay domain", 'type': 'debug', 'proto': proxy.proto}

    if domain_db.mode == DomainType.worker and proxy.transport == ProxyTransport.grpc:
        return {'name': name, 'msg': "worker does not support grpc", 'type': 'debug', 'proto': proxy.proto}

    if domain_db.mode != DomainType.old_xtls_direct and "tls" in proxy.l3 and proxy.cdn == ProxyCDN.direct and proxy.transport in [ProxyTransport.tcp, ProxyTransport.XTLS]:
        return {'name': name, 'msg': "only  old_xtls_direct  support this", 'type': 'debug', 'proto': proxy.proto}

    if proxy.proto == "trojan" and not is_tls(l3):
        return {'name': name, 'msg': "trojan but not tls", 'type': 'warning', 'proto': proxy.proto}

    if l3 == "http" and ProxyTransport.XTLS in proxy.transport:
        return {'name': name, 'msg': "http and xtls???", 'type': 'warning', 'proto': proxy.proto}

    if l3 == "http" and proxy.proto in [ProxyProto.ss, ProxyProto.ssr]:
        return {'name': name, 'msg': "http and ss or ssr???", 'type': 'warning', 'proto': proxy.proto}


def is_tls(l3):
    return 'tls' in l3 or "reality" in l3


def get_port(proxy, hconfigs, domain_db, ptls, phttp, pport):
    l3 = proxy.l3
    port = None
    if isinstance(phttp, str):
        phttp = int(phttp) if phttp != "None" else None
    if isinstance(ptls, str):
        ptls = int(ptls) if ptls != "None" else None
    if l3 == "kcp":
        port = hconfigs[ConfigEnum.kcp_ports].split(",")[0]
    elif proxy.proto == ProxyProto.wireguard:
        port = hconfigs[ConfigEnum.wireguard_port]
    elif proxy.proto == "tuic":
        port = domain_db.internal_port_tuic
    elif proxy.proto == "hysteria2":
        port = domain_db.internal_port_hysteria2
    elif l3 == 'ssh':
        port = hconfigs[ConfigEnum.ssh_server_port]
    elif is_tls(l3):
        port = ptls
    elif l3 == "http":
        port = phttp
    else:
        port = int(pport)
    return port


def make_proxy(hconfigs, proxy: Proxy, domain_db: Domain, phttp=80, ptls=443, pport=None) -> dict:
    l3 = proxy.l3
    domain = domain_db.domain
    child_id = domain_db.child_id
    name = proxy.name
    port = get_port(proxy, hconfigs, domain_db, ptls, phttp, pport)
    # if not port:
    #     return {'name': name, 'msg': "port not defined", 'type': 'error', 'proto': proxy.proto}
    # print("=========",proxy)
    if val_res := check_proxy_incorrect(proxy, domain_db, port):
        # print(val_res)
        return val_res

    if 'reality' in proxy.l3:
        alpn = "h2" if proxy.transport in ['h2', "grpc"] else 'http/1.1'
    else:
        alpn = "h2" if proxy.l3 in ['tls_h2'] or proxy.transport in ["grpc", 'h2'] else 'h2,http/1.1' if proxy.l3 == 'tls_h2_h1' else "http/1.1"
    cdn_forced_host = domain_db.cdn_ip or (domain_db.domain if domain_db.mode != DomainType.reality else hutils.network.get_direct_host_or_ip(4))
    is_cdn = ProxyCDN.CDN == proxy.cdn or ProxyCDN.Fake == proxy.cdn
    base = {
        'name': name,
        'cdn': is_cdn,
        'mode': "CDN" if is_cdn else "direct",
        'l3': l3,
        'host': domain,
        'port': port,
        'server': cdn_forced_host,
        'sni': domain_db.servernames if is_cdn and domain_db.servernames else domain,
        'uuid': str(g.account.uuid),
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
    if proxy.proto in ['tuic', 'hysteria2']:
        base['alpn'] = "h3"
        return base
    if proxy.proto in ['wireguard']:
        base['wg_pub'] = g.account.wg_pub
        base['wg_pk'] = g.account.wg_pk
        base['wg_psk'] = g.account.wg_psk
        base['wg_ipv4'] = hutils.network.add_number_to_ipv4(hconfigs[ConfigEnum.wireguard_ipv4], g.account.id)
        base['wg_ipv6'] = hutils.network.add_number_to_ipv6(hconfigs[ConfigEnum.wireguard_ipv6], g.account.id)
        base['wg_server_pub'] = hconfigs[ConfigEnum.wireguard_public_key]
        base['wg_noise_trick'] = hconfigs[ConfigEnum.wireguard_noise_trick]
        return base

    if proxy.proto in [ProxyProto.vmess]:
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
        base['cipher'] = hconfigs[ConfigEnum.shadowsocks2022_method]
        base['password'] = f'{hutils.encode.do_base_64(hconfigs[ConfigEnum.shared_secret].replace("-",""))}:{hutils.encode.do_base_64(g.account.uuid.replace("-",""))}'

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
        # base['sni'] = hconfigs[ConfigEnum.shadowtls_fakedomain]
        base['shared_secret'] = hconfigs[ConfigEnum.shared_secret]
        base['mode'] = 'ShadowTLS'
        return base
    elif "shadowsocks" in proxy.transport:
        return base
    if ProxyTransport.XTLS in proxy.transport:
        base['flow'] = 'xtls-rprx-vision'
        return {**base, 'transport': 'tcp'}

    if proxy.proto in {'vless', 'trojan', 'vmess'} and hconfigs.get(ConfigEnum.mux_enable):
        if hconfigs[ConfigEnum.mux_enable]:
            base['mux_enable'] = True
            base['mux_protocol'] = hconfigs[ConfigEnum.mux_protocol]
            base['mux_max_connections'] = hconfigs[ConfigEnum.mux_max_connections]
            base['mux_min_streams'] = hconfigs[ConfigEnum.mux_min_streams]
            base['mux_max_streams'] = hconfigs[ConfigEnum.mux_max_streams]
            base['mux_padding_enable'] = hconfigs[ConfigEnum.mux_padding_enable]

            # the hiddify next client doesn't support mux max streams
            base['mux_max_streams'] = hconfigs[ConfigEnum.mux_max_streams]

            if hconfigs[ConfigEnum.mux_brutal_enable]:
                base['mux_brutal_up_mbps'] = hconfigs[ConfigEnum.mux_brutal_up_mbps]
                base['mux_brutal_down_mbps'] = hconfigs[ConfigEnum.mux_brutal_down_mbps]

    if is_cdn and proxy.proto in {'vless', 'trojan', "vmess"}:
        if hconfigs[ConfigEnum.tls_fragment_enable]:
            base["tls_fragment_enable"] = True
            base["tls_fragment_size"] = hconfigs[ConfigEnum.tls_fragment_size]
            base["tls_fragment_sleep"] = hconfigs[ConfigEnum.tls_fragment_sleep]

        if hconfigs[ConfigEnum.tls_mixed_case]:
            base["tls_mixed_case"] = hconfigs[ConfigEnum.tls_mixed_case]

        if hconfigs[ConfigEnum.tls_padding_enable]:
            base["tls_padding_enable"] = hconfigs[ConfigEnum.tls_padding_enable]
            base["tls_padding_length"] = hconfigs[ConfigEnum.tls_padding_length]

    if "tcp" in proxy.transport:
        base['transport'] = 'tcp'
        base['path'] = f'/{path[base["proto"]]}{hconfigs[ConfigEnum.path_tcp]}'
        return base
    if proxy.transport in ["ws", "WS"]:
        base['transport'] = 'ws'
        base['path'] = f'/{path[base["proto"]]}{hconfigs[ConfigEnum.path_ws]}'
        base["host"] = domain
        return base

    if proxy.transport in [ProxyTransport.httpupgrade]:
        base['transport'] = 'httpupgrade'
        base['path'] = f'/{path[base["proto"]]}{hconfigs[ConfigEnum.path_httpupgrade]}'
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
        base['private_key'] = g.account.ed25519_private_key
        base['host_key'] = hiddify.get_hostkeys(False)
        # base['ssh_port'] = hconfig(ConfigEnum.ssh_server_port)
        return base
    return {'name': name, 'msg': 'not valid', 'type': 'error', 'proto': proxy.proto}


def to_link(proxy):
    if 'error' in proxy:
        return proxy
    # ignore httpupgrade for Streisand
    if g.user_agent.get('is_streisand') and proxy.get('transport') == 'httpupgrade':
        return {'msg': 'ignore httpupgrade for streisand'}

    orig_name_link = (proxy['extra_info'] + " " + proxy["name"]).strip()
    name_link = hutils.encode.url_encode(orig_name_link)
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

        add_tls_tricks_to_dict(vmess_data, proxy)
        add_mux_to_dict(vmess_data, proxy)

        return "vmess://" + hutils.encode.do_base_64(f'{json.dumps(vmess_data,cls=CustomEncoder)}')
    if proxy['proto'] == 'ssh':
        baseurl = 'ssh://'
        if g.user_agent.get('is_streisand'):
            streisand_ssh = hutils.encode.do_base_64(f'{proxy["uuid"]}:0:{proxy["private_key"]}::@{proxy["server"]}:{proxy["port"]}')
            baseurl += f'{streisand_ssh}#{name_link}'
        else:
            hk = ",".join(proxy["host_key"])
            pk = proxy["private_key"].replace('\n', '')
            baseurl += f'{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}/?file=ssh&pk={pk}&pp={pk}&hk={hk}#{name_link}'

        return baseurl
    if proxy['proto'] == "ssr":
        baseurl = f'ssr://{proxy["cipher"]}:{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}'
        return baseurl
    if proxy['proto'] in ['ss', 'v2ray']:
        baseurl = f'ss://{proxy["cipher"]}:{proxy["password"]}@{proxy["server"]}:{proxy["port"]}'
        if proxy['mode'] == 'faketls':
            return f'{baseurl}?plugin=obfs-local%3Bobfs%3Dtls%3Bobfs-host%3D{proxy["fakedomain"]}%3Budp-over-tcp=true#{name_link}'
        # if proxy['mode'] == 'shadowtls':
        #     return f'{baseurl}?plugin=shadow-tls%3Bpassword%3D{proxy["proxy_path"]}%3Bhost%3D{proxy["fakedomain"]}%3Budp-over-tcp=true#{name_link}'
        if proxy['proto'] == 'v2ray':
            return f'{baseurl}?plugin=v2ray-plugin%3Bmode%3Dwebsocket%3Bpath%3D{proxy["path"]}%3Bhost%3D{proxy["host"]}%3Btls%3Budp-over-tcp=true#{name_link}'
        if proxy['transport'] == 'shadowsocks':
            return baseurl
    if proxy['proto'] == 'tuic':
        baseurl = f'tuic://{proxy["uuid"]}:{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}?congestion_control=cubic&udp_relay_mode=native&sni={proxy["sni"]}&alpn=h3'
        if proxy['mode'] == 'Fake' or proxy['allow_insecure']:
            baseurl += "&allow_insecure=1"
        return f"{baseurl}#{name_link}"
    if proxy['proto'] == 'hysteria2':
        baseurl = f'hysteria2://{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}?hiddify=1&obfs=salamander&obfs-password={hconfig(ConfigEnum.proxy_path)}&sni={proxy["sni"]}'
        if proxy['mode'] == 'Fake' or proxy['allow_insecure']:
            baseurl += "&insecure=1"
        return f"{baseurl}#{name_link}"
    if proxy['proto'] == ProxyProto.wireguard:
        if g.user_agent.get('is_streisand'):
            return f'wireguard://{proxy["server"]}:{proxy["port"]}?private_key={proxy["wg_pk"]}&peer_public_key={proxy["wg_server_pub"]}&pre_shared_key={proxy["wg_psk"]}&reserved=0,0,0#{name_link}'
        else:
            # hiddify_format =
            # f'wg://{proxy["server"]}:{proxy["port"]}/?pk={proxy["wg_pk"]}&local_address={proxy["wg_ipv4"]}/32&peer_pk={proxy["wg_server_pub"]}&pre_shared_key={proxy["wg_psk"]}&workers=4&mtu=1380&reserved=0,0,0&ifp={proxy["wg_noise_trick"]}#{name_link}'
            return f'wg://{proxy["server"]}:{proxy["port"]}?publicKey={proxy["wg_pub"]}&privateKey={proxy["wg_pk"]}=&presharedKey={proxy["wg_psk"]}&ip=10.0.0.1&mtu=1380&keepalive=30&udp=1&reserved=0,0,0&ifp={proxy["wg_noise_trick"]}#{name_link}'

    baseurl = f'{proxy["proto"]}://{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}?hiddify=1'
    baseurl += f'&sni={proxy["sni"]}&type={proxy["transport"]}'
    baseurl += f"&alpn={proxy['alpn']}"

    # the ray2sing supports vless, vmess and trojan tls tricks and mux
    # the vmess handled already

    baseurl += add_mux_to_link(proxy)
    baseurl += add_tls_tricks_to_link(proxy)

    # infos+=f'&alpn={proxy["alpn"]}'
    baseurl += f'&path={proxy["path"]}' if "path" in proxy else ""
    baseurl += f'&host={proxy["host"]}' if "host" in proxy else ""
    if "grpc" == proxy["transport"]:
        baseurl += f'&serviceName={proxy["grpc_service_name"]}&mode={proxy["grpc_mode"]}'
    # print(proxy['cdn'],proxy["transport"])
    if request.args.get("fragment"):
        baseurl += f'&fragment=' + request.args.get("fragment")  # type: ignore
    if "ws" == proxy["transport"] and proxy['cdn'] and request.args.get("fragment_v1"):
        baseurl += f'&fragment_v1=' + request.args.get("fragment_v1")  # type: ignore
    if 'vless' == proxy['proto']:
        baseurl += "&encryption=none"
    if proxy.get('fingerprint', 'none') != 'none':
        baseurl += "&fp=" + proxy['fingerprint']
    if proxy['l3'] != 'quic':
        if proxy.get('transport') == ProxyTransport.tcp and proxy['proto'] in [ProxyProto.vless, ProxyProto.vmess] and proxy.get('l3') != ProxyL3.reality:
            baseurl += '&headerType=http'
        else:
            baseurl += '&headerType=None'
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

# region tls tricks & mux
# notice: combining the functions into two function would make code less readable and difficult to maintain


def add_tls_tricks_to_link(proxy) -> str:
    out = {}
    add_tls_tricks_to_dict(out, proxy)
    return convert_dict_to_url(out)


def add_tls_tricks_to_dict(d: dict, proxy):
    if proxy.get('tls_fragment_enable'):
        if g.user_agent.get('is_shadowrocket'):
            d['fragment'] = f'1,{proxy["tls_fragment_size"]},{proxy["tls_fragment_sleep"]}'
        else:
            d['fragment'] = f'{proxy["tls_fragment_size"]},{proxy["tls_fragment_sleep"]},tlshello'

    if proxy.get("tls_mixed_case"):
        d['mc'] = 1
    if proxy.get("tls_padding_enable"):
        d['padsize'] = proxy["tls_padding_length"]


def convert_dict_to_url(dict):
    return '&' + '&'.join([f'{k}={v}' for k, v in dict.items()]) if len(dict) else ''


def add_mux_to_link(proxy) -> str:
    out = {}
    add_mux_to_dict(out, proxy)
    return convert_dict_to_url(out)


def add_mux_to_dict(d: dict, proxy):
    if proxy.get('mux_enable'):
        # d['mux'] = proxy["mux_protocol"]
        # mux is equals to concurrency in clients
        d['mux'] = proxy["mux_max_streams"]
        d['mux_max'] = proxy["mux_max_connections"]
        d['mux_pad'] = proxy["mux_padding_enable"]
        # doesn't exist
        # d['mux_min'] = proxy["mux_min_connections"]

        if proxy.get('mux_brutal_enable'):
            d['mux_up'] = proxy["mux_brutal_up_mbps"]
            d['mux_down'] = proxy["mux_brutal_down_mbps"]

# endregion


# def to_clash_yml(proxy):
#     return yaml.dump(to_clash(proxy,'normal'))


def to_clash(proxy, meta_or_normal):

    name = proxy['name']
    if proxy['l3'] == "kcp":
        return {'name': name, 'msg': "clash does not support kcp", 'type': 'debug'}
    if proxy['proto'] == "ssh":
        return {'name': name, 'msg': "clash does not support ssh", 'type': 'debug'}
    if meta_or_normal == "normal":
        if proxy['proto'] in ["vless", 'tuic', 'hysteria2']:
            return {'name': name, 'msg': f"{proxy['proto']} not supported in clash", 'type': 'debug'}
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
    elif proxy["proto"] == "tuic":
        base["uuid"] = proxy["uuid"]
        base["password"] = proxy["uuid"]
        base["disable-sni"] = proxy['allow_insecure']
        base["reduce-rtt"] = True
        base["request-timeout"] = 8000
        base["udp-relay-mode"] = 'native'
        base["congestion-controller"] = 'cubic'
        base['sni'] = proxy['sni']
        return base
    elif proxy["proto"] in ["ss", "v2ray"]:
        base["cipher"] = proxy["cipher"]
        base["password"] = proxy["password"]
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
    if proxy["proto"] == ProxyProto.wireguard:
        add_singbox_wireguard(base, proxy)
        return all_base

    if proxy["proto"] in ["ss", "v2ray"]:
        add_singbox_shadowsocks_base(all_base, proxy)
        return all_base
    if proxy["proto"] == "ssh":
        add_singbox_ssh(all_base, proxy)
        return all_base

    if proxy["proto"] == "trojan":
        base["password"] = proxy["uuid"]

    if proxy['proto'] in ['vmess', 'vless']:
        base["uuid"] = proxy["uuid"]

    if proxy['proto'] in ['vmess', 'vless', 'trojan']:
        add_singbox_multiplex(base)

    add_singbox_tls(base, proxy)

    if g.user_agent.get('is_hiddify'):
        add_singbox_tls_tricks(base, proxy)

    if proxy.get('flow'):
        base["flow"] = proxy['flow']
        # base["flow-show"] = True

    if proxy["proto"] == "vmess":
        base["alter_id"] = 0
        base["security"] = proxy["cipher"]

    # base["udp"] = True
    if proxy["proto"] in ["vmess", "vless"]:
        base["packet_encoding"] = "xudp"  # udp packet encoding

    if proxy["proto"] == "tuic":
        add_tuic(base, proxy)
    elif proxy["proto"] == "hysteria2":
        add_hysteria(base, proxy)
    else:
        add_singbox_transport(base, proxy)

    return all_base


def add_tuic(base, proxy):
    base['congestion_control'] = "cubic"
    base['udp_relay_mode'] = 'native'
    base['zero_rtt_handshake'] = True
    base['heartbeat'] = "10s"
    base['password'] = proxy['uuid']
    base['uuid'] = proxy['uuid']


def add_hysteria(base, proxy):
    base['up_mbps'] = int(hconfig(ConfigEnum.hysteria_up_mbps))
    base['down_mbps'] = int(hconfig(ConfigEnum.hysteria_down_mbps))
    # TODO: check the obfs should be empty or not exists at all
    if hconfig(ConfigEnum.hysteria_obfs_enable):
        base['obfs'] = {
            "type": "salamander",
            "password": hconfig(ConfigEnum.proxy_path)
        }
    base['password'] = proxy['uuid']


def add_singbox_multiplex(base):
    if not hconfig(ConfigEnum.mux_enable):
        return
    base['multiplex'] = {
        "enabled": True,
        "protocol": hconfig(ConfigEnum.mux_protocol),
        "padding": hconfig(ConfigEnum.mux_padding_enable)
    }
    # Conflicts: max_streams with max_connections and min_streams
    mux_max_streams = int(hconfig(ConfigEnum.mux_max_streams))
    if mux_max_streams and mux_max_streams != 0:
        base['multiplex']['max_streams'] = mux_max_streams
    else:
        base['multiplex']['max_connections'] = int(hconfig(ConfigEnum.mux_max_connections))
        base['multiplex']['min_streams'] = int(hconfig(ConfigEnum.mux_min_streams))

    add_singbox_tcp_brutal(base)


def add_singbox_tcp_brutal(base):
    if 'multiplex' in base:
        base['multiplex']['brutal'] = {
            "enabled": hconfig(ConfigEnum.mux_brutal_enable),
            "up_mbps": int(hconfig(ConfigEnum.mux_brutal_up_mbps)),
            "down_mbps": int(hconfig(ConfigEnum.mux_brutal_down_mbps))
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
        "server_name": proxy["sni"]
    }
    if proxy['proto'] not in ["tuic", "hysteria2"]:
        base["tls"]["utls"] = {
            "enabled": True,
            "fingerprint": proxy.get('fingerprint', 'none')
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


def add_singbox_tls_tricks(base, proxy):
    if proxy.get('tls_fragment_enable'):
        base['tls_fragment'] = {
            'enabled': True,
            'size': proxy["tls_fragment_size"],
            'sleep': proxy["tls_fragment_sleep"]
        }

    if 'tls' in base:
        if proxy.get("tls_padding_enable") or proxy.get("tls_mixed_case"):
            base['tls']['tls_tricks'] = {}
        if proxy.get("tls_padding_enable"):
            base['tls']['tls_tricks']['padding_size'] = proxy["tls_padding_length"]

        if proxy.get("tls_mixed_case"):
            base['tls']['tls_tricks']['mixedcase_sni'] = True


def add_singbox_transport(base, proxy):
    if proxy['l3'] == 'reality' and proxy['transport'] not in ["grpc"]:
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

    if proxy['transport'] in [ProxyTransport.httpupgrade]:
        base["transport"] = {
            "type": "httpupgrade",
            "path": proxy["path"]
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


def add_singbox_wireguard(base, proxy):

    base["local_address"] = f'{proxy["wg_ipv4"]}/32'
    base["private_key"] = proxy["wg_pk"]
    base["peer_public_key"] = proxy["wg_server_pub"]

    base["pre_shared_key"] = proxy["wg_psk"]

    base["mtu"] = 1380
    if g.user_agent.get('is_hiddify') and hiddify.is_hiddify_next_version(0, 15, 0):
        base["fake_packets"] = proxy["wg_noise_trick"]


def add_singbox_shadowsocks_base(all_base, proxy):
    base = all_base[0]
    base["type"] = "shadowsocks"
    base["method"] = proxy["cipher"]
    base["password"] = proxy["password"]
    add_singbox_udp_over_tcp(base)
    add_singbox_multiplex(base)
    if proxy["transport"] == "faketls":
        base["plugin"] = "obfs-local"
        base["plugin_opts"] = f'obfs=tls;obfs-host={proxy["fakedomain"]}'
    if proxy['proto'] == 'v2ray':
        base["plugin"] = "v2ray-plugin"
        # "skip-cert-verify": proxy["mode"] == "Fake" or proxy['allow_insecure'],
        base["plugin_opts"] = f'mode=websocket;path={proxy["path"]};host={proxy["host"]};tls'

    if proxy["transport"] == "shadowtls":
        base['detour'] = base['tag'] + "_shadowtls-out §hide§"

        shadowtls_base = {
            "type": "shadowtls",
            "tag": base['detour'],
            "server": base['server'],
            "server_port": base['server_port'],
            "version": 3,
            "password": proxy["shared_secret"],
            "tls": {
                "enabled": True,
                "server_name": proxy["fakedomain"],
                "utls": {
                    "enabled": True,
                    "fingerprint": proxy.get('fingerprint', 'none')
                },
                # "alpn": proxy['alpn'].split(',')
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
        "tag": base['tag'] + "+UDP",
        "server": "127.0.0.1",
        "server_port": 2000,
        "version": "5",
        "udp_over_tcp": True,
        "network": "tcp",
        "detour": base['tag']
    }
    all_base.append(socks_front)


def make_full_singbox_config(domains, **kwargs):
    ua = hutils.flask.get_user_agent()
    base_config = json.loads(render_template('base_singbox_config.json.j2'))
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
    res = json.dumps(base_config, indent=4, cls=CustomEncoder)
    # if ua['is_hiddify']:
    #     res = res[:-1]+',"experimental": {}}'
    return res


def make_v2ray_configs(user, user_activate, domains, expire_days, ip_debug, db_domain, has_auto_cdn, asn, profile_title, **kwargs):
    res = []

    ua = hutils.flask.get_user_agent()
    if hconfig(ConfigEnum.show_usage_in_sublink):

        if not ua['is_hiddify']:

            fake_ip_for_sub_link = datetime.datetime.now().strftime(f"%H.%M--%Y.%m.%d.time:%H%M")
            # if ua['app'] == "Fair1":
            #     res.append(f'trojan://1@{fake_ip_for_sub_link}?sni=fake_ip_for_sub_link&security=tls#{round(user.current_usage_GB,3)}/{user.usage_limit_GB}GB_Remain:{expire_days}days')
            # else:

            # res.append(f'trojan://1@{fake_ip_for_sub_link}?sni=fake_ip_for_sub_link&security=tls#{hutils.encode.url_encode(profile_title)}')

            name = '⏳' if user_activate else '✖'
            if user.usage_limit_GB < 1000:
                name += f'{round(user.current_usage_GB,3)}/{str(user.usage_limit_GB).replace(".0","")}GB'
            elif user.usage_limit_GB < 100000:
                name += f'{round(user.current_usage_GB/1000,3)}/{str(round(user.usage_limit_GB/1000,1)).replace(".0","")}TB'
            else:
                res.append("#No Usage Limit")
            if expire_days < 1000:
                name += " " + _(f'📅%(expire_days)s days', expire_days=expire_days)
            else:
                res.append("#No Time Limit")

            name = name.strip()
            if len(name) > 3:
                res.append(f'trojan://1@{fake_ip_for_sub_link}?sni=fake_ip_for_sub_link&security=tls#{hutils.encode.url_encode(name)}')

    if ua['is_browser']:
        res.append(f'#Hiddify auto ip: {ip_debug}')

    if not user_activate:

        if hconfig(ConfigEnum.lang) == 'fa':
            res.append('trojan://1@1.1.1.1#' + hutils.encode.url_encode('✖بسته شما به پایان رسید'))
        else:
            res.append('trojan://1@1.1.1.1#' + hutils.encode.url_encode('✖Package_Ended'))
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
    added_ip = {}
    configsmap = {}
    proxeismap = {}
    for d in domains:
        if d.child_id not in configsmap:
            configsmap[d.child_id] = get_hconfigs(d.child_id)
            proxeismap[d.child_id] = all_proxies(d.child_id)
        hconfigs = configsmap[d.child_id]

        ip = hutils.network.get_domain_ip(d.domain, version=4)
        ip6 = hutils.network.get_domain_ip(d.domain, version=6)
        ips = [x for x in [ip, ip6] if x is not None]
        for type in proxeismap[d.child_id]:
            noDomainProxies = False
            if type.proto in [ProxyProto.ssh, ProxyProto.wireguard]:
                noDomainProxies = True
            if type.proto in [ProxyProto.ss] and type.transport not in [ProxyTransport.grpc, ProxyTransport.h2, ProxyTransport.WS, ProxyTransport.httpupgrade]:
                noDomainProxies = True
            options = []
            key = f'{type.proto}{type.transport}{type.cdn}{type.l3}'
            if key not in added_ip:
                added_ip[key] = {}
            if type.proto in [ProxyProto.ssh, ProxyProto.tuic, ProxyProto.hysteria2, ProxyProto.wireguard, ProxyProto.ss]:
                if noDomainProxies and all([x in added_ip[key] for x in ips]):
                    continue

                for x in ips:
                    added_ip[key][x] = 1

                if type.proto in [ProxyProto.ssh, ProxyProto.wireguard, ProxyProto.ss]:
                    if d.mode == 'fake':
                        continue
                    if type.proto in [ProxyProto.ssh]:
                        options = [{'pport': hconfigs[ConfigEnum.ssh_server_port]}]
                    elif type.proto in [ProxyProto.wireguard]:
                        options = [{'pport': hconfigs[ConfigEnum.wireguard_port]}]
                    elif type.transport in [ProxyTransport.shadowsocks]:
                        options = [{'pport': hconfigs[ConfigEnum.shadowsocks2022_port]}]
                    elif type.proto in [ProxyProto.ss]:
                        options = [{'pport': 443}]
                elif type.proto == ProxyProto.tuic:
                    options = [{'pport': hconfigs[ConfigEnum.tuic_port]}]
                elif type.proto == ProxyProto.hysteria2:
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
                pinfo = make_proxy(hconfigs, type, d, **opt)
                if 'msg' not in pinfo:
                    allp.append(pinfo)
    return allp


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, IPv4Address) or isinstance(obj, IPv6Address):
            return str(obj)
        return super().default(obj)
