import datetime
import uuid as uuid_mod
from sqlalchemy_serializer import SerializerMixin
from dateutil import relativedelta
from hiddifypanel.panel.database import db
from enum import auto
from strenum import StrEnum
from flask_babelex import gettext as __
from flask_babelex import lazy_gettext as _


class UserMode(StrEnum):
    """
    The "UserMode" class is an enumeration that defines five possible modes: "no_reset", "monthly", "weekly",
    "daily", and "disable". These modes represent different settings that can be applied to a user account,
    such as the frequency at which data is reset or whether the account is currently disabled. The class is
    implemented using the "StrEnum" base class and the "auto()" function to generate unique values for each mode.
    """
    no_reset = auto()
    monthly = auto()
    weekly = auto()
    daily = auto()

    # disable = auto()


class UserDetail(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), default=0, nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), default=0, nullable=False)
    last_online = db.Column(db.DateTime, nullable=False, default=datetime.datetime.min)
    current_usage_GB = db.Column(db.Numeric(6, 9, asdecimal=False), default=0, nullable=False)
    connected_ips = db.Column(db.String(512), default='', nullable=False)

    @property
    def ips(self):
        return [] if not self.connected_ips else self.connected_ips.split(",")


class User(db.Model, SerializerMixin):
    """
    This is a model class for a user in a database that includes columns for their ID, UUID, name, online status,
    account expiration date, usage limit, package days, mode, start date, current usage, last reset time, and comment.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(36), default=lambda: str(uuid_mod.uuid4()), nullable=False, unique=True)
    name = db.Column(db.String(512), nullable=False, default='')
    last_online = db.Column(db.DateTime, nullable=False, default=datetime.datetime.min)
    # removed
    expiry_time = db.Column(db.Date, default=datetime.date.today() + relativedelta.relativedelta(months=6))
    usage_limit_GB = db.Column(db.Numeric(6, 9, asdecimal=False), default=1000, nullable=False)
    package_days = db.Column(db.Integer, default=90, nullable=False)
    mode = db.Column(db.Enum(UserMode), default=UserMode.no_reset, nullable=False)
    monthly = db.Column(db.Boolean, default=False)  # removed
    start_date = db.Column(db.Date, nullable=True)
    current_usage_GB = db.Column(db.Numeric(6, 9, asdecimal=False), default=0, nullable=False)
    last_reset_time = db.Column(db.Date, default=datetime.date.today())
    comment = db.Column(db.String(512))
    telegram_id = db.Column(db.String(512))
    added_by = db.Column(db.Integer, db.ForeignKey('admin_user.id'), default=0)
    max_ips = db.Column(db.Integer, default=1000, nullable=False)
    details = db.relationship('UserDetail', cascade="all,delete", backref='user',    lazy='dynamic',)
    enable = db.Column(db.Boolean, default=True, nullable=False)
    ed25519_private_key = db.Column(db.String(500))
    ed25519_public_key = db.Column(db.String(100))

    @property
    def remaining_days(self):
        return remaining_days(self)

    @property
    def is_active(self):
        return is_user_active(self)

    @property
    def ips(self):
        res = {}
        for detail in UserDetail.query.filter(UserDetail.user_id == self.id):
            for ip in detail.ips:
                res[ip] = 1
        return list(res.keys())

    @staticmethod
    def by_id(user_id):
        """
        Retrieves a user from the database by their ID.
        """
        return User.query.get(user_id)

    @staticmethod
    def by_uuid(user_uuid, create=False):
        """
        Retrieves a user from the database by their UUID.
        """
        dbuser = User.query.filter_by(uuid=user_uuid).first()
        if not dbuser:
            dbuser = User(uuid=user_uuid)
            db.session.add(dbuser)
        return dbuser

    @staticmethod
    def from_dict(data):
        """
        Returns a new User object created from a dictionary.
        """

        return User(
            name=data.get('name', ''),
            expiry_time=data.get('expiry_time', datetime.date.today() + relativedelta.relativedelta(months=6)),
            usage_limit_GB=data.get('usage_limit_GB', 1000),
            package_days=data.get('package_days', 90),
            mode=UserMode[data.get('mode', 'no_reset')],
            monthly=data.get('monthly', False),
            start_date=data.get('start_date', None),
            current_usage_GB=data.get('current_usage_GB', 0),
            last_reset_time=data.get('last_reset_time', datetime.date.today()),
            comment=data.get('comment', None),
            telegram_id=data.get('telegram_id', None),
            added_by=data.get('added_by', 0)
        )

    # @staticmethod
    # def from_dict(data):

    #     allowed_fields = {'name', 'expiry_time', 'usage_limit_GB', 'package_days', 'mode', 'monthly', 'start_date',
    #                       'current_usage_GB', 'comment', 'telegram_id', 'added_by_uuid'}
    #     filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
    #     if 'mode' in filtered_data:
    #         filtered_data['mode'] = UserMode[filtered_data['mode']]
    #     if 'expiry_time' in filtered_data:
    #         filtered_data['expiry_time'] = datetime.fromisoformat(filtered_data['expiry_time']).date()
    #     if 'start_date' in filtered_data and filtered_data['start_date']:
    #         filtered_data['start_date'] = datetime.fromisoformat(filtered_data['start_date']).date()
    #     return User(**filtered_data)
    def to_dict(d):
        from hiddifypanel.panel import hiddify
        return {
            'uuid': d.uuid,
            'name': d.name,
            'last_online': hiddify.time_to_json(d.last_online),
            'usage_limit_GB': d.usage_limit_GB,
            'package_days': d.package_days,
            'mode': d.mode,
            'start_date': hiddify.date_to_json(d.start_date),
            'current_usage_GB': d.current_usage_GB,
            'last_reset_time': hiddify.date_to_json(d.last_reset_time),
            'comment': d.comment,
            'added_by_uuid': d.admin.uuid if d.admin else '',
            'telegram_id': d.telegram_id,
            'ed25519_private_key': d.ed25519_private_key,
            'ed25519_public_key': d.ed25519_public_key
        }


def remove(user: User, commit=True):
    from hiddifypanel.drivers import user_driver
    user_driver.remove_client(user)
    user.delete()
    if commit:
        db.session.commit()


def is_user_active(u):
    """
    The "is_user_active" function checks if the input user object "u" is active by verifying if their mode is not
    "disable", if their usage limit hasn't been exceeded, and if there are remaining days on their account. The
    function returns a boolean value indicating whether the user is active or not.
    """
    is_active = True
    if not u:
        is_active = False
    elif not u.enable:
        is_active = False
    elif u.usage_limit_GB < u.current_usage_GB:
        is_active = False
    elif remaining_days(u) < 0:
        is_active = False
    elif len(u.ips) > max(3, u.max_ips):
        is_active = False
    return is_active


def remaining_days(u):
    """
    The "remaining_days" function calculates the number of days remaining for a user's account package based on the
    current date and the user's start date. The function returns the remaining days as an integer value. If the start
    date is not available, the function returns the total package days.
    """
    res = -1
    if u.package_days is None:
        res = -1
    elif u.start_date:
        # print(datetime.date.today(), u.start_date,u.package_days, u.package_days - (datetime.date.today() - u.start_date).days)
        res = u.package_days - (datetime.date.today() - u.start_date).days
    else:
        # print("else",u.package_days )
        res = u.package_days
    return min(res, 10000)


package_mode_dic = {
    UserMode.daily: 1,
    UserMode.weekly: 7,
    UserMode.monthly: 30
}


def days_to_reset(user):
    """
    The "days_to_reset" function calculates the number of days until the user's data usage is reset, based on the
    user's start date and mode of usage. The function returns the remaining days as an integer value. If the start
    date is not available, the function returns the total days for the user's mode.
    """
    # print("start_date",user.start_date, "pack",package_mode_dic.get(user.mode,10000), "total",(datetime.date.today()-user.start_date).days)
    # if user.mode==UserMode.daily:
    #     return 0
    if user.start_date:
        days = package_mode_dic.get(user.mode, 10000)-(datetime.date.today()-user.start_date).days % package_mode_dic.get(user.mode, 10000)
    else:
        days = package_mode_dic.get(user.mode, 10000)
    return max(-100000, min(days, 100000))


def user_should_reset(user):
    """
    The "days_to_reset" function calculates the number of days until the user's data usage is reset, based on the
    user's start date and mode of usage. The function returns the remaining days as an integer value. If the start
    date is not available, the function returns the total days for the user's mode.
    """
    # print("start_date",user.start_date, "pack",package_mode_dic.get(user.mode,10000), "total",(datetime.date.today()-user.start_date).days)
    # if user.mode==UserMode.daily:
    #     return 0
    res = True
    if not user.last_reset_time:
        res = True
    elif not user.start_date or (datetime.date.today()-user.last_reset_time).days == 0:
        res = False
    else:
        res = ((datetime.date.today()-user.start_date).days % package_mode_dic.get(user.mode, 10000)) == 0

    return res


def user_by_uuid(uuid):
    return User.query.filter(User.uuid == uuid).first()


def user_by_id(id):
    return User.query.filter(User.id == id).first()


def add_or_update_user(commit=True, **user):
    # if not is_valid():return
    from hiddifypanel.panel import hiddify
    dbuser = User.by_uuid(user['uuid'], create=True)

    if user.get('added_by_uuid'):
        from .admin import get_admin_by_uuid
        admin = get_admin_by_uuid(user.get('added_by_uuid'), create=True)
        dbuser.added_by = admin.id
    else:
        dbuser.added_by = 1

    if user.get('expiry_time', ''):
        last_reset_time = hiddify.json_to_date(user.get('last_reset_time', '')) or datetime.date.today()

        expiry_time = hiddify.json_to_date(user['expiry_time'])
        dbuser.start_date = last_reset_time
        dbuser.package_days = (expiry_time-last_reset_time).days

    elif 'package_days' in user:
        dbuser.package_days = user['package_days']
        if user.get('start_date', ''):
            dbuser.start_date = hiddify.json_to_date(user['start_date'])
        else:
            dbuser.start_date = None
    dbuser.current_usage_GB = user['current_usage_GB']

    dbuser.usage_limit_GB = user['usage_limit_GB']
    dbuser.name = user.get('name') or ''
    dbuser.comment = user.get('comment', '')
    dbuser.enable = user.get('enable', True)
    if user.get('ed25519_private_key', ''):
        dbuser.ed25519_private_key = user.get('ed25519_private_key', '')
        dbuser.ed25519_public_key = user.get('ed25519_public_key', '')
    if not dbuser.ed25519_private_key:
        priv, publ = hiddify.get_ed25519_private_public_pair()
        dbuser.ed25519_private_key = priv
        dbuser.ed25519_public_key = publ

    mode = user.get('mode', UserMode.no_reset)
    if mode == 'disable':
        mode = UserMode.no_reset
        dbuser.enable = False

    dbuser.mode = mode

    dbuser.telegram_id = user.get('telegram_id')

    dbuser.last_online = hiddify.json_to_time(user.get('last_online')) or datetime.datetime.min

    if commit:
        db.session.commit()


def bulk_register_users(users=[], commit=True, remove=False):
    for u in users:
        add_or_update_user(commit=False, **u)
    if remove:
        dd = {u.uuid: 1 for u in users}
        for d in User.query.all():
            if d.uuid not in dd:
                db.session.delete(d)
    if commit:
        db.session.commit()
