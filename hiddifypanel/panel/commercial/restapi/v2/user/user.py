from urllib.parse import urlparse
from flask_restful import Resource
from hiddifypanel.models.config import StrConfig, hconfig
from hiddifypanel.models.config_enum import ConfigEnum
from hiddifypanel.models.domain import DomainType
from hiddifypanel.models.user import days_to_reset, user_by_uuid
from hiddifypanel.panel import hiddify
from hiddifypanel.panel.database import db
import requests
import user_agents

from flask_classful import FlaskView, route
from flask.views import MethodView
from flask import url_for
from flask import current_app as app
from flask import g, request
from apiflask import APIFlask, Schema, abort
from apiflask.fields import Integer, String, Float, URL,Dict
from apiflask.validators import Length, OneOf
from flask_babelex import lazy_gettext as _
from urllib.parse import quote_plus

from enum import Enum,auto

from hiddifypanel.panel.commercial.restapi.v2.user.DTO import *
from hiddifypanel.panel.user import link_maker
from hiddifypanel.panel.user.user import get_common_data
from hiddifypanel.utils import get_latest_release_url,do_base_64






class InfoAPI(MethodView):
    decorators = [hiddify.user_auth]

    @app.output(ProfileSchema)
    def get(self):
        c = get_common_data(g.user_uuid, 'new')

        dto = ProfileSchema()
        dto.profile_title = c['profile_title']
        dto.profile_url = f"https://{urlparse(request.base_url).hostname}/{g.proxy_path}/{g.user_uuid}/#{g.user.name}"
        dto.profile_usage_current = g.user.current_usage_GB
        dto.profile_usage_total = g.user.usage_limit_GB
        dto.profile_remaining_days = g.user.remaining_days
        dto.profile_reset_days = days_to_reset(g.user)
        dto.telegram_bot_url = f"https://t.me/{c['bot'].username}?start={g.user_uuid}" if c['bot'] else ""
        dto.telegram_id = c['user'].telegram_id
        dto.admin_message_html =  hconfig(ConfigEnum.branding_freetext)
        dto.admin_message_url = hconfig(ConfigEnum.branding_site)
        dto.brand_title = hconfig(ConfigEnum.branding_title)
        dto.brand_icon_url = ""
        dto.doh = f"https://{urlparse(request.base_url).hostname}/{g.proxy_path}/dns/dns-query"
        dto.lang = c['user'].lang
        return dto

    @app.input(UserInfoChangableSchema,arg_name='data')
    def patch(self,data):
        if data['telegram_id']:
            try:
                tg_id = int(data['telegram_id'])
            except:
                return {'message':'The telegram id field is invalid'}
            
            user = user_by_uuid(g.user_uuid)
            if user.telegram_id != tg_id:
                user.telegram_id = tg_id
                db.session.commit()

            
        if data['language']:
            user = user_by_uuid(g.user_uuid)
            if user.lang != data['language']:
                user.lang = data['language']
                db.session.commit()
        return {'message': 'ok'}
    
class MTProxiesAPI(MethodView):
    decorators = [hiddify.user_auth]
    @app.output(MtproxySchema(many=True))
    def get(self):
        # get domains
        c = get_common_data(g.user_uuid, 'new')
        dtos = []
        # TODO: Remove duplicated domains mapped to a same ipv4 and v6
        for d in c['domains']:
            if d.mode not in [DomainType.direct, DomainType.relay]:
                continue
            hexuuid = hconfig(ConfigEnum.shared_secret, d.child_id).replace('-', '')
            telegram_faketls_domain_hex = hconfig(ConfigEnum.telegram_fakedomain, d.child_id).encode('utf-8').hex()
            server_link = f'tg://proxy?server={d.domain}&port=443&secret=ee{hexuuid}{telegram_faketls_domain_hex}'
            dto = MtproxySchema()
            dto.title = d.alias or d.domain
            dto.link = server_link
            dtos.append(dto)
        return dtos



class AllConfigsAPI(MethodView):
    decorators = [hiddify.user_auth]

    @app.output(ConfigSchema(many=True))
    def get(self):
        def create_item(name, type, domain, protocol, transport, security, link):
            dto = ConfigSchema()
            dto.name = name
            dto.type = type
            dto.domain = domain
            dto.protocol = protocol
            dto.transport = transport
            dto.security = security
            dto.link = link
            return dto

        items = []
        base_url = f"https://{urlparse(request.base_url).hostname}/{g.proxy_path}/{g.user_uuid}/"
        c = get_common_data(g.user_uuid, 'new')

        # Add Auto
        items.append(
            create_item(
                "Auto", "All", "All", "All", "All", "All",
                f"{base_url}sub/?asn={c['asn']}")
        )

        # Add Full Singbox
        items.append(
            create_item(
                "Full Singbox", "All", "All", "All", "All", "All",
                f"{base_url}full-singbox.json?asn={c['asn']}"
            )
        )

        # Add Clash Meta
        items.append(
            create_item(
                "Clash Meta", "All", "All", "All", "All", "All",
                f"clashmeta://install-config?url={base_url}clash/meta/all.yml&name=mnormal_{c['db_domain'].alias or c['db_domain'].domain}-{c['asn']}-{c['mode']}&asn={c['asn']}&mode={c['mode']}"
            )
        )

        # Add Clash
        items.append(
            create_item(
                "Clash", "All", "All", "Except VLess", "All", "All",
                f"clash://install-config?url={base_url}clash/all.yml&name=new_normal_{c['db_domain'].alias or c['db_domain'].domain}-{c['asn']}-{c['mode']}&asn={c['asn']}&mode={c['mode']}"
            )
        )

        # Add Singbox: SSh
        if hconfig(ConfigEnum.ssh_server_enable):
            items.append(
                create_item(
                    "Singbox: SSH", "SSH", "SSH", "SSH", "SSH", "SSH",
                    f"{base_url}singbox.json?name={c['db_domain'].alias or c['db_domain'].domain}-{c['asn']}&asn={c['asn']}&mode={c['mode']}"
                )
            )

        # Add Subscription link
        items.append(
            create_item(
                "Subscription link", "All", "All", "All", "All", "All",
                f"{base_url}all.txt?name={c['db_domain'].alias or c['db_domain'].domain}-{c['asn']}&asn={c['asn']}&mode={c['mode']}"
            )
        )

        # Add Subscription link base64
        items.append(
            create_item(
                "Subscription link b64", "All", "All", "All", "All", "All",
                f"{base_url}all.txt?name=new_link_{c['db_domain'].alias or c['db_domain'].domain}-{c['asn']}-{c['mode']}&asn={c['asn']}&mode={c['mode']}&base64=True"
            )
        )

        for pinfo in link_maker.get_all_validated_proxies(c['domains']):
            items.append(
                create_item(
                    pinfo["name"].replace("_", " "),
                    f"{'Auto ' if pinfo['dbdomain'].has_auto_ip else ''}{pinfo['mode']}",
                    pinfo['server'],
                    pinfo['proto'],
                    pinfo['transport'],
                    pinfo['l3'],
                    f"{link_maker.to_link(pinfo)}"
                )
            )

        return items


class ShortAPI(MethodView):
    decorators = [hiddify.user_auth]

    @app.output(ShortSchema)
    def get(self):
        expire_in = 5
        short = hiddify.add_short_link("/"+hconfig(ConfigEnum.proxy_path)+"/"+g.g.user_uuid+"/",expire_in)
        full_url = f"https://{urlparse(request.base_url).hostname}/{short}"
        dto = ShortSchema()
        dto.full_url = full_url
        dto.short = short
        dto.expire_in = expire_in
        return dto

class AppAPI(MethodView):
    decorators = [hiddify.user_auth]

    def __init__(self) -> None:
        super().__init__()
        self.hiddify_github_repo = 'https://github.com/hiddify'
        req_platfrom = request.args.get('platform')

        # fill platform(os)
        self.platform = ''
        if req_platfrom:
            if req_platfrom.lower() not in Platform.__members__:
                abort(400,'Your selected platform is invalid!')
            self.platform = req_platfrom.lower()
        else:
            platfrom = self.__get_ua_platform()
            if not platfrom:
                abort(400,'Your selected platform is invalid!')
            self.platform = platfrom

        all_apps = request.args.get('all')
        self.all_apps = True if all_apps and all_apps.lower() == 'true' else False

        self.user_panel_url = f"https://{urlparse(request.base_url).hostname}/{g.proxy_path}/{g.user_uuid}/"
        self.user_panel_encoded_url = quote_plus(self.user_panel_url)
        c = get_common_data(g.user_uuid, 'new')
        self.subscription_link_url = f"{self.user_panel_url}all.txt?name={c['db_domain'].alias or c['db_domain'].domain}-{c['asn']}&asn={c['asn']}&mode={c['mode']}"
        self.subscription_link_encoded_url = do_base_64(self.subscription_link_url)
        domain = c['db_domain'].alias or c['db_domain'].domain
        self.profile_title = c['profile_title']
        # self.clash_all_sites = f"https://{domain}/{g.proxy_path}/{g.user_uuid}/clash/all.yml?mode={c['mode']}&asn={c['asn']}&name={c['asn']}_all_{domain}-{c['mode']}"
        # self.clash_foreign_sites = f"https://{domain}/{g.proxy_path}/{g.user_uuid}/clash/normal.yml?mode={c['mode']}&asn={c['asn']}&name={c['asn']}_normal_{domain}-{c['mode']}"
        # self.clash_blocked_sites = f"https://{domain}/{g.proxy_path}/{g.user_uuid}/clash/lite.yml?mode={c['mode']}&asn={c['asn']}&name={c['asn']}_lite_{c['db_domain'].alias or c['db_domain'].domain}-{c['mode']}"
        # self.clash_meta_all_sites = f"https://{domain}/{g.proxy_path}/{g.user_uuid}/clash/meta/all.yml?mode={c['mode']}&asn={c['asn']}&name={c['asn']}_mall_{domain}-{c['mode']}"
        # self.clash_meta_foreign_sites = f"https://{domain}/{g.proxy_path}/{g.user_uuid}/clash/meta/normal.yml?mode={c['mode']}&asn={c['asn']}&name={c['asn']}_mnormal_{domain}-{c['mode']}"
        self.clash_meta_blocked_sites = f"https://{domain}/{g.proxy_path}/{g.user_uuid}/clash/meta/lite.yml?mode={c['mode']}&asn={c['asn']}&name={c['asn']}_mlite_{domain}-{c['mode']}"
    @app.output(AppSchema(many=True))
    def get(self):
        # output data
        apps_data = []
        
        if self.all_apps:
            all_apps_dto = self.__get_all_apps_dto()
            return all_apps_dto
        
        match self.platform:
            case 'android':
                hiddify_next_dto = self.__get_hiddify_next_app_dto()
                hiddifyng_dto = self.__get_hiddifyng_app_dto()
                v2rayng_dto = self.__get_v2rayng_app_dto()
                hiddify_android_dto = self.__get_hiddify_android_app_dto()
                apps_data += ([hiddify_next_dto,hiddifyng_dto,v2rayng_dto,hiddify_android_dto])
            case 'windows':
                hiddify_next_dto = self.__get_hiddify_next_app_dto()
                hiddifyng_dto = self.__get_hiddifyng_app_dto()
                v2rayng_dto = self.__get_v2rayng_app_dto()
                hiddify_clash_dto = self.__get_hiddify_clash_app_dto()
                hiddifyn_dto = self.__get_hiddifyn_app_dto()
                apps_data += ([hiddify_next_dto,hiddifyng_dto,hiddify_clash_dto,hiddifyn_dto])
            case 'ios':
                stash_dto = self.__get_stash_app_dto()
                shadowrocket_dto = self.__get_shadowrocket_app_dto()
                foxray_dto = self.__get_foxray_app_dto()
                streisand_dto = self.__get_streisand_app_dto()
                loon_dto = self.__get_loon_app_dto()
                apps_data += ([stash_dto,shadowrocket_dto,foxray_dto,streisand_dto,loon_dto])              
            case 'linux':
                hiddify_clash_dto = self.__get_hiddify_clash_app_dto()
                hiddify_next_dto = self.__get_hiddify_next_app_dto()
                hiddifyn_dto = self.__get_hiddifyn_app_dto()
                apps_data += ([hiddify_next_dto,hiddify_clash_dto,hiddifyn_dto])
            case 'mac':
                hiddify_clash_dto = self.__get_hiddify_clash_app_dto()
                hiddify_next_dto = self.__get_hiddify_next_app_dto()
                apps_data += ([hiddify_next_dto,hiddify_clash_dto])

        return apps_data
    def __get_ua_platform(self):
        os = user_agents.parse(request.user_agent.string).os.family
        if os == 'Android':
            return os.lower()
        elif os == 'Windows':
            return os.lower()
        elif os == 'Mac OS X':
            return 'mac'
        elif os == 'iOS':
            return os.lower()
        elif 'Linux' in request.user_agent.string and 'X11' or 'Wayland' in request.user_agent.string:
            return 'linux'

        return None

    def __get_all_apps_dto(self):
        hiddifyn_app_dto = self.__get_hiddifyn_app_dto()
        v2rayng_app_dto = self.__get_v2rayng_app_dto()
        hiddifyng_app_dto = self.__get_hiddifyng_app_dto()
        hiddify_android_app_dto = self.__get_hiddify_android_app_dto()
        foxray_app_dto = self.__get_foxray_app_dto()
        shadowrocket_app_dto = self.__get_shadowrocket_app_dto()
        streisand_app_dto = self.__get_streisand_app_dto()
        loon_app_dto = self.__get_loon_app_dto()
        stash_app_dto = self.__get_stash_app_dto()
        hiddify_clash_app_dto = self.__get_hiddify_clash_app_dto()
        hiddify_next_app_dto = self.__get_hiddify_next_app_dto()
        return [
                hiddifyn_app_dto,v2rayng_app_dto,hiddifyng_app_dto,hiddify_android_app_dto,
                foxray_app_dto,shadowrocket_app_dto,streisand_app_dto,
                loon_app_dto,stash_app_dto,hiddify_clash_app_dto,hiddify_next_app_dto
            ]
    def __get_app_icon_url(self,app_name):
        base = f'https://{urlparse(request.base_url).hostname}'
        url = ''
        if app_name == _('app.hiddify.next.title'):
            url = base + url_for('static',filename='apps-icon/hiddify_next.ico')
        elif app_name == _('app.hiddifyn.title'):
            url = base + url_for('static',filename='apps-icon/hiddifyn.ico')
        elif app_name == _('app.v2rayng.title'):
            url = base + url_for('static',filename='apps-icon/v2rayng.ico')
        elif app_name == _('app.hiddifyng.title'):
            url = base + url_for('static',filename='apps-icon/hiddifyng.ico')
        elif app_name == _('app.hiddify-android.title'):
            url = base + url_for('static',filename='apps-icon/hiddify_android.ico')
        elif app_name == _('app.foxray.title'):
            url = base + url_for('static',filename='apps-icon/foxray.ico')
        elif app_name == _('app.shadowrocket.title'):
            url = base + url_for('static',filename='apps-icon/shadowrocket.ico')
        elif app_name == _('app.streisand.title'):
            url = base + url_for('static',filename='apps-icon/streisand.ico')
        elif app_name == _('app.loon.title'):
            url = base + url_for('static',filename='apps-icon/loon.ico')
        elif app_name == _('app.stash.title'):
            url = base + url_for('static',filename='apps-icon/stash.ico')
        elif app_name == _('app.hiddify.clash.title'):
            url = base + url_for('static',filename='apps-icon/hiddify_clash.ico')

        return url
    
    def __get_app_install_dto(self,install_type:AppInstallType,url,title=''):
            install_dto = AppInstall()
            install_dto.title = title
            install_dto.type = install_type
            install_dto.url = url
            return install_dto
    
    def __get_hiddifyn_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.hiddifyn.title')
        dto.description = _('app.hiddifyn.description')
        dto.icon_url = self.__get_app_icon_url(_('app.hiddifyn.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=o9L2sI2T53Q'
        dto.deeplink = f'hiddify://install-sub?url={self.subscription_link_url}'

        ins_url = f'{self.hiddify_github_repo}/HiddifyN/releases/latest/download/HiddifyN.zip'
        dto.install = [self.__get_app_install_dto(AppInstallType.APK,ins_url)]
        return dto

    def __get_v2rayng_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.v2rayng.title')
        dto.description = _('app.v2rayng.description')
        dto.icon_url = self.__get_app_icon_url(_('app.v2rayng.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=6HncctDHXVs'
        dto.deeplink = f'v2rayng://install-sub/?url={self.user_panel_encoded_url}'
                            
        # make v2rayng latest version url download
        latest_url, version = get_latest_release_url(f'https://github.com/2dust/v2rayNG/')
        ins_url = latest_url.split('releases/')[0] + f'releases/download/{version}/v2rayNG_{version}.apk'
        dto.install = [self.__get_app_install_dto(AppInstallType.APK,ins_url),]
        return dto

    def __get_hiddifyng_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.hiddifyng.title')
        dto.description = _('app.hiddifyng.description')
        dto.icon_url = self.__get_app_icon_url(_('app.hiddifyng.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=qDbI72J-INM'
        dto.deeplink = f'hiddify://install-sub/?url={self.user_panel_encoded_url}'
                            
        latest_url,version = get_latest_release_url(f'{self.hiddify_github_repo}/HiddifyNG/')
        ins_url = latest_url.split('releases/')[0] + f'releases/download/{version}/HiddifyNG.apk'
        dto.install = [self.__get_app_install_dto(AppInstallType.APK,ins_url),]
        return dto

    def __get_hiddify_android_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.hiddify-android.title')
        dto.description = _('app.hiddify-android.description')
        dto.icon_url = self.__get_app_icon_url(_('app.hiddify-android.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=mUTfYd1_UCM'
        dto.deeplink = f'clash://install-config/?url={self.user_panel_encoded_url}'
        latest_url,version = get_latest_release_url(f'{self.hiddify_github_repo}/HiddifyClashAndroid/')
        ins_url = latest_url.split('releases/')[0] + f'releases/download/{version}/hiddify-{version}-meta-alpha-universal-release.apk'
        dto.install = [self.__get_app_install_dto(AppInstallType.APK,ins_url),]
        return dto

    def __get_foxray_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.foxray.title')
        dto.description = _('app.foxray.description')
        dto.icon_url = self.__get_app_icon_url(_('app.foxray.title'))
        dto.guide_url = ''
        dto.deeplink = f'https://yiguo.dev/sub/add/?url={do_base_64(self.subscription_link_encoded_url)}#{self.profile_title}'

        ins_url = 'https://apps.apple.com/us/app/foxray/id6448898396'
        dto.install = [self.__get_app_install_dto(AppInstallType.APP_STORE,ins_url),]
        return dto

    def __get_shadowrocket_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.shadowrocket.title')
        dto.description = _('app.shadowrocket.description')
        dto.icon_url = self.__get_app_icon_url(_('app.shadowrocket.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=F2bC_mtbYmQ'
        dto.deeplink = f'sub://{do_base_64(self.user_panel_url)}'

        ins_url = 'https://apps.apple.com/us/app/shadowrocket/id932747118'
        dto.install = [self.__get_app_install_dto(AppInstallType.APP_STORE,ins_url),]
        return dto
    def __get_streisand_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.streisand.title')
        dto.description = _('app.streisand.description')
        dto.icon_url = self.__get_app_icon_url(_('app.streisand.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=jaMkZTLH2QY'
        dto.deeplink = f'streisand://import/{self.user_panel_url}#{self.profile_title}'
        ins_url = 'https://apps.apple.com/app/id6450534064'
        dto.install = [self.__get_app_install_dto(AppInstallType.APP_STORE,ins_url),]
        return dto
    def __get_loon_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.loon.title')
        dto.description = _('app.loon.description')
        dto.icon_url = self.__get_app_icon_url(_('app.loon.title'))
        dto.guide_url = ''
        dto.deeplink = f'loon://import?nodelist={self.user_panel_encoded_url}'
        ins_url = 'https://apps.apple.com/app/id1373567447'
        dto.install = [self.__get_app_install_dto(AppInstallType.APP_STORE,ins_url)]
    def __get_stash_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.stash.title')
        dto.description = _('app.stash.description')
        dto.icon_url = self.__get_app_icon_url(_('app.stash.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=D0Xv54nRSY8'
        dto.deeplink = f'clash://install-config/?url={self.user_panel_encoded_url}'

        ins_url = 'https://apps.apple.com/us/app/stash-rule-based-proxy/id1596063349'
        dto.install = [self.__get_app_install_dto(AppInstallType.APP_STORE,ins_url),]
        return dto

    def __get_hiddify_clash_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.hiddify.clash.title')
        dto.description = _('app.hiddify.clash.description')
        dto.icon_url = self.__get_app_icon_url(_('app.hiddify.clash.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=omGIz97mbzM'
        dto.deeplink = f'clash://install-config/?url={self.user_panel_encoded_url}'

        # make hiddify clash latest version url download
        latest_url, version = get_latest_release_url(f'{self.hiddify_github_repo}/hiddifydesktop')
        version = version.replace('v','')
        ins_url = ''
        ins_type = None
        match self.platform:
            case 'windows':
                ins_url = latest_url.split('releases/')[0] + f'releases/download/{version}/HiddifyClashDesktop_{version}_x64_en-US.msi'
                ins_type = AppInstallType.SETUP
            case 'linux':
                ins_url = latest_url.split('releases/')[0] + f'releases/download/{version}/hiddify-clash-desktop_{version}_amd64.AppImage'
                ins_type = AppInstallType.APPIMAGE
            case 'mac':
                ins_url = latest_url.split('releases/')[0] + f'releases/download/{version}/HiddifyClashDesktop_{version}x64.dmg'
                ins_type = AppInstallType.DMG

        dto.install = [self.__get_app_install_dto(ins_type,ins_url)]
        return dto

    def __get_hiddify_next_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.hiddify.next.title')
        dto.description = _('app.hiddify.next.description')
        dto.icon_url = self.__get_app_icon_url(_('app.hiddify.next.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=vUaA1AEUy1s'
        dto.deeplink = f'hiddify://install-config/?url={self.user_panel_encoded_url}'

        # availabe installatoin types
        installation_types = []
        match self.platform:
            case 'adnroid':
                installation_types = [AppInstallType.APK,AppInstallType.GOOGLE_PLAY]
            case 'windows':
                installation_types = [AppInstallType.SETUP,AppInstallType.PORTABLE]
            case 'linux':
                installation_types = [AppInstallType.APPIMAGE]
            case 'mac':
                installation_types = [AppInstallType.DMG]

        install_dtos = []
        for install_type in installation_types:
            install_dto = AppInstall()
            ins_url = ''
            match install_type:
                case AppInstallType.APK:
                    ins_url = f'{self.hiddify_github_repo}/hiddify-next/releases/latest/download/hiddify-android-universal.apk'
                case AppInstallType.GOOGLE_PLAY:
                    ins_url = 'https://play.google.com/store/apps/details?id=app.hiddify.com'
                case AppInstallType.SETUP:
                    ins_url = f'{self.hiddify_github_repo}/hiddify-next/releases/latest/download/hiddify-windows-x64-setup.zip'
                case AppInstallType.PORTABLE:
                    ins_url = f'{self.hiddify_github_repo}/hiddify-next/releases/latest/download/hiddify-windows-x64-portable.zip'
                case AppInstallType.APPIMAGE:
                    ins_url = f'{self.hiddify_github_repo}/hiddify-next/releases/latest/download/hiddify-linux-x64.zip'
                case AppInstallType.DMG:
                    ins_url = f'{self.hiddify_github_repo}/hiddify-next/releases/latest/download/hiddify-macos-universal.zip'
            
            install_dto = self.__get_app_install_dto(install_type,ins_url)
            install_dtos.append(install_dto)
        
        dto.install = install_dtos
        return dto
        
    