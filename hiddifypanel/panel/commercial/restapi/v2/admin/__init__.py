from apiflask import APIBlueprint, Schema
from apiflask.fields import Integer, String
from flask import g
from hiddifypanel.models import AdminUser

bp = APIBlueprint("api_admin", __name__, url_prefix="/<proxy_path>/api/v2/admin/", enable_openapi=True)

bp_uuid = APIBlueprint("api_admin_uuid", __name__, url_prefix="/<proxy_path>/<uuid:secret_uuid>/api/v2/admin/", enable_openapi=True)


def init_app(app):

    with app.app_context():
        from .admin_info_api import AdminInfoApi
        from .server_status_api import AdminServerStatusApi
        from .admin_user_api import AdminUserApi
        from .admin_users_api import AdminUsersApi
        from .admin_log_api import AdminLogApi
        bp.add_url_rule('/me/', view_func=AdminInfoApi)
        bp.add_url_rule('/server_status/', view_func=AdminServerStatusApi)
        bp.add_url_rule('/admin_user/<uuid:uuid>/', view_func=AdminUserApi)
        bp.add_url_rule('/admin_user/', view_func=AdminUsersApi)
        bp.add_url_rule('/log/', view_func=AdminLogApi)

        from .user_api import UserApi
        from .users_api import UsersApi
        bp.add_url_rule('/user/<uuid:uuid>/', view_func=UserApi)
        bp.add_url_rule('/user/', view_func=UsersApi)

        bp_uuid.add_url_rule('/me/', view_func=AdminInfoApi)
        bp_uuid.add_url_rule('/server_status/', view_func=AdminServerStatusApi)
        bp_uuid.add_url_rule('/admin_user/<uuid:uuid>/', view_func=AdminUserApi)
        bp_uuid.add_url_rule('/admin_user/', view_func=AdminUsersApi)
        bp_uuid.add_url_rule('/log/', view_func=AdminLogApi)
        bp_uuid.add_url_rule('/user/<uuid:uuid>/', view_func=UserApi)
        bp_uuid.add_url_rule('/user/', view_func=UsersApi)

    app.register_blueprint(bp)
    app.register_blueprint(bp_uuid)


def has_permission(model) -> bool:
    '''Check if the authenticated account has permission to do an action(get,insert,update,delete) on the another admin'''
    if not g.account.uuid != AdminUser.get_super_admin_uuid() and model.parent_admin_id != g.account.id:  # type: ignore
        return False
    return True


class SuccessfulSchema(Schema):
    status = Integer()
    msg = String()
