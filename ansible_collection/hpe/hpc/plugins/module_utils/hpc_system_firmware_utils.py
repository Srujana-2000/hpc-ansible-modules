# !/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import subprocess
import time
import os

from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils
from ansible.module_utils.urls import open_url
try:
    from requests_toolbelt import MultipartEncoder
    HAS_REQUESTS_TOOLBELT = True
except ImportError:
    HAS_REQUESTS_TOOLBELT = False


supported_models = ["HPE CRAY XD220V", "HPE CRAY XD225V", "HPE CRAY XD295V", "HPE CRAY XD665", "HPE CRAY XD670"]

# To get inventory, update
supported_targets = {
    "HPE CRAY XD220V": ["BMC", "BIOS", "MainCPLD", "HDDBPPIC", "PDBPIC"],
    "HPE CRAY XD225V": ["BMC", "BIOS", "MainCPLD", "HDDBPPIC", "PDBPIC"],
    "HPE CRAY XD295V": ["BMC", "BIOS", "MainCPLD", "HDDBPPIC", "PDBPIC"],
    "HPE CRAY XD665": ["BMC", "BIOS", "RT_NVME", "RT_OTHER", "RT_SA", "PDB", "MainCPLD", "UBM6"],
    "HPE CRAY XD670": ["BMCImage1", "BMCImage2", "BIOS", "BIOS2", "BPB_CPLD1", "BPB_CPLD2", "MB_CPLD1", "SCM_CPLD1"],
    }

all_targets = ['BMC', 'BMCImage1', 'BMCImage2', 'BIOS', 'BIOS2', 'MainCPLD',
               'MB_CPLD1', 'BPB_CPLD1', 'BPB_CPLD2', 'SCM_CPLD1', 'PDB', 'PDBPIC', 'HDDBPPIC', 'RT_NVME', 'RT_OTHER', 'RT_SA', 'UBM6']

REQUESTS_TOOLBELT_REQUIRED = "Requests_toolbelt is required for this module"


def has_requests_toolbelt(module):
    """
    Check Request_toolbelt is installed
    :param module:
    """
    if not HAS_REQUESTS_TOOLBELT:
        module.fail_json(msg=REQUESTS_TOOLBELT_REQUIRED)


class CrayRedfishUtils(RedfishUtils):
    def post_multi_request(self, uri, headers, payload):
        username, password, basic_auth = self._auth_params(headers)
        try:
            resp = open_url(uri, data=payload, headers=headers, method="POST",
                            url_username=username, url_password=password,
                            force_basic_auth=basic_auth, validate_certs=False,
                            follow_redirects='all',
                            use_proxy=True, timeout=self.timeout)
            resp_headers = dict((k.lower(), v) for (k, v) in resp.info().items())
            return True
        except Exception as e:
            return False

    def get_model(self):
        response = self.get_request(self.root_uri + "/redfish/v1/Systems/Self")
        if response['ret'] is False:
            return "NA"
        try:
            if 'Model' in response['data']:
                model = response['data'][u'Model']
                if model is not None:
                    model = model[:15]
                else:
                    model = 'None'
            else:
                model = 'None'
            return model
        except Exception:
            if 'Model' in response:
                model = response[u'Model']
                if model is not None:
                    model = model[:15]
                else:
                    model = 'None'
            else:
                model = 'None'
            return model

    def power_state(self):
        response = self.get_request(self.root_uri + "/redfish/v1/Systems/Self")
        if response['ret'] is False:
            return "NA"
        try:
            if 'PowerState' in response['data']:
                state = response['data'][u'PowerState']
                if state is None:
                    state = 'None'
            else:
                state = 'None'
            return state
        except Exception:
            if 'PowerState' in response:
                state = response[u'PowerState']
                if state is None:
                    state = 'None'
            else:
                state = 'None'
            return state

    def power_on(self):
        payload = {"ResetType": "On"}
        target_uri = "/redfish/v1/Systems/Self/Actions/ComputerSystem.Reset"
        response1 = self.post_request(self.root_uri + target_uri, payload)
        time.sleep(120)

    def power_off(self):
        payload = {"ResetType": "ForceOff"}
        target_uri = "/redfish/v1/Systems/Self/Actions/ComputerSystem.Reset"
        response1 = self.post_request(self.root_uri + target_uri, payload)
        time.sleep(120)

    def get_fw_version(self, target):
        try:
            response = self.get_request(self.root_uri + "/redfish/v1/UpdateService/FirmwareInventory" + "/" + target)
            try:
                version = response['data']['Version']
                return version
            except Exception:
                version = response['Version']
                return version
        except Exception:
            return "failed_FI_GET_call/no_version_field"

    def AC_PC_redfish(self):
        payload = {"ResetType": "ForceRestart"}
        target_uri = "/redfish/v1/Systems/Self/Actions/ComputerSystem.Reset"
        response1 = self.post_request(self.root_uri + target_uri, payload)
        time.sleep(180)
        target_uri = "/redfish/v1/Chassis/Self/Actions/Chassis.Reset"
        response2 = self.post_request(self.root_uri + target_uri, payload)
        time.sleep(180)
        return response1 or response2

    def AC_PC_ipmi(self, IP, username, password, routing_value):
        try:
            command = 'ipmitool -I lanplus -H ' + IP + ' -U ' + username + ' -P ' + password + ' raw ' + routing_value
            subprocess.run(command, shell=True, check=True, timeout=15, capture_output=True)
            time.sleep(300)
            return True
        except Exception:
            return False

    def get_sys_fw_inventory(self, attr):
        IP = attr.get('baseuri')
        csv_file_name = attr.get('output_file_name')
        if not os.path.exists(csv_file_name):
            f = open(csv_file_name, "w")
            to_write = """IP_Address, Model, BMC, BMCImage1, BMCImage2, BIOS, BIOS2, MainCPLD, MB_CPLD1,
                            BPB_CPLD1, BPB_CPLD2, SCM_CPLD1, PDB, PDBPIC, HDDBPPIC, RT_NVME, RT_OTHER, RT_SA, UBM6\n"""
            f.write(to_write)
            f.close()
        model = self.get_model()
        entry = []
        entry.append(IP)
        if model.upper() not in supported_models:
            entry.append("unsupported_model")
            for target in all_targets:
                entry.append("NA")
        else:
            entry.append(model)
            for target in all_targets:
                if target in supported_targets[model.upper()]:
                    version = self.get_fw_version(target)
                    if version.startswith("failed"):
                        version = "NA"  # "no_comp/no_version"
                else:
                    version = "NA"
                entry.append(version)
        new_data = ", ".join(entry)
        return {'ret': True, 'changed': True, 'msg': str(new_data)}
    
    def get_PS_CrayXD670(self, attr):
        IP = attr.get('baseuri')
        option = attr.get('power_state')
        csv_file_name = attr.get('output_file_name')
        if not os.path.exists(csv_file_name):
            f = open(csv_file_name, "w")
            to_write = "IP_Address, Model, Power_State\n"
            f.write(to_write)
            f.close()
        model = self.get_model()
        if model.upper() == "HPE CRAY XD670":
            power_state = self.power_state()
            if option.upper() == "NA":
                lis = [IP, model, power_state]
            elif option.upper() == "ON":
                if power_state.upper() == "OFF":
                    self.power_on()
                power_state = self.power_state()
                lis = [IP, model, power_state]
            elif option.upper() == "OFF":
                if power_state.upper() == "ON":
                    self.power_off()
                power_state = self.power_state()
                lis = [IP, model, power_state]
            else:
                return {'ret': False, 'changed': True, 'msg': 'Must specify the correct required option for power_state'}

        else:
            lis = [IP, model, "unsupported_model"]
        new_data = ", ".join(lis)
        return {'ret': True, 'changed': True, 'msg': str(new_data)}


    def target_supported(self, model, target):
        if target in supported_targets[model.upper()]:
            return True
        return False
