from flask_admin.contrib import sqla
from hiddifypanel.panel.database import db
import datetime
from hiddifypanel.models import  *
from flask import Markup,g
from wtforms.validators import Regexp,ValidationError
import re,uuid
from hiddifypanel import xray_api
from .adminlte import AdminLTEModelView
# from gettext import gettext as _
from flask_babelex import gettext as __
from flask_babelex import lazy_gettext as _
from babel.dates import format_timedelta


from hiddifypanel.panel import hiddify,custom_widgets
from hiddifypanel.panel.hiddify import flash
from wtforms.fields import StringField
from flask_bootstrap import SwitchField
class UserAdmin(AdminLTEModelView):
    
    list_template = 'model/user_list.html'    
    form_excluded_columns=['monthly','last_online']
    # edit_modal=True
    # create_modal=True
    # column_display_pk = True
    # can_export = True
    # form_overrides = dict(monthly=SwitchField)
    form_overrides = dict(expiry_time=custom_widgets.DaysLeftField,last_reset_time=custom_widgets.LastResetField)
    # form_widget_args={
    # 'expiry_time':{'class':'datepicker'}    
    # }
    form_args = {
    'uuid': {
        'validators': [Regexp(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',message=__("Should be a valid uuid"))]
    #     'label': 'First Name',
    #     'validators': [required()]
    }
    # ,
    # 'expiry_time':{
    # "":'%Y-%m-%d'
    # }
    }
    # column_labels={'uuid':_("user.UUID")}
    # column_filters=["uuid","name","usage_limit_GB",'monthly',"current_usage_GB","expiry_time"]
    
    column_labels={
        "Actions":_("actions"),
        "name": _("user.name"),
        "UserLinks":_("user.user_links"),
        "usage_limit_GB":_("user.usage_limit_GB"),
        "monthly":_("Reset every month"),
        "mode":_("Mode"),
        "current_usage_GB":_("user.current_usage_GB"),
        "expiry_time":_("user.expiry_time"),
        "last_reset_time":_("user.last_reset_time"),
        "uuid":_("user.UUID"),
        "comment":_("Note"),
        'last_online':_('Last Online')
     }
    column_searchable_list=[("uuid"),"name"]
    def search_placeholder(self):
        return f"{_('search')} {_('user.UUID')} {_('user.name')}"
    # def get_column_name(self,field):
    #         return "x"
    #  return column_labels[field]
    column_descriptions = dict(
        # name=_'just for remembering',
        # usage_limit_GB="in GB",
        # current_usage_GB="in GB"
        comment=_("Add some text that is only visible to you."),
        mode=_("Define the user mode. Should the usage reset every month?"),
        last_reset_time=_("If monthly is enabled, the usage will be reset after 30 days from this date.")
    )
    # column_editable_list=["usage_limit_GB","current_usage_GB","expiry_time"]
    # form_extra_fields={
    #     'uuid': {'label_name':"D"}
        
    #     }
    column_list = ["name","current_usage_GB","last_online","UserLinks","mode","expiry_time","uuid","comment"]
    # can_edit = False
    # def on_model_change(self, form, model, is_created):
    #     model.password = generate_password_hash(model.password)
    
    
    def _name_formatter(view, context, model, name):
        proxy_path=hconfig(ConfigEnum.proxy_path)
        if hconfig(ConfigEnum.is_parent):
            d=ParentDomain.query.first()
        else:
            d=Domain.query.filter(Domain.mode!=DomainType.fake).first()
        if d:
            link=f"<a target='_blank' href='https://{d.domain}/{proxy_path}/{model.uuid}/new'><i class='fa-solid fa-arrow-up-right-from-square'></i> {model.name}</a>"
            return Markup(link)
        else:
            return model.name
    def _ul_formatter(view, context, model, name):
        if hconfig(ConfigEnum.is_parent):
            domains=ParentDomain.query.all()
        else:    
            domains=Domain.query.filter(Domain.mode!=DomainType.fake).all()
        return Markup(" ".join([hiddify.get_user_link(model.uuid,d,'new') for d in domains]))
    
    def _uuid_formatter(view, context, model, name):
        return Markup(f"<span>{model.uuid}</span>")
    # def _usage_formatter(view, context, model, name):
    #     return round(model.current_usage_GB,3)

    def _usage_formatter(view, context, model, name):
        u= round(model.current_usage_GB,3)
        t=round(model.usage_limit_GB,3)
        rate=round(u*100/t)
        state= "danger" if u>=t else ('warning' if  rate>80 else 'success')
        color= "#ff7e7e" if u>=t else ('#ffc107' if  rate>80 else '#9ee150')
        return Markup(f"""
        <div class="progress progress-lg position-relative" style="min-width: 100px;">
          <div class="progress-bar progress-bar-striped" role="progressbar" style="width: {rate}%;background-color: {color};" aria-valuenow="{rate}" aria-valuemin="0" aria-valuemax="100"></div>
              <span class='badge position-absolute' style="left:auto;right:auto;width: 100%;font-size:1em">{u} {_('user.home.usage.from')} {t} GB</span>

        </div>
        """)

    def _expire_formatter(view, context, model, name):
        if not model.expiry_time: return "-"

        diff=(model.expiry_time-datetime.date.today())
        state='success' if diff.days>7 else ('warning' if diff.days>0 else 'danger') 
        return Markup(f"<span class='badge badge-{state}'>{format_timedelta(diff, add_direction=True, locale=hconfig(ConfigEnum.admin_lang))}</span>")
        # return Markup(f"<span class='badge ltr badge-}'>{days}</span> "+_('days'))

    def _online_formatter(view, context, model, name):
        if not model.last_online:
            return "-"
        diff=model.last_online-datetime.datetime.now()
        
        if diff.days<-1000:
            return "-"
        
        state="danger" if diff.days<-3 else ("success" if diff.days>=-1 else "warning")
        return Markup(f"<span class='badge badge-{state}'>{format_timedelta(diff, add_direction=True, locale=hconfig(ConfigEnum.admin_lang))}</span>")
        
        
        # return Markup(f"<span class='badge ltr badge-{'success' if days>7 else ('warning' if days>0 else 'danger') }'>{days}</span> "+_('days'))

    column_formatters = {
        'name': _name_formatter,
        'UserLinks': _ul_formatter,
        'uuid': _uuid_formatter,
        'current_usage_GB': _usage_formatter,
        "expiry_time":_expire_formatter,
        'last_online':_online_formatter
    }
    def on_model_delete(self, model):
        if len(User.query.all())<=1:
            raise ValidationError(f"at least one user should exist")    
        xray_api.remove_client(model.uuid)
        # hiddify.flash_config_success()

        
    # def is_accessible(self):
    #     return g.is_admin
    # def on_form_prefill(self, form, id):
    #     form.expiry_time=form.expiry_time-datetime.date.today()
    def on_model_change(self, form, model, is_created):
        if len(User.query.all())%4==0:
            flash(('<div id="show-modal-donation"></div>'), ' d-none')
        if not re.match("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", model.uuid):
            raise ValidationError('Invalid UUID e.g.,'+ str(uuid.uuid4()))
        else:
            super().on_model_change(form, model, is_created)
        
        # model.expiry_time=datetime.date.today()+datetime.timedelta(days=model.expiry_time)
        
        # if model.current_usage_GB < model.usage_limit_GB:
        #     xray_api.add_client(model.uuid)
        # else:
        #     xray_api.remove_client(model.uuid)
        # hiddify.flash_config_success()
        
    def after_model_change(self,form, model, is_created):
        hiddify.quick_apply_users()
    def after_model_delete(self,model):
        hiddify.quick_apply_users()