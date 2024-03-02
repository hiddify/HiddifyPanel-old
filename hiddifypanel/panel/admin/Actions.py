#!/usr/bin/env python3
import pprint
from flask_babelex import gettext as _
import pathlib
from hiddifypanel.models import *

from datetime import datetime, timedelta, date
import os
import sys
import json
import urllib.request
import subprocess
import re
from hiddifypanel.panel import hiddify, usage
from flask import current_app, render_template, request, Response, Markup, url_for, make_response, redirect
from hiddifypanel.panel.hiddify import flash

from flask_classful import FlaskView, route


class Actions(FlaskView):

    @hiddify.super_admin
    def index(self):
        return render_template('index.html')

    @hiddify.super_admin
    def reverselog(self, logfile):
        if logfile == None:
            return self.viewlogs()
        config_dir = current_app.config['HIDDIFY_CONFIG_PATH']

        with open(f'{config_dir}/log/system/{logfile}') as f:
            lines = [line for line in f]
            # logs="".join(lines[::-1])
            logs = "".join(lines)
        # resp= Response()
        # resp.mimetype="text/plain"
        from ansi2html import Ansi2HTMLConverter
        conv = Ansi2HTMLConverter()

        out = f'<div style="background-color:black; color:white;padding:10px">{conv.convert(logs)}</div>'
        # if len(lines)>5 and "----Finished!---" in "".join(lines[-min(10,len(lines)):]):
        #     out=f"<a href='#' target='_blank'><div style='background-color:#b1eab1; padding: 10px;border: solid;'>Finished! For scrolling the log click here.</div></a>{out}"

        response = make_response(out)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    @hiddify.super_admin
    def viewlogs(self):
        config_dir = current_app.config['HIDDIFY_CONFIG_PATH']
        res = []
        for filename in sorted(os.listdir(f'{config_dir}/log/system/')):
            res.append(f"<a href='{url_for('admin.Actions:reverselog',logfile=filename)}'>{filename}</a>")
        return Markup("<br>".join(res))

    @route('apply_configs', methods=['POST'])
    def apply_configs(self):
        return self.reinstall(False)

    @route('reset', methods=['POST'])
    def reset(self):
        return self.reset2()

    @hiddify.super_admin
    def reset2(self):
        status = self.status()
        # flash(_("rebooting system may takes time please wait"),'info')
        # os.system(f"echo 'reboot'|at now + 3s ")

        resp = render_template("result.html",
                               out_type="info",
                               out_msg="",
                               log_path=get_logpath("restart.log"),
                               show_success=True,
                               domains=get_domains(),



                               )
        file = "restart.sh"
        config = current_app.config
        subprocess.Popen(f"sudo {config['HIDDIFY_CONFIG_PATH']}/{file}".split(" "), cwd=f"{config['HIDDIFY_CONFIG_PATH']}", start_new_session=True)
        import time
        time.sleep(1)
        return resp

    @route('reinstall', methods=['POST'])
    def reinstall(self, complete_install=True, domain_changed=False):
        return self.reinstall2(complete_install, domain_changed)

    @hiddify.super_admin
    def reinstall2(self, complete_install=True, domain_changed=False):
        if int(hconfig(ConfigEnum.db_version)) < 9:
            return ("Please update your panel before this action.")
        # if hconfig(ConfigEnum.parent_panel):
        #     try:
        #         hiddify_api.sync_child_to_parent()
        #     except e as Exception:
        #         flash(_('can not sync child with parent panel')+" "+e)

        domain_changed = request.args.get("domain_changed", str(domain_changed)).lower() == "true"
        complete_install = request.args.get("complete_install", str(complete_install)).lower() == "true"
        if domain_changed:
            flash((_('Your domains changed. Please do not forget to copy admin links, otherwise you can not access to the panel anymore.')), 'info')
        # flash(f'complete_install={complete_install} domain_changed={domain_changed} ', 'info')
        # return render_template("result.html")
        config = current_app.config
        hiddify.add_temporary_access()
        file = "install.sh" if complete_install else "apply_configs.sh"
        try:
            server_ip = urllib.request.urlopen('https://v4.ident.me/').read().decode('utf8')
        except:
            server_ip = "server_ip"

        # subprocess.Popen(f"{config_dir}/update.sh",env=my_env,cwd=f"{config_dir}")
        # os.system(f'cd {config_dir};{env} ./install.sh &')
        # rc = subprocess.call(f"cd {config_dir};./{file} & disown",shell=True)

        admin_secret = get_super_admin_secret()
        proxy_path = hconfig(ConfigEnum.proxy_path)
        admin_links = f"<h5 >{_('Admin Links')}</h5><ul>"
        admin_links += f"<li><span class='badge badge-danger'>{_('Not Secure')}</span>: <a class='badge ltr share-link' href='http://{server_ip}/{proxy_path}/{admin_secret}/admin/'>http://{server_ip}/{proxy_path}/{admin_secret}/admin/</a></li>"
        domains = get_panel_domains()
        # domains=[*domains,f'{server_ip}.sslip.io']
        for d in domains:
            link = f'https://{d}/{proxy_path}/{admin_secret}/admin/'
            admin_links += f"<li><a target='_blank' class='badge ltr' href='{link}'>{link}</a></li>"

        resp = render_template("result.html",
                               out_type="info",
                               out_msg=_("Success! Please wait around 4 minutes to make sure everything is updated. During this time, please save your proxy links which are:") +
                               admin_links,
                               log_path=get_logpath("0-install.log"),
                               show_success=True,
                               domains=get_domains(),



                               )

        subprocess.Popen(f"sudo {config['HIDDIFY_CONFIG_PATH']}/{file}".split(" "), cwd=f"{config['HIDDIFY_CONFIG_PATH']}", start_new_session=True)
        import time
        time.sleep(1)
        return resp

    @hiddify.super_admin
    def change_reality_keys(self):
        key = hiddify.generate_x25519_keys()
        set_hconfig(ConfigEnum.reality_private_key, key['private_key'])
        set_hconfig(ConfigEnum.reality_public_key, key['public_key'])
        hiddify.flash_config_success(restart_mode='apply', domain_changed=False)
        return redirect(url_for('admin.SettingAdmin:index'))

    @hiddify.super_admin
    def status(self):
        # hiddify.add_temporary_access()
        config = current_app.config
        # configs=read_configs()
        # subprocess.Popen(f"{config_dir}/update.sh",env=my_env,cwd=f"{config_dir}")
        # os.system(f'cd {config_dir};{env} ./install.sh &')
        # rc = subprocess.call(f"cd {config_dir};./{file} & disown",shell=True)
        from urllib.parse import urlparse

        o = urlparse(request.base_url)
        domain = o.hostname
        subprocess.Popen(f"sudo {config['HIDDIFY_CONFIG_PATH']}/status.sh".split(" "), cwd=f"{config['HIDDIFY_CONFIG_PATH']}", start_new_session=True)

        return render_template("result.html",
                               out_type="info",
                               out_msg=_("see the log in the bellow screen"),
                               log_path=get_logpath(f"status.log"),
                               # log_path=f"status.log",
                               show_success=False,
                               domains=get_domains()
                               )

    # @hiddify.super_admin

    @route('update', methods=['POST'])
    def update(self):
        return self.update2()

    @hiddify.super_admin
    def update2(self):
        hiddify.add_temporary_access()
        config = current_app.config
        cwd = os.getcwd()

        # os.chdir(config_dir)
        # rc = subprocess.call(f"./install.sh &",shell=True)
        # rc = subprocess.call(f"cd {config_dir};./update.sh & disown",shell=True)
        # os.system(f'cd {config_dir};./update.sh &')

        subprocess.Popen(f"sudo {config['HIDDIFY_CONFIG_PATH']}/update.sh".split(" "), cwd=f"{config['HIDDIFY_CONFIG_PATH']}", start_new_session=True)
        return render_template("result.html",
                               out_type="success",
                               out_msg=_("Success! Please wait around 5 minutes to make sure everything is updated."),
                               show_success=True,
                               log_path=get_logpath(f"update.log"),
                               domains=get_domains(),
                               )

    def get_some_random_reality_friendly_domain(self):
        test_domain = request.args.get("test_domain")
        import ping3
        from hiddifypanel.panel.clean_ip import ipasn, ipcountry
        ipv4 = hiddify.get_ip(4)
        server_country = (ipcountry.get(ipv4) or {}).get('country', {}).get('iso_code', 'unknown')
        server_asn = (ipasn.get(ipv4) or {}).get('autonomous_system_organization', 'unknown')
        res = "<table><tr><th>Domain</th><th>IP</th><th>Country</th><th>ASN</th><th>Ping (ms)</th><th>TCP ping (ms)</th></tr>"
        res += f"<tr><td>Your Server</td><td>{ipv4}</td><td>{server_country}</td><td>{server_asn}</td><td>0</td></tr>"
        import time
        start = time.time()
        for d in [test_domain, *hiddify.get_random_domains(30)]:
            if not d:
                continue
            if time.time() - start > 20:
                break
            print(d)
            tcp_ping = hiddify.is_domain_reality_friendly(d)
            if tcp_ping:
                dip = hiddify.get_domain_ip(d)
                dip_country = (ipcountry.get(dip) or {}).get('country', {}).get('iso_code', 'unknown')
                if dip_country == "IR":
                    continue
                response_time = -1
                try:
                    response_time = ping3.ping(d, unit='ms')
                    if response_time:
                        response_time = int(response_time)
                except:
                    pass
                dip_asn = (ipasn.get(dip) or {}).get('autonomous_system_organization', 'unknown')
                res += f"<tr><td>{d}</td><td>{dip}</td><td>{dip_country}</td><td>{dip_asn}</td><td>{response_time}</td><td>{tcp_ping}<td></tr>"

        return res + "</table>"

    @hiddify.super_admin
    def update_usage(self):

        import json

        return render_template("result.html",
                               out_type="info",
                               out_msg=f'<pre class="ltr">{json.dumps(usage.update_local_usage(),indent=2)}</pre>',
                               log_path=None
                               )


def get_logpath(logfile):
    return f'{hiddify.get_admin_path()}actions/reverselog/{logfile}/'


def get_domains():
    return [d.domain.replace("*", hiddify.get_random_string(3, 6)) for d in get_panel_domains(always_add_all_domains=True, always_add_ip=True)]
