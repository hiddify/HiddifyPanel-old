from sqlalchemy import column
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, column

import datetime
from flask import Flask, g
from datetime import timedelta, date
from hiddifypanel.panel.database import db
from sqlalchemy_serializer import SerializerMixin



class DailyUsage(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, default=datetime.date.today())
    usage = db.Column(db.BigInteger, default=0, nullable=False)
    online = db.Column(db.Integer, default=0, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), default=0, nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), default=0, nullable=False)

    # def __str__(self):
    #     return str([id,date,usage,online,admin_id,child_id])


def get_daily_usage_stats(admin_id=None, child_id=None):
    from .admin import AdminUser
    if not admin_id:
        admin_id = g.admin.id
    sub_admins = AdminUser.query.filter(AdminUser.id == admin_id).first().recursive_sub_admins_ids()
    print(sub_admins)

    def filter_daily_usage_admin(query):
        # print('before',admin_id,query.all())
        if admin_id:
            query = query.filter(DailyUsage.admin_id.in_(sub_admins))
        if child_id:
            query = query.filter(DailyUsage.child_id == child_id)
        # print('after',admin_id,query.all())
        return query

    def filter_user_admin(query):
        if admin_id:
            query = query.filter(User.added_by.in_(sub_admins))

        return query

    from .user import User
    # Today's usage and online count
    today = date.today()
    today_stats = filter_daily_usage_admin(db.session.query(
        func.coalesce(func.sum(DailyUsage.usage), 0),
        func.coalesce(func.sum(DailyUsage.online), 0)
    ).filter(DailyUsage.date == today)).first()
    users_online_today = filter_user_admin(User.query.filter(User.last_online >= today)).count()

    h24 = datetime.datetime.now()-datetime.timedelta(days=1)
    users_online_h24 = filter_user_admin(User.query.filter(User.last_online >= h24)).count()

    m5 = datetime.datetime.now()-datetime.timedelta(minutes=5)
    users_online_m5 = filter_user_admin(User.query.filter(User.last_online >= m5)).count()

    # Yesterday's usage and online count
    yesterday = date.today() - timedelta(days=1)
    yesterday_stats = filter_daily_usage_admin(db.session.query(
        func.coalesce(func.sum(DailyUsage.usage), 0),
        func.coalesce(func.sum(DailyUsage.online), 0)
    ).filter(DailyUsage.date == yesterday)).first()
    # users_online_yesterday = User.query.filter(User.last_online >= yesterday, User.last_online < today).count()
    # Last 30 days' usage and online count
    last_30_days_start = date.today() - timedelta(days=30)
    last_30_days_stats = filter_daily_usage_admin(db.session.query(
        func.coalesce(func.sum(DailyUsage.usage), 0),
        func.coalesce(func.sum(DailyUsage.online), 0)
    ).filter(DailyUsage.date >= last_30_days_start)).first()
    users_online_last_month = filter_user_admin(User.query.filter(User.last_online >= last_30_days_start)).count()

    # Total usage and online count
    total_stats = filter_daily_usage_admin(db.session.query(
        func.coalesce(func.sum(DailyUsage.usage), 0),
        func.coalesce(func.sum(DailyUsage.online), 0)
    )).first()
    ten_years_ago = today - timedelta(days=365*10)
    users_online_last_10_years = filter_user_admin(User.query.filter(User.last_online >= ten_years_ago)).count()
    total_users = filter_user_admin(User.query).count()

    # Return the usage stats as a dictionary
    return {
        "today": {"usage": today_stats[0], "online": users_online_today},
        "h24": {"usage": 0, "online": users_online_h24},
        "m5": {"usage": 0, "online": users_online_m5},
        "yesterday": {"usage": yesterday_stats[0], "online": yesterday_stats[1]},
        "last_30_days": {"usage": last_30_days_stats[0], "online": users_online_last_month},
        "total": {"usage": total_stats[0], "online": users_online_last_10_years, "users": total_users}
    }
