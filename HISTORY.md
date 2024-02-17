# Changelog


## (unreleased)

#### New

* Add mass disable/enable to proxies. 

* Add support for httpupgrade. 

* Add switch for enable/disable ws, grpc, httpupgrade globally. 

* Add shadowsocks2022 support. 

* Add faketls with 2022 shadowsocks model. 

* Add search to proxy details. 

* Show progress details and hide log window. 

* Use fast_enum fix: bugs and refactor. 

* Optimize panel. 

* Add initial virtual child support. 

* Add wireguard. 

* Add indivisual config for relay. 

* Refactor configenum. 

* Customizable message added. 

* Add share link in user admin with qrcode. 

* Handle singbox v1.8 and v1.7. 

* Add insert secret code. 

* Add full backward compatiblity. 

* Add login page. 

* Use slugify. 

* Base class for admin and user models. 

* Check permission for AdminUserApi. 

* Check permission for AdminUsersApi. 

* Account atuhentication approach. 

* Implement custom flask-login for - seperate storing account id in session. 

* Handle new proxy paths (test) 

* Add login_required to user's apis. 

* Redirect old apis url to new url. 

* Use log api for getting logs. 

* JS to get logs files in result.html. 

* Auth.login_required (supports roles) 

* Better handling user change. 

* Add stars. 

* Better exception handling. 

* Add license to api. 

* Add user v2 API. 

* Add link to api. 

* Add api v2. 

* Fix quick stup stuck after restore backup. 

* Add last version of release and beta in make. 

* Add admin path to config. 

* Add admin links. 

* Hide incorrect mode proxies. 

* Filter the payment and big companies to avoid phishing detection in decoy site. 

* Add warp custom sites. 

* Add issue from menu. 

* Add custom CFG path. 

* Fix bug when no backup exist. 

* Add russian lang. 

* Add Russian translation. 

* Add reality port cli. 

* Better usage icon. 

* Add fake domains also. 

* Add hystria and tuic. 

* Add beta pre-release. 

#### Changes

* Show add telegram bot pop up. 

* Bool configs only return bool and others return str. update translations. 

* Refactor. 

* Don't send fragmentation to hiddify-next. 

* Override root admin is disabled by default. 

* Remove unused argument/parameter. 

* Send args in link (asn,mode...) 

* Seperate clash and clashmeta endpoints. 

* All-configs api links. 

* Update configs link. 

* Refactor getting lang. 

* Hide telegram id in add/edit page. 

* Hide histeria port from setting ui. 

* Hysteria link makeri (client link) 

* NOTHING IMPORTANT. 

* Make sessions permanent for two days. 

* Allow backward compatibility. 

* Refactor proxy model. 

* Refactor DailyUsage model. 

* Refactor. 

* Revert links to old format. 

* Update ui. 

* Add full backward compatiblity. 

* Add common_bp. 

* Refactor parent domain model. 

* Refactor DailyUsage. 

* Add backward compatibility. 

* Refactor admin and user model. 

* Refactor. 

* Refactor. 

* Fix role management. 

* Refactor. 

* Hidden old proxy path. 

* Remove duplicate password check. 

* Remove filter_by. 

* Refactor. 

* Admin login links. 

* Api v1 blueprint name. 

* Refactor. 

* APIs links to new format. 

* Refactor. 

* Authenticate user panel endponit with Authorization header even there is cookie. 

* Using server_status log api. 

* Send api calls with cookie instead of ApiKey. 

* Better readability. 

* Basic athentication realm value. 

* Better names. 

* Apiflask authentication to auth_back.py file & remove unused imports. 

* Backward compatibility. 

* Init. 

* New route page. 

* Rename. 

* Remove <user_secret> from routing in blueprint. 

* Authentication. 

* If client sent user/pass we try to authenticate with the user/pass, THEN we check session cookies. 

* Use hiddify-manager/common/commander.py instead of running the scripts directly. 

* Version parameter type to int in ip.py functions fix: typo and bugs. 

* Make ip_utils a package. 

* Get ip approach & validation in DomainAdmin.py. 

* Show xui_importer error if occurred. 

* Short api. 

* Ui files. 

* Use apiflask abort. 

* Change AdminDTO to AdminSchema. 

* Better naming. 

* Reorganize domain ports. 

* Update hysteria2 link. 

* Update hiddify next download link. 

#### Fix

* Ui. 

* Not showing reality and fake domains. 

* No success pop up. 

* Singbox fg parameter sending. 

* Backup restore bug. 

* Some config related issues. 

* Referrer only for same origin. 

* Bug when new domain changed. 

* Api key bug. 

* Anonymous account bug. 

* Ua bug. 

* Update translation. 

* Fragmentation & mux. 

* Mtproxies link. 

* Bug. 

* Backup & auto ip selector bug. 

* Bug. 

* Show sub link as profile url. 

* Wireguard link. 

* Bug in downloading backup. 

* Show log in status page by default. 

* Getting log file & refactor. 

* Silly db bug. 

* Proxies bug. 

* Bugs/typos. 

* Permission. 

* Send telegram message. 

* Bugss. 

* Child bug. 

* Bugs. 

* Bug. 

* Req. 

* Bug. 

* Bug. 

* Mtproxies api. 

* Mtprotoproxy library link. 

* Xray fg. 

* Fragmentation for other clients except hiddify-next. 

* Get app icon url bug. 

* Typo. 

* Bug in wireguard. 

* Bug. 

* Bug. 

* Bugs. 

* Bug. 

* Translation bug in babel. 

* Bug. 

* Bug. 

* Telegram sending msg bug & babel. 

* Telegram_id bug. 

* Bug in domain. 

* Telegram id. 

* Better comment. 

* Report not defined bug. 

* Typo. 

* Send tls tricks only if proxy is cdn and client supports. 

* Bug chg: refactor. 

* Showing default mux_protocol in ui. 

* Bug. 

* Import bug. 

* Typo. 

* Bug. 

* Bug. 

* Bug in user id. 

* Auth bug. 

* Exception in account. 

* Locale bug. 

* Agent admin permission. 

* User panel lang. 

* Send message to admin's users itself. not to other admins. 

* Telegram id active representationo add: telegram id field to user edit/add page. 

* Send message to user in telegram. 

* Bug. 

* Useragent echo. 

* Singbox 1.8. 

* Redis url. 

* Bug in release. 

* Bug for hiddify next. 

* Hysteria2 bug. 

* Bug in singbox. 

* Bug. 

* Typo. 

* Don't show progress bar for update usage too. 

* Bug in getting configs. 

* Don't show progress bar for restart/reset too. 

* Don't show progress bar in /status/ 

* Progress bar. 

* Lang. 

* Bug. 

* Bug. 

* Bug. 

* Bug in fill_username. 

* Empty admin message. 

* Compatibility issue with old version. 

* Bug. 

* Bug. 

* Bug in singbox 1.7. 

* Hiddify client version. 

* Bug. 

* Admin link bug. 

* Bug. 

* Bug in singbox config. 

* Limited length of username and password. 

* Issue in updating ua. 

* Fix: login by uuid@domain.com. 

* Bug. 

* All config bugs. 

* Singbox. 

* Deep link url. 

* Auth. 

* Typo. 

* Typo. 

* Typo. 

* Json serializer bug. 

* Bug in useragent. 

* Remove print. 

* Remove prints. 

* Bugs, refactor changes, remove unneccessary dependency to flask_login. 

* Bug. 

* Bug. 

* Bug. 

* Backward compatiblity. 

* Bug. 

* Bug. 

* Bugs. 

* Bugs. 

* Backward compatibility issues. 

* Bugs. 

* Telegram get_usage_data user link. 

* Admin/user APIs (validation,parenting,recursive fetching) 

* Bugs and add login blue print. 

* Static path. 

* Bugs. 

* User bug. 

* Proxy path validation. 

* Admin me api. 

* Bug. 

* Bug in QuickSetup. 

* Auto removing UUIDs from api requests. 

* Short api again. 

* Short api. 

* Api v1 routing. 

* Remove user/pass from short api link. 

* Api v1 telegram endpoints. 

* Backward compatibility. 

* Bug. 

* Typo in redirect.html file. 

* Add just proxy_path_admin and proxy_path_client. 

* Disable CORS for all endpoints and enable it just for adminlog api for now. 

* Domain in api. 

* Better account type selection in parse_auth_id. 

* Typo & imports. 

* Typo del: unused function. 

* Init_db filling user/admin username|passowrd fields. 

* Fill username & password in user/admin creation. 

* Bug. 

* Bug & authenticate api calls with session cookie. 

* New.html assests link. 

* Backward compatibility. 

* Bug. 

* First try to authenticate with HTTP Authorization header value then check the user session data. 
  _Think user is authenticated as A1 then they want to login as A2 on same
domain. in this case we should keep our eye on header not session.
because session is authenticated by A1 but now we want to authenticate
with A2_

* /admin/adminuser/ links username password bug. 

* Fix: accept authentication link to login(eg. https://username:password@domain.com/path) 

* No need to send g.proxy_path to templates (jinja has it) 

* Merging conflicts. 

* Status js log file call to use api. 

* Bug. 

* Creating empty session(in redis) for every request. 

* Unboundlocalerror bug. 

* Remove links with uuid. 

* Admin link in invalid proxy. 

* Backward compatibility. 

* Setup session data for admin. 

* Using g.account instead of g.user/g.admin. 

* Add authentication(role-based) for ModelView classes. 

* Basic authentication verify password function. 

* Rename. 

* Short_api. 

* Info api profile title. 

* Typo. 

* Profile name. 

* Remove run commander.py with "sudo python3" 

* Backup restoring. 

* Bug and refactor. 

* Bug. 

* Run_commander.py. 

* User apis bugs. 

* Typo. 

* Mistake. 

* Ip_utils imports. 

* Get_interface_public_ip (return [] instead of None) 

* Init_db bug. 

* Xui importer. 

* Ios bug. 

* Exception handle. 

* Bugs. 

* Import bug. 

* Bug and add description. 

* Change expire_in variable from minutes to seconds. 

* Hiddify_next.ico. 

* Bug in apiflask. 

* Security issue. 

* Bug. 

* Bug. 

* Heart icon. 

* Bug in user 'me' api. 

* Flask_migrate common errors. 

* Could not build url for endpoint 'admin.static' error. 

* Https://github.com/hiddify/HiddifyPanel/pull/45#discussion_r1390457377. 

* Https://github.com/hiddify/HiddifyPanel/pull/45#discussion_r1390456353. 

* User short link showing page. 

* Typo. 

* Proxy not updated  after delete. 

* Bug. 

* Security concern. 

* Permission issue. 

* Bug in new domain. 

* Domains not removed. 

* Domains in mtproxy. 

* Bug in user.py. 

* Get telegram bot in get_common_data method. 

* Backup restore. 

* Bug in report issue. 

* Multiple ip. 

* Common.py bug. 

* Admin link. 

* Admin link bug. 

* Bug in decoy selector. 

* Bug in clean install. 

* Typo. 

* Not preserving admin uuid when upgrade. 

* Bug. 

* Vmess bug. 

* Branding free text. 

* Grpc bug in singbox. 

* Grpc h2 bug. 

* Reality grpc  bug in singbox. 

* Telegram admin bot bug. 

* Bug in error report. 

* Reality bug. 

* Bug. 

* Agent bug. 

* Bug. 

* Bug. 

* User add bug. 

* Grpc bug. 

* Bug. 

* No commit message. 

* Typo. 

* Hysteria link. 

* Translation issue. 

* Typo. 

* Ipv6 ::1. 

* Bug in not restoring allowed subdomain. 

* Search and sort in user page. 

* Change in modes. 

* Bug in port. 

* Proto. 

* Tls bug. 

* Bug. 

* Typo. 

* Bug. 

* Bug in get singbox active users. 

* Setting issue. 

* Always shows error in dev version. 

* Child id. 

* Bug in cyclic loop. 

* Bugs in upgrading database. 

* Update enums automatically. 

* Owner. 

* Short. 

* Import old configs bug. 

* Shadowtls singbox. 

* Bugs. 

#### Other

* Update translation. 

* Merge branch 'main' of github.com:hiddify/Hiddify-Panel. 

* Merge pull request #127 from Iam54r1n4/dev-patch11. 
  _fix: singbox fg parameter sending_

* Merge branch 'main' of github.com:hiddify/Hiddify-Panel. 

* Merge pull request #126 from Iam54r1n4/dev-patch10. 
  _Delete admin telegram_proxy_enable & speedtest_enable api fields_

* Del: admin telegram_proxy_enable & speedtest_enable api fields. 

* Remove any refere from urls. 

* Merge pull request #125 from Iam54r1n4/dev-patch10. 
  _Add speetest & telegram proxy availability to api_

* Add: speetest & telegram proxy availability to admin "/me" api. 

* Add: speetest & telegram proxy availability to user "/me" api. 

* Merge pull request #123 from Iam54r1n4/dev-patch7. 
  _fix: ua bug_

* Merge branch 'main' into dev-patch7. 

* Merge pull request #124 from Iam54r1n4/dev-patch9. 
  _Fix fragmentation & mux_

* Merge branch 'main' into dev-patch9. 

* Remove user_agent cache and fix typo. 

* Merge branch 'main' of github.com:hiddify/Hiddify-Panel. 

* Merge pull request #122 from Iam54r1n4/dev-patch9. 
  _Fix mtproxies link_

* Merge pull request #121 from Iam54r1n4/dev-patch8. 
  _Fix backup restoring & auto ip selector bug_

* Merge pull request #119 from Iam54r1n4/dev-patch6. 
  _Fix show sub link as profile url_

* Chg. 

* Merge pull request #120 from Iam54r1n4/dev-patch7. 
  _Fix wireguard link_

* Chg. 

* Chg. 

* Merge pull request #117 from Iam54r1n4/dev-patch4. 
  _Fix bug in downloading backup_

* Merge pull request #118 from Iam54r1n4/dev-patch5. 
  _Show log in status page by default_

* Merge pull request #116 from Iam54r1n4/dev-patch3. 
  _Fix getting log file after quick setup_

* Merge pull request #115 from Iam54r1n4/dev-patch2. 
  _Fix db bool/str config tables bug_

* Update translations. 

* Refactor elements in useradmin. 

* Merge pull request #114 from Iam54r1n4/dev-patch. 
  _Fix bugs/typos_

* Merge pull request #113 from Iam54r1n4/bug-fix. 

* Fix bugs. 

* Enable cache again. 

* Big refactor. 

* Increase session lifetime to 10 days. 

* Merge. 

* Merge pull request #111 from Iam54r1n4/fix-mtproxy. 
  _fix: mtprotoproxy library link_

* Merge pull request #109 from Iam54r1n4/fix-xray-fg. 
  _fix: fragmentation_

* Merge pull request #110 from Iam54r1n4/bug-fix. 
  _Fix client app icon bug_

* Merge pull request #107 from Iam54r1n4/refactor_configenum. 
  _Complete configenum refactoring_

* Refactor: configenum complete. 

* Merge pull request #106 from Iam54r1n4/refac-configenum. 
  _Refactor config_enum_

* Update config_enum.py. 

* Refactor: config enum. 

* Merge pull request #105 from Iam54r1n4/tel_bug. 
  _fix: telegram sending msg bug & babel_

* Force https and basic auth for admins. 

* Update cache to 3.0.0. 

* Merge pull request #101 from Iam54r1n4/bug-fix. 
  _Fix telegram_id bug_

* Merge pull request #102 from Iam54r1n4/refactor-xui_importer. 
  _Refactor xui importer_

* Merge branch 'main' into refactor-xui_importer. 

* Merge pull request #103 from Iam54r1n4/refactor-hiddifypy. 
  _Refactor hiddify.py and hutils_

* Refactor: hiddify.py & type hint. 

* Refactor: network. 

* Refactor: hiddify.py system. 

* Refactor: xui importer. 

* Merge branch 'main' of github.com:hiddify/Hiddify-Panel. 

* Merge pull request #100 from Iam54r1n4/refactor-hutils. 
  _Refactor hutils_

* Refactor: github issue generator. 

* Refactor: hutils/hiddify flask & fix bug. 

* Merge pull request #99 from Iam54r1n4/refactor-hutils. 
  _Refactor hutils_

* Refactor: hutils convert. 

* Refactor: hutils random. 

* Refactor: hutils encode. 

* Refactor: hutils auth. 

* Refactor: hutils json. 

* Disable proxy create. 

* Add uwsgi to req. 

* Merge pull request #96 from Iam54r1n4/xray-cfg. 
  _Add tls fragmentation & mux parameters to subscription's links for xray_

* Add: tls fragmentation & mux parameters to subscription's links for xray. 

* Merge pull request #97 from Iam54r1n4/singbox-mux. 
  _Fix bug in sending singbox client's config_

* Merge pull request #95 from Iam54r1n4/singbox-mux. 
  _Add Singbox multiplex & tls_fragment object to configs (client-side)_

* Add: tls padding to singbox client's config. 

* Merge branch 'singbox-mux' of github.com:Iam54r1n4/HiddifyPanel into singbox-mux. 

* Merge branch 'hiddify:main' into singbox-mux. 

* Add: tls fragment to singbox client side config file if the client supports. 

* Add: singbox multiplex object to configs (client-side) 

* Remove sysout. 

* Refactor: account and others. 

* Update. 

* Update lang. 

* Merge pull request #94 from Iam54r1n4/fix-agent-role. 
  _fix: agent admin permission_

* Merge pull request #91 from Iam54r1n4/new-links. 
  _Add new config endpoints_

* Merge pull request #92 from Iam54r1n4/fix-lang. 
  _Fix lang_

* Add: new config links. 

* Merge pull request #93 from Iam54r1n4/tel_bug. 
  _Fix telegram id bugs_

* Merge branch 'main' of github.com:hiddify/Hiddify-Panel. 

* Merge pull request #89 from Iam54r1n4/mux. 
  _Add multiplexer config fields_

* Change defaults for mux. 

* Fix the locale generated dynamically. 

* Add: validation for mux fields. 

* Add: db version for mux fields. 

* Add: mux new fields. 

* Merge pull request #90 from Iam54r1n4/tel_bug. 
  _Fix sending message to user in with telegram bot_

* Merge pull request #88 from Iam54r1n4/validation. 
  _Add validation for tls tricks and  hysteria new fields_

* Add: validation for hysteria fields. 

* Add: tls tricks validations. 

* Better singbox config. 

* Remove: print. 

* Merge pull request #87 from Iam54r1n4/hysteria2. 
  _Hysteria2 link maker dynamically with DB (client side link)_

* Add: todo. 

* Merge pull request #86 from Iam54r1n4/hysteria2. 

* Add: hysteria2 setting to database. 

* Merge pull request #85 from Iam54r1n4/tls-trick. 
  _Bug fix_

* Merge pull request #84 from Iam54r1n4/domain-chg. 

* Add: extra_params field to domain model. 

* Merge pull request #83 from Iam54r1n4/tls-trick. 
  _add: tls fragment fields_

* Add: tls_trick config category. 

* Add: tls fragment fields in db. 

* Merge pull request #82 from Iam54r1n4/bug-fix. 

* Update: ui. 

* Remove geoip for singbox 1.8. 

* Merge. 

* Merge branch 'main' of github.com:hiddify/Hiddify-Panel. 

* Merge pull request #81 from er888kh/patch-3. 
  _Update hiddify.py_

* Update hiddify.py. 
  _Guard against concatenation with non-string host values (such as IP address)_

* Remove temporary access, refactor panel links, refactor user.py. 

* Merge pull request #76 from Iam54r1n4/refactor-proxy. 
  _Refactor proxy model_

* Merge pull request #77 from Iam54r1n4/refactor-parent-domain. 
  _Refactor parent domain_

* Merge branch 'main' into refactor-parent-domain. 

* Merge pull request #80 from Iam54r1n4/refactor-daily-usage. 
  _Refactor DailyUsage model_

* Login by uuid@domain.com/path/l. 

* Remove old user_agent. 

* Merge pull request #78 from Iam54r1n4/fix-auth. 
  _fix: typo_

* Merge branch 'main' into fix-auth. 

* Update ui. 

* Update ui. 

* Update translation. 

* Update version. 

* Merge pull request #74 from Iam54r1n4/auth. 
  _Better role management & api validating/parenting/recursiving & refactoring models_

* Merge branch 'auth' of github.com:Iam54r1n4/HiddifyPanel into HEAD. 

* Merge pull request #73 from Iam54r1n4/auth. 
  _Auth_

* Merge branch 'hiddify:main' into auth. 

* Merge pull request #72 from Iam54r1n4/auth. 
  _Implement session authentication (removing uuid from url)_

* Add: AccountType enum for sake of readability(will be used more) 

* Del: duplicate function. 

* Add: get by username password. 

* Del: unused var. 

* Using: proper using of proxy path (for panel links) 

* Clean: unused var. 

* Add: new fields to str_config(proxy paths) 

* Del: using g.account.uuid instead of g.account_uuid. 

* Refactor. 

* Add: user/pass to hiddifypanel admin-links command(cli) 

* Add: user/pass to user admin links. 

* Clean up. 

* Add: login_required to quicksetup. 

* Add: authentication for user panel. 

* Add: user:pass to non-secure link too. 

* Add: user:pass to /admin/adminuser/ links. 

* Add: new format of domain showing (https://user:pass@domain.com) 

* Add: get current logged account apikey (draft) 

* Merge commit '26b0713eba52700902e5b530b62a276e3d7dae0a' into auth. 

* Using: new login_required. 

* Add: role property to user and admin models & implement Role enum new: override user/admin get_id method. 

* Using flask_login instead of old authenticator. 

* Add: flask_login & add flask_login.UserMixin to User and AdminUser models. 

* Support app changes. 

* Add: CORS for javascript calls. 

* Add: admin log api. 

* Add: auth for apps api. 

* Merge branch 'auth' of github.com:Iam54r1n4/HiddifyPanel into auth. 

* Merge pull request #71 from Iam54r1n4/fix-apps-api. 
  _fix: unboundlocalerror bug_

* Update ui. 

* Merge pull request #70 from Iam54r1n4/main. 
  _fix: info api profile title & short api expire time_

* Add: server-side(redis) session instead of client-side. 

* Add: redirect_to_user.html. 

* Add: role authentication for views. 

* Add: api auth, basic auth, old url backward compatibility middlewares chg: g.user and g.admin to g.account. 

* Add: some functions in utils. 

* Add: admin route backward compatibility. 

* Add: athentication with session. 

* Using non-assci name in building username because we send username and password with base64 encoding, so we're not limited to assci. 

* Add: auth to admin panel endpoints. 

* Refactor: user apis. 

* Add: get_user_roles to authentication.py. 

* Add: auth to admin apis. 

* Add: username & password to user model and admin model - filling the username and password (password saved in database as   plaintext) 

* Add: auth to api (incomplete) 

* Update ui. 

* Merge pull request #69 from Iam54r1n4/main. 
  _fix: profile title_

* Merge branch 'hiddify:main' into main. 

* Merge branch 'main' of github.com:Iam54r1n4/HiddifyPanel. 

* Update ui. 

* Update. 

* Merge pull request #68 from Iam54r1n4/main. 

* Merge branch 'hiddify:main' into main. 

* Update. 

* Merge branch 'main' of github.com:hiddify/Hiddify-Panel. 

* Merge pull request #67 from Iam54r1n4/commander. 

* Update ui. 

* Merge pull request #66 from Iam54r1n4/commander. 
  _Using commander.py_

* Merge branch 'hiddify:main' into commander. 

* Merge pull request #65 from Iam54r1n4/xui_importer. 

* Update: cli. 

* Update: using commander.py apply-user instead of running install.sh apply_users directly. 

* Update: apply_users command. 

* Update: using commander.py get-cert instead of using get-cert.sh directly. 

* Update: run_commander. 

* Merge pull request #64 from Iam54r1n4/fix-user-apis. 
  _Fix user apis_

* Add: nekobox app to ../apps/ api (in android platform) 

* Update version. 

* Update ui. 

* Add new ui. 

* Merge pull request #61 from Iam54r1n4/main. 
  _refactor: utils and other things_

* Add: version parameter type. 

* Move clean_ip to hutils/auto_ip_selector better imports. 

* Refactor: add types to funcitons. 

* Del: myip & myipv6 variables. 

* Merge pull request #60 from Iam54r1n4/main. 
  _fix: init_db bug_

* Merge pull request #59 from Iam54r1n4/xui_importer. 
  _Xui importer_

* Add: xui importer cli. 

* Add: xui importer. 

* Update translations. 

* Update translations. 

* Install app. 

* Update. 

* Merge pull request #56 from er888kh/main. 
  _Check all IP addresses while adding a domain_

* Make public ip finding more robust. 

* Check all ip addresses when adding domains. 

* Add missing dependency. 

* Merge pull request #58 from Iam54r1n4/main. 
  _fix: import bug_

* Merge pull request #53 from Iam54r1n4/refactor_api. 
  _Refactor user & admin APIs_

* Del: unnecessary imports. 

* Add: description to api schemas. 

* Refactor: admin APIs. 

* Refactor: user APIs. 

* Merge pull request #52 from Iam54r1n4/reform_apps_api. 
  _Reform apps api_

* Merge branch 'reform_apps_api' of github.com:Iam54r1n4/HiddifyPanel into reform_apps_api. 

* Merge pull request #51 from Iam54r1n4/reform_apps_api. 
  _Reform apps api_

* Merge branch 'hiddify:main' into reform_apps_api. 

* Merge pull request #50 from Iam54r1n4/reform_apps_api. 
  _Reform apps api_

* Reform: apps api. 

* Merge pull request #48 from Iam54r1n4/main. 
  _Add apps api_

* Reform: apps api. 

* Add: client apps icon for apps api. 

* Api things - change dto suffixes to Schema - add apps api - add expire_in field in short api. 

* Merge branch 'main' of github.com:Iam54r1n4/HiddifyPanel. 

* Merge branch 'hiddify:main' into main. 

* Merge pull request #47 from MichaelUray/main. 
  _Update UserAdmin.py_

* Update UserAdmin.py. 
  _Shows Telegram icons for all users in the admin panel, if Telegram is enabled.

Users which are not registered for Telegram are shown with greyed out disabled buttons, registered users with blue buttons.
It is a visual improvement to have all users aligned in the table._

* Merge branch 'main' of github.com:Iam54r1n4/HiddifyPanel. 

* Merge branch 'hiddify:main' into main. 

* Add: 'api/v2/admin/server_status/ api. 

* Add: "lang" field to admin '/me/' api DTO. 

* Create database tables with flask_migrate. 

* Add: "api/v2/admin/me" & "api/v2/user/me" api. 

* Merge pull request #46 from Iam54r1n4/main. 
  _remove UserLang duplicated defination_

* Remove duplicated definations. 

* Merge pull request #45 from Iam54r1n4/main. 
  _Complete user api_

* User area APIs tested and fixed. 

* Edit: create a jinja template for github isuee. 

* Add: lang field to User model. 

* Merge pull request #44 from er888kh/patch-1. 
  _Update requirements.txt_

* Update requirements.txt. 
  _Add missing dependency flask-apispec_

* Update. 

* Add def lang to info and tags to all-configs. 

* Better mtproxy. 

* Review code. 

* Merge pull request #42 from Iam54r1n4/main. 

* Merge github.com:hiddify/HiddifyPanel Add user.py api. 

* Fix typo. 

* Refactor github issue things. 

* Merge branch 'main' of github.com:Iam54r1n4/HiddifyPanel. 

* Add json5. 

* Hide v2ray configs. 

* Rm old. 

* Add six. 

* Add default warp_sites. 

* Merge branch 'main' of github.com:Iam54r1n4/HiddifyPanel. 

* Fix version in the dependencies. 

* Change name to hiddify manager. 

* Add po to json convertor. 

* Update name to hiddify manager. 

* Merge pull request #41 from Iam54r1n4/main. 
  _Internal server error issue_

* Feature: implement issue generator for internal server error (500.html) 

* Add: github_issue_generator.py. 

* Merge pull request #40 from pjrobertson/main. 
  _Translation Improvements_

* Further translation improvements. 

* Fix Chinese User UI for iOS + English slight modification. 

* Merge pull request #39 from pjrobertson/main. 
  _中国人 > 简体中文_

* 中国人 > 简体中文. 

* Remove: release_old. 

* Add tuic and hysteria to configs. 

* Fix. 

* Add hidden char. 

* Remove reality servernames as it is not really useful. 

* Add hysteria2 link. 

* Merge branch 'main' of github.com:hiddify1/HiddifyPanel. 

* Merge pull request #32 from elia07/hiddifyDevelop. 
  _fix creating new user via api, add delete api for deleting users_

* Fix creating new user via api, add delete api for deleting users. 

* Merge pull request #29 from er888kh/main. 
  _Generate X25519 keys using `python-cryptography`_

* General code refactor and optimization. 
  _Improve UUID checking_

* Optimize more imports. 

* Optimize imports. 

* Generate X25519 keys using `python-cryptography` 

* Remove not needed configs. 

* Update tuic link. 

* Update master. 

* Update tuic. 

* Remove utls in tuic and hystria. 

* Add tuic link and clashmeta. 

* Fix zero. 

* Add no-gui for update. 

* Merge branch 'v8' 

* Better upgrading database. 

* Better manage override admin. 

* Merge branch 'main' of github.com:hiddify1/HiddifyPanel. 

* Merge pull request #26 from mortza/fix-api-endpoints. 
  _Fixed filtering resources_

* Fixed filtering resources. 
  _Fixed user and admin filtering using get parameter_

* Merge pull request #23 from er888kh/main. 
  _Block QUIC to improve performance_

* Fix formatting. 

* Block QUIC to improve performance. 

* Update to v8 changes. 

* Merge branch 'v8' 

* Disable cache during update. 

* Convert old db to new. 

* Add pysql req. 



## 8.8.95 (2024-01-22)

#### Fix

* No admin bug. 



## 8.8.94 (2024-01-16)

#### Fix

* Singbox1.8. 



## 8.8.93 (2024-01-15)

#### Other

* Better singbox config. 



## 8.8.92 (2024-01-14)

#### Fix

* Bug for hiddify next. 



## 8.8.91 (2024-01-13)

#### Fix

* Bug in singbox. 



## 8.8.9 (2024-01-13)

#### Fix

* Bug in singbox 1.8. 



## 8.8.8 (2024-01-09)

#### Fix

* User agent issue for singbox 1.7 and hiddify next. 



## 8.8.7 (2024-01-09)

#### Fix

* Singbox 1.8 issue. 



## 8.8.6 (2024-01-09)

#### Fix

* Not import in hiddify bug. 



## 8.8.5 (2024-01-09)

#### Fix

* Bug in user agent. 



## 8.8.3 (2024-01-09)

#### New

* Add auto support for singbox 1.8 and 1.7. 

#### Fix

* Validation error bug. 

#### Other

* Merge pull request #62 from Iam54r1n4/v8. 
  _fix: validation error bug_



## 8.8.2 (2023-11-26)

#### Other

* Merge pull request #57 from Iam54r1n4/v8. 
  _fix bug in admin.py_

* Fix bug in admin.py. 

* Merge pull request #55 from Iam54r1n4/v8. 
  _fix bug in admin.py_

* Fix bug in admin.py. 



## 8.8.1 (2023-11-22)

#### Other

* Allow incompatible server names for reality. 



## 8.8.0 (2023-11-22)

#### Other

* NEW: allow reality to be incorrect. 



## 8.7.1 (2023-11-02)

#### Fix

* Bug. 



## 8.7.0 (2023-11-02)

#### Fix

* Api issues and resolve security issue. 



## 8.6.11 (2023-10-19)

#### Fix

* Req issue. 



## 8.6.8 (2023-10-12)

#### Fix

* Bug in russian lang. 



## 8.6.7 (2023-10-12)

#### New

* Add russian translation. 

#### Fix

* Add domain bug. 



## 8.6.6 (2023-10-08)

#### Changes

* Update hiddify next links. 



## 8.6.4 (2023-10-06)

#### New

* Add hidden chars. 

#### Fix

* Bug in translation. 



## 8.6.2 (2023-10-02)

#### Fix

* Backup? 

* Has update. 



## 8.6.1 (2023-09-13)

#### Other

* Link to right repo. 



## 8.6.0 (2023-09-13)

#### New

* Add beta release. 

#### Fix

* User count in sub admins. 

* Restore multiple admin types. 



## 8.5.3 (2023-09-12)

#### Fix

* Bug. 



## 8.5.2 (2023-09-12)

#### New

* Add reality h2. 



## 8.5.1 (2023-09-12)

#### Fix

* Bug in change reality id. 

* Translation. 



## 8.5.0 (2023-09-11)

#### Fix

* Backup, override owners. 

* Port already used. 

#### Other

* Fix api get uuid. 

* Update to latest hiddify next release. 



## 8.4.2 (2023-09-09)

#### Fix

* Autocdn ip. 



## 8.4.1 (2023-09-09)

#### New

* Add singbox user detector. 



## 8.4.0 (2023-09-08)

#### Fix

* Speed issue. 

* Speed issue in adding users. 



## 8.3.9 (2023-09-06)

#### Fix

* TB bug. 



## 8.3.8 (2023-09-04)

#### Fix

* V2ray typo. 



## 8.3.7 (2023-09-04)

#### New

* Change usage to TB if more than 1TB. 

#### Fix

* V2ray config. 



## 8.3.6 (2023-09-03)

#### Fix

* Bug in reality grpc apply config. 



## 8.3.5 (2023-09-03)

#### Fix

* Singbox bug. 



## 8.3.4 (2023-09-03)

#### Fix

* Reality singbox. 

#### Other

* Add Streisand deep link. 



## 8.3.3 (2023-09-02)

#### Changes

* Disable firewall by default. 

#### Other

* Add quic in singbox configs. 



## 8.3.2 (2023-08-31)

#### Fix

* Singbox hiddify. 

* Shadowsocks. 



## 8.3.1 (2023-08-31)

#### Fix

* Manifest bug. 

#### Other

* Adding ssh singbox config in all configs. 

* Remove last_version. 



## 8.3.0 (2023-08-31)

#### Other

* Invalidate cache in start. 



## 8.2.4 (2023-08-31)

#### Other

* Disable indexing by search engings. 

* Remove user secret from static files. 

* Make sure cache will be empty. 



## 8.2.3 (2023-08-30)

#### Other

* Fox" bug. 



## 8.2.2 (2023-08-30)

#### Fix

* Typo for quick settings. 



## 8.2.1 (2023-08-30)

#### Fix

* Short link. 



## 8.2.0 (2023-08-30)

#### Fix

* Utls in shadowtls. 



## 8.1.9 (2023-08-30)

#### Other

* Fix singbox comment. 

* Remove profile name. 



## 8.1.8 (2023-08-30)

#### Other

* Remove ssh singbox from all-configs. if your ssh server is enable your user can still use this link until next release. 



## 8.1.7 (2023-08-30)

#### Fix

* Multiple qrcode. 

#### Other

* Fix tag. 



## 8.1.6 (2023-08-30)

#### New

* Add prerelease. 

#### Fix

* One click qrcode. 

* Typo. 

* Prerelease. 

* Tag version. 

#### Other

* Test. 



## 8.1.4 (2023-08-30)

#### Other

* Better downgrade. 



## 8.1.3 (2023-08-30)

#### Other

* Show short link url. 



## 8.1.2 (2023-08-30)

#### Fix

* Disable user bug. 



## 8.1.1 (2023-08-30)

#### Fix

* Bug in disabling users. 



## 8.1.0 (2023-08-30)

#### Fix

* Download issue. 

#### Other

* Disable name in configs. 



## 8.0.3 (2023-08-29)

#### Other

* Use singbox config in hiddifynext. 

* Optimize get configs. 



## 8.0.2 (2023-08-29)

#### New

* Add download directly from github. 



## 8.0.1 (2023-08-29)

#### Other

* Better error logs. 

* Better fix. 



## 8.0.0 (2023-08-29)

#### New

* Disable cache on error. 

* Add short link for ease user access. 

* Add unified link. 

* Add auto page. 

* Add full singbox config. 

* Add UDP support for SSH. 

* Force user to double check decoy site. 

* Generate ssh key if empty. 

* Reset cache on change any config. 

* Change caching method to pickle. 

* Speed up the panel. 

* Speed up the panel by using redis. 

* Add auto button. 

* Add auto sub. 

* Add report analyser. 

* Add ssh keys to the backup. 

* Add ability to change reality keys. 

* Add unsigned https ip. 

* Better singbox config. 

* Add caching for speed up some process. 

* Add singbox config. 

* Add singbox config for ssh. 

* Add ssh server port. 

* Add ssh user support. 

#### Changes

* Remove access by https://ip if there is some domains. 

* Better singbox config. 

* Handle exception for redis. 

* Disable ui download. 

* Add dns to tcp. 

* Update usage. 

* Add restart on change ssh configs. 

* Remove ssh key info. 

* Disable caching. 

#### Fix

* Better open. 

* _ in the begin of profile name. 

* Caching error. 

* Rocket Loader. 

* Bug. 

* Bug in cache. 

* Usage info and sub. 

* Bug. 

* Font issue. 

* Rounding option in v2ray configs. 

* Ssh multiple time added. 

* Linux. 

* Lang issues. 

* Delay in updating proxies. 

* Ssh ip domain bug. 

* Ssh ip. 

* Bug. 

* Bug in secure link. 

* Bug in reality when asn failed. 

* Release message bug. 

* Clash config. 

* Singbox config. 

* Bug. 

* No commit message. 

* Bug in singbox. 

* Bug. 

* Singbox config issue. 

* Add remove bug. 

* Ssh keys json. 

* Bug. 

* Ssh config. 

* Bugs. 

* Singbox api. 

* Bug in userusage. 

* Singbox comment. 

* Singbox. 

* Bool. 

* Remove client. 

* Singbox error. 

* Config issue. 

* Bug. 

* Bug. 

* Bug. 

* Typo. 

* Bug. 

* Ssh liberty redis path. 

#### Other

* Fix bug with rocket loader. 

* Fewer click in auto link. 

* Better translations. 

* Add unlimited usage. 

* Update translations. 

* Remove expire days from report if it is more than 1000 days or if usage limit is more than 100,000G. 

* Better display of user info in non hiddify apps. 

* Update link maker. 

* Translate to persian. 

* Set default stack to system. 

* Merge branch 'main' of github.com:hiddify1/HiddifyPanel. 

* Merge pull request #18 from randomguy-on-internet/main. 
  _fixing IPv6 issue for resolving IPv6's behind domain in auto cdn_

* Fixing IPv6 issue for resolving IPv6's behind domain in auto cdn. 
  _adding brackets to avoid errors when converting domains to ipv6.

aaaa:bbbb:cccc:dddd -> [aaaa:bbbb:cccc:dddd]_

* Fix; v2ray bug. 

* New; add ssh in sub link. 

* Update. 

* Update. 

* Merge branch 'main' of github.com:hiddify1/HiddifyPanel. 

* Merge pull request #17 from randomguy-on-internet/main. 
  _Reality utls bug_

* Utls bug. 
  _fixing utls bug for reality configs_

* Fix singbox ip. 

* FIX: 

* Merge branch 'main' of github.com:hiddify1/HiddifyPanel. 

* Merge pull request #14 from randomguy-on-internet/patch-1. 
  _clash GRPC bug_

* Update link_maker.py. 

* Update link_maker.py. 



## 7.2.0 (2023-08-05)

#### New

* Add  compatibility for downgrade for ssh. 



## 7.1.9 (2023-07-30)

#### Fix

* Bugs. 



## 7.1.8 (2023-07-30)

#### Other

* Update license. 

* Update license. 



## 7.1.7 (2023-07-30)

#### Other

* Update. 



## 7.1.6 (2023-07-30)

#### New

* Update to open source. 

#### Other

* Apply formating. 



## 7.1.3 (2023-06-14)

#### New

* Remove old runs. 

#### Fix

* Reset bug. 

#### Other

* Add manually. 



## 7.1.2 (2023-06-13)

#### Other

* Update translation. 



## 7.1.1 (2023-06-13)

#### Fix

* Cpu percentage. 



## 7.1.0 (2023-06-13)

#### Fix

* Setting not saved. 

* Restart. 

* Loading issues. 

#### Other

* Update. 



## 7.0.9 (2023-06-04)

#### Fix

* Domain mode. 



## 7.0.8 (2023-06-04)

#### New

* Group modes. 



## 7.0.7 (2023-06-04)

#### New

* Remove gov websites from decoy sites. 

* Add domain fronting to the domains. 

#### Fix

* Telegram section will be displayed only when the domain. 

* Revert. 



## 7.0.6 (2023-05-30)

#### Fix

* Domain. 



## 7.0.5 (2023-05-30)

#### Fix

* Backup. 

* Ping. 

* Backup domains. 



## 7.0.4 (2023-05-30)

#### Fix

* Home not loading. 



## 7.0.3 (2023-05-29)

#### New

* If some configs are removed add them. 

* Remove old access. 

#### Fix

* Removing faketls domain. 

#### Other

* Remove grpc. 

* Remove grpc. 



## 7.0.2 (2023-05-29)

#### Fix

* Exception. 



## 7.0.1 (2023-05-29)

#### Fix

* Install bugs. 



## 7.0.0 (2023-05-29)

#### New

* Update panel. 

* Now get video from youtube if fail get it from local. 

* Add rest api. 

* Update lang. 

* Disable tcp mode. 

* Add more things. 

* Add head request. 

* Add head request. 

* Add head request. 

* Update backup with the new domains. 

* Add singbox usage. 

* Add notes for domain selection and add grpc reality. 

* Update lang. 

* Gun mode for grpc. 

* Fix ip behind cdn. 

* Add singbox api. 

* Remove hiddify:// on copy. 

* Do not inverse logs. 

* Add downgrade. 

* Add core selector. 

* Show error when autocdn format has problem. 

* Add reality. 

* Add worker domain. 

* Add multi domain reality, add core selector. 

* Add pt lang. 

#### Changes

* FirstAdmin->owner. 

#### Fix

* Bug. 

* Worker bug. 

* Downgrade. 

* Quick-setup bug. 

* Sublink only links. 

* Singbox bug. 

* Subonly links. 

* Lastindexof. 

* Installation finished. 

* Bug. 

* Bug. 

* Bug. 

* Singbox only support one servername. 

* New reality issues. 

* Typo. 

* Bug. 

* Sort bug. 

#### Other

* Better display logs. 

* Add: X-Real-IP header. 

* Remove extra text in footer. 



## 6.5.4 (2023-05-09)

#### Fix

* Bug in sort by expire date. 

#### Other

* Merge branch 'main' of github.com:hiddify1/HiddifyPanel. 

* Update custom.css. 

* Update custom.css. 



## 6.5.3 (2023-05-06)

#### Other

* Better result. 



## 6.5.2 (2023-05-05)

#### New

* Add dns. 

#### Fix

* Colors and result dialog. 



## 6.5.1 (2023-05-05)

#### New

* Add color in output. 

#### Other

* Update: lang. 



## 6.5.0 (2023-05-05)

#### New

* Add mode for warp. 



## 6.4.2 (2023-05-04)

#### Changes

* Fix shadowtls. 

#### Other

* Remove shadow tls from sub link. 



## 6.4.1 (2023-05-04)

#### New

* Show notification. 



## 6.4.0 (2023-05-04)

#### New

* Add warp plus code. 

#### Fix

* Bug. 



## 6.3.0 (2023-05-04)

#### Other

* Fix translate. 

* Enable warp. 



## 6.2.1 (2023-05-04)

#### Fix

* Base64. 



## 6.2.0 (2023-05-04)

#### New

* Add button. 

* Auto redirect to quick setup if not setup. 

#### Fix

* V2rayng. 

* Bug. 



## 6.1.7 (2023-05-04)

#### New

* Add HiddifyNG google play link. 



## 6.1.6 (2023-05-04)

#### Other

* Update links. 



## 6.1.4 (2023-05-03)

#### Fix

* Persian user profile. 



## 6.1.3 (2023-05-03)

#### New

* Add fragment in url. 



## 6.1.2 (2023-05-03)

#### Other

* Temp disable fragment. 



## 6.1.1 (2023-05-03)

#### Fix

* V2rayng download link. 



## 6.1.0 (2023-05-03)

#### Other

* Add profile title. 



## 6.0.1 (2023-05-01)

#### Other

* Update lang. 



## 6.0.0 (2023-05-01)

#### New

* Add fragment. 

* Add hiddify ng. 

* Better. 

* Add hiddify. 

* Add fragment. 

* Allow cdn and relay to add as only panel domains. 

#### Fix

* Color. 

#### Other

* UPDATE LANG. 

* Fix. 

* Update lang. 

* Temporary remove auto ip display. 

* Update lang. 

* Only 10 second to propose domains. 



## 5.0.3 (2023-04-27)

#### New

* Change back ios. 



## 5.0.2 (2023-04-26)

#### Other

* Change color. 



## 5.0.1 (2023-04-26)

#### New

* Add usage in sublink. 



## 5.0.0 (2023-04-26)

#### Fix

* Domain type. 

#### Other

* Better adding domains. 



## 4.5.1 (2023-04-26)

#### Other

* Update hiddify clash. 



## 4.5.0 (2023-04-26)

#### New

* Add ipv6 in cf api. 

* Fix v2rayng. 

* Add disable button and new style. 

* Better result page. 

* Add minimum valid users. 

* Add ip limits. 

* Organize better. 

#### Fix

* Bugs. 

* Bug. 

* Reality and xtls clash. 

* Bugs in update. 

* Usage bug. 

* Bug. 

* Selection. 

* Reality. 

* Bug. 

* Update. 

* Bug. 

* Auto cdn in user links. 

* Min users. 

#### Other

* Add hiddify links. 

* Better backup. 

* Fix. 

* Fix. 

* Fix. 

* Fix import. 



## 4.3.1 (2023-04-21)

#### Fix

* Backup date. 



## 4.3.0 (2023-04-21)

#### New

* Apple Colors. 



## 4.2.9 (2023-04-21)

#### New

* Super user infinit users. 



## 4.2.8 (2023-04-21)

#### Fix

* Bug. 



## 4.2.7 (2023-04-21)

#### Fix

* Sysout. 

* Typo. 



## 4.2.6 (2023-04-21)

#### New

* Priority in sublink only link. 



## 4.2.5 (2023-04-21)

#### Fix

* User. 



## 4.2.4 (2023-04-21)

#### Fix

* Backup bug. 

* Release issue. 



## 4.2.1 (2023-04-21)

#### Fix

* Usage. 



## 4.2.0 (2023-04-21)

#### New

* Click on admin. 

* Sub admins can have limits. 



## 4.1.2 (2023-04-20)

#### Fix

* No commit message. 



## 4.1.1 (2023-04-20)

#### Fix

* Bug. 



## 4.1.0 (2023-04-20)

#### New

* Fix backup. 

* Add permission for admin. 

#### Other

* Check datetime. 



## 4.0.5 (2023-04-19)

#### New

* Update. 

#### Fix

* Usage not counted. 



## 4.0.4 (2023-04-19)

#### Fix

* Alias. 



## 4.0.3 (2023-04-19)

#### Fix

* Xtls. 



## 4.0.2 (2023-04-19)

#### Fix

* Check proxy add. 



## 4.0.1 (2023-04-19)

#### Fix

* Bug. 



## 4.0.0 (2023-04-19)

#### New

* Telegram error check. 

* Change slave to agent. 

* Verify reality configs correctness. 

* Add warning for reality. 

* Disable warning to close. 

* Add telegram messages. 

* Send message to clients. 

* Reality is comming. 

* Add reality. 

* Ask before doing actions. 

* Better domain manager. 

* Hirarchy admin. 

* Multiple admin level, seperated usage per admin, parent_panel, backup to telegram, send message to telegram. 

* Add parent panel. 

#### Fix

* 7days. 

* Flow. 

* Bug in adding special char. 

* Flow bug. 

* Reality xtls. 

* No commit message. 

* Unsupported reality. 

* Update. 

* Permission erros and coutdown in persian error. 

* Telegram bot. 

* Bug. 

* Bug. 

#### Other

* Check. 

* Test: reality domains. 

* Chack organizarion name. 

* Add user link to msg. 

* Show warning for invalid alias. 

* Test: reality. 

* Add reality. 

* Add reality tag. 

* Update lang. 

* Remove speedtest. 

* Update to 1.8.1. 

* Fix. 

* Update: translation. 

* Fix bugs. 

* Update py. 



## 3.1.19 (2023-04-17)

#### Fix

* * domain. 



## 3.1.17 (2023-04-17)

#### Fix

* Bug in new installs. 



## 3.1.16 (2023-04-17)

#### Fix

* Fix new installation bug. 



## 3.1.15 (2023-04-17)

#### New

* Fix bug. 



## 3.1.14 (2023-04-16)

#### Fix

* Bot issue. 

#### Other

* Update. 



## 3.1.13 (2023-04-15)

#### Fix

* Loading dep. 



## 3.1.12 (2023-04-15)

#### Fix

* Bug. 

* Bug. 



## 3.1.10 (2023-04-15)

#### New

* Add confirmation before actions. 



## 3.1.9 (2023-04-15)

#### Other

* Fix. 



## 3.1.6 (2023-04-11)

#### Fix

* Yesterdays online. 



## 3.1.5 (2023-04-11)

#### New

* Fix the error in restoring configs. 



## 3.1.4 (2023-04-10)

#### Fix

* Bug. 



## 3.1.3 (2023-04-10)

#### Fix

* Issue with first setup. 



## 3.1.2 (2023-04-10)

#### Changes

* Add profile-web-page-url. 

#### Fix

* Persian ips. 

* Too much print. 



## 3.1.1 (2023-04-10)

#### Other

* Update. 



## 3.1.0 (2023-04-10)

#### New

* Optimize user changes. 

* Make footer in center for small devices. 

* Add more ips from ircf. 

#### Changes

* Change today's color. 

#### Fix

* Bot issue. 



## 3.0.9 (2023-04-09)

#### Fix

* Display issue of network. 

#### Other

* Update. 



## 3.0.8 (2023-04-09)

#### Fix

* Tgbot. 

#### Other

* Register bot if not registered. 

* Registerbot if not registered. 



## 3.0.7 (2023-04-09)

#### Fix

* G. 



## 3.0.6 (2023-04-09)

#### New

* Update translations. 

#### Other

* Force register bot if not registered. 



## 3.0.5 (2023-04-09)

#### Fix

* Folder size. 

* Versioning. 

* Bot add loading animation. 



## 3.0.4 (2023-04-09)

#### Fix

* Issues. 

* Issues. 



## 3.0.3 (2023-04-09)

#### Fix

* Error in changelog. 

#### Other

* Add auto cdn ip maker. 



## 3.0.2 (2023-04-09)

#### Other

* Remove change log. 



## 3.0.0 (2023-04-09)

#### New

* Show pwa notif only in home screen. 

* Update translation, remove tuic. 

* Fix package ended. 

* Add username in the link. 

* Add identify ip from X-Forwarded-For. 

* Auto update tails. 

* Add other country. 

* Search by english keyword in persian. 

* Remove netdata add history. 

* Add auto dark mode detector. 

* New sidebar. 

* Fix fingerprint. 

* Add darkmode. 

* Add new shatel. 

* Add wingsx. 

* Better user update usage. 

#### Changes

* Better style. 

#### Fix

* No commit message. 

* Style. 

* Daily, montly and weekly. 

* Vpn window for other countries. 

* Dark mode issues. 

* Progress bar. 

* Typo. 

* Last usage. 

* Usage. 

* Style. 

* No commit message. 

* No commit message. 

* Sidebar in xs. 

* Remaing days. 

* Big int issues. 

* Daily usage. 

* No commit message. 

* Do not show countdown in status. 

* Close boxes after search. 

* Bug. 

* Issues. 

* Bug. 

* Some updates. 

* Bug. 

* Template. 

* Pwa notification. 

* Dark mode issue. 

* No commit message. 

* Reset xray on model change. 

#### Other

* Update lang. 

* Disable netdata fix new user. 

* Add disbale user, network speed and more. 

* Remove sub links when package ended, add more and more. 

* Remove disk on small screens. 

* Show 3 column in big screens. 

* Update. 

* Add hiddify. 

* Remove test. 

* Add multiple process in dashboard. 

* Fix. 

* Fix big int. 

* Not using  * in ssl domains. 

* New; add support for * domains. add search in settings,fix bugs. 

* Update. 

* Fix the problem. 

* Fix bug. 

* Reduce build time. 

* Fix release message. 

* Commit all changes. 

* Add: cloudflare api. 



## 2.9.0 (2023-03-30)

#### New

* Select random operator if not detected. select random operator if multiple item exist. 

* Add notif when outdated. 

* Add asiatech. 

* Better information and fixed ip. 

* Add window only if cdn exist. 

* Fixing asn in sub link. 

* Show timer in apply configs. 

* Add ip info in sub link. 

* Add ip debug info in speed test. 

* Add backward compatibility. 

* Show version in error page. 

* Add clean ip support. 

* Add cloudflare api. if you add cloud flare api it will create or update domains automatically. 

* Add alias support for parent domain. 

* Central panel. 

* Disallow bot and search engines to access the site. 

* Add country for specific country needs. 

* Add restart action. 

* Auto reset if needed after changing configs. 

* Update. 

* Show notif on ios. 

* Add splash. 

* Same format. 

* Add splash screen. 

* Adding panel app :) 

* Increase user page size to 50. 

* Add encryption to vmess. 

* Add tls_h2 in sublinks. 

* Add h2 protocols. 

* Add encryption for vmess for better hidding traffic in http. 

* You can now remove port 80 and 443 from the proxies. 

* Convert old domain fronting configs to fake. 

* Open bot directly in telegram. 

* Open tgbot directly in telegram. 

* Add h2 support. 

* Add ios, none, edge, random to the utls settings. 

* Do not show http if http is diabled. 

* Add ports to all configs and in clash configs. 

* Make proxynames editable. 

* Add multiple ports. 

* Support multiple ports. 

#### Changes

* Ip only for auto cdn ip. 

* Better manage db init. 

* Better manage domains. 

* Show android webapp. 

* Remove  fingerprint. 

* Update android hiddify app. 

* Remove fingerprint. 

* Add get_domain. 

* Optimise link maker. 

* Move utls config to tls config. 

#### Fix

* No commit message. 

* Mokhaberat. 

* Error prune auto cdn ip. 

* Has cdn. 

* Zitel. 

* All errors. 

* Twitter. 

* Asn bug. 

* Video playback. 

* Cleanip. 

* Bug. 

* Error in access user page in some domains. 

* Description. 

* Backward compatibility. 

* Massive sysout. 

* Not showing all proxies. 

* Clean ip bug. 

* User ip. 

* Bug. 

* Auto cdn ip proxy. 

* Bugs. 

* Bug. 

* Bug. 

* Update. 

* Bug. 

* Resolve a problem. 

* Duplicate bug  in alias. 

* Configs in bot notworking. 

* Quick setup bug. 

* Bug in first install. 

* Show apply config on new domain. 

* Quicksetup bug. 

* Db init. 

* Telegram start. 

* New telegram bot format. 

* Bugs. 

* Compile issue. 

* Release. 

* Bugs. 

* Test. 

* Do not show fake domains in user links. 

* Bug in user page in title. 

* Bug in incorrect admin link print. 

* Workflow. 

* Release bug. 

* Exception in number of days. 

* Add delay before finishing the request in applying actions. 

* Showing toast on pwa. 

* Video and toast. 

* Bug not updating users. 

* Typo. 

* Bug in db domain. 

* First setup. 

* Bug in init db. 

* Not showing home title in homepage. 

* Update translations. 

* Disable some protocols in clash. 

* Clash bugs. 

* Add port. 

* Bug in model. 

* Cipher. 

* Configs in clash. 

* Clash links. 

* Clash proxies. 

* Ptls bug. 

* Clash proxies. 

* H2 links. 

* Linkmaker. 

* Import. 

* Add vless xtls. 

* H2 not showing. 

* Show v2ray configs if enabled. 

* Db. 

* Ports. 

* Typo. 

* Alpn. 

* Bug in clash. 

* Bug in ws. 

* Domain bug. 

* Clash bug. 

* Revert using api for disconnect connect users. 

* Domain. 

* Typo. 

* Python bug. 

* Typo. 

* Not showing apply config dialog. 

* Delete h1 in transport. 

* Sublink for ios. 

* Vmess host not in link. 

#### Other

* Fix bug. 

* Add hiddify. 

* Remove dynaconf. 

* Update and remove extra libs. 

* Refactor. 

* Update. 

* Add clean ip support. 

* Disbale main workflow. 

* New. 

* Test. 

* Test release. 

* Fix compile error. 

* Check. 

* Fix big. 

* New test. 

* Fix. 

* Fix. 

* Fix. 

* Fix. 

* Test. 

* Set to python 3.10. 

* Add version. 

* Pypi to hiddify-config. 

* Update. 

* Test. 

* Fix support page. 

* Remove extra log. 

* Fix xtls alpn. 



## 1.6.8 (2023-03-09)

#### Fix

* Bug in clash config. 



## 1.6.7 (2023-03-08)

#### New

* Revert back to old clash config. 

#### Changes

* Update clash configs. 

#### Fix

* Bug in clash profiles. 



## 1.6.6 (2023-03-08)

#### Fix

* Restore backup when no start days. 



## 1.6.5 (2023-03-08)

#### New

* Add backup by cli. 

#### Changes

* Better backup file name format. 

#### Fix

* Change subscription link to trojan for better compatibility. 

* When package days is not defined. 



## 1.6.0 (2023-03-08)

#### New

* New telegram bot features. 

* Update bot features. 

#### Fix

* Telegrambot. 

#### Other

* Merge branch 'main' of github.com:hiddify/HiddifyPanel. 

* Merge pull request #9 from ehsanmqn/main. 
  _Cleaning some codes based on PEP8 and adding description to the vital classes_

* Merge branch 'main' into main. 

* Short descriptions added to the classes and functions within the user.py file. 

* Imports rearranged. 

* Useless imports removed. 

* File reorganized according to PEP8 principles for increasing code readability. 

* File reorganized according to PEP8 principles for increasing code readability. 

* Merge remote-tracking branch 'refs/remotes/origin/main' 

* File reorganized according to PEP8 principles for increasing code readability. 

* File reorganized according to PEP8 principles for increasing code readability. 



## 1.5.3 (2023-03-08)

#### Changes

* Add username to bot. 

#### Fix

* Bug in v2rayng link. 

* Bug in launching app if telegram has error. 



## 1.5.2 (2023-03-08)

#### Fix

* Bug in v2ray. 



## 1.5.1 (2023-03-08)

#### Fix

* Bug in editing page. 



## 1.5.0 (2023-03-08)

#### New

* Make proxy path to be changed. 

* Add multi remove. 

* New path format. 

* Better displaying usage in ios. 

* Change proxy_path for more security. 

* Add random path for vmess,vless,v2ray,trojan. 

#### Changes

* Change base proxy path to too advanced. 

* V2ray to ss. 

#### Fix

* Bug in import users. 

* Bug in editing users. 

* Domain not showing in the domain section. 

* Red color in user page. 

* Theme bug. 

* Vmess grpc link. 

* Usage. 

* Bug in grpc vmess. 

* Wrong user usage update. 

* Remove old user when change uuid. 

* Bug not disconnecting a user on delete. 

* Add_path. 

* More stable green cadre. 



## 1.4.2 (2023-03-07)

#### New

* Add /admin without / as correct path. 

#### Fix

* Bug in telegrambot. 



## 1.4.1 (2023-03-07)

#### Fix

* Bug in add new user. 



## 1.4.0 (2023-03-07)

#### New

* Show usage in user panel. 

#### Fix

* Add some log into bot. 

* Telegram bot. 

#### Other

* Update translation. 

* Merge pull request #7 from ehsanmqn/main. 
  _Updating the telegram bot commands_

* Merge branch 'main' into main. 

* Text updated. 

* Text updated. 

* Text updated. 

* Text updated. 

* Docs added to telegram commands. 

* Docs added to telegram commands. 

* Doc added to prepare_welcome_message. 

* Doc added to prepare_welcome_message. 

* Doc added to prepare_help_message. 

* Doc added to prepare_me_info. 

* Start command changed to hello. 

* Imports rearranged. 

* Command_me completed. 

* Command_me updated. 

* Command_start updated. 

* Command_start updated. 

* Prepare_me_info added. 

* Function name updated to command_info. 

* Function name updated to command_start. 

* Command_help added. 

* Information bot updated. 

* Information bot added. 

* Information bot added. 

* Useless imports removed. 

* Welcome message updated. 

* Welcome message updated. 

* Imports reorganized. 

* Text formatted according to PEP8. 

* Useless imports removed. 

* Useless lines removed from the update_usage_callback function. 

* Useless lines removed from the get_usage_msg function. 

* Useless lines removed from the send_welcome function. 

* File reformatted according to PEP8. 

* File reorganized. 

* File reorganized. 

* Useless commented get function removed. 

* Useless imports removed. 

* Import moved to top. 

* Import moved to top. 

* Useless comment removed. 

* File reformatted according to PEP8. 

* Imports reorganized for better code review. 

* Useless commented import removed. 

* .vscode removed from the project. 



## 1.3.0 (2023-03-07)

#### New

* Add reset user's package (usage and days) 

#### Changes

* Better displaying how to change user mode. 



## 1.2.2 (2023-03-07)

#### New

* Change the default link. 



## 1.2.1 (2023-03-07)

#### New

* New favicon. 



## 1.2.0 (2023-03-07)

#### New

* Add hour in the fakeip. 

* Add fetch date as ip in the subscription link. 

* Add v2rayng as supported link for android. 

* Hide decoy port setting :D. 

* Speedup user add or remove using renewed api. 

* Speedup xray fire user. 

* Add expire days in subscription link. 

* Add usage to subscription link. 

* Add disable to users. 

* Add telegram bot command for create multiple account. 

* Users expire time will now starts from their first connection. 

#### Changes

* Add all proxies again in the clash config. 

#### Fix

* Add space in subscription link. 

* Log in xray api. 

* Bug in xray api. 

* Bug in update usage. 

* Bug in calculating active users. 

* Bug in cli. 

* Not showing reset time. 

* Bug in date. 

* Name in clash. 

#### Other

* Fix exception in remove. 

* Add log in xray api. 

* Update xray log. 



## 1.1.2 (2023-03-05)

#### New

* New icon. 

* Change backend uwsgi. 



## 1.1.1 (2023-03-05)

#### Fix

* Bug in update when one usage used out usage. 



## 1.1.0 (2023-03-05)

#### New

* Enable tuic and shadowtls for public. 

* Enable tuic for all. 

* Add tuic !!! The fastest protocol with lowest latency. 

* Add alias for telegram. 

* Add support for shadowtls. 

* Make proxies selectable for each domain. 

* Show selectable proxies first. 

* Remove all proxies. 

* Better organization of proxies in clash. 

* Add a profile for each domain in clash configs. 

* Show apply config on changing domain only when needed. 

* Add description for adding alias. 

* Add custom name for domain (alias) 

* Allow users to select proxies from only one domain in clash. 

* Add sequential, loadbalance and auto as an option to select specific domain in clash. 

* Add load balance in clash rules. 

* Telegram bot, We need contributors in this part. 

* Add simple telegram bot. 

#### Changes

* Add demo bot request. 

* Improve translations. 

#### Fix

* Tuic will not shown in normal clash. 

* Change tuic params. 

* Bug in clash config for tuic. 

* Clash config with tuic. 

* Showing tuic only for direct domains. 

* Tuic in proxies. 

* Bug in clash profile. 

* Not displaying green box in update. 

* Db version. 

* Add consistency in changing dbversion. 

* Bug in enabling tuic and shadowtls. 

* Telegram link bug. 

* Hide release commits. 

* Alias name in clash config. 

* Bug in showing a specific domain. 

* Bug in clash config. 

* Bug in usage reset time. 

* Bug in showing last day. 

#### Other

* Fix cert error in tuic. 

* Change release log format. 



## 1.0.0 (2023-02-28)

#### New

* Add default parent domain. 

#### Fix

* Show success message only on end. 

#### Other

* Add utls to be configured. 

* Show domain change window after quick setup. 



## 0.9.111 (2023-02-28)

#### Other

* Add dev branch. 



## 0.9.110 (2023-02-28)

#### Fix

* Restore error. 



## 0.9.109 (2023-02-28)

#### Fix

* Adding unique id for old installations. 



## 0.9.108 (2023-02-28)

#### Fix

* Bug in quick setup. 

* Bug in quick setup. 



## 0.9.107 (2023-02-28)

#### Fix

* Bug in restore domain. 



## 0.9.106 (2023-02-28)

#### Fix

* Bug in child. 



## 0.9.105 (2023-02-28)

#### Fix

* Bug in child_ip. 



## 0.9.104 (2023-02-28)

#### Fix

* Bug in admin layout. 



## 0.9.103 (2023-02-28)

#### New

* Add actions in parent. 



## 0.9.102 (2023-02-28)

#### Fix

* Bug in setting child. 



## 0.9.101 (2023-02-28)

#### New

* Add api. 



## 0.9.100 (2023-02-28)

#### Other

* Change default fingerprint to andorid. 



## 0.9.99 (2023-02-28)

#### New

* Add telegram_bot_token. 

* Better verify domain. 



## 0.9.98 (2023-02-27)

#### Fix

* Relase message bug. 

* Bug in release message. 

* Version error. 

#### Other

* Update. 

* Update. 



## 0.9.96 (2023-02-27)

#### Other

* Update relative date to days if less than 2 months. 



## 0.9.95 (2023-02-27)

#### Fix

* Bug in user panel. 

#### Other

* Update. 



## 0.9.94 (2023-02-27)

#### Other

* Update. 

* Update stash and shadowlink. 



## 0.9.93 (2023-02-27)

#### Other

* Fix bug when user max usage is zero. 

* Add parent_domains to cli. 



## 0.9.92 (2023-02-27)

#### Other

* Fix expirydate issue. 



## 0.9.91 (2023-02-26)

#### Other

* Fix bool config. 



## 0.9.90 (2023-02-26)

#### Other

* Fix last online. 



## 0.9.89 (2023-02-26)

#### Other

* Fix. 

* Fix bug. 



## 0.9.88 (2023-02-26)

#### Other

* Add pyyaml. 



## 0.9.87 (2023-02-26)

#### Other

* Remove update db notif. 



## 0.9.86 (2023-02-26)

#### Other

* Fix auto update usage. 

* Update db on init. 



## 0.9.85 (2023-02-26)

#### Other

* Fix update usage. 



## 0.9.84 (2023-02-26)

#### Other

* Fix null bug. 



## 0.9.83 (2023-02-26)

#### Other

* Update. 

* Add chart for online user. 

* Add online users. 



## 0.9.82 (2023-02-26)

#### Other

* Fix bad bug. 



## 0.9.81 (2023-02-26)

#### Other

* Add tun mode in clash proxies. 

* Not exist domain. 



## 0.9.80 (2023-02-26)

#### Other

* Update. 

* Fix bug in import users. 

* Update centeral panel layoutt. 



## 0.9.79 (2023-02-26)

#### Other

* Fix. 



## 0.9.78 (2023-02-26)

#### Other

* Fix. 

* Update. 



## 0.9.77 (2023-02-26)

#### Other

* Update. 



## 0.9.76 (2023-02-26)

#### Other

* Fix change lang issue. 



## 0.9.75 (2023-02-26)

#### Other

* Fix backup. 

* Update. 



## 0.9.74 (2023-02-26)

#### Other

* Fix. 

* Update. 



## 0.9.73 (2023-02-26)

#### Other

* Fix. 



## 0.9.72 (2023-02-26)

#### Other

* Fix. 



## 0.9.71 (2023-02-26)

#### Other

* Fix update panel. 



## 0.9.70 (2023-02-26)

#### Other

* Update. 

* Update. 

* Fix updateusage. 

* Fix. 

* Update panel. 

* Fix. 

* Fix child. 

* Fix db. 

* Add config cli. 

* Fix. 

* Fix domains. 

* Update. 

* Updaet. 

* Add unique id. 

* Update. 

* Update. 

* Update. 

* Update. 

* Add json. 

* Update. 

* Fix. 

* Update. 

* Update. 

* Add set config from cli. 

* Fix all configs. 

* Add parent panel. 



## 0.9.66 (2023-02-25)

#### Other

* Fix multi link. 

* Merge branch 'main' of github.com:hiddify/HiddifyPanel. 

* Update README.md. 



## 0.9.65 (2023-02-24)

#### Other

* Fix restore and backup of domains. 



## 0.9.64 (2023-02-23)

#### Other

* Fix backup. 



## 0.9.63 (2023-02-23)

#### Other

* Fix backup. 



## 0.9.62 (2023-02-22)

#### Other

* Fix loop. 



## 0.9.61 (2023-02-22)

#### Other

* Fix. 



## 0.9.60 (2023-02-22)

#### Other

* Add hiddify desktop. 

* Add ability to change proxy path. 

* Add restore settings enable disable. 

* Add more info about relay and fake. 



## 0.9.59 (2023-02-22)

#### Other

* Update. 

* Update. 

* Update. 



## 0.9.58 (2023-02-22)

#### Other

* Add autopep8. 

* Adding domain specific configuration. 

* Add reset after 30 days. 

* Add version to home. 



## 0.9.57 (2023-02-17)

#### Other

* FIX. 

* Change  admin secret to lower case. 

* Update ios. 



## 0.9.56 (2023-02-16)

#### Other

* Add ios. 



## 0.9.55 (2023-02-16)

#### Other

* Fix stash link in ios. 



## 0.9.54 (2023-02-16)

#### Other

* Fix support box in mobile. 



## 0.9.53 (2023-02-16)

#### Other

* Add version in menu. 



## 0.9.52 (2023-02-16)

#### Other

* Add version to sidebar. 



## 0.9.51 (2023-02-16)

#### Other

* Fix layout. 



## 0.9.50 (2023-02-16)

#### Other

* Update. 

* Notify domain change on backup. 



## 0.9.49 (2023-02-16)

#### Other

* Update. 



## 0.9.47 (2023-02-16)

#### Other

* Fix click. 



## 0.9.46 (2023-02-16)

#### Other

* Fix error. 



## 0.9.45 (2023-02-16)

#### Other

* Update. 

* Fix not showing date in firefox. 



## 0.9.44 (2023-02-16)

#### Other

* Update. 

* Fix error in change proxy apply. 



## 0.9.43 (2023-02-16)

#### Other

* Remove some dependencies. 



## 0.9.42 (2023-02-16)

#### Other

* Update. 



## 0.9.41 (2023-02-16)

#### Other

* Update. 



## 0.9.40 (2023-02-15)

#### Other

* Fix exception. 



## 0.9.39 (2023-02-15)

#### Other

* Add domain name to clash proxy. 

* Allow ipv6. 

* Update. 

* Fix invalid domain names for decoy website. 



## 0.9.38 (2023-02-15)

#### Other

* Add hiddify proxy v0.11. 



## 0.9.37 (2023-02-15)

#### Other

* Update. 

* Update. 



## 0.9.35 (2023-02-15)

#### Other

* Add version. 

* Add version in panel. 



## 0.9.33 (2023-02-15)

#### Other

* Add hiddify android v 0.10. 

* Add global client fingerprint. 

* Fix ipv6. 



## 0.9.31 (2023-02-15)

#### Other

* Fix full install everytime. 



## 0.9.30 (2023-02-15)

#### Other

* Fix represntation of fake in user page. 



## 0.9.29 (2023-02-15)

#### Other

* Add fake domain. 



## 0.9.28 (2023-02-15)

#### Other

* Add fake domain. 



## 0.9.27 (2023-02-15)

#### Other

* Update. 



## 0.9.26 (2023-02-14)

#### Other

* Update. 



## 0.9.25 (2023-02-14)

#### Other

* Update. 



## 0.9.22 (2023-02-14)

#### Other

* Fix. 



## 0.9.21 (2023-02-14)

#### Other

* Remove direct links in CDN. 



## 0.9.20 (2023-02-14)

#### Other

* Fix direct domain db. 



## 0.9.19 (2023-02-14)

#### Other

* Add ipv6 connections. 



## 0.9.18 (2023-02-14)

#### Other

* Update multi domain. 



## 0.9.17 (2023-02-14)

#### Other

* Update. 



## 0.9.15 (2023-02-14)

#### Other

* Add multi link. 



## 0.9.14 (2023-02-14)

#### Other

* Update. 



## 0.9.13 (2023-02-14)

#### Other

* Fix. 



## 0.9.12 (2023-02-13)

#### Other

* Add fingerprint in share link. 



## 0.9.11 (2023-02-13)

#### Other

* Remove need for apply for adding a user. 

* Update. 



## 0.9.10 (2023-02-10)

#### Other

* Add grpc direct. 

* Add relay mode. 



## 0.9.9 (2023-02-09)

#### Other

* Update quick setup. 

* Update. 

* Update. 



## 0.9.8 (2023-02-09)

#### Other

* Update. 



## 0.9.7 (2023-02-09)

#### Other

* Fix translation. 



## 0.9.6 (2023-02-09)

#### Other

* Add specified ip for cdn hosts. 

* Add forced ip. 



## 0.9.5 (2023-02-09)

#### Other

* Remove. 



## 0.9.4 (2023-02-09)

#### Other

* Update. 



## 0.9.3 (2023-02-09)

#### Other

* Update. 

* Add fingerprint. 

* Add fingerprint. 



## 0.9.2 (2023-02-09)

#### Other

* Fix xtls vision. 

* Remove trojan and add vless. 

* Remove xtls direct. 



## 0.9.1 (2023-02-09)

#### Other

* Fix layout. 

* Update. 

* Update link. 

* Update. 

* Update. 

* Update. 

* Update. 

* Update. 

* Add link from domain to admin page. 

* Update ui. 

* Ram update. 

* Update. 

* Update. 

* Update. 

* Update. 

* Update. 

* Update. 

* Update. 

* Update. 

* Update ux and ui in admin. 

* Update. 

* Fix emergency access. 

* Fix. 

* Organizing db. 

* Fix error csrf. 

* Fix. 

* Update. 

* Remove verification. 

* Fix setting admin. 

* Fix. 

* Update. 

* Update. 

* Fix caps domain. 

* Fix v2ray. 

* Remove csrf. 

* Fix not creating same uuid in restore. 

* Fix alpn. 

* Remove alpn for h2 in links. 

* Fix faketls. 

* Update. 

* Update. 

* Update. 

* Update link_maker.py. 

* Update link_maker.py. 

* Update. 

* Fix. 

* Update icon. 

* Update usage. 

* Add domain to infoname. 

* Fix bug. 

* Fix domain fronting. 

* Showing alert before leaving apply settings page. 

* Update. 

* Lang update. 

* Update. 

* Fix. 

* Fix. 

* Fix fake. 

* Update. 

* Fix bug. 

* Add temporary link. 

* Fix bug. 

* Fix. 

* Update. 

* Update. 

* Add an option to select between monthly and total. 

* Update translation. 

* Add some configs. 

* Update. 

* Update. 

* Update translation. 

* Add backup and restore. 

* Fix support link. 

* Fix admin link. 

* Update. 

* Fix bug in domain. 

* Update. 

* Fix ip removed. 

* Update lang. 

* Validate domain. 

* Fix domian. 

* Add user error message. 

* Fix bug. 

* Update. 

* Fix. 

* Add first setup. 

* Fix init bug. 

* Update. 

* Update. 



## 0.9.0 (2023-02-04)

#### Other

* Update translations. 

* Update. 

* Add donation link. 

* Add apply config for users. 

* Update. 

* Add branding link. 

* Update. 

* Update ui. 

* Full. 

* Update. 

* Add full install option. 

* Update. 

* Update. 

* Update telegram lib. 

* Quicksetup lang. 

* Add admin language. 

* Update. 

* Update admin lang. 

* Fix delete user error. 

* Fix. 

* Update. 

* Fix update db version. 

* Update db. 

* Add log for initdb. 

* Update. 

* Fixed. 

* Fix user. 

* Update translations. 

* Update. 

* Charts info. 

* Update. 

* Update. 

* Add telegram lib. 

* Fix float. 

* Fix sqlalchemy. 

* Update. 

* Remove some logs. 

* Update. 

* Add temporary rule for firewall to access. 

* Random port. 

* Fix not reset the usage. 

* Add icon, add temp port update message. 

* Update remove incomplete configs. 

* Small fix. 

* Fix user remove error and more checkings. 

* Fix link. 

* Fix link. 

* Add api. 

* Fix usage shown. 

* Update. 

* Add log finish message. 

* Add default user link info message for quick setup. 



## 0.8.6 (2023-02-03)

#### Other

* Update. 



## 0.8.5 (2023-02-03)

#### Other

* Fix grpc link. 

* Fix normal clash link. 

* Fix bug in versioning. 



## 0.8.4 (2023-02-03)

#### Other

* Fix bugs. 



## 0.8.3 (2023-02-03)

#### Other

* Fix uuid. 



## 0.8.2 (2023-02-03)

#### Other

* Fix vmess links. 

* Fix grpc. 

* Fix ios links. 

* Fix bug in telegram and not showing all emails. 



## 0.8.1 (2023-02-02)

#### Other

* Fix bug in time. 



## 0.8.0 (2023-02-02)

#### Other

* Update. 

* Update. 

* Update. 

* Update ui. 

* Update style. 

* Update style. 

* Update. 

* Update http-opts. 

* Fix. 

* Update link maker. 

* Fix port bug. 

* Update. 

* Fix bug. 

* Remove vless and xtls and shadowtls for normal clash. 



## 0.7.0 (2023-02-02)

#### Other

* Update. 

* Update clashlinks. 

* Fix update usage. 



## 0.6.0 (2023-02-02)

#### Other

* Update. 

* New translations. 

* Fix. 

* Fix bug. 



## 0.5.0 (2023-02-02)

#### Other

* Update translation. 

* Add auto update translations. 

* Fix import. 

* Add mo files. 

* Trying to fix translation issues. 

* Update translations. 

* Update. 

* Add translations. 

* Update. 

* Add link. 

* Add chinese lang. 

* Add auto translate. 

* Fix. 

* Fix translations. 

* Remove changing proxy path. 

* Add success notification to domain. 

* Remove category from config. 

* Update. 

* Update. 

* Fix decoy site to domain. 

* Update order. 

* Update. 

* Reorgnizing. 

* Fix cli bug. 

* Update. 

* Update. 



## 0.4.0 (2023-02-01)

#### Other

* Update FUNDING.yml. 

* Update. 

* Add selectable proxies. 

* Selectable proxy. 

* Update. 

* Latest update. 

* Update. 

* Adding tuic, shadowtls, ssr, ui improvment. 

* Update user ui. 

* Update. 



## 0.3.0 (2023-01-22)

#### Other

* Include static files. 

* Update cli. 

* Fix prob. 



## 0.0.2 (2023-01-22)

#### Other

* Update. 

* Update. 

* Update and reset automatically the usage. 



## 0.0.1 (2023-01-21)

#### Other

* Remove windows and mac. 

* Update. 

* Add update storage. 

* First working version. 

* Create default db. 

* Update to bootstrap 5. 

* ✅ Ready to clone and code. 

* Initial commit. 



