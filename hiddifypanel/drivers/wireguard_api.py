import subprocess
import json
import os

from .abstract_driver import DriverABS
from hiddifypanel.models import User
from hiddifypanel.panel.run_commander import Command, commander


class WireguardApi(DriverABS):
    WG_RAW_USAGE_FILE_PATH = '/opt/hiddify-manager/other/wireguard/raw_wg_usage.json'

    def __init__(self) -> None:
        super().__init__()
        self.local_usage_path = "./hiddify_usages.json"
        # create empty local usage file
        if not os.path.isfile(self.local_usage_path):
            with open(self.local_usage_path, 'w+') as f:
                json.dump({}, f)

    def __get_wg_usages(self) -> dict:
        commander(Command.update_wg_usage)
        raw_output = ''
        if not os.path.isfile(WireguardApi.WG_RAW_USAGE_FILE_PATH):
            return {}
        with open(WireguardApi.WG_RAW_USAGE_FILE_PATH, 'r') as f:
            raw_output = f.read()
        data = {}
        for line in raw_output.split('\n'):
            if not line:
                continue
            sections = line.split()
            if len(sections) < 1:
                continue
            data[sections[0]] = {
                'down': int(sections[1]),
                'up': int(sections[2]),
            }
        return data

    def __get_local_usage(self) -> dict:

        with open(self.local_usage_path, 'r') as f:
            data = json.load(f)
            return data

    def __sync_local_usages(self, reset: bool = False) -> None:
        local_usage = self.__get_local_usage()
        wg_usage = self.__get_wg_usages()

        for wg_pub, wg_usage in wg_usage.items():
            if not local_usage.get(wg_pub):
                local_usage[wg_pub] = wg_usage
                continue

            if reset:
                if local_usage[wg_pub].get('up') != 0 and local_usage[wg_pub].get('down') != 0:
                    local_usage[wg_pub]['last_usage'] = {
                        'up': local_usage[wg_pub]['up'],
                        'down': local_usage[wg_pub]['down'],
                    }
                reset_usage = self.calculate_reset(local_usage[wg_pub]['last_usage'], wg_usage)
                local_usage[wg_pub]['up'] = reset_usage['up']
                local_usage[wg_pub]['down'] = reset_usage['down']
            else:
                local_usage[wg_pub]['up'] = wg_usage['up']
                local_usage[wg_pub]['down'] = wg_usage['down']

        with open(self.local_usage_path, 'w') as f:
            json.dump(local_usage, f)

    def calculate_reset(self, last_usage: dict, current_usage: dict) -> dict:
        res = {
            'up': current_usage['up'] - last_usage['up'],
            'down': current_usage['down'] - last_usage['down'],
        }

        if res['up'] < 0:
            res['up'] = 0
        if res['down'] < 0:
            res['down'] = 0
        return res

    def get_enabled_users(self):
        self.__sync_local_usages()
        usages = self.__get_local_usage()
        wg_pubs = list(usages.keys())

        users = User.query.all()
        enabled = {}
        for u in users:
            if u.wg_pub in wg_pubs:
                enabled[u.uuid] = 1
            else:
                enabled[u.uuid] = 0
        return enabled

    def add_client(self, user):
        pass

    def remove_client(self, user):
        pass

    def __get_usage(self, uuid, reset=True):
        user = User.by_uuid(uuid)
        if not user:
            return 0
        wg_pub = user.wg_pub
        user_usage = self.__get_local_usage().get(wg_pub)
        if not user_usage:
            return 0
        up = user_usage.get('up')
        down = user_usage.get('down')

        res = None
        if down is None:
            res = up
        elif up is None:
            res = down
        else:
            res = down + up
        if res:
            print(f"Wireguard usage {uuid} d={down} u={up} sum={res}")
        return res

    def get_all_usage(self, users, reset=True):
        self.__sync_local_usages(reset)
        return {u: self.__get_usage(u.uuid, reset) for u in users}