from hiddifypanel.panel import hiddify
from flask.views import MethodView
from flask import url_for
from flask import current_app as app
from flask import g, request
from apiflask import Schema, abort
from apiflask.fields import String,URL,Enum,List,Nested
from flask_babelex import lazy_gettext as _
from urllib.parse import quote_plus,urlparse
import user_agents
from strenum import StrEnum
from enum import auto


from hiddifypanel.panel.user.user import get_common_data
from hiddifypanel.hutils.utils import get_latest_release_url,do_base_64

#region App Api DTOs
class AppInstallType(StrEnum):
    google_play = auto()
    app_store = auto()
    appimage = auto()
    snapcraft = auto()
    microsoft_store = auto()
    apk = auto()
    dmg = auto()
    setup = auto()
    portable = auto()
    other = auto()

class AppInstall(Schema):
    title = String()
    type = Enum(AppInstallType,required=True,description='The platform that provides the app to download')
    url = URL(required=True,description='The url to download the app')

class AppSchema(Schema):
    title = String(required=True,description='The title of the app')
    description = String(required=True,description='The description of the app')
    icon_url = URL(required=True,description='The icon url of the app')
    guide_url = URL(description='The guide url of the app')
    deeplink = URL(required=True,description='The deeplink of the app to imoprt configs')
    install = List(Nested(AppInstall()),required=True,description='The install url of the app')

# this class is not a Data Transfer Object, It's just an enum
class Platform(StrEnum):
    all = auto()
    android = auto()
    ios = auto()
    windows = auto()
    linux = auto()
    mac = auto()
    auto = auto()

class AppInSchema(Schema):
    platform = Enum(Platform,load_default=Platform.auto,required=False,description='The platform (Operating System) to know what clients should be send. Possible values are: all, android, ios, windows, linux, mac, auto.')
#endregion



class AppAPI(MethodView):
    decorators = [hiddify.user_auth]

    def __init__(self) -> None:
        super().__init__()
        self.hiddify_github_repo = 'https://github.com/hiddify'

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
    
    @app.input(AppInSchema, arg_name='data', location="query")
    @app.output(AppSchema(many=True))
    def get(self,data):
        # parse user agent
        if data['platform'] == Platform.auto:
            platfrom = self.__get_ua_platform()
            if not platfrom:
                abort(400,'Your selected platform is invalid!')
            self.platform = platfrom
        else:
            self.platform = data['platform']

        # output data
        apps_data = []
        
        match self.platform:
            case Platform.all:
                apps_data = self.__get_all_apps_dto()
            case Platform.android:
                hiddify_next_dto = self.__get_hiddify_next_app_dto()
                hiddifyng_dto = self.__get_hiddifyng_app_dto()
                v2rayng_dto = self.__get_v2rayng_app_dto()
                hiddify_android_dto = self.__get_hiddify_android_app_dto()
                hiddify_clash_dto = self.__get_hiddify_clash_app_dto()
                nekobox_dto = self.__get_nekobox_app_dto()
                apps_data += ([hiddify_next_dto,hiddifyng_dto,v2rayng_dto,hiddify_android_dto,hiddify_clash_dto,nekobox_dto])
            case Platform.windows:
                hiddify_next_dto = self.__get_hiddify_next_app_dto()
                hiddifyng_dto = self.__get_hiddifyng_app_dto()
                v2rayng_dto = self.__get_v2rayng_app_dto()
                hiddify_clash_dto = self.__get_hiddify_clash_app_dto()
                hiddifyn_dto = self.__get_hiddifyn_app_dto()
                apps_data += ([hiddify_next_dto,hiddifyng_dto,hiddify_clash_dto,hiddifyn_dto])
            case Platform.ios:
                stash_dto = self.__get_stash_app_dto()
                shadowrocket_dto = self.__get_shadowrocket_app_dto()
                foxray_dto = self.__get_foxray_app_dto()
                streisand_dto = self.__get_streisand_app_dto()
                loon_dto = self.__get_loon_app_dto()
                apps_data += ([streisand_dto,stash_dto,shadowrocket_dto,foxray_dto,loon_dto])              
            case Platform.linux:
                hiddify_clash_dto = self.__get_hiddify_clash_app_dto()
                hiddify_next_dto = self.__get_hiddify_next_app_dto()
                hiddifyn_dto = self.__get_hiddifyn_app_dto()
                apps_data += ([hiddify_next_dto,hiddify_clash_dto,hiddifyn_dto])
            case Platform.mac:
                hiddify_clash_dto = self.__get_hiddify_clash_app_dto()
                hiddify_next_dto = self.__get_hiddify_next_app_dto()
                apps_data += ([hiddify_next_dto,hiddify_clash_dto])

        return apps_data

    def __get_ua_platform(self):
        os = user_agents.parse(request.user_agent.string).os.family
        if os == 'Android':
            return Platform.android
        elif os == 'Windows':
            return Platform.windows
        elif os == 'Mac OS X':
            return Platform.mac
        elif os == 'iOS':
            return Platform.ios
        elif 'Linux' in request.user_agent.string and 'X11' or 'Wayland' in request.user_agent.string:
            return Platform.linux

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
        elif app_name == _('app.nekobox.title'):
            url = base + url_for(endpoint='static',filename='apps-icon/nekobox.ico')

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
        dto.install = [self.__get_app_install_dto(AppInstallType.apk,ins_url)]
        return dto

    def __get_nekobox_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.nekobox.title')
        dto.description = _('app.nekobox.description')
        dto.icon_url = self.__get_app_icon_url(_('app.nekobox.title'))
        dto.guide_url = ''
        dto.deeplink = f'clash://install-config?url={self.user_panel_encoded_url}'

        latest_url, version = get_latest_release_url(f'https://github.com/MatsuriDayo/NekoBoxForAndroid')
        ins_url = latest_url.split('releases/')[0] + f'releases/download/{version}/NB4A-{version}-x86_64.apk'
        dto.install = [self.__get_app_install_dto(AppInstallType.apk,ins_url)]
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
        dto.install = [self.__get_app_install_dto(AppInstallType.apk,ins_url),]
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
        dto.install = [self.__get_app_install_dto(AppInstallType.apk,ins_url),]
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
        dto.install = [self.__get_app_install_dto(AppInstallType.apk,ins_url),]
        return dto

    def __get_foxray_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.foxray.title')
        dto.description = _('app.foxray.description')
        dto.icon_url = self.__get_app_icon_url(_('app.foxray.title'))
        dto.guide_url = ''
        dto.deeplink = f'https://yiguo.dev/sub/add/?url={do_base_64(self.subscription_link_encoded_url)}#{self.profile_title}'

        ins_url = 'https://apps.apple.com/us/app/foxray/id6448898396'
        dto.install = [self.__get_app_install_dto(AppInstallType.app_store,ins_url),]
        return dto

    def __get_shadowrocket_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.shadowrocket.title')
        dto.description = _('app.shadowrocket.description')
        dto.icon_url = self.__get_app_icon_url(_('app.shadowrocket.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=F2bC_mtbYmQ'
        dto.deeplink = f'sub://{do_base_64(self.user_panel_url)}'

        ins_url = 'https://apps.apple.com/us/app/shadowrocket/id932747118'
        dto.install = [self.__get_app_install_dto(AppInstallType.app_store,ins_url),]
        return dto
    def __get_streisand_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.streisand.title')
        dto.description = _('app.streisand.description')
        dto.icon_url = self.__get_app_icon_url(_('app.streisand.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=jaMkZTLH2QY'
        dto.deeplink = f'streisand://import/{self.user_panel_url}#{self.profile_title}'
        ins_url = 'https://apps.apple.com/app/id6450534064'
        dto.install = [self.__get_app_install_dto(AppInstallType.app_store,ins_url),]
        return dto
    def __get_loon_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.loon.title')
        dto.description = _('app.loon.description')
        dto.icon_url = self.__get_app_icon_url(_('app.loon.title'))
        dto.guide_url = ''
        dto.deeplink = f'loon://import?nodelist={self.user_panel_encoded_url}'
        ins_url = 'https://apps.apple.com/app/id1373567447'
        dto.install = [self.__get_app_install_dto(AppInstallType.app_store,ins_url)]
    def __get_stash_app_dto(self):
        dto = AppSchema()
        dto.title = _('app.stash.title')
        dto.description = _('app.stash.description')
        dto.icon_url = self.__get_app_icon_url(_('app.stash.title'))
        dto.guide_url = 'https://www.youtube.com/watch?v=D0Xv54nRSY8'
        dto.deeplink = f'clash://install-config/?url={self.user_panel_encoded_url}'

        ins_url = 'https://apps.apple.com/us/app/stash-rule-based-proxy/id1596063349'
        dto.install = [self.__get_app_install_dto(AppInstallType.app_store,ins_url),]
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
            case Platform.windows:
                ins_url = latest_url.split('releases/')[0] + f'releases/download/{version}/HiddifyClashDesktop_{version}_x64_en-US.msi'
                ins_type = AppInstallType.setup
            case Platform.linux:
                ins_url = latest_url.split('releases/')[0] + f'releases/download/{version}/hiddify-clash-desktop_{version}_amd64.AppImage'
                ins_type = AppInstallType.appimage
            case Platform.mac:
                ins_url = latest_url.split('releases/')[0] + f'releases/download/{version}/HiddifyClashDesktop_{version}x64.dmg'
                ins_type = AppInstallType.dmg

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
            case Platform.android:
                installation_types = [AppInstallType.apk,AppInstallType.google_play]
            case Platform.windows:
                installation_types = [AppInstallType.setup,AppInstallType.portable]
            case Platform.linux:
                installation_types = [AppInstallType.appimage]
            case Platform.mac:
                installation_types = [AppInstallType.dmg]

        install_dtos = []
        for install_type in installation_types:
            install_dto = AppInstall()
            ins_url = ''
            match install_type:
                case AppInstallType.apk:
                    ins_url = f'{self.hiddify_github_repo}/hiddify-next/releases/latest/download/hiddify-android-universal.apk'
                case AppInstallType.google_play:
                    ins_url = 'https://play.google.com/store/apps/details?id=app.hiddify.com'
                case AppInstallType.setup:
                    ins_url = f'{self.hiddify_github_repo}/hiddify-next/releases/latest/download/hiddify-windows-x64-setup.zip'
                case AppInstallType.portable:
                    ins_url = f'{self.hiddify_github_repo}/hiddify-next/releases/latest/download/hiddify-windows-x64-portable.zip'
                case AppInstallType.appimage:
                    ins_url = f'{self.hiddify_github_repo}/hiddify-next/releases/latest/download/hiddify-linux-x64.zip'
                case AppInstallType.dmg:
                    ins_url = f'{self.hiddify_github_repo}/hiddify-next/releases/latest/download/hiddify-macos-universal.zip'
            
            install_dto = self.__get_app_install_dto(install_type,ins_url)
            install_dtos.append(install_dto)
        
        dto.install = install_dtos
        return dto
        
    