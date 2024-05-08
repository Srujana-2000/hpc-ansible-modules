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

from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils
from ansible.module_utils.urls import open_url
try:
    from requests_toolbelt import MultipartEncoder
    HAS_REQUESTS_TOOLBELT = True
except ImportError:
    HAS_REQUESTS_TOOLBELT = False


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
