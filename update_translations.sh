#!/bin/bash
source .env
exit 0
PATH=/config/.local/bin:$PATH

python3 -c "
import hiddifypanel;
print(''.join([f'{{{{_(\"config.{c}.label\")}}}}{{{{_(\"config.{c}.description\")}}}}' for c in hiddifypanel.models.ConfigEnum]));print(''.join([f'{{{{_(\"config.{cat}.label\")}}}}{{{{_(\"config.{cat}.description\")}}}}' for cat in hiddifypanel.models.ConfigCategory]));
def print_enum(en):
  print(''.join([f'{{{{_(\"{item}\")}}}}' for item in en]))  
print_enum(hiddifypanel.models.DomainType)
print_enum(hiddifypanel.models.UserMode)
" >hiddifypanel/templates/fake.html
pybabel extract -F babel.cfg -o messages.pot hiddifypanel

wget -O hiddifypanel/translations/en/LC_MESSAGES/messages.po "https://localise.biz/api/export/locale/en-US.po?index=id&key=5Tqp1dLHQSk98s-twNF6RpwZu7lZSLLM"

wget -O hiddifypanel/translations/fa/LC_MESSAGES/messages.po "https://localise.biz/api/export/locale/fa.po?index=id&key=5Tqp1dLHQSk98s-twNF6RpwZu7lZSLLM"
wget -O hiddifypanel/translations/zh/LC_MESSAGES/messages.po "https://localise.biz/api/export/locale/zh.po?index=id&key=RDCQeBGpPujIly8PXA_7CjhNVgn9Jt64"
wget -O hiddifypanel/translations/pt/LC_MESSAGES/messages.po "https://localise.biz/api/export/locale/pt.po?index=id&key=Y1DZZCqzlzT8rgfKImXbNzr-jTLB6c7H"
wget -O hiddifypanel/translations/ru/LC_MESSAGES/messages.po "https://localise.biz/api/export/locale/ru.po?index=id&key=Y1DZZCqzlzT8rgfKImXbNzr-jTLB6c7H"

pybabel update -N -i messages.pot -d hiddifypanel/translations -l en

pip install polib deep-translator
python3 auto_translate.py fa en
python3 auto_translate.py en fa
python3 auto_translate.py en zh
python3 auto_translate.py en pt
python3 auto_translate.py en ru

pybabel update -N -i messages.pot -d hiddifypanel/translations -l fa
pybabel update -N -i messages.pot -d hiddifypanel/translations -l zh
pybabel update -N -i messages.pot -d hiddifypanel/translations -l pt
pybabel compile -f -d hiddifypanel/translations

function update_localise() {
  lang=$1
  curl "https://localise.biz/api/import/po?index=id&delete-absent=false&ignore-existing=false&locale=$lang&flag-new=Provisional&key=$LOCALIZ_KEY" \
    -H 'Accept: application/json' \
    --data-binary "@hiddifypanel/translations/$lang/LC_MESSAGES/messages.po" \
    --compressed
}

function update_localise2() {
  lang=$1
  curl "https://localise.biz/api/import/po?index=id&delete-absent=false&ignore-existing=false&locale=$lang&flag-new=Provisional&key=$LOCALIZ_KEY2" \
    -H 'Accept: application/json' \
    --data-binary "@hiddifypanel/translations/$lang/LC_MESSAGES/messages.po" \
    --compressed
}

function update_localise3() {
  lang=$1
  curl "https://localise.biz/api/import/po?index=id&delete-absent=false&ignore-existing=false&locale=$lang&flag-new=Provisional&key=$LOCALIZ_KEY3" \
    -H 'Accept: application/json' \
    --data-binary "@hiddifypanel/translations/$lang/LC_MESSAGES/messages.po" \
    --compressed
}

update_localise fa
update_localise en
update_localise3 en
update_localise3 zh

update_localise2 en
update_localise2 pt
# update_localise2 ru
