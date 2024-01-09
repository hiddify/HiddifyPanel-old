from flask import g, jsonify, abort, render_template, request, send_from_directory
from hiddifypanel.models import *
from hiddifypanel.panel import hiddify
import uuid
from flask import g, send_from_directory, url_for, session, Markup
import traceback
import user_agents
import hiddifypanel
import datetime
from flask_babelex import gettext as _


def init_app(app):
    app.jinja_env.globals['ConfigEnum'] = ConfigEnum
    app.jinja_env.globals['DomainType'] = DomainType
    app.jinja_env.globals['UserMode'] = UserMode
    app.jinja_env.globals['hconfig'] = hconfig

    @app.errorhandler(Exception)
    def internal_server_error(e):
        if not hasattr(e, 'code') or e.code == 500:
            trace = traceback.format_exc()

            last_version = hiddify.get_latest_release_version('hiddifypanel')
            has_update = "dev" not in hiddifypanel.__version__ and f'{last_version}' != hiddifypanel.__version__
            if "T" in hiddifypanel.__version__:
                has_update = False
            return render_template('500.html', error=e, trace=trace, has_update=has_update, last_version=last_version), 500
        # if e.code in [400,401,403]:
        #     return render_template('access-denied.html',error=e), e.code

        return render_template('error.html', error=e), e.code

    @app.url_defaults
    def add_proxy_path_user(endpoint, values):

        if 'user_secret' not in values and hasattr(g, 'user_uuid'):
            values['user_secret'] = f'{g.user_uuid}'
        if 'proxy_path' not in values:
            # values['proxy_path']=f'{g.proxy_path}'
            values['proxy_path'] = hconfig(ConfigEnum.proxy_path)

    @app.route("/<proxy_path>/videos/<file>")
    def videos(file):
        print("file", file, app.config['HIDDIFY_CONFIG_PATH'] +
              '/hiddify-panel/videos/'+file)
        return send_from_directory(app.config['HIDDIFY_CONFIG_PATH']+'/hiddify-panel/videos/', file)
    # @app.template_filter()
    # def rel_datetime(value):
    #     diff=datetime.datetime.now()-value
    #     return format_timedelta(diff, add_direction=True, locale=hconfig(ConfigEnum.lang))

    @app.url_value_preprocessor
    def pull_secret_code(endpoint, values):
        # print("Y",endpoint, values)
        # if values is None:
        #     return
        # if hiddifypanel.__release_date__ + datetime.timedelta(days=40) < datetime.datetime.now() or hiddifypanel.__release_date__ > datetime.datetime.now():
        #     abort(400, _('This version of hiddify panel is outdated. Please update it from admin area.'))
        g.user = None
        g.user_uuid = None
        g.is_admin = False

        if request.args.get('darkmode') != None:
            session['darkmode'] = request.args.get('darkmode', '').lower() == 'true'
        g.darkmode = session.get('darkmode', False)
        import random
        g.install_pwa = random.random() <= 0.05
        if request.args.get('pwa') != None:
            session['pwa'] = request.args.get('pwa', '').lower() == 'true'
        g.pwa = session.get('pwa', False)

        g.user_agent = hiddify.get_user_agent()
        if g.user_agent["is_bot"]:
            abort(400, "invalid")
        g.proxy_path = values.pop('proxy_path', None) if values else None
        if g.proxy_path != hconfig(ConfigEnum.proxy_path):
            if app.config['DEBUG']:
                abort(400, Markup(f"Invalid Proxy Path <a href=/{hconfig(ConfigEnum.proxy_path)}/{get_super_admin_secret()}/admin>admin</a>"))
            abort(400, "Invalid Proxy Path")
        if endpoint == 'static' or endpoint == "videos":
            return
        tmp_secret = values.pop('user_secret', None) if values else None
        try:
            if tmp_secret:
                g.user_uuid = uuid.UUID(tmp_secret)
        except:
            # raise PermissionError("Invalid secret")
            abort(400, 'invalid user')
        g.admin = get_admin_user_db(tmp_secret)
        g.is_admin = g.admin is not None
        bare_path = request.path.replace(g.proxy_path, "").replace(tmp_secret, "").lower()
        if not g.is_admin:
            g.user = User.query.filter(User.uuid == f'{g.user_uuid}').first()
            if not g.user:
                abort(401, 'invalid user')
            if endpoint and ("admin" in endpoint or "api" in endpoint):
                # raise PermissionError("Access Denied")
                abort(403, 'Access Denied')
            if "admin" in bare_path or "api" in bare_path:
                abort(403, 'Access Denied')

        if hconfig(ConfigEnum.telegram_bot_token):
            import hiddifypanel.panel.commercial.telegrambot as telegrambot
            if (not telegrambot.bot) or (not telegrambot.bot.username):
                telegrambot.register_bot()
            g.bot = telegrambot.bot
        # print(g.user)
