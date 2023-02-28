import flask_babel,flask_babelex
from hiddifypanel.models import BoolConfig,StrConfig,ConfigEnum,hconfig,ConfigCategory
from wtforms.validators import Regexp, ValidationError
from flask_babelex import lazy_gettext as _
# from flask_babelex import gettext as _
import wtforms as wtf
from flask_wtf import FlaskForm, CSRFProtect
from flask_bootstrap import SwitchField

from flask_admin.base import expose
# from gettext import gettext as _


import re
from flask import render_template,current_app, Markup,url_for
from hiddifypanel.panel.hiddify import flash
from hiddifypanel.models import  *
from hiddifypanel.panel.database import db
from wtforms.fields import *
from flask_classful import FlaskView
from hiddifypanel.panel import hiddify,hiddify_api,custom_widgets
class SettingAdmin(FlaskView):
    


    def index(self):
        # return "d"
        
        

        # form=HelloForm()
        # # return render('config.html',form=form)
        # return render_template('config.html',form=HelloForm())
        form=get_config_form()
        return render_template('config.html',form=form)


    def post(self):
        form=get_config_form()
        if form.validate_on_submit():
            

            boolconfigs=BoolConfig.query.filter(BoolConfig.child_id==0).all()
            bool_types={c.key:'bool' for c in boolconfigs}
            old_configs=get_hconfigs()
            for cat,vs in form.data.items():#[c for c in ConfigEnum]:
            
                if type(vs) is dict:
                    for k,v in vs.items():
            
                        if k in [c for c in ConfigEnum]:
                            if k in bool_types:
                                BoolConfig.query.filter(BoolConfig.key==k,BoolConfig.child_id==0).first().value=v
                            else:
                                if "_domain" in k or k in [ConfigEnum.admin_secret]:
                                    v=v.lower()
                                if k == ConfigEnum.parent_panel and v!='':
                                    # v=(v+"/").replace("/admin",'')
                                    v=re.sub("/admin/.*","",v)

                                    try:
                                        if hiddify_api.sync_child_to_parent(v)['status']!=200:
                                            flash(_("Can not connect to parent panel!"),'error')
                                            return render_template('config.html', form=form)
                                    except:
                                        flash(_("Can not connect to parent panel!"),'error')
                                        return render_template('config.html', form=form)
                                StrConfig.query.filter(StrConfig.key==k,StrConfig.child_id==0).first().value=v

                # print(cat,vs)

            db.session.commit()
            flask_babel.refresh()
            flask_babelex.refresh()
            
            if old_configs[ConfigEnum.proxy_path]!=hconfig(ConfigEnum.proxy_path):
                from . import Actions
                action=Actions()
                return action.reinstall(complete_install=False,domain_changed=True)
                
            hiddify.check_need_reset(old_configs)
            
            if old_configs[ConfigEnum.admin_lang]!=hconfig(ConfigEnum.admin_lang):
                form=get_config_form()
            return render_template('config.html', form=form)
        flash(_('config.validation-error'), 'danger')
        return render_template('config.html', form=form)

        
        
        

        # form=HelloForm()
        # # return render('config.html',form=form)
        # return render_template('config.html',form=HelloForm())
        form=get_config_form()
        return render_template('config.html',form=form)

    def get_babel_string(self):
        res=""
        strconfigs=StrConfig.query.all()
        boolconfigs=BoolConfig.query.all()
        bool_types={c.key:'bool' for c in boolconfigs}

        configs=[*boolconfigs,*strconfigs]
        for cat in ConfigCategory:
            if cat=='hidden':continue

            cat_configs=[c for c in configs if c.key.category()==cat]
            
            for c in cat_configs:
                res+=f'{{{{_("config.{c.key}.label")}}}} {{{{_("config.{c.key}.description")}}}}'
                

            res+=f'{{{{_("config.{cat}.label")}}}}{{{{_("config.{cat}.description")}}}}'
        for c in ConfigEnum:
            res+=f'{{{{_("config.{c}.label")}}}} {{{{_("config.{c}.description")}}}}'
        return res
        

def get_config_form():
    
    
    strconfigs=StrConfig.query.filter(StrConfig.child_id==0).all()
    boolconfigs=BoolConfig.query.filter(BoolConfig.child_id==0).all()
    bool_types={c.key:'bool' for c in boolconfigs}

    configs=[*boolconfigs,*strconfigs]
    # categories=sorted([ c for c in {c.key.category():1 for c in configs}])
    # dict_configs={cat:[c for c in configs if c.category==cat] for cat in categories}
    class DynamicForm(FlaskForm):pass
    is_parent=hconfig(ConfigEnum.is_parent)
    for cat in ConfigCategory:
        if cat=='hidden':continue

        cat_configs=[c for c in configs if c.key.category()==cat and (not is_parent or c.key.show_in_parent())]
        if len(cat_configs)==0:continue
        
        class CategoryForm(FlaskForm):
            description_for_fieldset=wtf.fields.TextAreaField("",description=_(f'config.{cat}.description'),render_kw={"class":"d-none"})
        for c in cat_configs:
            if c.key in bool_types:
                field= SwitchField(_(f'config.{c.key}.label'), default=c.value,description=_(f'config.{c.key}.description')) 
            elif c.key==ConfigEnum.lang or c.key==ConfigEnum.admin_lang:
                field=wtf.fields.SelectField(_(f"config.{c.key}.label"),choices=[("en",_("lang.en")),("fa",_("lang.fa")),("zh",_("lang.zh"))],description=_(f"config.{c.key}.description"),default=hconfig(c.key))
            elif c.key==ConfigEnum.telegram_lib:
                # if hconfig(ConfigEnum.telegram_lib)=='python':
                #     continue6
                libs=[("python",_("lib.telegram.python")),("tgo",_("lib.telegram.go")),("orig",_("lib.telegram.orignal")),("erlang",_("lib.telegram.erlang"))]
                field=wtf.fields.SelectField(_("config.telegram_lib.label"),choices=libs,description=_("config.telegram_lib.description"),default=hconfig(ConfigEnum.telegram_lib))
            elif c.key==ConfigEnum.branding_freetext:
                validators=[wtf.validators.Length(max=2048)]
                render_kw={'class':"ltr",'maxlength':2048}
                field= custom_widgets.CKTextAreaField(_(f'config.{c.key}.label'), validators, default=c.value, description=_(f'config.{c.key}.description'),render_kw=render_kw) 
            else:
                render_kw={'class':"ltr"}
                validators=[]
                if c.key==ConfigEnum.domain_fronting_domain:
                    validators.append(wtf.validators.Regexp("^([A-Za-z0-9\-\.]+\.[a-zA-Z]{2,})|$",re.IGNORECASE,_("config.Invalid domain")))
                    validators.append(hiddify.validate_domain_exist)
                elif '_domain' in c.key:
                    validators.append(wtf.validators.Regexp("^([A-Za-z0-9\-\.]+\.[a-zA-Z]{2,})$",re.IGNORECASE,_("config.Invalid domain")))
                    validators.append(hiddify.validate_domain_exist)

                    if c.key!=ConfigEnum.decoy_domain:
                        validators.append(wtf.validators.NoneOf([d.domain.lower() for d in Domain.query.all()],_("config.Domain already used")))
                        validators.append(wtf.validators.NoneOf([cc.value.lower() for cc in StrConfig.query.filter(StrConfig.child_id==0).all() if cc.key!=c.key and  "fakedomain" in cc.key and cc.key!=ConfigEnum.decoy_domain],_("config.Domain already used")))
                    render_kw['required']=""
                
                if c.key ==ConfigEnum.parent_panel:
                    validators.append(wtf.validators.Regexp("()|(http(s|)://([A-Za-z0-9\-\.]+\.[a-zA-Z]{2,})/.*)",re.IGNORECASE,_("Invalid admin link")))
                if c.key == ConfigEnum.telegram_bot_token:
                    validators.append(wtf.validators.Regexp("()|^([0-9]{8,12}:[a-zA-Z0-9_-]{30,40})|$",re.IGNORECASE,_("config.Invalid telegram bot token")))
                if c.key==ConfigEnum.branding_site :
                    validators.append(wtf.validators.Regexp("()|(http(s|)://([A-Za-z0-9\-\.]+\.[a-zA-Z]{2,})/?.*)",re.IGNORECASE,_("config.Invalid brand link")))
                    # render_kw['required']=""

                if 'secret' in c.key:
                    validators.append(wtf.validators.Regexp("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",re.IGNORECASE,_('config.invalid uuid')))
                    render_kw['required']=""

                if c.key==ConfigEnum.proxy_path:
                    validators.append(wtf.validators.Regexp("^[a-zA-Z0-9]*$",re.IGNORECASE,_("config.Invalid proxy path")))
                    render_kw['required']=""

                if 'port' in c.key:
                    validators.append(wtf.validators.Regexp("^(\d,?)*$",re.IGNORECASE,_("config.Invalid port")))

                if c.key==ConfigEnum.http_ports:
                    validators.append(wtf.validators.Regexp("^(\d,?)*80(\d,?)*$",re.IGNORECASE,_("config.port 80 is required")))
                    render_kw['required']=""
                if c.key==ConfigEnum.tls_ports:
                    validators.append(wtf.validators.Regexp("^(\d,?)*443(\d,?)*$",re.IGNORECASE,_("config.port 443 is required")))
                    render_kw['required']=""
                for val in validators:
                    if hasattr(val,"regex"):
                        render_kw['pattern']=val.regex.pattern
                        render_kw['title']=val.message
                field= wtf.fields.StringField(_(f'config.{c.key}.label'), validators, default=c.value, description=_(f'config.{c.key}.description'),render_kw=render_kw) 
            setattr(CategoryForm,c.key , field)    

        multifield=wtf.fields.FormField(CategoryForm,Markup('<i class="fa-solid fa-plus"></i>&nbsp'+_(f'config.{cat}.label')))
            
        setattr(DynamicForm, cat,  multifield)    

    setattr(DynamicForm,"submit",wtf.fields.SubmitField(_('Submit')))
        

    return DynamicForm()
        
        
    
